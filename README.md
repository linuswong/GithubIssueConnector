# GitHub issue snapshot connector

Import one page of open issues from a public GitHub repository into SQLite, then read the saved issues locally. Repeated imports update titles and URLs without duplicates. Rows absent from a later page remain saved.

The project includes a CLI, reusable Python functions, and an optional desktop viewer. Windows verification passed **180 offline tests** on October 7, 2026. Fresh-environment setup and real GitHub imports were verified separately on October 6; see [AI and verification notes](docs/AI_NOTES.md).

## Prerequisites and dependencies

Use Python 3.11 or newer; only Python **3.13.5 on Windows** has been tested. That installation includes SQLite 3.49.1 and Tcl/Tk 8.6.15. Git is needed to clone and manage the repository.

[requirements.txt](requirements.txt) pins the tested direct dependencies:

| Dependency | Version | Purpose |
| --- | --- | --- |
| requests | 2.34.2 | GitHub HTTP requests |
| pytest | 9.1.1 | Automated tests |

SQLite, argparse, JSON, pathlib, tkinter/ttk, and webbrowser come with Python. The optional viewer requires Tk, which some Python distributions install separately. Public repositories need no GitHub token.

## Setup

Run these commands from the project root in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip check
```

Use the environment's executable directly in the commands below. The package is importable from the project root without installing the project or changing PYTHONPATH.

To use the shorter `python` command, activate the environment in the current terminal:

| Shell | Activation command |
| --- | --- |
| PowerShell | `.\.venv\Scripts\Activate.ps1` |
| Command Prompt | `.venv\Scripts\activate.bat` |

If you see `ModuleNotFoundError: No module named 'requests'`, check the interpreter with `python -c "import sys; print(sys.executable)"`. Install dependencies and run the connector with the same environment's Python. If an activation script opens in Notepad, enter its command in the terminal instead. Activation affects only that terminal session. See [Python's venv documentation](https://docs.python.org/3.13/library/venv.html#how-venvs-work).

## Import and read issues

```powershell
.\.venv\Scripts\python.exe main.py import pallets/flask --db issues.db
.\.venv\Scripts\python.exe main.py read pallets/flask --db issues.db
.\.venv\Scripts\python.exe main.py --help
```

Supply a repository as `owner/name`. URLs, whitespace, extra slashes, empty components, backslashes, and exact `.` or `..` components are rejected before HTTP or database work. Repository casing is normalized to lowercase; a valid-looking nonexistent name produces an API error.

The default database is **issues.db in the current working directory**. Relative `--db` paths use that directory; absolute paths select a fixed file. Parent directories must already exist. The connector does not create parents or choose another path on failure.

A read of a missing file in an existing folder, or a database without an issues table, succeeds with an empty result and creates nothing. Corrupt or unusable databases and missing parent folders return `database_error`.

### Example output

This is actual live import output from October 6, 2026, formatted for readability. GitHub data can change:

```json
{
  "success": true,
  "operation": "import",
  "repository": "pallets/flask",
  "count": 1,
  "issues": [
    {
      "repository": "pallets/flask",
      "issue_number": 6146,
      "title": "Add Cloudflare to Flask Hosting Platforms docs?",
      "url": "https://github.com/pallets/flask/issues/6146"
    }
  ],
  "error": null
}
```

A separate read process returned the same issue with `"operation": "read"`. Repeating the import preserved one row; an independent SQLite query found no duplicate composite keys.

An invalid command such as `python main.py import owner/repo/extra` returns the following JSON on stderr with exit code 1:

```json
{
  "success": false,
  "operation": "import",
  "repository": null,
  "count": 0,
  "issues": [],
  "error": {
    "code": "invalid_repository",
    "message": "Use owner/name with letters, digits, dots, underscores, or hyphens; no whitespace, URLs, extra slashes, backslashes, or . / .. components."
  }
}
```

## Reusable functions and result contract

```python
from github_issue_connector import import_issues, read_issues

