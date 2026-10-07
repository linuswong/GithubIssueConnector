# Historical milestone 0 prompt

This is the original setup/planning request, preserved as evidence. Milestones 0–3 are implemented and milestone 4 verification is complete. Use README.md for current setup and docs/DEMO.md for recording and delivery.

## Original prompt

Help me build this RocketRide assessment project while teaching me enough to explain and maintain it. This is an individual project; AI use is explicitly permitted. I want strong correctness and evidence, with a small implementation.

First read AGENTS.md, docs/PROJECT_BRIEF.md, and docs/BUILD_PLAN.md. Inspect the current directory and git status. Preserve existing work. The assessment brief is authoritative; distinguish required behavior from our design choices.

Use Python with requests, built-in sqlite3 and argparse, and pytest. Create a flat github_issue_connector package when we implement it. Expose import_issues(repo, db_path) and read_issues(repo, db_path) with a consistent JSON-compatible result contract. The CLI should support:

    python main.py import owner/repo --db ./issues.db
    python main.py read owner/repo --db ./issues.db

Import one page of open issues, exclude PRs, and transactionally upsert repository, issue_number, title, and html_url into SQLite. Use (repository, issue_number) as the composite key. Retain rows absent from later pages. Read locally only. The database path must be configurable in both operations.

Work only on milestone 0 in this first response. Do not write the full connector or prepopulate tests that merely mirror a guessed implementation.

For milestone 0:
1. Summarize requirements and the main risks in plain language.
2. Verify local Python and Git; identify whether this is an existing repository.
3. Set up a project virtual environment and install requirements if available. Record tested versions. Initialize local git only if necessary; do not create a remote or push.
4. Propose the small package structure, function signatures, result contract, default database path, and empty-database behavior. Explain each decision without generating the implementation.
5. Make one exploratory unauthenticated GET to the GitHub repository issues endpoint with state=open, per_page=100, and page=1 for pallets/flask, if network access is available. Inspect a small subset of number, title, html_url, and any pull_request field. Do not save anything to the database yet. Explain the response and verify API nuances using GitHub's official docs. If networking is blocked, say so and distinguish sample data from a real response.
6. Update progress and truthful AI-use notes. Explain what was checked and give me one comprehension question. Then stop at this milestone so we can review it before implementing the client.

For later milestones, follow AGENTS.md: small changes, explanations, mocked HTTP tests with real temporary SQLite files, verified documentation, and no unrequested features. Report evidence and limitations honestly. Do not send the submission or publish anything on my behalf.
