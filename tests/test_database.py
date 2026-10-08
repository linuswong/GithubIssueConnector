import json
from pathlib import Path
import sqlite3
from unittest.mock import Mock

import pytest
import requests

from github_issue_connector import database
from github_issue_connector.database import read_repository_counts, read_saved_issues, upsert_issues
from github_issue_connector.errors import ConnectorError


@pytest.fixture(autouse=True)
def no_http(monkeypatch):
    """Fail if any storage test opens a GitHub session or sends HTTP."""
    session = Mock(side_effect=AssertionError("Storage must not create HTTP sessions."))
    send = Mock(side_effect=AssertionError("Storage must not send HTTP."))
    monkeypatch.setattr(requests, "Session", session)
    monkeypatch.setattr(requests.adapters.HTTPAdapter, "send", send)


def issue(number=7, repository="owner/repo", **changes):
    record = {
        "repository": repository,
        "issue_number": number,
        "title": "Fix Unicode café ☕",
        "url": f"https://github.com/{repository}/issues/{number}",
    }
    record.update(changes)
    return record


def query_file(path, sql, parameters=()):
    """Inspect committed data using an independent, explicitly closed connection."""
    connection = sqlite3.connect(path)
    try:
        return connection.execute(sql, parameters).fetchall()
    finally:
        connection.close()


def test_repository_counts_are_sorted_isolated_and_do_not_change_file(tmp_path):
    path = tmp_path / "snapshot # café.sqlite3"
    upsert_issues([
        issue(7, "owner/zebra"), issue(8, "owner/zebra"), issue(7, "owner/alpha")
    ], path)
    before = path.read_bytes()

    assert read_repository_counts(path) == [
        {"repository": "owner/alpha", "count": 1},
        {"repository": "owner/zebra", "count": 2},
    ]
    assert path.read_bytes() == before


@pytest.mark.parametrize("kind", ["missing", "empty", "tableless"])
def test_repository_counts_handle_empty_databases_without_creating_schema(tmp_path, kind):
    path = tmp_path / "snapshot.db"
    if kind == "empty":
        upsert_issues([], path)
    elif kind == "tableless":
        query_file(path, "CREATE TABLE unrelated (value TEXT)")
    before = path.read_bytes() if path.exists() else None

    assert read_repository_counts(path) == []

    assert (path.read_bytes() if path.exists() else None) == before


@pytest.mark.parametrize("kind", ["corrupt", "view", "missing_column", "missing_parent"])
def test_repository_counts_report_database_failures(tmp_path, kind):
    path = tmp_path / "snapshot.db"
    if kind == "corrupt":
        path.write_bytes(b"not sqlite")
    elif kind == "view":
        query_file(path, "CREATE VIEW issues AS SELECT 'owner/repo' AS repository")
    elif kind == "missing_column":
        query_file(path, "CREATE TABLE issues (other TEXT)")
    else:
        path = tmp_path / "absent" / "snapshot.db"

    with pytest.raises(ConnectorError) as error:
        read_repository_counts(path)

    assert error.value.code == "database_error"
    assert not (tmp_path / "absent").exists()


def test_repository_count_connection_is_read_only_and_closed(tmp_path, monkeypatch):
    path = tmp_path / "snapshot.db"
    upsert_issues([issue()], path)
    real_connect = sqlite3.connect
    connections = []

    def inspect_connect(*args, **kwargs):
        connection = real_connect(*args, **kwargs)
        connections.append(connection)
        with pytest.raises(sqlite3.OperationalError, match="readonly"):
            connection.execute("DELETE FROM issues")
        return connection

    monkeypatch.setattr(database.sqlite3, "connect", inspect_connect)
    assert read_repository_counts(path) == [{"repository": "owner/repo", "count": 1}]
    assert len(connections) == 1
    with pytest.raises(sqlite3.ProgrammingError, match="closed"):
        connections[0].execute("SELECT 1")


