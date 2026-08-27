import os
import sys
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
from dotenv import load_dotenv

load_dotenv()   # load variables from .env file

# ------------------------------------------------------------
# Helper to discover all accounts from environment variables
# ------------------------------------------------------------
def get_accounts_from_env():
    """
    Looks for variables like ACCOUNT_1_USERNAME, ACCOUNT_1_PASSWORD, ...
    Returns a list of dicts: [{'username': ..., 'password': ...}, ...]
    Also falls back to single PA_USERNAME/PA_PASSWORD if no multiple accounts found.
    """
    accounts = []
    # First, try to find multiple accounts
    i = 1
    while True:
        username = os.environ.get(f'ACCOUNT_{i}_USERNAME')
        password = os.environ.get(f'ACCOUNT_{i}_PASSWORD')
        if username and password:
            accounts.append({'username': username, 'password': password})
            i += 1
        else:
            # If we didn't find any at all, break
            if i == 1:
                break
            # If we found some but the next is missing, stop searching
            else:
                break

    # If no multiple accounts found, fall back to single-account variables
    if not accounts:
        single_user = os.environ.get('PA_USERNAME')
        single_pass = os.environ.get('PA_PASSWORD')
        if single_user and single_pass:
            accounts.append({'username': single_user, 'password': single_pass})

    return accounts

# ------------------------------------------------------------
# Original functions (slightly adapted to take username/password)
# ------------------------------------------------------------
def login(session, username, password):
    BASE_URL = "https://www.pythonanywhere.com"
    LOGIN_URL = f"{BASE_URL}/login/"
    print(f"🔐 Logging in as {username}...")
    login_page = session.get(LOGIN_URL, timeout=10)
    login_page.raise_for_status()
    soup = BeautifulSoup(login_page.content, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'})
    if not csrf_token:
        print("❌ Could not find CSRF token on login page")
        return False
    csrf_token = csrf_token['value']

    payload = {
        'csrfmiddlewaretoken': csrf_token,
        'auth-username': username,
        'auth-password': password,
        'login_view-current_step': 'auth'
    }
    response = session.post(
        LOGIN_URL,
        data=payload,
        headers={'Referer': LOGIN_URL},
        timeout=10,
        allow_redirects=True
    )
    response.raise_for_status()

    if "Log out" not in response.text and "logout" not in response.text.lower():
        print("❌ Login failed - 'Log out' not found in response")
        return False
    if "login" in response.url.lower():
        print("❌ Login failed - still on login page")
        return False

    print("✅ Login successful")
    return True


def get_webapp_expiry(soup, domain):
    pane_id = f"id_{domain.replace('.', '_')}"
    pane = soup.find(id=pane_id)
    if pane:
        expiry_elem = pane.find('p', class_='webapp_expiry')
        if expiry_elem and expiry_elem.find('strong'):
            return expiry_elem.find('strong').text.strip()
    return "Unknown Date"


def renew_webapps(session, username):
    BASE_URL = "https://www.pythonanywhere.com"
    DASHBOARD_URL = f"{BASE_URL}/user/{username}/webapps/"
    print("📊 Checking web apps...")
    time.sleep(1)
    dashboard = session.get(DASHBOARD_URL, timeout=10)
    dashboard.raise_for_status()
    soup = BeautifulSoup(dashboard.content, 'html.parser')

    forms = [f for f in soup.find_all('form', action=True) if '/extend' in f['action'].lower()]
    renewed_details = []

    if not forms:
        print("ℹ️ No web apps found on this account.")
        return True, renewed_details

    ok = True
    for form in forms:
        action = urljoin(BASE_URL, form['action'])
        domain = action.rstrip('/').split('/webapps/')[-1].replace('/extend', '')
        csrf = form.find('input', {'name': 'csrfmiddlewaretoken'})
        if not csrf:
            print(f"❌ No CSRF token for {domain}, skipping")
            ok = False
            continue

        old_expiry = get_webapp_expiry(soup, domain)

        r = session.post(
            action,
            data={'csrfmiddlewaretoken': csrf['value']},
            headers={'Referer': DASHBOARD_URL},
            timeout=10
        )
        if r.status_code == 200 and 'webapps' in r.url.lower():
            time.sleep(1)
            dash_after = session.get(DASHBOARD_URL, timeout=10)
            soup_after = BeautifulSoup(dash_after.content, 'html.parser')
            new_expiry = get_webapp_expiry(soup_after, domain)

            detail = f"Web App: {domain} ({old_expiry} → {new_expiry})"
            print(f"✅ Renewed web app: {domain} ({old_expiry} → {new_expiry})")
            renewed_details.append(detail)
        else:
            print(f"❌ Failed to renew web app: {domain} (status {r.status_code})")
            ok = False

    print(f"📋 Web apps renewed: {len(renewed_details)}")
    return ok, renewed_details


def renew_scheduled_tasks(session, username):
    BASE_URL = "https://www.pythonanywhere.com"
    TASKS_PAGE_URL = f"{BASE_URL}/user/{username}/tasks_tab/"
    TASKS_API_URL = f"{BASE_URL}/api/v0/user/{username}/schedule/"
    print("🗓️ Checking scheduled tasks...")
    time.sleep(1)
    csrftoken = session.cookies.get('csrftoken')
    r = session.get(TASKS_API_URL, headers={'Referer': TASKS_PAGE_URL}, timeout=10)

    renewed_details = []

    if r.status_code != 200:
        print(f"❌ Could not fetch scheduled tasks (status {r.status_code})")
        return False, renewed_details

    try:
        tasks = r.json()
    except ValueError:
        print("❌ Scheduled tasks response was not valid JSON")
        return False, renewed_details

    if not tasks:
        print("ℹ️ No scheduled tasks found on this account.")
        return True, renewed_details

    ok = True
    for task in tasks:
        extend_url = task.get('extend_url')
        desc = task.get('command') or f"task {task.get('id')}"
        old_expiry = task.get('expiry')
        if not extend_url:
            continue

        resp = session.post(
            urljoin(BASE_URL, extend_url),
            headers={'X-CSRFToken': csrftoken, 'Referer': TASKS_PAGE_URL},
            timeout=10
        )
        if resp.status_code == 200:
            time.sleep(1)
            r_after = session.get(TASKS_API_URL, headers={'Referer': TASKS_PAGE_URL}, timeout=10)
            new_expiry = old_expiry
            try:
                tasks_after = r_after.json()
                new_expiry = next((t.get('expiry') for t in tasks_after if t.get('id') == task.get('id')), old_expiry)
            except ValueError:
                pass

            if new_expiry != old_expiry:
                detail = f"Task: {desc} ({old_expiry} → {new_expiry})"
                print(f"✅ Renewed scheduled task: {desc} ({old_expiry} → {new_expiry})")
                renewed_details.append(detail)
            else:
                detail = f"Task: {desc} (Already maxed out at: {old_expiry})"
                print(f"✅ Task {desc} returned 200 (expiry unchanged at {old_expiry} — already maxed out)")
                renewed_details.append(detail)
        else:
            print(f"❌ Failed to renew scheduled task: {desc} (status {resp.status_code})")
            ok = False

    print(f"📋 Scheduled tasks renewed: {len(renewed_details)}")
    return ok, renewed_details


def renew_account(username, password):
    """Renew web apps and tasks for a single account."""
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })

    try:
        if not login(session, username, password):
            return False, []

        webapps_ok, webapps_renewed = renew_webapps(session, username)
        tasks_ok, tasks_renewed = renew_scheduled_tasks(session, username)
        all_renewed = webapps_renewed + tasks_renewed
        return (webapps_ok and tasks_ok), all_renewed

    except requests.Timeout:
        print("❌ Request timed out")
        return False, []
    except requests.RequestException as e:
        print(f"❌ Network error: {e}")
        return False, []
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False, []


