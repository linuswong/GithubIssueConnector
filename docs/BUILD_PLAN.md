# Build plan

Milestones 0–3 and milestone 4's local verification/documentation/demo preparation are complete on October 6, 2026. Recording, publication, reviewer access, and email submission remain manual and unverified. Historical milestone entries describe what was true at the end of each milestone.

## 0. Initialize and understand

- [x] Read AGENTS.md, PROJECT_BRIEF.md, BUILD_PLAN.md, and CODING_PROMPT.md; inspect existing work and Git status.
- [x] Confirm Python 3.13.5 and Git 2.33.0.windows.2; create a fresh project .venv.
- [x] Install requirements; verify requests 2.34.2 and pytest 9.1.1 imports/startup, then pin those direct dependencies. pip check passed.
- [x] Existing repository (commit 63eb423); no git init needed. Verify ignore rules for environment, databases, caches, and .env. Nothing staged or committed.
- [x] Agree on function inputs and success/failure result keys. Documented in Architecture.MD; developer approved with "LGTM" on October 6, 2026.
- [x] Propose and document issues.db relative to the caller's current working directory, configurable in both functions and CLI; implemented in milestones 2–3.
- [x] Make one unauthenticated public GET for pallets/flask with state=open, per_page=100, page=1: HTTP 200, 4 entries, 1 issue, 3 PRs. Inspect fields; no database writes.

Evidence and limitations: initial sandboxed venv creation failed on ensurepip temporary-directory permissions, including a retry using project-local temporary files. A retry with sandbox restrictions lifted completed setup. Verified isolated interpreter, built-in sqlite3/argparse imports (SQLite 3.49.1), pytest startup, and dependency consistency. Initial sandboxed pytest runs hit cache/collection permission errors; the one generated temporary directory was removed and a rerun outside the sandbox reported no tests ran (exit 5). No connector tests exist yet. No connector implementation, persistence check, or demo import has occurred. See docs/AI_NOTES.md for actual tool use and API observations.

Explain: What is the difference between an API response, Python objects, and saved database rows?

## 1. GitHub client

- [x] Validate repository input, make one request with a finite timeout, check HTTP status, and parse JSON.
- [x] Filter pull requests and map records to the required fields.
- [x] Test one page, mixed issue/PR data, empty data, malformed data, and request failure using mocks.

Evidence: `fetch_issues(repo)` validates/normalizes before creating a Session, requests state=open/per_page=100/page=1 with timeout=20 and redirects disabled, requires HTTP 200, and returns a sorted list or an expected error carrying an agreed code/message. All retained records must validate; pull_request key presence excludes PRs regardless of value. Supporting validation/error modules preserve the approved future public interface and result keys.

Final focused command: `.\.venv\Scripts\python.exe -m pytest tests/test_github_client.py -q -p no:cacheprovider` — 92 passed in 0.45s, exit 0. Full available suite: `.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider` — 92 passed in 0.36s, exit 0. HTTPAdapter.send is mocked and guarded in every test; no live API request occurs. Initial fixture failures, their correction, and the optional cache-plugin restriction are recorded in docs/AI_NOTES.md.

Limits: no SQLite storage, public import/read operation, CLI, persistence check, fresh setup rerun, or real import/demo was added in this milestone. The fresh environment and live exploration remain milestone 0 evidence; a real connector demo and full setup verification remain milestone 4 work. The comprehension question is offered for developer review, not recorded as answered.

Explain: Why can a page contain fewer saved issues than the requested page size?

## 2. SQLite storage

- [x] Create the table with the composite key; implement transactional upsert and deterministic read.
- [x] Explicitly close connections; test persistence across new connections.
- [x] Test title updates, duplicates, repository isolation, configurable file paths, and rollback.

Evidence: database.py exposes internal upsert_issues and read_saved_issues functions, preserving the future approved public signatures and result keys. Required columns use NOT NULL and PRIMARY KEY (repository, issue_number). Bound SQL inserts/updates title and URL; missing rows are retained. One explicit BEGIN includes schema creation and the batch, with commit/rollback via the connection context and close in finally. Storage has no HTTP/client dependency; repository normalization precedes SQLite access.

Path evidence: default issues.db follows current working directory; str/Path, absolute/relative paths, separate files, and a filename containing #/Unicode are tested. Missing-file and missing-table reads return [] without creation; missing parents fail without creating directories or selecting a fallback. Existing databases are read with mode=ro. Corrupt/incompatible databases produce database_error; unexpected programming errors propagate.