@pytest.mark.parametrize("path_type", [str, Path])
def test_initial_insert_read_order_and_json_structure(tmp_path, path_type):
    path = path_type(tmp_path / "snapshot.db")
    records = [issue(12), issue(3)]

    assert upsert_issues(records, path) is None
    saved = read_saved_issues("owner/repo", path)

    assert saved == [issue(3), issue(12)]
    assert json.loads(json.dumps(saved)) == saved
    assert read_saved_issues("owner/unknown", path) == []


def test_repeated_writes_have_no_duplicates(tmp_path):
    path = tmp_path / "snapshot.db"
    records = [issue(7), issue(12)]
    upsert_issues(records, path)
    upsert_issues(records, path)

    assert read_saved_issues("owner/repo", path) == records
    assert query_file(path, "SELECT COUNT(*) FROM issues") == [(2,)]


def test_existing_title_and_url_are_updated(tmp_path):
    path = tmp_path / "snapshot.db"
    upsert_issues([issue()], path)
    changed = issue(title="Renamed issue", url="https://github.com/owner/repo/issues/7?new=1")

    upsert_issues([changed], path)

    assert read_saved_issues("owner/repo", path) == [changed]
    assert query_file(path, "SELECT COUNT(*) FROM issues") == [(1,)]


def test_same_number_in_two_repositories_stays_separate(tmp_path):
    path = tmp_path / "snapshot.db"
    first = issue(repository="owner/alpha")
    second = issue(repository="owner/beta", title="Another issue")
    upsert_issues([first, second], path)
    changed = issue(repository="owner/alpha", title="Only alpha changes")
    upsert_issues([changed], path)

    assert read_saved_issues("owner/alpha", path) == [changed]
    assert read_saved_issues("owner/beta", path) == [second]


def test_repository_casing_is_normalized_for_writes_and_reads(tmp_path):
    path = tmp_path / "snapshot.db"
    mixed = issue(repository="Owner/Repo")
    upsert_issues([mixed], path)
    changed = issue(title="Updated using lowercase")
    upsert_issues([changed], path)

    assert read_saved_issues("OWNER/REPO", path) == [changed]
    assert query_file(path, "SELECT repository FROM issues") == [("owner/repo",)]


def test_data_persists_in_a_new_connection(tmp_path):
    path = tmp_path / "snapshot.db"
    upsert_issues([issue()], path)

    assert query_file(
        path, "SELECT repository, issue_number, title, url FROM issues"
    ) == [("owner/repo", 7, issue()["title"], issue()["url"])]
    assert read_saved_issues("owner/repo", path) == [issue()]


def test_configured_paths_select_separate_files(tmp_path):
    first_path = tmp_path / "first.db"
    second_path = tmp_path / "second.db"
    second = issue(title="Second file")
    upsert_issues([issue()], first_path)
    upsert_issues([second], second_path)

    assert read_saved_issues("owner/repo", first_path) == [issue()]
    assert read_saved_issues("owner/repo", second_path) == [second]
    assert not (tmp_path / "issues.db").exists()


