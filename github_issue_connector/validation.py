"""Repository validation shared by import and local-read operations."""

import re

from .errors import ConnectorError


def normalize_repository(repo: str) -> str:
    """Validate owner/name syntax and return its lowercase identity."""
    message = (
        "Use owner/name with letters, digits, dots, underscores, or hyphens; "
        "no whitespace, URLs, extra slashes, backslashes, or . / .. components."
    )
    if not isinstance(repo, str) or not re.fullmatch(
        r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo
    ):
        raise ConnectorError("invalid_repository", message)
    if any(component in (".", "..") for component in repo.split("/")):
        raise ConnectorError("invalid_repository", message)
    return repo.lower()