Final focused command: `.\.venv\Scripts\python.exe -m pytest tests/test_database.py -q -p no:cacheprovider --basetemp .venv/pytest-m2-focused-7c889d20 --tb=short` — 33 passed in 0.65s, exit 0. Full available suite: `.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp .venv/pytest-m2-full-849a931f --tb=short` — 125 passed in 0.76s, exit 0 (92 client + 33 storage). Actual calls supplied absolute paths to these basetemp directories. Both ran with sandbox restrictions lifted after temporary-directory PermissionErrors; the earlier blocked attempts are recorded in docs/AI_NOTES.md.

Rollback evidence: a real SQLite trigger observes the updated title/URL of issue 7 and new issue 8 inside the transaction before RAISE(ABORT) rejects issue 99. The resulting IntegrityError becomes database_error. Independent connections then see the original issue 7, no issues 8/99, and the other repository unchanged. Other cases cover initial writes, repeat writes, persistence, empty/omitted rows, literal SQL-like values, offline reads, and closed connections on success/empty read/failure.

Limits: no orchestration, public import/read envelope, CLI, fresh environment re-verification, or real connector import/demo was added. The GitHub client and shared validation/error definitions were preserved. The developer's comprehension response and review are pending; no learning outcome is claimed.

Explain: Why does issue number alone fail as a primary key? Why is deletion based on an incomplete page unsafe?

## 3. Reusable connector and CLI

- [x] Implement import_issues and read_issues with consistent results.
- [x] Add argparse import/read commands and --db; print parseable JSON and useful exit codes.
- [x] Prove read cannot make a network call and a failed import preserves existing rows.
- [x] Distinguish per-import count from total stored count in behavior and documentation.

Evidence: connector.py coordinates the unchanged validator/client/storage interfaces and catches only ConnectorError. Both public functions are exported from the package and use the shared issues.db default. Import validates input and fetches the whole validated/sorted page before transactional upsert; read validates input and calls SQLite storage only. Both return the approved six-key result. Invalid input has repository=null; valid input uses lowercase repository even on failure. Failed results expose no partial issue list, and unexpected programming bugs propagate.

CLI evidence: main.py parses import/read, owner/repo, and --db, calls the corresponding reusable function, prints JSON on stdout with exit 0 for success or stderr with exit 1 for expected failure. Syntax errors retain argparse usage/error text on stderr and exit 2 before an operation; --help prints text and exits 0. Help documents operations, paths/defaults, and exit behavior. README and Architecture.MD describe the implemented contract and synthetic verified examples.

Final focused command: `.\.venv\Scripts\python.exe -m pytest tests/test_connector.py tests/test_cli.py -q -p no:cacheprovider --basetemp .venv/pytest-m3-focused-e9281c6d --tb=short` — 32 passed in 1.03s, exit 0. Full suite: `.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp .venv/pytest-m3-full-4be28d19 --tb=short` — 157 passed in 1.55s, exit 0 (92 client + 33 storage + 32 integration). Actual calls supplied absolute fresh temporary paths under ignored .venv and used sandbox restrictions lifted, based on prior verified temporary-file restrictions. Initial help-test assertion failures and their correction are recorded in docs/AI_NOTES.md. Direct main.py --help and read --help also ran with exit 0.

Integration evidence: mocked HTTP plus real tmp_path SQLite files verify import/read, PR exclusion/order, updates without duplicates, retained omissions, page count=1 versus stored count=2, API/timeout failures and a malformed page preserving existing data, invalid input before Session/SQLite creation, both configured str/Path files, shared default/empty import/missing read, useful database errors without fallback, and unexpected-error propagation. Read tests make Session/HTTP raise if touched. Separate CLI processes use controlled committed rows, check both --db and current-directory default, repository isolation/order, JSON/exit codes, and child-local HTTP guards. Storage is not mocked for persistence checks; existing milestone 2 rollback tests pass in the full suite.

Limits: no dependency installation, new virtual environment, live GitHub request, real connector demo, commit, publication, or submission occurred. Milestone 4 remains unstarted. The developer's comprehension answer is pending, not recorded as a learning outcome.

Explain: Why does application logic belong in reusable functions rather than the CLI?

## 4. Final verification and submission preparation

