# Instructions for coding agents

## Goal and scope

Build a small, reliable GitHub issue snapshot connector for an individual assessment. The developer is learning and must be able to explain the code. Read [docs/PROJECT_BRIEF.md](docs/PROJECT_BRIEF.md) and [docs/BUILD_PLAN.md](docs/BUILD_PLAN.md) before changing the project. User instructions take precedence over this file.

Use Python, requests, built-in sqlite3 and argparse, and pytest. Keep a flat, importable package at github_issue_connector/ plus a thin root main.py. Prefer functions and standard-library tools over frameworks and unnecessary classes. No UI, pagination, background polling, deployment, ORM, Docker, or required authentication. Do not delegate to sub-agents.

The developer explicitly requested the optional Tkinter viewer on October 7, 2026, overriding the original no-UI scope for that extension. Preserve its read-only behavior and the existing CLI/public contract. The other scope limits still apply.

## Learning workflow

- Follow the milestone requested by the user. Do not generate the entire implementation when asked for a first step.
- Before implementing a new concept, explain its purpose, inputs, outputs, and one relevant tradeoff in plain language.
- Make small, coherent changes. Explain non-obvious decisions; avoid comments that merely repeat code.
- After each milestone, explain what changed, how it was checked, remaining limitations, and one question the developer should be able to answer.
- Record the actual use of AI and verification in docs/AI_NOTES.md. Never invent tools used, learning experiences, test results, or manual checks.
- Research unfamiliar API and database behavior using primary documentation; record relevant links.

## Required behavior

- Accept a public repository as owner/name; reject malformed input before network or database work. Normalize repository casing consistently for storage and lookup. Reject URLs, extra slashes, empty components, whitespace, and path traversal components. Avoid a needlessly restrictive validator; a valid-looking but nonexistent repository is an API error.
- Import exactly one page of open issues from GitHub. Do not follow pagination links. Exclude objects containing the pull_request key. Store repository, issue_number, title, and the browser-facing issue URL (html_url).
- Validate and transform the whole fetched page before writing. Do not silently discard malformed issue records.
- Use a composite PRIMARY KEY (repository, issue_number). Upsert returned issues and update title and URL on conflict. Retain prior rows absent from later pages; absence does not prove closure or deletion.
- Apply each import's issue writes in one transaction so a failure cannot leave a partly written batch. Commit successful writes and close connections explicitly.
- Read saved rows for the requested repository from SQLite only. Reading must not instantiate a GitHub client or perform HTTP. Return rows in a deterministic order.
- Support a configurable database file path in both public functions and CLI commands. Choose and document a default path and its relation to the current working directory. Do not silently create parent directories or choose another path on failure.
- Expose reusable import_issues and read_issues functions; the CLI only parses arguments, calls them, prints JSON, and sets an exit code.
- Choose one JSON-compatible response contract with stable keys for success and failure. Explain count semantics: issues imported in this page may differ from all stored issues. Avoid a catch-all exception handler that hides programming bugs.
- Use useful errors for malformed repository input, failed HTTP requests, timeouts, malformed responses, and database failures. Use a finite request timeout, parameterized SQL, and no SQL interpolation of user values. Keep error output separate from unexpected internal tracebacks.
- Public repository access must work without a token. Never print or commit credentials.

## Verification

Automated tests must not contact live GitHub. Mock the HTTP boundary rather than mocking away the storage being verified; use pytest tmp_path for real temporary database files.

Cover import, local read, duplicate-free repeated import, changed-title updates, PR exclusion, API failure, and two repositories with the same issue number. Prove persistence using a new connection or process. Patch HTTP to fail if called during a read. Check invalid input, an empty page, configurable paths, and failed-import preservation of saved data. Add transaction rollback verification when implementing that behavior.

Run relevant tests for each milestone, then the full suite before delivery. Use python -m pytest. Do not claim tests passed unless you ran them; report restrictions honestly. Verify setup from a fresh virtual environment and perform a real import for the demo separately from automated tests.

## Repository and documentation

- Inspect existing files and git status before editing. Preserve unrelated changes. Never overwrite existing work merely to match the proposed structure.
- Keep database files, virtual environments, caches, and credentials out of git.
- Keep dependencies minimal; record versions actually tested after installation. Do not invent pins.
- README.md must include prerequisites, dependencies, setup, run/test commands, example inputs/outputs, specific tools and their uses, and one unfamiliar problem with evidence of verification or correction.
- Architecture.MD must concisely explain interface, components, data flow, schema, configuration, errors, and tradeoffs. Update it to match the implementation.
- Keep progress and actual AI-use notes in docs/BUILD_PLAN.md and docs/AI_NOTES.md. Do not mark work complete without evidence.
- Local commits may be made when requested. Do not push, publish, send a submission, or change external access unless the user requests that action. Never rewrite git history or discard changes without explicit authorization.
