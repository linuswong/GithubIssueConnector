# Architecture

A flat Python package provides the connector logic. Thin CLI and optional Tkinter launchers call it. [Verification evidence](docs/AI_NOTES.md) is separate from this implementation reference.

## Interfaces and results

```python
from github_issue_connector import import_issues, read_issues

imported = import_issues("owner/repo", db_path="issues.db")
saved = read_issues("owner/repo", db_path="issues.db")
```

Both functions accept string or pathlib.Path paths and return a dictionary with success, operation, repository, count, issues, and error. Issue records contain repository, issue_number, title, and url.

Success has error=null. Expected failure has count=0, issues=[], and error with code/message. Repository is lowercase for valid input and null for invalid input. Import count covers this page after PR filtering, including updates; read count covers all saved rows. Both issue lists sort by issue_number.

The CLI is `python main.py import|read owner/repo [--db PATH]`. The optional desktop launcher is `python viewer.py [--db PATH]`. [README.md](README.md) provides runnable commands and JSON examples.

## Components

Paths below are relative to the repository root.

| File | Responsibility |
| --- | --- |
| main.py | Parse arguments, call one public function, print JSON, set exit code |
| viewer.py | Parse the initial database path and start the desktop window |
| github_issue_connector/__init__.py | Export the two public functions |
| github_issue_connector/connector.py | Coordinate validation, client, storage, and result construction |
| github_issue_connector/validation.py | Validate owner/name and normalize casing |
| github_issue_connector/github_client.py | Fetch one page, validate records, exclude PRs |
| github_issue_connector/database.py | Schema, transactional upsert, read-only queries, explicit connection close |
| github_issue_connector/errors.py | Expected ConnectorError code/message |
| github_issue_connector/viewer.py | Database picker, repository/issue tables, search, details, and link actions |
| tests/ | Guarded HTTP mocks, real SQLite files, CLI processes, and Tk events |

## Data flow

**Import:** validate repository → fetch and validate the entire page → upsert records in one transaction → return page records/count. Input, HTTP, and malformed-page failures cause no database work. Database failure rolls back the batch.

**Read:** validate repository → query SQLite → return all saved rows for that repository. It never calls the GitHub client or creates an HTTP session. Loading package modules performs no HTTP.

**Viewer:** discover or browse for a database → read_repository_counts → select a repository → read_saved_issues → filter loaded rows locally. Shared read-only storage handling closes each connection explicitly. Refresh reloads saved data; changing databases clears old search/details. One class holds window state and callbacks; connector/storage operations remain functions.

The CLI diagram is [sysDes.mmd](sysDes.mmd). Its narration is in [DEMO.md](docs/DEMO.md#explaining-sysdesmmd); early repository validation, configurable paths, and argparse errors are described here.

## GitHub boundary

Validation accepts ASCII letters, digits, dots, underscores, and hyphens in each repository component. It rejects URLs, whitespace, extra slashes, backslashes, empty components, and exact . or .. components before HTTP/SQLite. A valid-looking nonexistent name reaches GitHub; no guessed name-length restrictions are imposed.

One context-managed Requests Session sends a GET to /repos/{owner}/{name}/issues with:

| Setting | Value |
| --- | --- |
| Query | state=open, per_page=100, page=1 |
| Accept | application/vnd.github+json |
| X-GitHub-Api-Version | 2026-03-10 |
| Timeout | 20 seconds for connection/read waits |
| Redirects | Disabled |
| Environment credentials/proxies | Disabled with trust_env=False |

HTTP 200 and a JSON list of objects are required. Objects containing the pull_request key are excluded regardless of its value. Retained records require a positive integer number excluding bool, a nonblank string title, and an absolute HTTP(S) html_url with hostname, valid port, and no whitespace.

Mapping uses number → issue_number and html_url → url. Titles/URLs are preserved and rows sorted. A malformed retained entry rejects the whole page; URL validation does not establish link existence. No retries or pagination requests are made.

## Schema and transactions

```sql
CREATE TABLE IF NOT EXISTS issues (
    repository TEXT NOT NULL,
    issue_number INTEGER NOT NULL,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    PRIMARY KEY (repository, issue_number)
);
```

Issue numbers are local to a repository. INSERT ... ON CONFLICT (repository, issue_number) DO UPDATE replaces title and URL. Omitted rows are retained. All user values use bound parameters.

Storage receives validated four-field records and prepares normalized parameters before opening SQLite. Writes use isolation_level=None and explicit BEGIN before schema creation and the batch. The connection context commits or rolls back; finally closes it. Failed first writes may leave an empty file, while schema and row changes remain atomic.

Reads use an escaped file URI with mode=ro, bound repository selection, deterministic ordering, and explicit close. The viewer's grouped count query sorts repositories alphabetically. A real late-failure trigger test verifies earlier inserts/updates are rolled back, then inspects persisted rows through new connections.

## Paths and errors

Both functions and CLI commands default to issues.db relative to the **process's current working directory**. Absolute paths select a fixed file. Parent directories must exist; no parent creation or fallback occurs.

Import creates the database/table only after page validation, including an empty page. Read of a missing file in an existing parent, or a database without an issues table, returns an empty success without creation. Missing parents, unusable/corrupt files, and incompatible queried schemas return database_error; a view named issues is incompatible.

The viewer discovers .db/.sqlite/.sqlite3 files directly in the working directory, preferring issues.db then the first alphabetically sorted file. --db overrides selection; Browse can choose another folder. Missing selected files are reported instead of created.

| Expected error code | Cause |
| --- | --- |
| invalid_repository | Repository type or syntax |
| request_timeout | Requests Timeout |
| network_error | Other Requests request failures |
| http_error | HTTP status other than 200 |
| invalid_response | Invalid JSON, page shape, or required fields |
| database_error | SQLite or filesystem failure |

Public functions catch only ConnectorError. Storage re-raises sqlite3.ProgrammingError; other programming errors retain tracebacks. API errors omit response bodies and underlying network details. Database errors identify the action, path, reason, and useful checks.

CLI success prints JSON on stdout and exits 0; expected operation failure prints JSON on stderr and exits 1. Argument errors use argparse usage text on stderr and exit 2 before an operation. Help exits 0. The viewer shows expected storage/filesystem errors in its status; unexpected callback errors keep Tk's traceback behavior.

## Tradeoffs and limits

- Functions and a flat package keep the connector explainable without frameworks, an ORM, or project installation.
- SQLite provides persistence without a server. The composite key isolates repositories and makes repeated imports update existing rows.
- One page bounds scope. PRs count toward the 100 API entries; retained older rows mean read counts can exceed import counts and include later-closed issues.
- Public access needs no token but remains subject to rate limits. Disabling environment credentials also ignores proxies/CA overrides; TLS verification stays enabled. Timeout is not a total-runtime deadline.
- The optional user-requested viewer reuses local reads. Its shared palette/themes keep presentation separate from storage; native window chrome/dialogs follow the OS. Synchronous reads can pause large/locked databases.
- No migration or background polling is implemented. Other Python versions, proxy-dependent networks, native file-picker selection, and actual browser launching remain unverified. Final compact layout passed geometry tests; the final reopened preview was not visually inspected.
