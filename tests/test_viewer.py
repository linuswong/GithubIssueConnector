"""Exercise real Tk selection events and temporary SQLite files without HTTP."""

import sqlite3
import sys
import tkinter as tk
from unittest.mock import Mock

import pytest
import requests

from github_issue_connector.database import upsert_issues
from github_issue_connector import viewer


def issue(number=7, repository="owner/alpha", title="Fix café layout", url=None):
    return {
        "repository": repository,
        "issue_number": number,
        "title": title,
        "url": url or f"https://github.com/{repository}/issues/{number}",
    }


@pytest.fixture(scope="module")
def desktop():
    try:
        root = tk.Tk()
    except tk.TclError as error:
        if sys.platform == "win32":
            raise
        pytest.skip(f"Tk needs a desktop display: {error}")
    root.withdraw()
    yield root
    root.destroy()


@pytest.fixture
def window(desktop, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(requests, "Session", Mock(side_effect=AssertionError("Viewer must be offline.")))
    root = tk.Toplevel(desktop)
    root.withdraw()
    # Surface callback failures as test failures, instead of printing and continuing.
    def raise_callback_error(_kind, value, traceback):
        raise value.with_traceback(traceback)

    monkeypatch.setattr(desktop, "report_callback_exception", raise_callback_error)
    yield root
    root.destroy()


def test_default_database_repository_selection_and_all_saved_rows(window, tmp_path):
    path = tmp_path / "issues.db"
    records = [issue(number) for number in range(1, 105)]
    upsert_issues(records + [issue(1, "owner/beta")], path)
    upsert_issues([issue(title="Different database")], tmp_path / "a.sqlite")
    before = path.read_bytes()

    app = viewer.IssueViewer(window)
    window.update()

    assert app.db_path.get() == str(path)
    assert app.repositories.get_children() == ("owner/alpha", "owner/beta")
    assert app.repositories.item("owner/alpha", "values") == ("owner/alpha", "104")
    assert len(app.issue_table.get_children()) == 104
    assert app.issues == records
    app.repositories.selection_set("owner/beta")
    window.update()
    assert app.issues == [issue(1, "owner/beta")]
    assert app.heading.get() == "owner/beta"
    assert path.read_bytes() == before


def test_switching_databases_clears_old_search_selection_and_details(window, tmp_path):
    first = tmp_path / "first.db"
    second = tmp_path / "second.sqlite3"
    upsert_issues([issue()], first)
    upsert_issues([issue(title="Second database")], second)
    app = viewer.IssueViewer(window, first)
    window.update()
    app.search.set("café")
    app.issue_table.selection_set("0")
    window.update()
    assert app.selected_issue == issue()

    app.db_path.set(str(second))
    app.database_picker.event_generate("<<ComboboxSelected>>")
    window.update()

    assert app.search.get() == ""
    assert app.issues == [issue(title="Second database")]
    assert app.selected_issue is None
    assert app.open_button.instate(["disabled"])
    assert "Select an issue" in app.details.get("1.0", "end")


def test_browse_selects_external_file_and_cancel_preserves_selection(window, tmp_path, monkeypatch):
    external = tmp_path / "other folder"
    external.mkdir()
    path = external / "snapshot # café.db"
    upsert_issues([issue()], path)
    app = viewer.IssueViewer(window)
    assert app.db_path.get() == ""
    pick = Mock(side_effect=[str(path), ""])
    monkeypatch.setattr(viewer.filedialog, "askopenfilename", pick)

    app.browse_button.invoke()
    window.update()
    assert app.db_path.get() == str(path)
    assert str(path) in app.database_picker.cget("values")
    assert app.issues == [issue()]
    app.browse_button.invoke()
    window.update()
    assert app.db_path.get() == str(path)
    assert app.issues == [issue()]


def test_search_and_details_are_local_and_url_can_be_copied(window, tmp_path):
    path = tmp_path / "issues.db"
    long_title = "Full title café " * 25
    records = [issue(title=long_title), issue(12, title="Another title")]
    upsert_issues(records, path)
    app = viewer.IssueViewer(window, path)
    window.update()
    app.search.set("CAFÉ")
    assert len(app.issue_table.get_children()) == 1
    app.issue_table.selection_set("0")
    window.update()
    assert long_title in app.details.get("1.0", "end")
    assert records[0]["url"] in app.details.get("1.0", "end")
    app.copy_button.invoke()
    assert window.clipboard_get() == records[0]["url"]
    app.search.set("#12")
    assert app.issue_table.item(app.issue_table.get_children()[0], "values") == ("#12", "Another title")
    app.search.set("no such title")
    window.update()
    assert not app.issue_table.get_children()
    assert app.issue_summary.get() == "No issues match your search."
    assert app.copy_button.instate(["disabled"])
    app.search.set("")
    assert len(app.issue_table.get_children()) == 2


def test_refresh_rereads_saved_data_keeps_repository_and_finds_new_database(window, tmp_path):
    path = tmp_path / "issues.db"
    upsert_issues([issue(), issue(1, "owner/beta")], path)
    app = viewer.IssueViewer(window, path)
    window.update()
    app.repositories.selection_set("owner/beta")
    window.update()
    updated = issue(1, "owner/beta", title="Updated elsewhere")
    upsert_issues([updated, issue(2, "owner/beta")], path)
    new_file = tmp_path / "new.sqlite"
    upsert_issues([], new_file)

    app.refresh_button.invoke()
    window.update()

    assert app.repository == "owner/beta"
    assert app.issues == [updated, issue(2, "owner/beta")]
    assert app.repositories.item("owner/beta", "values") == ("owner/beta", "2")
    assert str(new_file) in app.database_picker.cget("values")


@pytest.mark.parametrize("kind", ["missing", "corrupt", "incompatible"])
def test_database_errors_clear_stale_data_and_allow_recovery(window, tmp_path, kind):
    good = tmp_path / "good.db"
    bad = tmp_path / "bad.db"
    upsert_issues([issue()], good)
    if kind == "corrupt":
        bad.write_bytes(b"not sqlite")
    elif kind == "incompatible":
        connection = sqlite3.connect(bad)
        try:
            connection.execute("CREATE TABLE issues (repository TEXT)")
            connection.execute("INSERT INTO issues VALUES ('owner/alpha')")
            connection.commit()
        finally:
            connection.close()
    app = viewer.IssueViewer(window, good)
    window.update()
    app.issue_table.selection_set("0")
    window.update()
    app.db_path.set(str(bad))
    app.database_picker.event_generate("<<ComboboxSelected>>")
    window.update()

    assert not app.issue_table.get_children()
    assert app.selected_issue is None
    assert app.open_button.instate(["disabled"])
    expected_message = "does not exist" if kind == "missing" else "Could not read"
    assert expected_message in app.status.get()
    if kind == "missing":
        assert not bad.exists()
    app.db_path.set(str(good))
    app.database_picker.event_generate("<<ComboboxSelected>>")
    window.update()
    assert app.issues == [issue()]
    assert "Read only" in app.status.get()


def test_no_database_and_empty_database_show_empty_states(window, tmp_path):
    app = viewer.IssueViewer(window)
    window.update()
    assert "Browse" in app.status.get()
    assert not (tmp_path / "issues.db").exists()
    path = tmp_path / "empty.db"
    upsert_issues([], path)
    before = path.read_bytes()
    app.db_path.set(str(path))
    app.refresh_button.invoke()
    window.update()
    assert not app.repositories.get_children()
    assert not app.issue_table.get_children()
    assert app.status.get() == "No saved repositories in this database."
    assert path.read_bytes() == before


@pytest.mark.parametrize("size", ["900x640", "1180x780"])
def test_controls_fit_at_minimum_and_default_window_sizes(window, tmp_path, size):
    path = tmp_path / "issues.db"
    upsert_issues([issue()], path)
    app = viewer.IssueViewer(window, path)
    window.attributes("-alpha", 0)
    window.geometry(size)
    window.deiconify()
    window.update()

    first_row = app.issue_table.bbox("0")
    assert first_row
    assert first_row[1] + first_row[3] <= app.issue_table.winfo_height()
    for widget in (
        app.database_picker, app.repositories, app.issue_table,
        app.details, app.open_button, app.copy_button,
    ):
        assert widget.winfo_ismapped()
        top = widget.winfo_rooty() - window.winfo_rooty()
        left = widget.winfo_rootx() - window.winfo_rootx()
        assert top >= 0 and left >= 0
        assert top + widget.winfo_height() <= window.winfo_height()
        assert left + widget.winfo_width() <= window.winfo_width()


@pytest.mark.parametrize("url, opened", [
    ("https://github.com/owner/alpha/issues/7", True),
    ("https://github.com/owner/alpha/issues/7", False),
    ("file:///C:/local.txt", True),
])
def test_open_button_uses_selected_web_url_only(window, tmp_path, monkeypatch, url, opened):
    path = tmp_path / "issues.db"
    upsert_issues([issue(url=url)], path)
    open_browser = Mock(return_value=opened)
    monkeypatch.setattr(viewer.webbrowser, "open", open_browser)
    app = viewer.IssueViewer(window, path)
    window.update()
    app.issue_table.selection_set("0")
    window.update()
    app.open_button.invoke()

    if url.startswith("https://"):
        open_browser.assert_called_once_with(url, new=2)
        assert ("Opened issue" if opened else "Copy URL") in app.status.get()
    else:
        open_browser.assert_not_called()
        assert "HTTP or HTTPS" in app.status.get()
