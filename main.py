"""Translate terminal arguments into connector calls and JSON output."""

import argparse
import json
import sys

from github_issue_connector import import_issues, read_issues
from github_issue_connector.database import DEFAULT_DB_PATH


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Import one page of open GitHub issues or read a saved SQLite snapshot.",
        epilog="Results: success JSON on stdout (exit 0), failure JSON on stderr (exit 1). "
        "Argument errors print usage on stderr (exit 2).",
    )
    commands = parser.add_subparsers(dest="operation", required=True)
    for operation, description in (
        ("import", "Fetch one page, exclude pull requests, and save returned issues."),
        ("read", "Read all saved issues for a repository from SQLite without HTTP."),
    ):
        command = commands.add_parser(operation, help=description, description=description)
        command.add_argument("repo", metavar="owner/repo", help="Repository in owner/name format.")
        command.add_argument(
            "--db",
            metavar="PATH",
            default=DEFAULT_DB_PATH,
            help="SQLite file (default: %(default)s relative to the current working directory). "
            "Parent directories must already exist.",
        )

    args = parser.parse_args(argv)
    if args.operation == "import":
        result = import_issues(args.repo, args.db)
    else:
        result = read_issues(args.repo, args.db)
    print(json.dumps(result), file=sys.stdout if result["success"] else sys.stderr)
    return 0 if result["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
