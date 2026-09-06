# PythonAnywhere Auto-Renewal Bot

Automatically renew PythonAnywhere free-tier web apps and scheduled tasks every 15 days using GitHub Actions. Version 1.4.0 supports one or many accounts without requiring the legacy account variables.

![Python](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-Automated-2088FF?logo=github-actions&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Schedule](https://img.shields.io/badge/Runs-1st%20%26%2015th%20Monthly-brightgreen.svg)

**[Main App Demo](https://tanishqmudaliar.pythonanywhere.com)** | **[Weather Monitoring System](https://github.com/tanishqmudaliar/Weather-Monitoring-System)**

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Quick Setup](#quick-setup)
  - [Local Testing](#local-testing)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Account Configuration Examples](#account-configuration-examples)
- [Workflow Logs](#workflow-logs)
- [Related Repositories](#related-repositories)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

PythonAnywhere free tier apps expire after ~~3 months~~ **1 month** of inactivity _(updated Jan 2026)_. This bot automatically renews your web app by logging into PythonAnywhere and clicking the "Extend" button every 15 days via GitHub Actions.

Combined with the [Weather-Monitoring-System](https://github.com/tanishqmudaliar/Weather-Monitoring-System) auto-deployment webhook, this creates a completely hands-off hosting solution that stays alive indefinitely on the free tier.

### The Problem

```
Day 1:   Deploy app ✅
Day 30:  App expires ❌
Day 31:  Users see error page 😢
Day 32:  Manual renewal... again 😤
```

### The Solution

```
Day 1:   Deploy app ✅
Day 15:  Bot auto-renews ✅
Day 30:  Bot auto-renews ✅
...forever! 🎉
```

---

## Features

### Automation

- Scheduled renewal on the 1st and 15th of every month (04:00 UTC / 09:30 IST)
- Manual trigger available from GitHub Actions tab
- Automatic log commits prevent GitHub from disabling the workflow
- Renews every configured account independently with a separate login session

### Logging & Monitoring

- Complete audit trail in `.github/logs/workflow_runs.log`
- Clear SUCCESS, PARTIAL, or FAILED status indicators
- Timestamps, run IDs, and trigger source for debugging
- Detailed per-account results showing exactly which items were renewed and
  their old vs. new expiry dates
- Explicit reporting for incomplete credentials, duplicate accounts, skipped
  items, and request failures

### Security

- Credentials stored as encrypted GitHub Secrets or a local `.env` file
- Passwords are never written to the committed audit log
- GitHub Actions masks configured usernames and passwords in the live console
- HTTPS for all PythonAnywhere connections

---

## Tech Stack

| Layer         | Technologies                            |
| ------------- | --------------------------------------- |
| **Language**  | Python 3.9+                             |
| **Libraries** | requests, beautifulsoup4, python-dotenv |
| **CI/CD**     | GitHub Actions                          |
| **Target**    | PythonAnywhere Free Tier                |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    FULLY AUTOMATED PYTHONANYWHERE HOSTING                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                              GITHUB                                  │   │
│  │                                                                      │   │
│  │   ┌─────────────────────────────┐  ┌─────────────────────────────┐   │   │
│  │   │  Weather-Monitoring-System  │  │  PythonAnywhere-Auto-Renew  │   │   │
│  │   │                             │  │                             │   │   │
│  │   │  • Main application code    │  │  • Renewal bot (this repo)  │   │   │
│  │   │  • Deployment endpoint      │  │  • Runs 1st & 15th monthly  │   │   │
│  │   │  • Auto-deploys on push     │  │  • Keeps app alive forever  │   │   │
│  │   └──────────────┬──────────────┘  └──────────────┬──────────────┘   │   │
│  │                  │ POST request                   │ GitHub           │   │
│  │                  │ (/github-webhook)              │ Actions          │   │
│  │                  ▼                                ▼                  │   │
│  └──────────────────┼────────────────────────────────┼──────────────────┘   │
│                     │                                │                      │
│  ┌──────────────────▼────────────────────────────────▼──────────────────┐   │
│  │                            PYTHONANYWHERE                            │   │
│  │                                                                      │   │
│  │      ┌─────────────────────────┐    ┌─────────────────────────┐      │   │
│  │      │   Deployment Endpoint   │    │     Auto-Renewal        │      │   │
│  │      │  • git pull             │    │  • Extends app expiry   │      │   │
│  │      │  • pip install          │    │  • Prevents shutdown    │      │   │
│  │      │  • Reload webapp        │    │  • Zero maintenance     │      │   │
│  │      └─────────────────────────┘    └─────────────────────────┘      │   │
│  │                                                                      │   │
│  │              https://tanishqmudaliar.pythonanywhere.com              │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│               Push code → Instantly live → Stays alive forever              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### How It Works

1. GitHub Actions runs the workflow on the 1st and 15th of each month.
2. The script discovers complete `PA_*`, numbered, and JSON account
   configurations.
3. Each configured account gets its own authenticated session.
4. The script renews web apps and scheduled tasks for that account.
5. Results are written directly to `.github/logs/workflow_runs.log`.
6. The workflow commits the detailed log and pushes it back to the repository.

---

## Getting Started

### Prerequisites

- PythonAnywhere free account with a web app or scheduled task
- GitHub account
- 5 minutes of setup time

### Quick Setup

#### Step 1: Fork or Clone

```bash
git clone https://github.com/tanishqmudaliar/PythonAnywhere-Auto-Renew.git
cd PythonAnywhere-Auto-Renew
```

Or click **"Use this template"** on GitHub.

#### Step 2: Add GitHub Secrets

1. Go to your repository → **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret** and add:

| Secret Name   | Value                        |
| ------------- | ---------------------------- |
| `PA_USERNAME` | Optional legacy account username |
| `PA_PASSWORD` | Optional legacy account password |

For multiple accounts, add numbered secret pairs such as
`ACCOUNT_1_USERNAME` and `ACCOUNT_1_PASSWORD`. Numbered pairs do not need to be
consecutive. The `PA_*` pair is optional and can be used together with numbered
pairs or omitted entirely.

The workflow exposes numbered pairs 1 through 10. For more than ten accounts,
or to manage all accounts in one secret, use `ACCOUNT_CREDENTIALS_JSON`:

```json
[
  {"username": "account_one", "password": "password_one"},
  {"username": "account_two", "password": "password_two"}
]
```

#### Step 3: Enable Workflow Permissions

1. Go to **Settings** → **Actions** → **General**
2. Under **Workflow permissions**, select **"Read and write permissions"**
3. Check **"Allow GitHub Actions to create and approve pull requests"**
4. Click **Save**

#### Step 4: Test the Workflow

1. Go to the **Actions** tab
2. Click **Auto-Renew PythonAnywhere**
3. Click **Run workflow** → **Run workflow**
4. Verify the run shows each configured account and creates a detailed entry in
   `.github/logs/workflow_runs.log`.

### Local Testing

1. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

2. **Create a `.env` file**

   ```env
   PA_USERNAME=your_username
   PA_PASSWORD=your_password
   ```

   The legacy pair is optional. Numbered local variables also work:

   ```env
   ACCOUNT_1_USERNAME=first_username
   ACCOUNT_1_PASSWORD=first_password
   ACCOUNT_3_USERNAME=third_username
   ACCOUNT_3_PASSWORD=third_password
   ```

   Or use JSON for any number of accounts:

   ```env
   ACCOUNT_CREDENTIALS_JSON=[{"username":"first_username","password":"first_password"}]
   ```

3. **Run the script**
   ```bash
   python renew_python_anywhere.py
   ```

The script writes the detailed result to `.github/logs/workflow_runs.log`.
The terminal output includes one processing section per complete account:

```
🔐 Logging in as your_username...
✅ Login successful
📊 Checking web apps...
🗓️ Checking scheduled tasks...
```

---

## Project Structure

```
PythonAnywhere-Auto-Renew/
├── .github/
│   ├── workflows/
│   │   └── renew.yml              # GitHub Actions workflow
│   └── logs/
│       └── workflow_runs.log      # Auto-generated run history
├── renew_python_anywhere.py       # Main renewal script
├── requirements.txt               # Python dependencies
├── .env                           # Local credentials (not in git)
├── .gitignore                     # Git ignore rules
├── LICENSE                        # MIT License
└── README.md                      # Project documentation
```

## Account Configuration Examples

### Legacy account only

```env
PA_USERNAME=main_username
PA_PASSWORD=main_password
```

### Numbered accounts only

```env
ACCOUNT_1_USERNAME=first_username
ACCOUNT_1_PASSWORD=first_password
ACCOUNT_3_USERNAME=third_username
ACCOUNT_3_PASSWORD=third_password
```

Account 2 may be absent. The script still discovers account 3.

### Mixed legacy and numbered accounts

```env
PA_USERNAME=main_username
PA_PASSWORD=main_password
ACCOUNT_1_USERNAME=first_username
ACCOUNT_1_PASSWORD=first_password
```

All complete unique accounts are processed. If the same credentials are
configured twice, the duplicate is skipped and recorded as a warning.

### Incomplete credentials

```env
ACCOUNT_2_USERNAME=missing_password
```

The account is not processed and the run is marked `PARTIAL` if at least one
other complete account runs successfully.

### JSON credentials

```json
[
  {"username": "first_username", "password": "first_password"},
  {"username": "second_username", "password": "second_password"}
]
```

Store the JSON as the value of `ACCOUNT_CREDENTIALS_JSON`. Invalid JSON or
incomplete entries are reported in the log.

---

## Configuration

### Environment Variables

| Variable      | Description             | Required |
| ------------- | ----------------------- | -------- |
| `PA_USERNAME` | Optional PythonAnywhere username | No |
| `PA_PASSWORD` | Optional PythonAnywhere password | No |
| `ACCOUNT_N_USERNAME` | Optional numbered account username | No |
| `ACCOUNT_N_PASSWORD` | Optional numbered account password | No |
| `ACCOUNT_CREDENTIALS_JSON` | Optional JSON list or object of accounts | No |

### Schedule Customization

Edit `.github/workflows/renew.yml` to change the cron schedule:

```yaml
# Current: 1st and 15th at 04:00 UTC
- cron: "0 4 1,15 * *"

# Alternative: Every Monday at noon UTC
- cron: "0 12 * * 1"

# Alternative: Every 10 days
- cron: "0 4 1,11,21 * *"
```

---

## Workflow Logs

Every run is logged to `.github/logs/workflow_runs.log`:

Every run appends one detailed block to `.github/logs/workflow_runs.log`.
`SUCCESS` means every configured account completed. `PARTIAL` means the
renewals completed but at least one credential pair was incomplete.
`FAILED` means at least one account renewal failed or no complete account was
available.

### Success Entry

```
========================================
Workflow Run: 2026-07-15 04:00:00 UTC
Status: SUCCESS
Trigger: schedule
Repository: username/PythonAnywhere-Auto-Renew
Branch: main
Run ID: 123456789
Configured accounts:
- PA: mainuser
- ACCOUNT_1: accountone
Renewal details:
- PA: SUCCESS
  - Web App: mainuser.pythonanywhere.com (old date → new date)
- ACCOUNT_1: SUCCESS
  - Task: python3 sync.py (Already maxed out at: 2026-08-11)
========================================
```

### Partial Entry

```
========================================
Workflow Run: 2026-07-15 04:00:00 UTC
Status: PARTIAL
Trigger: schedule
Repository: username/PythonAnywhere-Auto-Renew
Branch: main
Run ID: 123456790
Configured accounts:
- PA: mainuser
Incomplete or skipped credentials:
- ACCOUNT_2_USERNAME/ACCOUNT_2_PASSWORD
Renewal details:
- PA: SUCCESS
  - Web App: mainuser.pythonanywhere.com (old date → new date)
========================================
```

### Failed Entry

```text
========================================
Workflow Run: 2026-07-15 04:00:00 UTC
Status: FAILED
Trigger: schedule
Repository: username/PythonAnywhere-Auto-Renew
Branch: main
Run ID: 123456790
Configured accounts:
- PA: mainuser
- ACCOUNT_1: accountone
Renewal details:
- PA: SUCCESS
  - Web App: mainuser.pythonanywhere.com (old date → new date)
- ACCOUNT_1: FAILED
  - Login failed
========================================
```

---

## Related Repositories

| Repository                                                                                | Purpose                                       |
| ----------------------------------------------------------------------------------------- | --------------------------------------------- |
| [Weather-Monitoring-System](https://github.com/tanishqmudaliar/Weather-Monitoring-System) | Main weather app with auto-deployment webhook |
| [PythonAnywhere-Auto-Renew](https://github.com/tanishqmudaliar/PythonAnywhere-Auto-Renew) | Keeps the app alive on free tier (this repo)  |

Together, these repositories provide:

- Instant automated deployment on every push
- 24/7 uptime without manual intervention
- Zero-maintenance free-tier hosting

---

## Troubleshooting

### "Login failed"

- Verify the relevant `PA_*`, `ACCOUNT_N_*`, or JSON credentials are correct
- Try logging in manually to confirm credentials work
- Check if PythonAnywhere changed their login page

### "No complete accounts were configured"

- Add either a complete `PA_USERNAME` and `PA_PASSWORD` pair.
- Add at least one complete numbered pair.
- Add a valid `ACCOUNT_CREDENTIALS_JSON` list or object.
- Empty numbered slots are ignored. Partially populated slots are reported as
  incomplete.

### "No web apps found on this account"

- This is normal, your app doesn't need renewal yet
- The renewal form only appears when renewal is due
- Logged as SUCCESS ✅ (not an error)

### "Task returned 200 (expiry unchanged... already maxed out)"

- PythonAnywhere caps scheduled task extensions (usually a maximum of 30 days into the future).
- If you run the bot frequently or trigger it manually, a task might already be at its maximum expiry limit.
- The bot recognizes this and safely logs it as a SUCCESS ✅ without failing your workflow.

### "Workflow disabled"

- GitHub disables inactive workflows after 60 days
- This bot commits logs every 15 days to prevent this
- Re-enable manually if needed, then run the workflow

### Log shows "FAILED"

- Check the GitHub Actions workflow run for detailed error logs
- Common causes: wrong credentials, PythonAnywhere site changes
- Workflow retries automatically on the next scheduled run

---

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Commit your changes (`git commit -m 'Add improvement'`)
4. Push to the branch (`git push origin feature/improvement`)
5. Open a Pull Request

---

## License

This project is open source and available under the [MIT License](LICENSE).

---

Made with ❤️ by [Tanishq Mudaliar](https://github.com/tanishqmudaliar)

**Stop manually clicking that extend button. Automate it! 🚀**






# Update



## same as before; but this time, you can create any number of env variables:

Create env variables:

ACCOUNT_1_USERNAME
ACCOUNT_1_PASSWORD

ACCOUNT_2_USERNAME
ACCOUNT_2_PASSWORD

ACCOUNT_3_USERNAME
ACCOUNT_3_PASSWORD

and so on...

fill it valid data and the code should renew webapps on all the accounts