def test_default_path_is_relative_to_current_working_directory(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    assert read_saved_issues("owner/repo") == []
    assert not (tmp_path / "issues.db").exists()
    upsert_issues([issue()])

    assert (tmp_path / "issues.db").is_file()
    assert read_saved_issues("owner/repo") == [issue()]


def test_relative_configured_path_and_escaped_filename(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    path = "snapshot # café.db"
    upsert_issues([issue()], path)

    assert (tmp_path / path).is_file()
    assert read_saved_issues("owner/repo", path) == [issue()]


def test_empty_batch_preserves_saved_rows(tmp_path):
    path = tmp_path / "snapshot.db"
    upsert_issues([issue()], path)

    upsert_issues([], path)

    assert read_saved_issues("owner/repo", path) == [issue()]


def test_first_empty_batch_creates_an_empty_table(tmp_path):
    path = tmp_path / "snapshot.db"
    upsert_issues([], path)

    assert path.is_file()
    assert query_file(path, "SELECT COUNT(*) FROM issues") == [(0,)]
    assert read_saved_issues("owner/repo", path) == []


def test_omitted_rows_remain_saved(tmp_path):
    path = tmp_path / "snapshot.db"
    upsert_issues([issue(7), issue(12)], path)
    changed = issue(12, title="Still returned")

    upsert_issues([changed], path)

    assert read_saved_issues("owner/repo", path) == [issue(7), changed]


def test_missing_database_read_does_not_create_a_file(tmp_path):
    path = tmp_path / "missing.db"

    assert read_saved_issues("owner/repo", path) == []

    assert not path.exists()


def test_database_without_issues_table_read_does_not_change_schema(tmp_path):
    path = tmp_path / "snapshot.db"
    query_file(path, "CREATE TABLE unrelated (value TEXT)")
    before = path.read_bytes()

    assert read_saved_issues("owner/repo", path) == []

    assert path.read_bytes() == before
    assert query_file(path, "SELECT name FROM sqlite_master WHERE type = 'table'") == [
        ("unrelated",)
    ]


@pytest.mark.parametrize("operation", ["read", "save"])
def test_missing_parent_is_an_error_without_creation_or_fallback(
    tmp_path, monkeypatch, operation
):
    monkeypatch.chdir(tmp_path)
    path = tmp_path / "missing-parent" / "snapshot.db"

    with pytest.raises(ConnectorError) as failure:
        if operation == "read":
            read_saved_issues("owner/repo", path)
        else:
            upsert_issues([issue()], path)

    assert failure.value.code == "database_error"
    assert operation in failure.value.message
    assert str(path) in failure.value.message
    assert not path.parent.exists()
    assert not (tmp_path / "issues.db").exists()


@pytest.mark.parametrize("operation", ["read", "save"])
def test_corrupt_database_is_a_useful_error_and_is_preserved(tmp_path, operation):
    path = tmp_path / "corrupt.db"
    before = b"This is not a SQLite database."
    path.write_bytes(before)

    with pytest.raises(ConnectorError) as failure:
        if operation == "read":
            read_saved_issues("owner/repo", path)
        else:
            upsert_issues([issue()], path)

    assert failure.value.code == "database_error"
    assert operation in failure.value.message
    assert str(path) in failure.value.message
    assert "not a database" in failure.value.message
    assert path.read_bytes() == before


@pytest.mark.parametrize("operation", ["read", "save"])
def test_incompatible_table_is_a_database_error(tmp_path, operation):
    path = tmp_path / "incompatible.db"
    query_file(path, "CREATE TABLE issues (unrelated TEXT)")

    with pytest.raises(ConnectorError) as failure:
        if operation == "read":
            read_saved_issues("owner/repo", path)
        else:
            upsert_issues([issue()], path)

    assert failure.value.code == "database_error"
    assert str(path) in failure.value.message


def test_view_named_issues_is_incompatible_instead_of_empty(tmp_path):
    path = tmp_path / "incompatible.db"
    query_file(path, "CREATE VIEW issues AS SELECT 1 AS unrelated")

    with pytest.raises(ConnectorError, match="must be a table") as failure:
        read_saved_issues("owner/repo", path)

    assert failure.value.code == "database_error"


@pytest.mark.parametrize("operation", ["read", "save"])
@pytest.mark.parametrize("repository", ["owner/repo/extra", "../repo"])
def test_invalid_repository_is_rejected_before_opening_sqlite(
    tmp_path, monkeypatch, operation, repository
):
    connect = Mock(side_effect=AssertionError("Invalid input must not open SQLite."))
    monkeypatch.setattr(database.sqlite3, "connect", connect)
    path = tmp_path / "snapshot.db"

    with pytest.raises(ConnectorError) as failure:
        if operation == "read":
            read_saved_issues(repository, path)
        else:
            upsert_issues([issue(), issue(12, repository=repository)], path)

    assert failure.value.code == "invalid_repository"
    connect.assert_not_called()
    assert not path.exists()


def test_sql_like_title_and_url_are_saved_as_literal_data(tmp_path):
    path = tmp_path / "snapshot.db"
    record = issue(
        title="Robert'); DROP TABLE issues; --",
        url="https://github.com/owner/repo/issues/7?label=O'Reilly",
    )
    upsert_issues([record], path)

    assert read_saved_issues("owner/repo", path) == [record]
    assert query_file(path, "SELECT COUNT(*) FROM issues") == [(1,)]


def test_late_sqlite_failure_rolls_back_prior_insert_and_update(tmp_path):
    path = tmp_path / "snapshot.db"
    other = issue(repository="owner/other")
    upsert_issues([issue(), other], path)
    query_file(
        path,
        """
        CREATE TRIGGER reject_late_issue BEFORE INSERT ON issues
        WHEN NEW.issue_number = 99
        BEGIN
            SELECT CASE
                WHEN EXISTS (
                    SELECT 1 FROM issues
                    WHERE repository = NEW.repository AND issue_number = 7
                        AND title = 'Changed before failure'
                        AND url = 'https://github.com/owner/repo/issues/7?changed=1'
                ) AND EXISTS (
                    SELECT 1 FROM issues
                    WHERE repository = NEW.repository AND issue_number = 8
                )
                THEN RAISE(ABORT, 'forced failure after insert and update')
                ELSE RAISE(ABORT, 'test did not reach both earlier writes')
            END;
        END
        """,
    )
    changed = issue(
        title="Changed before failure",
        url="https://github.com/owner/repo/issues/7?changed=1",
    )

    with pytest.raises(ConnectorError) as failure:
        upsert_issues([changed, issue(8), issue(99)], path)

    assert failure.value.code == "database_error"
    assert isinstance(failure.value.__cause__, sqlite3.IntegrityError)
    assert str(failure.value.__cause__) == "forced failure after insert and update"
    assert read_saved_issues("owner/repo", path) == [issue()]
    assert read_saved_issues("owner/other", path) == [other]
    assert query_file(
        path, "SELECT issue_number, title, url FROM issues WHERE repository = ?",
        ("owner/repo",),
    ) == [(7, issue()["title"], issue()["url"])]


def test_connections_are_closed_after_success_empty_read_and_sqlite_errors(
    tmp_path, monkeypatch
):
    real_connect = sqlite3.connect
    connections = []

    def track_connect(*args, **kwargs):
        connection = real_connect(*args, **kwargs)
        connections.append(connection)
        return connection

    monkeypatch.setattr(database.sqlite3, "connect", track_connect)
    path = tmp_path / "snapshot.db"
    upsert_issues([issue()], path)
    assert read_saved_issues("owner/repo", path) == [issue()]
    tableless = tmp_path / "tableless.db"
    query_file(tableless, "CREATE TABLE unrelated (value TEXT)")
    assert read_saved_issues("owner/repo", tableless) == []
    corrupt = tmp_path / "corrupt.db"
    corrupt.write_bytes(b"not a SQLite database")
    with pytest.raises(ConnectorError):
        upsert_issues([issue()], corrupt)
    with pytest.raises(ConnectorError):
        read_saved_issues("owner/repo", corrupt)

    assert len(connections) == 6
    for connection in connections:
        with pytest.raises(sqlite3.ProgrammingError, match="closed database"):
            connection.execute("SELECT 1")


@pytest.mark.parametrize("operation", ["read", "save"])
@pytest.mark.parametrize(
    "error", [RuntimeError("unexpected bug"), sqlite3.ProgrammingError("bad binding")]
)
def test_unexpected_errors_are_not_wrapped(tmp_path, monkeypatch, operation, error):
    path = tmp_path / "snapshot.db"
    upsert_issues([issue()], path)
    monkeypatch.setattr(database.sqlite3, "connect", Mock(side_effect=error))

    with pytest.raises(type(error), match=str(error)):
        if operation == "read":
            read_saved_issues("owner/repo", path)
        else:
            upsert_issues([issue()], path)
