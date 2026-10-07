# GitHub issue snapshot connector

Import one page of open issues from a public GitHub repository into SQLite, then read saved issues locally. Repeated imports update returned records without duplicates. Previously saved rows remain when absent from later pages.

Final verification completed on October 6, 2026: clean-environment setup, 157 automated tests, two real imports, separate-process reads, SQLite key/uniqueness checks, and expected errors. Recording, reviewer access, and submission remain manual tasks. See [verification evidence](docs/AI_NOTES.md#milestone-4--october-6-2026) and the [1:45 demo script](docs/DEMO.md).

## Prerequisites and dependencies

Python 3.11+ is the chosen baseline; Windows verification used Python 3.13.5 and bundled SQLite 3.49.1. Only that Python version was tested. Git 2.33.0.windows.2 was used for repository review; Git is needed to clone/manage the source, not to run the connector.

requirements.txt pins the direct dependencies actually tested: requests 2.34.2 for HTTP and pytest 9.1.1 for tests. pip installs their transitive dependencies. sqlite3, argparse, json, and pathlib come with Python. No GitHub token or package installation of this project is required.

## Setup

From the project root in Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m pytest --version
```

Use the environment's executable directly; activation and execution-policy changes are unnecessary. Keep the project root as the working directory for the commands and Python imports below. The flat package is importable there without PYTHONPATH or global packages.

To verify setup separately without reusing an existing environment, choose an unused path. Milestone 4 used the following path under ignored .venv and substituted that executable in all run/test commands:

```powershell
python -m venv .venv/verification-m4
.\.venv\verification-m4\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\verification-m4\Scripts\python.exe -m pip check
.\.venv\verification-m4\Scripts\python.exe -m pytest --version
```

It initially contained only pip, had include-system-site-packages=false, and loaded requests/pytest from its own site-packages. pip check reported no broken requirements. Agent-run environment creation, installation, tests, and live requests used approved execution outside sandbox restrictions because earlier milestones demonstrated temporary-file permission failures. This is an agent-environment limitation, not a dependency or application setup step; details are in AI_NOTES.md.

## Commands and actual output

```powershell
.\.venv\Scripts\python.exe main.py --help
.\.venv\Scripts\python.exe main.py import --help
.\.venv\Scripts\python.exe main.py read --help
.\.venv\Scripts\python.exe main.py import pallets/flask --db ./issues.db
.\.venv\Scripts\python.exe main.py read pallets/flask --db ./issues.db
```

Supply owner/name, not a URL. Repository casing is normalized to lowercase. With the environment active, the equivalent command starts with `python main.py`.

Actual live import output on October 6, 2026, using the clean interpreter and disposable ./milestone4-live.db:

```json
{"success": true, "operation": "import", "repository": "pallets/flask", "count": 1, "issues": [{"repository": "pallets/flask", "issue_number": 6146, "title": "Add Cloudflare to Flask Hosting Platforms docs?", "url": "https://github.com/pallets/flask/issues/6146"}], "error": null}
```

A separate CLI read returned the same data with operation="read". Repeating the real import and read returned that row again. A direct SQLite GROUP BY repository, issue_number HAVING COUNT(*) > 1 query returned no rows after each import; PRAGMA table_info confirmed the two-column primary key. These are live connector results, distinct from mocked tests. GitHub data can change before recording.

Both commands default to issues.db in the process's **current working directory**, rather than beside main.py. Relative --db paths follow that rule; an absolute path selects a fixed file. Parent directories must exist; the connector neither creates them nor chooses a fallback. Reading a missing file in an existing parent, or a valid database without an issues table, succeeds with an empty result without creating anything. Unusable databases and missing parents return database_error.

## Reusable functions and result contract

```python
from github_issue_connector import import_issues, read_issues

imported = import_issues("pallets/flask", db_path="snapshot.db")
saved = read_issues("PALLETS/FLASK", db_path="snapshot.db")
```

The functions return dictionaries; they do not print or exit. The same functions are available from github_issue_connector.connector. Both accept str or pathlib.Path database paths.

Stable keys are success, operation, repository, count, issues, and error. Successful results have error=null. Expected failures have count=0, issues=[], and error={"code": ..., "message": ...}. Invalid input has repository=null; otherwise it is normalized. Check success to distinguish an empty success from a failure.

Import count is the number of validated issues processed **in this page**, after PR exclusion, including updates to saved rows. Read count is **all saved rows** for the requested repository, sorted by issue_number. Import count=1 can accompany read count=2 when an earlier row is retained. Import results are also sorted by issue_number.

This malformed input was verified to return the following JSON on stderr and exit 1, with stdout empty and the saved database unchanged:

```powershell
.\.venv\Scripts\python.exe main.py import owner/repo/extra --db ./issues.db
```

```json
{"success": false, "operation": "import", "repository": null, "count": 0, "issues": [], "error": {"code": "invalid_repository", "message": "Use owner/name with letters, digits, dots, underscores, or hyphens; no whitespace, URLs, extra slashes, backslashes, or . / .. components."}}
```

| CLI outcome | Output | Exit code |
| --- | --- | --- |
| Successful import/read | JSON on stdout; stderr empty | 0 |
| Expected operation failure | JSON on stderr; stdout empty | 1 |
| Argument-parser error | Usage/error text on stderr; stdout empty | 2 |
| --help | Help text on stdout; stderr empty | 0 |

Missing/unknown commands, missing repository arguments, unknown flags, and --db without a path use [argparse's standard usage/error behavior](https://docs.python.org/3.13/library/argparse.html#exiting-methods); they are outside the operation JSON contract. The --db-without-path case was checked in a separate process and returned exit 2. Unexpected programming bugs propagate with a traceback.

## Tests

```powershell
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
```

For focused checks, add tests/test_github_client.py, tests/test_database.py, or tests/test_connector.py tests/test_cli.py before -q. The optional cache plugin is disabled because earlier agent runs encountered cache-directory permission failures.

The documented full command, with only the clean interpreter path substituted and PYTHONPATH unset, passed all 157 tests. Tests intercept HTTPAdapter.send and guard child processes against HTTP; no automated test contacts live GitHub. Real tmp_path SQLite files verify persistence, updates, uniqueness, repository isolation, configured/default paths, empty results, retained omissions, malformed-page/API-failure preservation, rollback, and connection cleanup. CLI tests check streams, JSON, help, exit codes, and separate-process reads. No tests or features were added during final verification.

## Architecture and limitations

See [Architecture.MD](Architecture.MD). Exactly one page is requested with state=open, per_page=100, page=1; PRs count toward those 100 entries before exclusion. No retries, redirects, or pagination are followed. The 20-second timeout bounds connection/read waits, not total runtime. Public access requires no token; rate limits and network/API failures remain possible. trust_env=False prevents implicit .netrc credentials and also ignores environment proxies and CA-bundle overrides. TLS verification stays enabled.

Upserts retain absent rows because a partial page cannot establish closure/deletion. Saved data can therefore include issues that later closed. There is no schema migration. Older Python versions and proxy-dependent networks remain unverified.

## AI and other tools actually used

| Tool | Actual use |
| --- | --- |
| ChatGPT/Codex | Clarified requirements, explained decisions, implemented milestones 1–3, reviewed code/docs, and prepared verification/demo instructions |
| PowerShell, Python venv, pip | Ran commands, created isolated environments, installed documented dependencies, and checked actual versions |
| Requests | Performed unauthenticated GitHub requests; prepared/decoded controlled responses in tests |
| sqlite3 | Persisted records, inspected schema and duplicate groups, and exercised a real late-failure trigger in tests |
| pytest, unittest.mock | Ran automated checks with a guarded HTTP boundary and real temporary databases |
| subprocess | Ran independent CLI processes and captured stdout, stderr, and exit codes |
| Git, apply_patch | Inspected tracked and untracked contents, checked ignore rules, edited documentation, and staged/reviewed the submission for a local commit; publication and submission remain pending |
| Web browsing | Checked primary GitHub, Requests, Python, and SQLite documentation across milestones |

[AI_NOTES.md](docs/AI_NOTES.md) records actual commands, results, corrections, and limitations. Developer review/comprehension is not claimed merely because agent checks passed.

## Unfamiliar problem and verification

GitHub's Issues endpoint also returns pull requests. Codex proposed filtering by the presence of pull_request and storing html_url for the browser link. [GitHub's primary documentation](https://docs.github.com/en/rest/issues/issues#list-repository-issues) confirms the PR marker and public access. Milestone 0's live exploration returned four entries: one issue and three PRs. Milestone 1 tests verify key presence even when its value is null/empty/false and distinguish html_url from the API url. Milestone 4's real connector import saved issue #6146. These are distinct observations and test checks, not a claim that the developer has mastered the API.

A second subtlety is transaction cleanup. [Python's sqlite3 documentation](https://docs.python.org/3.13/library/sqlite3.html#how-to-use-the-connection-context-manager) says its connection context handles commit/rollback without opening a transaction or closing the connection. Codex proposed explicit BEGIN plus finally-close. A real SQLite trigger verifies an earlier insert and update occurred before rejecting a later write; independent connections then verify both earlier changes were rolled back. This test passed again in final verification.