# ------------------------------------------------------------
# Main: loop over all accounts discovered from environment
# ------------------------------------------------------------
def main():
    accounts = get_accounts_from_env()

    if not accounts:
        print("❌ No accounts found. Please set environment variables:")
        print("   Either ACCOUNT_1_USERNAME/ACCOUNT_1_PASSWORD, ACCOUNT_2_..., etc.")
        print("   Or fallback to PA_USERNAME/PA_PASSWORD.")
        sys.exit(1)

    all_summaries = []
    overall_success = True

    for idx, acc in enumerate(accounts, 1):
        username = acc.get('username')
        password = acc.get('password')
        if not username or not password:
            print(f"⚠️ Skipping account #{idx} – missing username or password")
            continue

        print(f"\n{'='*50}")
        print(f"Processing account {idx}/{len(accounts)}: {username}")
        print('='*50)

        success, details = renew_account(username, password)
        if not success:
            overall_success = False

        all_summaries.append(f"Account: {username}")
        if details:
            for d in details:
                all_summaries.append(f"  - {d}")
        else:
            all_summaries.append("  - No items renewed (or nothing to renew).")
        all_summaries.append("")

    # Write combined summary to file (for GitHub Actions, etc.)
    with open("renewal_summary.txt", "w", encoding="utf-8") as f:
        if all_summaries:
            f.write("\n".join(all_summaries))
        else:
            f.write("No accounts processed.\n")

    sys.exit(0 if overall_success else 1)


if __name__ == "__main__":
    main()
