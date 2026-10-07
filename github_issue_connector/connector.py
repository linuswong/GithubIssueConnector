"""Coordinate issue fetching/storage and return the public result contract."""

from pathlib import Path

from .database import DEFAULT_DB_PATH, read_saved_issues, upsert_issues
from .errors import ConnectorError
from .github_client import fetch_issues
from .validation import normalize_repository


def import_issues(repo: str, db_path: str | Path = DEFAULT_DB_PATH) -> dict:
    """Save one validated page; count includes returned issues already saved."""
    repository = None
    try:
        repository = normalize_repository(repo)
        issues = fetch_issues(repository)
        upsert_issues(issues, db_path)
    except ConnectorError as error:
        return _result("import", repository, [], error)
    return _result("import", repository, issues)


def read_issues(repo: str, db_path: str | Path = DEFAULT_DB_PATH) -> dict:
    """Read SQLite only; count is all saved issues returned for this repository."""
    repository = None
    try:
        repository = normalize_repository(repo)
        issues = read_saved_issues(repository, db_path)
    except ConnectorError as error:
        return _result("read", repository, [], error)
    return _result("read", repository, issues)


def _result(
    operation: str,
    repository: str | None,
    issues: list[dict],
    error: ConnectorError | None = None,
) -> dict:
    return {
        "success": error is None,
        "operation": operation,
        "repository": repository,
        "count": len(issues),
        "issues": issues,
        "error": None if error is None else {"code": error.code, "message": error.message},
    }
