import json
from pathlib import Path
import subprocess
import sys
from unittest.mock import Mock

import pytest

import main
from github_issue_connector.database import upsert_issues


MAIN_PATH = Path(__file__).resolve().parents[1] / "main.py"


def run_cli(arguments, cwd):
    # Monkeypatches do not cross process boundaries, so guard HTTP in each child.
    guarded_entry = """
import runpy
import sys
from pathlib import Path
import requests

def no_http(*args, **kwargs):
    raise AssertionError("Live HTTP is forbidden in CLI process tests.")

requests.Session = no_http
requests.adapters.HTTPAdapter.send = no_http
main_path = sys.argv.pop(1)
sys.path.insert(0, str(Path(main_path).parent))
sys.argv[0] = main_path
runpy.run_path(main_path, run_name="__main__")
"""
    return subprocess.run(
        [sys.executable, "-c", guarded_entry, str(MAIN_PATH), *arguments],
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=10,
        check=False,
    )


@pytest.mark.parametrize("operation", ["import", "read"])
@pytest.mark.parametrize("configured", [True, False])
def test_cli_forwards_arguments_to_only_the_selected_operation(
    monkeypatch, capsys, operation, configured
):
    result = {
        "success": True, "operation": operation, "repository": "owner/repo",
        "count": 0, "issues": [], "error": None,
    }
    selected = Mock(return_value=result)
    other = Mock(side_effect=AssertionError("Wrong operation called."))
    monkeypatch.setattr(main, "import_issues", selected if operation == "import" else other)
    monkeypatch.setattr(main, "read_issues", selected if operation == "read" else other)
    path = "./selected snapshot.db" if configured else "issues.db"
    arguments = [operation, "Owner/Repo"]
    if configured:
        arguments.extend(["--db", path])

    assert main.main(arguments) == 0

    selected.assert_called_once_with("Owner/Repo", path)
    other.assert_not_called()
    output = capsys.readouterr()
    assert json.loads(output.out) == result
    assert output.err == ""


@pytest.mark.parametrize("status", [200, 503])
def test_cli_import_outputs_only_json_with_success_or_failure_exit(
    tmp_path, serve_page, capsys, status
):
    serve_page([
        {"number": 7, "title": "Fix café ☕", "html_url": "https://github.com/owner/repo/issues/7"}
    ], status=status)
    path = tmp_path / "snapshot.db"

    exit_code = main.main(["import", "Owner/Repo", "--db", str(path)])

    output = capsys.readouterr()
    successful = status == 200
    assert exit_code == (0 if successful else 1)
    result = json.loads(output.out if successful else output.err)
    assert (output.err if successful else output.out) == ""
    assert result["success"] is successful
    assert result["operation"] == "import"
    assert result["repository"] == "owner/repo"
    assert result["count"] == (1 if successful else 0)
    if successful:
        assert result["issues"][0]["title"] == "Fix café ☕"
        assert result["error"] is None
        assert path.is_file()
    else:
        assert result["issues"] == []
        assert result["error"]["code"] == "http_error"
        assert not path.exists()


@pytest.mark.parametrize("arguments", [
    [], ["unknown"], ["import"], ["read", "owner/repo", "--db"],
    ["read", "owner/repo", "--unknown"],
])
def test_argument_errors_print_usage_and_exit_two_before_operations(
    monkeypatch, capsys, arguments
):
    operation = Mock(side_effect=AssertionError("Parser error must not call operations."))
    monkeypatch.setattr(main, "import_issues", operation)
    monkeypatch.setattr(main, "read_issues", operation)

    with pytest.raises(SystemExit) as failure:
        main.main(arguments)

    assert failure.value.code == 2
    output = capsys.readouterr()
    assert output.out == ""
    assert "usage:" in output.err
    assert "error:" in output.err
    operation.assert_not_called()


@pytest.mark.parametrize("arguments", [["--help"], ["import", "--help"], ["read", "--help"]])
def test_help_describes_operations_and_paths(capsys, arguments):
    with pytest.raises(SystemExit) as completion:
        main.main(arguments)

    assert completion.value.code == 0
    output = capsys.readouterr()
    assert output.err == ""
    if arguments == ["--help"]:
        assert "import" in output.out
        assert "read" in output.out
        assert "exit 2" in output.out
    else:
        assert "owner/repo" in output.out
        assert "--db" in output.out
        assert "issues.db" in output.out
        assert "current working directory" in " ".join(output.out.split())


def test_cli_preserves_unexpected_programming_errors(monkeypatch):
    monkeypatch.setattr(main, "read_issues", Mock(side_effect=RuntimeError("unexpected bug")))

    with pytest.raises(RuntimeError, match="unexpected bug"):
        main.main(["read", "owner/repo"])


def test_saved_data_persists_through_separate_guarded_cli_processes(tmp_path):
    path = tmp_path / "issues.db"
    records = [
        {"repository": "owner/repo", "issue_number": number, "title": f"Controlled issue {number}",
         "url": f"https://github.com/owner/repo/issues/{number}"}
        for number in (3, 12)
    ]
    other = {**records[0], "repository": "owner/other", "title": "Another repository"}
    upsert_issues([records[1], other, records[0]], path)

    first = run_cli(["read", "OWNER/REPO", "--db", str(path)], cwd=tmp_path)
    second = run_cli(["read", "owner/repo"], cwd=tmp_path)

    expected = {
        "success": True, "operation": "read", "repository": "owner/repo",
        "count": 2, "issues": records, "error": None,
    }
    for process in (first, second):
        assert process.returncode == 0, process.stderr
        assert process.stderr == ""
        assert json.loads(process.stdout) == expected


def test_cli_process_operation_failure_returns_json_and_exit_one(tmp_path):
    process = run_cli(["import", "owner/repo/extra", "--db", "selected.db"], cwd=tmp_path)

    assert process.returncode == 1
    assert process.stdout == ""
    result = json.loads(process.stderr)
    assert result["success"] is False
    assert result["operation"] == "import"
    assert result["repository"] is None
    assert result["count"] == 0
    assert result["issues"] == []
    assert result["error"]["code"] == "invalid_repository"
    assert not (tmp_path / "selected.db").exists()
