"""Save validated issue batches and read local snapshots using SQLite only."""

from pathlib import Path
import sqlite3

from .errors import ConnectorError
from .validation import normalize_repository


DEFAULT_DB_PATH = "issues.db"

CREATE_ISSUES = """
    CREATE TABLE IF NOT EXISTS issues (
        repository TEXT NOT NULL,
        issue_number INTEGER NOT NULL,
        title TEXT NOT NULL,
        url TEXT NOT NULL,
        PRIMARY KEY (repository, issue_number)
    )
"""

UPSERT_ISSUE = """
    INSERT INTO issues (repository, issue_number, title, url)
    VALUES (?, ?, ?, ?)
    ON CONFLICT (repository, issue_number) DO UPDATE SET
        title = excluded.title,
        url = excluded.url
"""


def upsert_issues(issues: list[dict], db_path: str | Path = DEFAULT_DB_PATH) -> None:
    """Save an already validated batch atomically; never delete omitted rows."""
    # Prepare all rows before opening SQLite; invalid repositories cannot write.
    rows = [
        (
            normalize_repository(issue["repository"]),
            issue["issue_number"],
            issue["title"],
            issue["url"],
        )
        for issue in issues
    ]
    path = Path(db_path).absolute()
    try:
        connection = sqlite3.connect(
            path.as_uri() + "?mode=rwc", uri=True, isolation_level=None
        )
        try:
            # The context commits or rolls back; BEGIN also includes table creation.
            with connection:
                connection.execute("BEGIN")
                connection.execute(CREATE_ISSUES)
                connection.executemany(UPSERT_ISSUE, rows)
        finally:
            connection.close()
    except sqlite3.ProgrammingError:
        raise
    except (sqlite3.DatabaseError, OSError) as exc:
        raise _database_error("save", path, exc) from exc


def read_saved_issues(repo: str, db_path: str | Path = DEFAULT_DB_PATH) -> list[dict]:
    """Return one repository's saved rows in order without creating a file/table."""
    repository = normalize_repository(repo)
    return _read_saved_rows(
        "SELECT repository, issue_number, title, url FROM issues "
        "WHERE repository = ? ORDER BY issue_number",
        (repository,),
        db_path,
    )


def read_repository_counts(db_path: str | Path = DEFAULT_DB_PATH) -> list[dict]:
    """List repositories with all saved row counts, alphabetically and offline."""
    return _read_saved_rows(
        "SELECT repository, COUNT(*) AS count FROM issues "
        "GROUP BY repository ORDER BY repository",
        (),
        db_path,
    )


def _read_saved_rows(query: str, parameters: tuple, db_path: str | Path) -> list[dict]:
    """Share read-only connection/schema/error handling for the two local queries."""
    path = Path(db_path).absolute()
    try:
        try:
            path.stat()
        except FileNotFoundError:
            if path.parent.is_dir():
                return []
            raise

        # URI escaping preserves literal filename characters; mode=ro cannot create.
        connection = sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)
        try:
            connection.row_factory = sqlite3.Row
            schema = connection.execute(
                "SELECT type FROM sqlite_master WHERE name = ? COLLATE NOCASE",
                ("issues",),
            ).fetchone()
            if schema is None:
                return []
            if schema["type"] != "table":
                raise sqlite3.DatabaseError("The issues schema entry must be a table.")
            rows = connection.execute(query, parameters).fetchall()
            return [dict(row) for row in rows]
        finally:
            connection.close()
    except sqlite3.ProgrammingError:
        raise
    except (sqlite3.DatabaseError, OSError) as exc:
        raise _database_error("read", path, exc) from exc


def _database_error(action: str, path: Path, error: Exception) -> ConnectorError:
    return ConnectorError(
        "database_error",
        f"Could not {action} issues in database '{path}': {error}. "
        "Check the path, permissions, database schema, and whether the file is locked.",
    )