- [x] Create a separate clean environment; install only documented dependencies; verify versions, import paths, all help commands, and the full test suite without PYTHONPATH/global-package dependencies.
- [x] Perform two real public imports into a new disposable file and read after each in separate CLI processes.
- [x] Query SQLite for duplicate composite-key groups, inspect the primary key, and check integrity; equal counts alone are not the evidence.
- [x] Verify an expected operation error's JSON/stderr/exit 1 and saved-data preservation; separately verify argparse text/stderr/exit 2.
- [x] Review README and concise architecture against implementation/evidence; add actual live output and remove stale starter descriptions.
- [x] Record actual AI/tool use, commands/results, and verification limitations.
- [x] Review tracked and non-ignored submission candidates for source/tests/dependencies/docs and unwanted artifacts; preserve prior work.
- [x] Prepare and execute readable live-demo commands; provide a narration schedule targeting 1:45 in docs/DEMO.md.
- [ ] Rehearse narration with a stopwatch and record a demo under two minutes.
- [x] Review tracked and untracked submission contents, stage the intended files, and inspect the staged diff for the requested local commit (see final Git review below).
- [ ] Publish the reviewed source and verify repository access. No push or access check has occurred.
- [ ] Upload the recording to Google Drive and verify reviewer access/playback.
- [ ] Reply only to the sender in the original email thread before the deadline.

Evidence: a newly created .venv/verification-m4 initially contained only pip and had include-system-site-packages=false. Installing requirements.txt gave requests 2.34.2 and pytest 9.1.1; Python 3.13.5, SQLite 3.49.1, and pip 25.1.1 were observed. pip check passed. Public package/module imports resolved from the project root with PYTHONPATH unset. All three help commands worked. The documented full command using that interpreter passed 157 tests in 1.37s, exit 0. Approved execution outside sandbox restrictions was used for setup/tests/live networking based on earlier permission failures; no test contacted GitHub.

Live evidence: import pallets/flask --db ./milestone4-live.db, separate read, repeated import, and another separate read all returned success JSON on stdout, empty stderr, exit 0, count=1, and issue #6146. SQLite duplicate-group queries returned [] after each import; PRAGMA table_info showed repository as key position 1 and issue_number as position 2; integrity_check returned ok. Invalid owner/repo/extra returned JSON only on stderr with invalid_repository and exit 1, leaving the database bytes unchanged. read pallets/flask --db returned usage/error text only on stderr and exit 2. Commands, exact output, versions, and limitations are recorded in docs/AI_NOTES.md.

Final delivery check: after documentation/docstring edits, the same full-suite command passed 157 tests in 1.45s, exit 0. The exact demo PowerShell blocks ran successfully with a different fresh disposable filename, showing actual live import/read output, duplicate_groups: [], and the expected JSON/exit 1. Command execution took 2.116 seconds without narration; this does not verify recorded-demo duration.

Limits: no functional defect was found, no feature/test was added, and only stale source docstrings/dependency commentary changed outside documentation. Other Python versions and proxy-dependent networks were not verified. Git initially tracked only README.md; source/tests/docs were untracked and remain unstaged. Live databases and the clean environment are ignored and must stay out of the eventual commit. Narration/video timing, reviewer access, publication, and submission are not verified.

Demo schedule: intro 10 s; live import 25 s; separate read 15 s; repeat import/read plus SQL uniqueness 30 s; error 15 s; composite-key decision 10 s = 1:45. See docs/DEMO.md for the exact commands and manual checklist. Counts may change with GitHub data; uniqueness is checked by grouping on the key.

Explain: Why do unchanged counts after a repeated import fail to prove that the database contains no duplicate issue identities?

## Final Git review

The developer separately requested staging and a descriptive local commit, with no push. All 23 submission candidates were read, including previously untracked contents: the six package modules, root CLI, five test files, requirements.txt, README.md, Architecture.MD, .gitignore, and seven project instruction/planning/demo documents. No unrelated candidate was found. Existing source, tests, dependency pins, and ignore rules were preserved.

Evidence: the verified milestone 4 interpreter ran `python -m pytest -q -p no:cacheprovider` again: **157 passed in 1.54s, exit 0**. All 12 Python candidates parsed. A scan of all candidate contents found no matching common credential patterns or trailing whitespace. `git check-ignore -v` confirmed environment, bytecode, cache, SQLite/sidecar, and .env exclusions. Explicit file paths were staged and `git diff --cached --check`, staged source/test diffs, and the 23-file staged manifest were inspected. Documentation now distinguishes this review from milestone 4's earlier unstaged state.

Git configuration: current branch main tracks origin/main; origin fetch and push URLs are https://github.com/linuswong/GithubIssueConnector.git. The publishing command from this project is `git push origin main:main`. Publication, remote access, recording, and email submission remain unverified. The local commit is the final operation after reviewing these documentation updates; its identity is reported in the delivery response.

Explain: Why does `git diff` alone miss files that have never been tracked?
