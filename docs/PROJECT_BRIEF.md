# Project brief and acceptance criteria

Source: RocketRide_Student_Challenge.docx, read October 6, 2026. This paraphrases the assessment requirements and separates them from chosen design decisions. See [BUILD_PLAN.md](BUILD_PLAN.md) for implementation status.

## Required by the assessment

- Individual project; suggested effort 4–6 hours.
- Deadline: Wednesday, October 7, 2026, 11:59 p.m. Pacific.
- Import one page of open issues from a public GitHub repository supplied as `owner/name`; exclude pull requests.
- Store repository, issue number, title, and URL in a local SQLite database.
- Repeated imports update records without duplicates.
- Read saved issues for one repository without contacting GitHub. Data persists across restarts.
- Reusable import and read functions return consistent JSON-compatible results.
- Database path is configurable. Invalid repositories and API failures return useful errors.
- Automated checks cover import/read, repeated imports without duplicates, and an API failure. Mocks are allowed; a real API call is required in the demo.
- Any language is permitted; CLI is sufficient. Public reads need no token. UI, pagination, deployment, and RocketRide setup are not required.
- Root README.md includes prerequisites, dependencies, setup, run/test commands, example inputs/outputs, specific AI and other tools used, and one unfamiliar problem solved with AI plus verification/correction.
- Root Architecture.MD explains interface, components, API-to-database flow, schema, configuration, errors, and tradeoffs concisely.
- Demo is at most two minutes: real import, local read, repeated import without duplicates, one error, and one decision explained. Upload to Google Drive with working viewer access.
- Submit repository and demo links by replying only to the sender in the original email thread.

## Chosen design decisions, not extra assessment requirements

- Python with requests, sqlite3, argparse, and pytest.
- One database file can store several repositories; `PRIMARY KEY (repository, issue_number)`.
- Only insert/update returned rows; never delete rows absent from a later page. This is retained imported data, not a complete view of current open issues.
- One transaction per imported batch; malformed input or a failed request must not partially change saved issue rows.
- Normalize repository casing; order reads by issue number.
- Fetch up to 100 API entries on one page. Filtering PRs may leave fewer than 100 issues.
- Use GitHub's `html_url` for a browser-facing link.
- Add focused tests for API nuances and repository isolation.

## User-requested extension

On October 7, 2026, the developer requested an optional desktop viewer, then GitHub-inspired styling. This extends the original CLI scope; it does not add assessment requirements. The viewer selects existing databases and displays saved snapshots with read-only access. See [Architecture.MD](../Architecture.MD).

## Primary references

- [GitHub Issues API](https://docs.github.com/en/rest/issues/issues)
- [Python sqlite3](https://docs.python.org/3.13/library/sqlite3.html)
- [SQLite UPSERT](https://www.sqlite.org/lang_upsert.html)
- [Requests quickstart](https://requests.readthedocs.io/en/latest/user/quickstart/)
- [Pytest temporary files](https://docs.pytest.org/en/stable/how-to/tmp_path.html)
- [Pytest monkeypatch](https://docs.pytest.org/en/stable/how-to/monkeypatch.html)
