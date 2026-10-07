"""Fetch and validate one page of open issues, without persistence."""

from urllib.parse import urlsplit

import requests

from .errors import ConnectorError
from .validation import normalize_repository


REQUEST_TIMEOUT = 20


def fetch_issues(repo: str) -> list[dict]:
    """Return normalized issue records, or raise an expected ConnectorError."""
    repository = normalize_repository(repo)
    try:
        with requests.Session() as session:
            # Public access should not pick up implicit .netrc credentials.
            session.trust_env = False
            response = session.get(
                f"https://api.github.com/repos/{repository}/issues",
                params={"state": "open", "per_page": 100, "page": 1},
                headers={
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": "2026-03-10",
                },
                timeout=REQUEST_TIMEOUT,
                allow_redirects=False,
            )
    except requests.exceptions.Timeout as exc:
        raise ConnectorError(
            "request_timeout",
            f"GitHub request for {repository} timed out (timeout: {REQUEST_TIMEOUT}s).",
        ) from exc
    except requests.exceptions.RequestException as exc:
        raise ConnectorError(
            "network_error", f"Could not complete the GitHub request for {repository}."
        ) from exc

    # Redirects and other non-200 statuses are not successful issue pages.
    if response.status_code != 200:
        raise ConnectorError(
            "http_error",
            f"GitHub returned HTTP {response.status_code} for {repository}; "
            "expected HTTP 200. Check the repository name, public visibility, "
            "and GitHub rate limits.",
        )
    try:
        page = response.json()
    except requests.exceptions.JSONDecodeError as exc:
        raise ConnectorError(
            "invalid_response", f"GitHub returned invalid JSON for {repository}."
        ) from exc
    return _extract_issues(page, repository)


def _extract_issues(page: object, repository: str) -> list[dict]:
    if not isinstance(page, list):
        raise ConnectorError("invalid_response", "GitHub issue data must be a JSON list.")

    issues = []
    for position, entry in enumerate(page, start=1):
        prefix = f"GitHub page entry {position}"
        if not isinstance(entry, dict):
            raise ConnectorError("invalid_response", f"{prefix} must be an object.")
        if "pull_request" in entry:
            continue

        number = entry.get("number")
        title = entry.get("title")
        url = entry.get("html_url")
        # bool is a subclass of int in Python, but is not an issue number.
        if type(number) is not int or number <= 0:
            raise ConnectorError(
                "invalid_response", f"{prefix}: number must be a positive integer."
            )
        if not isinstance(title, str) or not title.strip():
            raise ConnectorError(
                "invalid_response", f"{prefix}: title must be a nonempty string."
            )
        if not _is_browser_url(url):
            raise ConnectorError(
                "invalid_response",
                f"{prefix}: html_url must be an absolute HTTP(S) URL without whitespace.",
            )
        issues.append(
            {
                "repository": repository,
                "issue_number": number,
                "title": title,
                "url": url,
            }
        )

    return sorted(issues, key=lambda issue: issue["issue_number"])


def _is_browser_url(value: object) -> bool:
    if not isinstance(value, str) or any(character.isspace() for character in value):
        return False
    try:
        parsed = urlsplit(value)
        # Accessing port rejects malformed or out-of-range port numbers.
        parsed.port
        return parsed.scheme in ("http", "https") and bool(parsed.hostname)
    except ValueError:
        return False