imported = import_issues("pallets/flask", db_path="snapshot.db")
saved = read_issues("PALLETS/FLASK", db_path="snapshot.db")
```

Both functions accept a string or pathlib.Path database path and return dictionaries without printing or exiting. Their stable keys are:

| Key | Meaning |
| --- | --- |
| success | Whether the operation succeeded |
| operation | import or read |
| repository | Lowercase owner/name; null for invalid input |
| count | Length of the returned issues list |
| issues | Records with repository, issue_number, title, and url |
| error | null on success; an object with code and message on expected failure |

**Import count** covers validated issues in this page after PR exclusion, including updates. **Read count** covers all saved rows for the repository. Import count 1 can accompany read count 2 when an older row is retained. Both lists are ordered by issue number. Failures return count 0 and an empty list; check success to distinguish failure from an empty success.

| CLI outcome | Output | Exit code |
| --- | --- | --- |
| Successful import/read | JSON on stdout | 0 |
| Expected operation failure | JSON on stderr | 1 |
| Missing/invalid arguments | Usage and error text on stderr | 2 |
| --help | Help text on stdout | 0 |

The other output stream is empty in each case. Syntax errors use standard argparse behavior outside the operation JSON contract. Unexpected programming errors keep their tracebacks. See [manual error cases](docs/ERROR_CASES.md) for commands and expected codes.

## Optional desktop viewer

```powershell
.\.venv\Scripts\python.exe viewer.py
.\.venv\Scripts\python.exe viewer.py --db issues.db
```

The viewer uses a GitHub-inspired dark theme. Select a database, click a repository, then select an issue to see its full title and URL.

- The dropdown discovers .db, .sqlite, and .sqlite3 files directly in the working directory. Startup prefers issues.db, otherwise the first discovered file; --db overrides this choice.
- Browse selects an existing file elsewhere. Refresh reloads the database after a separate CLI import.
- Repository counts include all saved rows. Search filters loaded issues by title or number.
- Copy URL copies the selected link. Open on GitHub, double-click, or Enter opens it in the default browser.

Database access is read-only and makes no GitHub request. Missing/corrupt files and incompatible schemas show a message in the window. The viewer supports the connector schema and does not import issues. Native title bars and file dialogs follow the operating system's theme.

## Tests and verification

```powershell
.\.venv\Scripts\python.exe -m pytest -q -rs -p no:cacheprovider
```

Add a test filename before -q for focused checks. Tests mock and guard HTTP while using real temporary SQLite files. They cover import/read, persistence through new connections and processes, updates without duplicates, PR exclusion, repository isolation, configured paths, empty results, failures preserving saved data, rollback, and connection cleanup. CLI tests check JSON, streams, help, and exit codes.

Viewer tests exercise real Tk events, temporary databases, search/selection, error recovery, clipboard/browser boundaries, and layout at 900×640 and 1180×780. They require Tk and a desktop display; unavailable displays skip GUI tests on non-Windows hosts. The cache plugin is disabled because agent runs encountered cache-directory permission errors.

The latest full run passed **180 tests in 2.64 seconds, with no skips**. Fresh-environment verification used a separate .venv/verification-m4, installed only requirements.txt, checked package locations with PYTHONPATH unset, and passed the then-current 157-test CLI suite. Real imports and independent reads were checked separately from automated tests. Commands, corrections, and remaining verification limits are in [AI_NOTES.md](docs/AI_NOTES.md).

## Architecture and limitations

[Architecture.MD](Architecture.MD) describes the components, data flow, schema, configuration, and errors. [sysDes.mmd](sysDes.mmd) contains the CLI flow diagram.

The client requests exactly one page with state=open, per_page=100, and page=1. PRs count toward the 100 entries before filtering. No retries, redirects, or pagination are followed. The 20-second timeout applies to connection/read waits, not total elapsed time. Unauthenticated rate limits and network failures remain possible.

Returned rows are upserted in one transaction; omitted rows remain because a partial page cannot prove closure or deletion. Saved snapshots may therefore include issues that later closed. There is no schema migration or background polling.

The client disables environment-derived authentication with trust_env=False, which also ignores environment proxies and CA-bundle overrides. TLS verification remains enabled. Other Python versions and proxy-dependent networks are unverified. Synchronous viewer reads can pause the window for large or locked databases; native Browse and real browser launching have only been mocked in tests.

## Tools and AI use

| Tool | Use in this project |
| --- | --- |
| ChatGPT/Codex | Requirements, explanations, implementation, review, troubleshooting, documentation, and demo preparation |
| PowerShell, venv, pip | Commands, isolated environments, dependency installation, and version checks |
| requests | Real public imports and prepared responses at the mocked HTTP boundary |
| sqlite3 | Persistence, schema/uniqueness inspection, and transaction rollback verification |
| pytest, unittest.mock, subprocess | Offline tests, temporary databases, and independent CLI processes |
| Git, rg, apply_patch, Python file tools | Source/doc review, edits, ignore checks, and local commits |
| Web browsing | Primary GitHub, Requests, Python, and SQLite references |
| tkinter/ttk, webbrowser | Desktop viewer and its explicit link action |
| Computer-use skill, node_repl, @oai/sky | Earlier Windows viewer inspection and repository/issue selection |

An unfamiliar API detail was that GitHub's Issues endpoint also returns PRs. Codex proposed filtering by the presence of pull_request and saving html_url instead of the API URL. [GitHub's documentation](https://docs.github.com/en/rest/issues/issues#list-repository-issues), a live response containing one issue and three PRs, and tests for null/empty/false PR markers verified the choice.

Another subtlety was transaction cleanup: [Python's sqlite3 connection context](https://docs.python.org/3.13/library/sqlite3.html#how-to-use-the-connection-context-manager) handles commit/rollback but does not open a transaction or close the connection. Explicit BEGIN and finally-close address this. A real trigger rejects a late write after earlier inserts/updates; new connections confirm those earlier changes were rolled back.

## Project documents

- [Start here](START_HERE.md): reading guide.
- [Project brief](docs/PROJECT_BRIEF.md): assessment requirements and design choices.
- [Build plan](docs/BUILD_PLAN.md): completed work and remaining delivery steps.
- [AI notes](docs/AI_NOTES.md): actual tools, results, corrections, and limitations.
- [Demo script](docs/DEMO.md): 1:45 walkthrough and delivery checklist.
- [Agent instructions](AGENTS.md) and [historical setup prompt](CODING_PROMPT.md): development guidance.

Recording, publication, reviewer access, and email submission remain unverified.
