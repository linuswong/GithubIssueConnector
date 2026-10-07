from pathlib import Path
from unittest.mock import Mock

import pytest
import requests

from github_issue_connector import connector, import_issues, read_issues
from github_issue_connector import database


def api_issue(number=7, title="Fix Unicode café ☕"):
    return {
        "number": number,
        "title": title,
        "html_url": f"https://github.com/Owner/Repo/issues/{number}",
    }


def saved_issue(number=7, title="Fix Unicode café ☕"):
    return {
        "repository": "owner/repo",
        "issue_number": number,
        "title": title,
        "url": f"https://github.com/Owner/Repo/issues/{number}",
    }


def test_public_import_then_read_is_normalized_ordered_and_offline(
    tmp_path, serve_page, http_send, monkeypatch
):
    path = tmp_path / "snapshot.db"
    serve_page([api_issue(12), {"pull_request": None}, api_issue(3)])

    imported = import_issues("Owner/Repo", path)

    assert imported == {
        "success": True,
        "operation": "import",
        "repository": "owner/repo",
        "count": 2,
        "issues": [saved_issue(3), saved_issue(12)],
        "error": None,
    }
    http_send.assert_called_once()
    session = Mock(side_effect=AssertionError("Read must not create a GitHub session."))
    monkeypatch.setattr(requests, "Session", session)
    http_send.reset_mock()
    http_send.side_effect = AssertionError("Read must not send HTTP.")

    assert read_issues("OWNER/REPO", path) == {**imported, "operation": "read"}
    session.assert_not_called()
    http_send.assert_not_called()


def test_repeat_import_updates_without_duplicates_and_retains_omitted_rows(
    tmp_path, serve_page
):
    path = tmp_path / "snapshot.db"
    serve_page([api_issue(7), api_issue(12)])
    assert import_issues("owner/repo", path)["success"]
    serve_page([api_issue(7, title="Updated title")])

    updated = import_issues("OWNER/REPO", path)
    saved = read_issues("owner/repo", path)

    assert updated["success"]
    assert updated["count"] == 1
    assert updated["issues"] == [saved_issue(7, title="Updated title")]
    assert saved["count"] == 2
    assert saved["issues"] == [saved_issue(7, title="Updated title"), saved_issue(12)]


@pytest.mark.parametrize("failure", ["http", "timeout"])
def test_api_failure_returns_contract_and_preserves_saved_data(
    tmp_path, serve_page, http_send, failure
):
    path = tmp_path / "snapshot.db"
    serve_page([api_issue()])
    assert import_issues("owner/repo", path)["success"]
    before = path.read_bytes()
    if failure == "http":
        serve_page({"message": "Unavailable"}, status=503)
        code = "http_error"
    else:
        http_send.side_effect = requests.exceptions.Timeout("controlled timeout")
        code = "request_timeout"

    result = import_issues("Owner/Repo", path)

    assert result == {
        "success": False,
        "operation": "import",
        "repository": "owner/repo",
        "count": 0,
        "issues": [],
        "error": {"code": code, "message": result["error"]["message"]},
    }
    assert result["error"]["message"]
    assert path.read_bytes() == before
    assert read_issues("owner/repo", path)["issues"] == [saved_issue()]


def test_entire_page_validates_before_any_issue_writes(tmp_path, serve_page):
    path = tmp_path / "snapshot.db"
    serve_page([api_issue()])
    assert import_issues("owner/repo", path)["success"]
    before = path.read_bytes()
    serve_page([api_issue(title="Must not update"), api_issue(12), {"number": 99}])

    result = import_issues("owner/repo", path)

    assert result["success"] is False
    assert result["error"]["code"] == "invalid_response"
    assert result["count"] == 0
    assert result["issues"] == []
    assert path.read_bytes() == before
    assert read_issues("owner/repo", path)["issues"] == [saved_issue()]


@pytest.mark.parametrize("operation", [import_issues, read_issues])
def test_invalid_input_returns_failure_before_http_or_sqlite(
    tmp_path, monkeypatch, http_send, operation
):
    session = Mock(side_effect=AssertionError("Invalid input must not open a session."))
    connect = Mock(side_effect=AssertionError("Invalid input must not open SQLite."))
    monkeypatch.setattr(requests, "Session", session)
    monkeypatch.setattr(database.sqlite3, "connect", connect)
    path = tmp_path / "snapshot.db"

    result = operation("owner/repo/extra", path)

    assert result == {
        "success": False,
        "operation": "import" if operation is import_issues else "read",
        "repository": None,
        "count": 0,
        "issues": [],
        "error": {
            "code": "invalid_repository",
            "message": result["error"]["message"],
        },
    }
    assert "owner/name" in result["error"]["message"]
    session.assert_not_called()
    http_send.assert_not_called()
    connect.assert_not_called()
    assert not path.exists()


@pytest.mark.parametrize("path_type", [str, Path])
def test_both_public_functions_use_the_configured_file(
    tmp_path, monkeypatch, serve_page, path_type
):
    monkeypatch.chdir(tmp_path)
    first = path_type(tmp_path / "first.db")
    second = path_type(tmp_path / "second.db")
    serve_page([api_issue(title="First file")])
    assert import_issues("owner/repo", first)["success"]
    serve_page([api_issue(title="Second file")])
    assert import_issues("owner/repo", second)["success"]

    assert read_issues("owner/repo", first)["issues"] == [saved_issue(title="First file")]
    assert read_issues("owner/repo", second)["issues"] == [saved_issue(title="Second file")]
    assert not (tmp_path / "issues.db").exists()


def test_default_path_missing_read_and_empty_import(tmp_path, monkeypatch, serve_page):
    monkeypatch.chdir(tmp_path)
    expected = {
        "success": True,
        "operation": "read",
        "repository": "owner/repo",
        "count": 0,
        "issues": [],
        "error": None,
    }
    assert read_issues("Owner/Repo") == expected
    assert not (tmp_path / "issues.db").exists()
    serve_page([])

    assert import_issues("Owner/Repo") == {**expected, "operation": "import"}
    assert (tmp_path / "issues.db").is_file()
    assert read_issues("Owner/Repo") == expected


@pytest.mark.parametrize("operation", [import_issues, read_issues])
def test_database_failure_is_wrapped_without_path_fallback(
    tmp_path, monkeypatch, serve_page, operation
):
    monkeypatch.chdir(tmp_path)
    path = tmp_path / "missing-parent" / "snapshot.db"
    serve_page([api_issue()])

    result = operation("Owner/Repo", path)

    assert result["success"] is False
    assert result["repository"] == "owner/repo"
    assert result["count"] == 0
    assert result["issues"] == []
    assert result["error"]["code"] == "database_error"
    assert str(path) in result["error"]["message"]
    assert not path.parent.exists()
    assert not (tmp_path / "issues.db").exists()


@pytest.mark.parametrize(
    ("operation", "component"),
    [(import_issues, "fetch_issues"), (import_issues, "upsert_issues"),
     (read_issues, "read_saved_issues")],
)
def test_unexpected_programming_errors_propagate(
    tmp_path, monkeypatch, serve_page, operation, component
):
    serve_page([api_issue()])
    monkeypatch.setattr(connector, component, Mock(side_effect=RuntimeError("unexpected bug")))

    with pytest.raises(RuntimeError, match="unexpected bug"):
        operation("owner/repo", tmp_path / "snapshot.db")
