# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.3.0] - 2026-07-14

### Added

- Detailed account, web app, and scheduled-task results are written directly to
  `.github/logs/workflow_runs.log`.
- Support for optional legacy credentials, numbered account pairs, and JSON
  account credentials.

### Changed

- Web app expiry date extraction now uses robust HTML DOM parsing (via BeautifulSoup) instead of regex.
- Scheduled tasks renewal now re-fetches the tasks API to guarantee accurate logging of the updated expiry date.
- GitHub Actions now passes configured account credentials to the renewal script.

### Fixed

- Fixed an issue where scheduled tasks already at their maximum expiry limit caused the GitHub Actions workflow to fail. Unchanged dates are now treated as successful "maxed out" renewals.

## [1.2.1] - 2026-07-13

### Changed

- Reformatted README tables and code fences for consistent Markdown styling

## [1.2.0] - 2026-01-25

### Changed

- Overhauled README documentation for clarity, structure, and additional usage details

## [1.1.0] - 2026-01-10

### Added

- Manual workflow trigger via GitHub Actions `workflow_dispatch`
- Success/failure run logging, committed to `.github/logs/workflow_runs.log`
- MIT License

### Changed

- Refactored renewal and keep-alive logic for reliability
- Renamed and reorganized the renewal script
- Revised README for clarity and additional feature coverage

## [1.0.0] - 2026-01-10

### Added

- Initial renewal script (`renew_python_anywhere.py`) using `requests` + `BeautifulSoup`
- GitHub Actions workflow to run the renewal job on a schedule
- `.gitignore` for environment and IDE files
- Initial README

[Unreleased]: https://github.com/tanishqmudaliar/PythonAnywhere-Auto-Renew/compare/v1.3.0...HEAD
[1.3.0]: https://github.com/tanishqmudaliar/PythonAnywhere-Auto-Renew/compare/v1.2.1...v1.3.0
[1.2.1]: https://github.com/tanishqmudaliar/PythonAnywhere-Auto-Renew/compare/v1.2.0...v1.2.1
[1.2.0]: https://github.com/tanishqmudaliar/PythonAnywhere-Auto-Renew/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/tanishqmudaliar/PythonAnywhere-Auto-Renew/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/tanishqmudaliar/PythonAnywhere-Auto-Renew/releases/tag/v1.0.0
