import json
from unittest.mock import Mock
from urllib.parse import parse_qs, urlsplit

import pytest
import requests

from github_issue_connector.errors import ConnectorError
from github_issue_connector.github_client import fetch_issues
from github_issue_connector.validation import normalize_repository


def make_response(page, status=200, headers=None):
    response = requests.Response()
    response.status_code = status
    response.encoding = "utf-8"
    response._content = json.dumps(page).encode("utf-8")
    response.headers.update(headers or {})
    response.url = "https://api.github.com/repos/owner/repo/issues"
    return response


def serve(http_send, response):
    def respond(prepared, **kwargs):
        response.request = prepared
        response.url = prepared.url
        return response

    http_send.side_effect = respond


def issue(number=7, **changes):
    record = {
        "id": 999999,
        "number": number,
        "title": "Fix Unicode café ☕",
        "html_url": f"https://github.com/Owner/Repo/issues/{number}",
        "url": f"https://api.github.com/repos/Owner/Repo/issues/{number}",
    }
    record.update(changes)
    return record


def test_exactly_one_open_page_with_timeout_and_no_credentials(monkeypatch, http_send):
    netrc_auth = Mock(side_effect=AssertionError("Implicit credentials are forbidden."))
    monkeypatch.setattr(requests.sessions, "get_netrc_auth", netrc_auth)
    serve(
        http_send,
        make_response(
            [issue()],
            headers={
                "Link": '<https://api.github.com/repos/owner/repo/issues?page=2>; rel="next"'
            },
        ),
    )

    fetch_issues("Owner/Repo")

    http_send.assert_called_once()
    prepared = http_send.call_args.args[0]
    parsed = urlsplit(prepared.url)
    assert prepared.method == "GET"
    assert parsed.scheme == "https"
    assert parsed.netloc == "api.github.com"
    assert parsed.path == "/repos/owner/repo/issues"
    assert parse_qs(parsed.query) == {
        "state": ["open"], "per_page": ["100"], "page": ["1"]
    }
    assert http_send.call_args.kwargs["timeout"] == 20
    assert prepared.headers["Accept"] == "application/vnd.github+json"
    assert prepared.headers["X-GitHub-Api-Version"] == "2026-03-10"
    assert "Authorization" not in prepared.headers
    netrc_auth.assert_not_called()


def test_extracts_required_fields_and_orders_by_issue_number(http_send):
    serve(http_send, make_response([issue(12), issue(3)]))

    result = fetch_issues("Owner/Repo")

    assert result == [
        {
            "repository": "owner/repo",
            "issue_number": number,
            "title": "Fix Unicode café ☕",
            "url": f"https://github.com/Owner/Repo/issues/{number}",
        }
        for number in (3, 12)
    ]
    assert json.loads(json.dumps(result)) == result


@pytest.mark.parametrize("pr_value", [None, {}, False, {"html_url": "a PR link"}])
def test_excludes_pull_requests_by_key_presence(http_send, pr_value):
    serve(http_send, make_response([{"pull_request": pr_value}, issue()]))

    result = fetch_issues("owner/repo")

    assert [record["issue_number"] for record in result] == [7]


@pytest.mark.parametrize("page", [[], [{"pull_request": None}]])
def test_empty_successful_issue_list(http_send, page):
    serve(http_send, make_response(page))
    assert fetch_issues("owner/repo") == []
    http_send.assert_called_once()


@pytest.mark.parametrize("status", [204, 301, 302, 304, 403, 404, 422, 429, 500])
def test_http_failure_before_json_decoding_and_no_redirect(http_send, status):
    response = make_response([], status, headers={"Location": "https://github.com/"})
    response.json = Mock(side_effect=AssertionError("Status must be checked first."))
    serve(http_send, response)

    with pytest.raises(ConnectorError) as failure:
        fetch_issues("Owner/Repo")

    assert failure.value.code == "http_error"
    assert f"HTTP {status}" in failure.value.message
    assert "owner/repo" in failure.value.message
    response.json.assert_not_called()
    http_send.assert_called_once()


@pytest.mark.parametrize(
    ("error", "code"),
    [
        (requests.exceptions.Timeout("timed out"), "request_timeout"),
        (requests.exceptions.ConnectTimeout("connect failed"), "request_timeout"),
        (requests.exceptions.ReadTimeout("read failed"), "request_timeout"),
        (requests.exceptions.ConnectionError("connection failed"), "network_error"),
        (requests.exceptions.RequestException("request failed"), "network_error"),
    ],
)
def test_request_failures_are_useful_and_not_retried(http_send, error, code):
    http_send.side_effect = error

    with pytest.raises(ConnectorError) as failure:
        fetch_issues("owner/repo")

    assert failure.value.code == code
    assert "owner/repo" in failure.value.message
    if code == "request_timeout":
        assert "20s" in failure.value.message
    http_send.assert_called_once()


