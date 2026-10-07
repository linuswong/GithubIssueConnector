# Architecture

The connector is implemented and verified on Python 3.13.5 with requests 2.34.2, pytest 9.1.1, and SQLite 3.49.1. Final automated and live evidence is in [docs/AI_NOTES.md](docs/AI_NOTES.md#milestone-4--october-6-2026).

## Interface and contract

```python
from github_issue_connector import import_issues, read_issues

import_issues(repo: str, db_path: str | Path = "issues.db") -> dict
read_issues(repo: str, db_path: str | Path = "issues.db") -> dict
```

The functions are also exported from github_issue_connector.connector. The CLI is `python main.py import owner/repo --db PATH` or `python main.py read owner/repo --db PATH`.

Both operations return success, operation, repository, count, issues, and error. Each issue contains repository, issue_number, title, and url. Success has error=null; an expected failure has count=0, issues=[], and error with code/message. repository is lowercase for valid input, null for invalid input. Import count includes every processed issue in this page, including updates; read count includes all saved rows for that repository. Both issue lists sort by issue_number. Check success when count is zero. README contains actual live JSON examples.

## Components and flow

| File | Responsibility |
| --- | --- |
| main.py | argparse input, one public function call, JSON output, exit code |
| github_issue_connector/__init__.py | Public function exports |
| connector.py | Coordinate validation/client/storage; build consistent results |
| validation.py | Validate owner/name and normalize casing |
| github_client.py | One HTTP request; status/JSON/field validation; PR exclusion |
| database.py | Schema, transactional upsert, ordered SQLite read, explicit close |
| errors.py | ConnectorError with expected code/message |
| tests/ | Guarded HTTP mocks, real temporary SQLite files, CLI processes |

Import: validate repository → fetch and validate the whole page → save its records in one transaction → return page records/count. Input, HTTP, or malformed-page failures cause no database work; database failures roll back writes and return no partial issue list.

Read: validate repository → query SQLite for that repository → return all saved records/count. It never calls the client or creates an HTTP Session. Importing the package loads its modules, but loading them does not perform HTTP. The CLI contains no SQL or fetching logic.

Validation permits ASCII letters, digits, dots, underscores, and hyphens in both components; rejects URLs, whitespace, extra slashes, backslashes, empty components, and exact . / .. components before HTTP/SQLite. Valid-looking nonexistent names reach the API. No guessed name-length restriction is imposed.

The client requests state=open, per_page=100, page=1 with Accept application/vnd.github+json and X-GitHub-Api-Version 2026-03-10. It requires HTTP 200 and a JSON list of objects. Objects containing pull_request are excluded by key presence. Retained entries require a positive integer number (not bool), nonblank string title, and structural absolute HTTP(S) html_url with hostname, valid port, and no whitespace. Mapping uses number → issue_number and html_url → url, preserving titles/URLs. One malformed retained entry rejects the whole page. Links are not checked for existence.

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

Issue numbers are local to a repository. INSERT ... ON CONFLICT (repository, issue_number) DO UPDATE replaces title/url; omitted rows are retained. API validation precedes storage, which accepts validated four-field records and prepares normalized row parameters before opening SQLite. Writes and repository lookups use bound parameters.

Each batch opens SQLite with isolation_level=None, executes explicit BEGIN before table creation/writes, commits on success or rolls back through the connection context on failure, then explicitly closes in finally. Reads also explicitly close. A failed first import may leave an empty database file; atomicity covers schema/rows. A real late-failure trigger test verifies rollback of earlier inserts and updates, followed by inspection through new connections.

## Configuration and errors

Both public functions and --db use database.DEFAULT_DB_PATH="issues.db", relative to the process's current working directory. Absolute paths select a fixed file. No parent creation or fallback occurs. Import creates the file/table after page validation, even for an empty page. Read of a missing file in an existing parent or a database without an issues table returns an empty success without creation. Existing files use an escaped file URI with mode=ro. Missing parents, corrupt/unusable databases, and incompatible schemas produce database_error; a view named issues is incompatible.

| Expected code | Cause |
| --- | --- |
| invalid_repository | Repository type/syntax |
| request_timeout | Requests Timeout |
| network_error | Other Requests request failures |
| http_error | Any status other than 200 |
| invalid_response | JSON/page/required-field validation |
| database_error | SQLite database or filesystem failure |

Public functions catch only ConnectorError. Storage deliberately re-raises sqlite3.ProgrammingError; unexpected programming bugs retain tracebacks. API messages omit response bodies/underlying network details; database messages identify action/path/reason and useful checks.

CLI success is JSON on stdout, exit 0. Expected operation failure is JSON on stderr, exit 1. argparse syntax errors are usage/error text on stderr, exit 2, before calling an operation; help is text on stdout, exit 0. Syntax errors are outside the operation JSON contract.

## Tradeoffs and verification limits

A flat package and functions keep the code explainable without project installation/PYTHONPATH or frameworks. SQLite gives local persistence without a server. One page bounds scope, and PR exclusion may yield fewer than 100 issues. Absence cannot establish closure/deletion, so reads can include later-closed issues and counts can exceed the latest import count.

The client uses one context-managed Session, no token, no retries, and no redirect/pagination following. timeout=20 bounds connection/read waits, not total elapsed time. trust_env=False prevents implicit .netrc credentials but also ignores environment proxies/CA overrides; TLS verification remains enabled. Unauthenticated API rate limits still apply. No migration, UI, or background polling is included. Other Python versions and proxy-dependent networks have not been verified.
