"""Start the optional local database viewer."""

import argparse

from github_issue_connector.viewer import run_viewer


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Browse saved GitHub issues in a read-only desktop window."
    )
    parser.add_argument(
        "--db",
        metavar="PATH",
        help="Open this existing SQLite file. Otherwise use issues.db or another "
        "database in the current working directory. Browse can select files elsewhere.",
    )
    args = parser.parse_args(argv)
    run_viewer(args.db)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