def test_invalid_json(http_send):
    response = make_response([])
    response._content = b"not JSON"
    serve(http_send, response)

    with pytest.raises(ConnectorError) as failure:
        fetch_issues("owner/repo")

    assert failure.value.code == "invalid_response"
    assert "invalid JSON" in failure.value.message


@pytest.mark.parametrize("page", [None, {}, {"message": "error"}, "text", 5])
def test_response_must_be_a_list(http_send, page):
    serve(http_send, make_response(page))
    with pytest.raises(ConnectorError, match="JSON list") as failure:
        fetch_issues("owner/repo")
    assert failure.value.code == "invalid_response"


@pytest.mark.parametrize("entry", [None, [], "text", 5, True])
def test_each_page_entry_must_be_an_object(http_send, entry):
    serve(http_send, make_response([issue(), entry]))
    with pytest.raises(ConnectorError, match="entry 2 must be an object") as failure:
        fetch_issues("owner/repo")
    assert failure.value.code == "invalid_response"


@pytest.mark.parametrize("field", ["number", "title", "html_url"])
def test_missing_required_field_rejects_entire_page(http_send, field):
    malformed = issue()
    del malformed[field]
    serve(http_send, make_response([issue(), malformed]))

    with pytest.raises(ConnectorError) as failure:
        fetch_issues("owner/repo")

    assert failure.value.code == "invalid_response"
    assert "entry 2" in failure.value.message
    assert field in failure.value.message


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("number", None), ("number", True), ("number", False),
        ("number", 0), ("number", -1), ("number", 1.5), ("number", "7"),
        ("title", None), ("title", 123), ("title", ""), ("title", " \t"),
        ("html_url", None), ("html_url", 123), ("html_url", ""),
        ("html_url", " \t"), ("html_url", "/relative/path"),
        ("html_url", "ftp://github.com/owner/repo/issues/7"),
        ("html_url", "https:///missing-host"),
        ("html_url", "https://github.com/contains space"),
        ("html_url", "https://[broken"),
        ("html_url", "https://github.com:invalid/issues/7"),
        ("html_url", "https://github.com:99999/issues/7"),
    ],
)
def test_malformed_required_field_rejects_entire_page(http_send, field, value):
    serve(http_send, make_response([issue(), issue(**{field: value})]))
    with pytest.raises(ConnectorError) as failure:
        fetch_issues("owner/repo")
    assert failure.value.code == "invalid_response"
    assert "entry 2" in failure.value.message
    assert field in failure.value.message


@pytest.mark.parametrize(
    "repo",
    [
        None, 7, "", "owner", "owner/", "/repo", "/", "owner/repo/extra",
        "owner//repo", "owner/repo/", "https://github.com/owner/repo",
        "github.com/owner/repo", " owner/repo", "owner/repo ", "own er/repo",
        "owner/re po", "owner/\trepo", "owner/repo\n", "owner/\u00a0repo",
        "owner\\repo", "owner/re\\po", "./repo", "../repo", "owner/.",
        "owner/..", "owner/%2e%2e", "owner/repo?state=all", "owner/repo#fragment",
    ],
)
def test_invalid_repository_rejected_before_session_or_request(
    monkeypatch, http_send, repo
):
    session = Mock(side_effect=AssertionError("Invalid input must not open a session."))
    monkeypatch.setattr(requests, "Session", session)

    with pytest.raises(ConnectorError) as failure:
        fetch_issues(repo)

    assert failure.value.code == "invalid_repository"
    assert "owner/name" in failure.value.message
    session.assert_not_called()
    http_send.assert_not_called()


@pytest.mark.parametrize(
    ("repo", "normalized"),
    [
        ("Owner/Repo", "owner/repo"),
        ("owner-name/Repo_Name.v2", "owner-name/repo_name.v2"),
        ("x/.github", "x/.github"),
        ("owner/repo..name", "owner/repo..name"),
    ],
)
def test_validation_does_not_reject_normal_name_punctuation(repo, normalized):
    assert normalize_repository(repo) == normalized


def test_valid_looking_nonexistent_repository_is_an_http_error(http_send):
    serve(http_send, make_response({"message": "Not Found"}, status=404))
    with pytest.raises(ConnectorError) as failure:
        fetch_issues("unknown-owner/unknown-repo")
    assert failure.value.code == "http_error"
    http_send.assert_called_once()


def test_unexpected_programming_errors_are_not_wrapped(http_send):
    http_send.side_effect = RuntimeError("unexpected bug")
    with pytest.raises(RuntimeError, match="unexpected bug"):
        fetch_issues("owner/repo")
