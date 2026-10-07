# AI and verification notes

## Planning completed

Used ChatGPT/Codex to clarify the assessment, sketch architecture, and prepare project instructions and milestones. Read the actual assessment brief. Discussed why missing from one fetched page does not establish that an issue was closed or deleted.

The milestone entries below distinguish planning from implementation and verification. Milestones 1–3 implement the connector; milestone 4 verifies fresh setup, automated checks, real CLI imports/reads, key uniqueness, errors, and prepares documentation/demo instructions. Recording, external sharing/publication, and submission remain pending. Historical entries describe the evidence available at the time.

## Evidence policy

For each meaningful unfamiliar problem, record:

- Problem and what you initially did not understand.
- Specific AI tool and how it helped.
- Proposal accepted, modified, or rejected; why.
- Primary documentation consulted.
- Actual test or manual verification and result.
- What you can now explain without AI.

Do not include secrets, personal information, or unnecessary full chat transcripts.

## Milestone 0 — October 6, 2026

Scope: setup, design proposals, and one read-only public API exploration. No connector functions, CLI, database, or tests were implemented. This entry records agent actions; it does not claim the developer has already learned or accepted the proposals.

Tools and actual use:

- Codex inspected AGENTS.md, docs/PROJECT_BRIEF.md, docs/BUILD_PLAN.md, CODING_PROMPT.md, and the remaining starter files; proposed interfaces/path behavior and edited planning/setup documentation.
- PowerShell ran commands. Git status/diff/history showed an existing repository at 63eb423 with a previously modified README and untracked planning files; those contents were preserved/extended. No staging, commits, remotes, or push.
- Python venv created a new .venv. Initial sandboxed creation failed during ensurepip; a direct ensurepip diagnostic showed PermissionError on temporary files. A project-local TEMP/TMP retry also failed. Retrying the same venv setup with sandbox restrictions lifted succeeded, followed by pip install -r requirements.txt.
- Environment checks: Python 3.13.5, Git 2.33.0.windows.2, requests 2.34.2, pytest 9.1.1, SQLite 3.49.1. sys.prefix differed from sys.base_prefix and sys.executable pointed to .venv/Scripts/python.exe. requests, pytest, sqlite3, and argparse imported. pip check: "No broken requirements found." python -m pytest --version: pytest 9.1.1.
- requirements.txt now pins the two direct dependency versions observed above. Installed transitive versions: certifi 2026.7.22, charset_normalizer 3.5.2, idna 3.20, urllib3 2.8.0, colorama 0.4.6, iniconfig 2.3.1, packaging 26.3, pluggy 1.6.0, pygments 2.21.0. This is not a complete dependency lock or connector compatibility test.
- git check-ignore confirmed .venv/Scripts/python.exe, issues.db, __pycache__/example.pyc, .pytest_cache/example, and .env are excluded. Example paths were checked as names; no database or credential file was created.
- Initial python -m pytest -q encountered a cache permission warning. A retry with the cache plugin disabled hit a collection PermissionError on the generated pytest-cache-files-uv7ip89s directory (exit 2). That exact directory was removed after verifying its absolute path, with sandbox restrictions lifted. A final python -m pytest -q outside the sandbox returned "no tests ran" and exit 5. No tests passed; none exist yet.
- Requests made exactly one unauthenticated GET to https://api.github.com/repos/pallets/flask/issues?state=open&per_page=100&page=1, timeout=20, redirects disabled. A Session with trust_env=False prevented implicit .netrc authentication for this exploration. Headers: Accept application/vnd.github+json and X-GitHub-Api-Version 2026-03-10. No token supplied; no retry, pagination request, or database write.
- Live result: HTTP 200, application/json; charset=utf-8, no Link header. JSON list: 4 entries, 1 without pull_request, 3 with pull_request. Issue #6146: "Add Cloudflare to Flask Hosting Platforms docs?", html_url https://github.com/pallets/flask/issues/6146. PR #5918: "automatic options as separate route", html_url https://github.com/pallets/flask/pull/5918; pull_request contained API/browser/diff/patch URLs and merged_at=null. Printed only selected fields, not the full response.
- Web browsing consulted GitHub's primary documentation: https://docs.github.com/en/rest/issues/issues#list-repository-issues. It confirms public unauthenticated access, case-insensitive owner/repo names, max per_page=100, page selection, and identification of PRs by pull_request key. Future SQLite behavior still requires documentation research and tests in milestone 2.

Unfamiliar API problem and evidence: a repository Issues response mixes issues and PRs. Codex proposed filtering by key presence (even if the value is empty/null), not guessing from titles or using the global id. Official documentation and the observed 3 PR entries support this proposal. number is the repository-local issue number; title is display text; html_url is the browser-facing link. The top-level url is an API endpoint. Neither filtering code nor malformed-response handling has been tested yet.

Design proposals await developer review: import_issues(repo, db_path="issues.db") and read_issues(repo, db_path="issues.db"); stable success/operation/repository/count/issues/error keys; page count for import, all saved rows for read; default path relative to current working directory; no automatic parent creation/fallback; successful empty read of a missing database in an existing parent directory without creating it. Full detail is in Architecture.MD. The illustrative JSON uses a live observed issue but is not connector output.

Remaining evidence at the end of setup: no persistence, transactional rollback, CLI/error handling, offline read, or automated connector verification exists. No assessment demo, external publication, or submission occurred. Developer review and the comprehension question were pending at that point.

### Milestone 0 review — October 6, 2026

The developer answered the count question: import count is 1; a subsequent read is 10 when updating an existing issue or 11 when adding a new issue. Codex confirmed that this matches the contract. The developer then explicitly approved the function inputs and success/failure result keys with "LGTM". Codex updated the checklist and architecture status to record that approval. This completes milestone 0; milestone 1 was not started. These were documentation-only changes, inspected for the approval wording; no new runtime verification or tests were needed or claimed.

## Milestone 1 — October 6, 2026

Scope: GitHub client and focused mocked-HTTP tests only. The developer requested this milestone and explicitly excluded SQLite, connector orchestration, and CLI. Approved milestone 0 public signatures, result keys, normalization, page/count decisions, and planned database behavior were preserved. This records agent actions, not a claim that the developer has mastered or reviewed the new code.

Tools and actual use:

- Codex read AGENTS.md, docs/PROJECT_BRIEF.md, docs/BUILD_PLAN.md, Architecture.MD, docs/AI_NOTES.md, and starter/setup files. Git status showed the already modified README and untracked planning/setup files; existing work was preserved and extended. No sub-agents were used.
- Codex explained inputs, outputs, expected failures, whole-page validation, and the one-page/timeout tradeoffs before coding. It added fetch_issues, a shared normalize_repository function, a small ConnectorError type, an empty package initializer, and tests. The future public JSON envelope is not implemented by this client; later orchestration will translate code/message into the already approved failure contract.
- PowerShell ran the existing .venv interpreter. Python 3.13.5, requests 2.34.2, and pytest 9.1.1 were rechecked; pip check reported "No broken requirements found." No dependencies were installed or pins changed. Fresh-environment setup was not repeated; milestone 0 setup evidence remains separate.
- Web browsing consulted the primary GitHub and Requests references listed below. apply_patch made small source/test/documentation edits. Git status/diff and source inspection reviewed the work. No staging, commit, push, remote change, publication, or submission occurred.
- pytest and unittest.mock intercept HTTPAdapter.send for every test. Real Requests prepares URLs/headers, handles mocked response statuses/redirect metadata, and decodes mocked JSON bytes. An autouse guard raises if a test attempts unconfigured HTTP; no test contacts live GitHub. No new live API exploration, database write, or demo import was performed.
- Final review inspected source/tests and documentation, confirmed generated bytecode and .venv are ignored, and found no trailing whitespace in the nine edited/created files. git diff --check reported no whitespace errors (Git emitted its LF-to-CRLF notice). A request to show github_client.py in the Codex editor returned queued; an open tab was not verified.

Actual test runs, in order:

1. `.\.venv\Scripts\python.exe -m pytest tests/test_github_client.py -q`: 2 failed, 88 passed, 2 cache-permission warnings in 0.76s, exit 1. The two failures were redirect fixture errors (missing response.request metadata), not passing client checks. The existing sandbox cache directory denied writes; no directory was deleted or permissions changed.
2. After correcting the fixture to attach the PreparedRequest and adding an implicit-.netrc guard: `.\.venv\Scripts\python.exe -m pytest tests/test_github_client.py -q -p no:cacheprovider`: 90 passed in 0.39s, exit 0. Disabling the optional cache plugin removed the permission warnings while retaining the tests.
3. After adding invalid/out-of-range URL-port checks and two corresponding cases, the final focused command above reported 92 passed in 0.45s, exit 0.
4. Full available suite: `.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider`: 92 passed in 0.36s, exit 0. Only milestone 1 tests exist; this is not storage/CLI verification.

Verified cases: correct endpoint/query/headers/finite timeout, exactly one transport call despite a next-page link or redirect Location, no implicit credentials, lowercase identity, deterministic issue-number ordering, repository-local number rather than global id, html_url rather than API url, Unicode title preservation, PR exclusion by key presence (null/empty/false/object values), empty/PR-only pages, non-200 status before JSON parsing, timeout and other request errors without retry, invalid JSON, wrong page/entry types, missing/malformed fields after a valid prefix, positive integer number excluding booleans, structural browser-URL checks, invalid input before Session creation, ordinary repository punctuation, valid-looking nonexistent repo reaching HTTP 404, and unexpected programming errors propagating.

Unfamiliar behavior and correction: mocking the transport leaves Requests' real redirect bookkeeping active. The initial fake Response lacked the original PreparedRequest, so 301/302 tests failed inside Requests while it prepared a possible next request even with allow_redirects=False. Codex modified the test fixture to supply response.request and response.url as a real adapter would. The same cases then passed and asserted one adapter call and no JSON parsing of failed statuses. The fixture correction preserved the test's ability to catch accidental redirect following; the client was not weakened to hide the failure. Requests' advanced documentation identifies Response.request as the PreparedRequest, and the traceback supplied direct evidence of the missing metadata.

Implementation choices and limits: only HTTP 200 is accepted; redirects are failures to preserve one request. Returned titles and html_url values are preserved after validation; record errors identify a field and page position without echoing response data. Whole-page validation returns no partial list. PR objects are excluded before checking issue-specific fields. A context-managed Session closes after the request; trust_env=False prevents implicit .netrc authentication but also ignores environment proxies/CA-bundle overrides. URL checks do not establish link existence. The 20-second timeout bounds connection/read waits, not total runtime. No retries, pagination, storage, CLI, or token support was added.

Primary documentation consulted:

- https://docs.github.com/en/rest/issues/issues#list-repository-issues — public unauthenticated access, case-insensitive names, state/page parameters, PR key, status codes, and number/title/html_url examples.
- https://requests.readthedocs.io/en/latest/user/quickstart/ — JSONDecodeError, JSON success versus HTTP success, timeout semantics, request failures, and disabling redirects.
- https://requests.readthedocs.io/en/latest/user/advanced/ — Session context cleanup and Response.request/PreparedRequest metadata.
- https://requests.readthedocs.io/en/latest/user/authentication/#netrc-authentication — implicit netrc authentication and trust_env=False.

Progress: only the three milestone 1 checklist items were marked complete based on the final tests. Milestones 2–4 remain pending. The developer's comprehension answer and review have not yet occurred; no learning outcome is invented.

## Milestone 2 — October 6, 2026

Scope: SQLite storage and focused real-file tests only, as explicitly requested. The approved milestone 0 public signatures, result keys, path/missing-database behavior, and milestone 1 client behavior were preserved. No orchestration or CLI was implemented. This records agent actions; it does not claim the developer has reviewed or mastered the code.

Tools and actual use:

- Codex read AGENTS.md, Architecture.MD, docs/PROJECT_BRIEF.md, docs/BUILD_PLAN.md, docs/AI_NOTES.md, the existing client/error/validation modules, tests, README, setup files, and instructions. Git status showed the previously modified README and untracked project files; their existing contents were preserved and extended. No sub-agents were used.
- Before coding, Codex explained a database file versus a connection, repository-local issue identity, and what a transaction protects, including storage inputs/outputs and tradeoffs. It used apply_patch to add database.py and tests/test_database.py and update documentation/progress. The shared client, validation, error class, and package initializer were not changed.
- PowerShell rechecked the existing .venv: Python 3.13.5, SQLite 3.49.1, requests 2.34.2, pytest 9.1.1. No dependencies were installed or pins changed. Fresh-virtual-environment setup was not rerun; milestone 0 evidence remains separate, and final setup/demo verification stays milestone 4 work.
- Web browsing read primary Python/SQLite references listed below. These informed explicit BEGIN, transaction-context commit/rollback, explicit close, bound parameters, sqlite3.Row, read-only URI paths, composite keys, upsert excluded values, and the failure-trigger test.
- pytest used real SQLite files in tmp_path for storage behavior, including independent connections to inspect committed rows. Tests guard Requests Session creation and HTTPAdapter.send; no live GitHub calls occurred. Storage functions were not mocked to verify persistence or rollback. Connection interception was limited to rejecting invalid input before access, unexpected-error propagation, and recording real connections for close verification.
- Sandbox execution could not access pytest temporary directories. Two low-risk test commands with sandbox restrictions lifted were approved and ran with fresh, dedicated --basetemp paths under the ignored .venv directory. No temporary-directory permissions were changed and no cleanup command was issued.
- Final review inspected database.py, Git status, and documentation status/result wording. git diff --check reported no whitespace errors (with Git's LF-to-CRLF notice for README); a separate scan found no trailing whitespace in the six created/edited files, including untracked files. git check-ignore confirmed the test temporary directories, example database names, and generated bytecode are ignored. AST inspection confirmed storage imports only pathlib, sqlite3, errors, and validation. A filesystem check confirmed main.py and connector.py remain absent.

Actual test runs, in order:

1. `.\.venv\Scripts\python.exe -m pytest tests/test_database.py -q -p no:cacheprovider` — 30 setup errors in 5.44s, exit 1. tmp_path could not scan C:/Users/Linus/AppData/Local/Temp/pytest-of-Linus (PermissionError); no storage case ran or passed.
2. After adding close verification and read-side unexpected-error cases, a sandboxed retry used a previously nonexistent `.venv/pytest-m2-focused-5cb180b1` basetemp directory with --tb=short. It printed 33 error markers and then failed during pytest session cleanup with PermissionError accessing that directory, exit 1. No passing result was reported. Moving temporary files within the writable workspace did not resolve this sandbox restriction.
3. With sandbox restrictions lifted: `.\.venv\Scripts\python.exe -m pytest tests/test_database.py -q -p no:cacheprovider --basetemp .venv/pytest-m2-focused-7c889d20 --tb=short` — 33 passed in 0.65s, exit 0.
4. With sandbox restrictions lifted: `.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp .venv/pytest-m2-full-849a931f --tb=short` — 125 passed in 0.76s, exit 0. This includes all 92 existing client cases and 33 storage cases. The actual shell calls supplied absolute basetemp paths; each path was checked not to exist before running, avoiding replacement of an existing directory.

Verified storage cases: initial insert/read and JSON-compatible structure; deterministic ordering and repository filtering; duplicate-free repeats; changed title/URL updates; equal issue numbers across repositories; lowercase identity; persistence through an independent connection; separate configured files; str/Path inputs and default/relative paths; escaped #/Unicode filenames; empty first/saved batches and omitted-row retention; missing file/table reads without creation; missing parent with no automatic directory/fallback; corrupt/incompatible databases with useful database_error messages; invalid repositories before SQLite access; SQL-like strings stored literally; connections closed after writes, reads, early empty-table reads, and SQLite failures; unexpected RuntimeError/ProgrammingError propagation on both operations.

Unfamiliar database behavior and verification: SQLite's failed statement does not always undo earlier statements in the transaction. Python's connection context manages commit/rollback but does not itself open a transaction or close the connection. Codex proposed explicit BEGIN before schema/batch work, the connection context for commit/rollback, and finally for close. Official documentation supports this design. The rollback test installs a real BEFORE INSERT trigger for issue 99 using RAISE(ABORT), rather than RAISE(ROLLBACK), so the storage transaction must undo earlier statements. The trigger checks that the changed title/URL on issue 7 and new issue 8 are already visible before raising the expected error; its exact IntegrityError message proves both preceding writes occurred. After failure, independent connections observe the original issue 7, no 8/99, and the other repository's row unchanged. Real-connection cleanup tests also pass. No test claims a mock or pre-write failure proves transactional rollback.

Implementation decisions and limitations: storage accepts issue records already validated by the client; it normalizes all repositories and builds row parameters before database access. NOT NULL covers required fields, and composite identity prevents cross-repository collisions. INSERT ... ON CONFLICT updates title/URL without deleting omissions. One explicit transaction includes table creation and all issue writes; failed first writes may still leave an empty database file. Reads use mode=ro and never create schema. Expected database/filesystem errors become ConnectorError(database_error) with path/action/reason and checks; ProgrammingError and other programming bugs propagate. No schema migration, pagination, retry, HTTP dependency in storage, public result envelope, CLI, live import, or demo was added.

Primary documentation consulted:

- https://docs.python.org/3.13/library/sqlite3.html — parameters/placeholders, Row, exception hierarchy, isolation_level=None and explicit transactions, context-manager commit/rollback without closing/opening a transaction, read-only URI examples.
- https://www.sqlite.org/lang_upsert.html — composite conflict target and excluded.title/url as incoming values.
- https://www.sqlite.org/uri.html — mode=ro versus mode=rwc and escaped file URI handling.
- https://www.sqlite.org/lang_transaction.html — errors can leave earlier statements pending; rollback restores the transaction.
- https://www.sqlite.org/lang_createtable.html — required NOT NULL columns and primary-key constraints.
- https://www.sqlite.org/lang_createtrigger.html — trigger conditions and RAISE(ABORT) returns a SQLite constraint failure during a real write.

Progress: milestone 2's three checklist items are marked complete based on passing focused and full suites. Milestones 3 and 4 remain pending. No commit, push, publication, submission, or external access change was performed. The comprehension question is for developer review, not recorded as answered.

## Milestone 3 — October 6, 2026

Scope: reusable connector functions, a thin argparse CLI, focused integration tests, and corresponding documentation only, as explicitly requested. Approved signatures, six result keys, normalization, path/default/missing-database behavior, ordering, retained rows, and existing client/storage interfaces were preserved. This records agent work; it does not claim the developer has reviewed or mastered the implementation.

Tools and actual use:

- Codex read AGENTS.md, Architecture.MD, docs/PROJECT_BRIEF.md, docs/BUILD_PLAN.md, docs/AI_NOTES.md, README, requirements/ignore files, existing client/database/errors/validation/package files, and both existing test modules. Git status and README diff showed existing modified/untracked work, which was preserved and extended. No sub-agents were used.
- Before coding, Codex explained that connector functions coordinate existing components and return results, whereas the CLI parses arguments, calls functions, serializes results, and chooses an exit code. It explained inputs/outputs, the separate argparse syntax-error behavior, whole-page-before-write flow, offline reads, expected-versus-programming errors, and page-versus-stored counts.
- apply_patch added connector.py and main.py, exported import_issues/read_issues from the package, added tests/test_connector.py and tests/test_cli.py, and updated documentation. The existing HTTPAdapter.send autouse guard moved from test_github_client.py to tests/conftest.py for reuse; a controlled-page fixture was added there. Client, validation, database, and error implementations and dependencies were not changed.
- PowerShell rechecked the existing .venv: Python 3.13.5, SQLite 3.49.1, requests 2.34.2, pytest 9.1.1. No dependencies were installed or pins changed. No fresh virtual environment was created or verified; milestone 0 setup evidence remains historical, and final setup/demo verification remains milestone 4 work.
- Web browsing consulted the primary Python argparse and subprocess references below. They informed standard syntax-error text/exit 2, generated help/default descriptions, required subcommands, and running another interpreter with sys.executable and argument lists while capturing streams/exit codes.
- pytest and unittest.mock intercept the HTTP transport. Public import tests retain real Requests page decoding/validation and real SQLite writes under tmp_path. Read checks reject Session creation and HTTP. CLI dispatch-only tests mock the public functions to inspect forwarded arguments; CLI operation/output tests use the real functions. subprocess.run launches separate CLI processes through runpy with child-local Session/HTTP guards and controlled committed SQLite data; no child process performs a live import. Parent monkeypatches are not assumed to apply in child processes.
- Based on milestone 2's observed pytest temporary-directory restrictions, test commands used sandbox restrictions lifted directly and new basetemp paths under ignored .venv. Each absolute temporary path was checked not to exist before pytest ran. No new sandbox failure, permission change, deletion/cleanup command, or fallback location was used in milestone 3.
- Direct `.\.venv\Scripts\python.exe main.py --help` and `.\.venv\Scripts\python.exe main.py read --help` ran with exit 0. They displayed the implemented operations, JSON/error stream and exit behavior, repository argument, configurable file, default relative-to-current-directory rule, and existing-parent requirement. These were help checks, not API imports.
- Final review read the new source and inspected Git status. git diff --check reported no whitespace errors (with Git's LF-to-CRLF notice for README); a separate scan found no trailing whitespace across all 11 created/edited files, including untracked files. Python ast parsed the seven created/edited Python files and confirmed the connector's only two exception handlers catch ConnectorError and the CLI has none. git check-ignore confirmed all three test temporary directories, generated bytecode, and example database names are ignored. Historical milestone notes remain distinguished from current progress; no existing changes were discarded or staged. A request to show connector.py in the Codex editor returned queued; an open tab was not verified.

Actual test runs, in order (shell calls passed absolute basetemp paths):

1. `.\.venv\Scripts\python.exe -m pytest tests/test_connector.py tests/test_cli.py -q -p no:cacheprovider --basetemp .venv/pytest-m3-focused-c81746fa --tb=short` — 2 failed, 30 passed in 1.12s, exit 1. Both failures were help-test assumptions: the contiguous phrase "current working directory" was wrapped across a newline by argparse. They were not operation failures or passing help checks.
2. After changing that assertion to normalize help-output whitespace, the same focused test selection with fresh `.venv/pytest-m3-focused-e9281c6d` reported 32 passed in 1.03s, exit 0. Help output and CLI behavior were preserved.
3. `.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp .venv/pytest-m3-full-4be28d19 --tb=short` — 157 passed in 1.55s, exit 0: all 92 client, 33 storage, and 32 connector/CLI integration cases. Existing transactional rollback verification remains passing; it was not duplicated at the connector layer.

Verified integration behavior: public import then SQLite-only read; lowercase identity and ascending issue order; PR exclusion; repeat import updates a title without duplicates and retains an omitted issue; imported page count=1 versus read count=2; HTTP 503 and timeout failures preserve the database; malformed later page entries prevent any earlier page writes; invalid input returns null repository and the expected failure contract before HTTP or SQLite; both functions select configured str/Path files without writing the default; missing default-file read succeeds without creation, empty import creates the default table, and missing parents return database_error without fallback; unexpected client/write/read and CLI bugs propagate. Expected failure records never expose partial page data.

Verified CLI behavior: selected operation receives raw repository and explicit/default path unchanged, and the other operation is not called; real import success/failure JSON parses from only the correct stream with exit 0/1; Unicode titles survive JSON; five syntax-error cases produce usage/error text and exit 2 without calling operations; main/import/read help returns 0 with useful text; independent guarded CLI processes return controlled committed records with correct ordering and repository isolation, once with explicit --db and once using the current-directory default; a separate malformed-repository import process returns parseable failure JSON and process exit 1 without creating a database.

Unfamiliar boundary and correction: argparse's syntax-error convention differs from the approved operation JSON convention. Codex proposed retaining standard parser behavior and documenting/test-verifying the distinction, keeping the CLI small. Primary argparse documentation supports the convention. The first test run exposed a brittle assumption about help line wrapping; normalizing whitespace corrected the tests without weakening their check of the documented default. Separately, persistence tests must install HTTP guards inside each child interpreter because a pytest monkeypatch is local to its process. Python's subprocess documentation informed launching the same environment via sys.executable with argument lists; the independent CLI reads passed against real saved data. These are agent verification results, not invented developer learning experiences.

Primary documentation consulted:

- https://docs.python.org/3.13/library/argparse.html — required subcommands, generated help, default values, syntax-error usage text on stderr, and exit 2.
- https://docs.python.org/3.13/library/subprocess.html — subprocess.run, capture_output/text, returncode, timeout, argument lists, and sys.executable for another Python process.

Progress: milestone 3's four checklist items are marked complete based on the focused and full suites. Documentation now describes implemented interfaces, count semantics, paths, errors/help, verified synthetic examples, and actual verification. Milestone 4 remains unstarted. No live GitHub call or real connector demo import was made; milestone 0's live exploration is separate evidence. No commit, push, publication, submission, or external access change occurred. The developer's comprehension answer remains pending.

## Milestone 4 — October 6, 2026

Scope: final verification, documentation/repository review, and demo preparation, as requested. No functional defect was found. No feature or automated test was added. This records agent verification; the developer's understanding, narrated demo timing, recording, access, and submission are not inferred from it.

### Tools and changes

- Codex read AGENTS.md, README.md, Architecture.MD, docs/PROJECT_BRIEF.md, docs/BUILD_PLAN.md, docs/AI_NOTES.md, source/tests, dependencies/ignore rules, and the original starter instructions. Git initially tracked only README.md, which was already modified; all other project files were untracked. Existing implementation/tests and historical evidence were preserved. No sub-agents were used.
- PowerShell/Python venv/pip created a separate environment and installed only requirements.txt. subprocess ran the actual main.py in separate child interpreters with captured streams/exit codes. Requests performed real unauthenticated imports; sqlite3 independently inspected the disposable saved database. No HTTP mock was installed for these live CLI calls.
- pytest used the existing guarded HTTP boundary and real tmp_path SQLite files. The full suite was run twice: first to verify fresh setup, then after documentation/source-docstring edits before delivery. No automated test contacted GitHub.
- Web browsing rechecked [GitHub's list-repository-issues documentation](https://docs.github.com/en/rest/issues/issues#list-repository-issues) and [Python 3.13 venv documentation](https://docs.python.org/3.13/library/venv.html): public unauthenticated access, PR key presence, one-page parameters, isolated site-packages, and direct executable use. No new unfamiliar behavior required a product change. Previous unfamiliar-problem proposals/corrections remain documented in milestones 1–3.
- apply_patch shortened README/architecture around the final implementation, added actual live output, updated current progress, replaced stale START_HERE descriptions, labeled CODING_PROMPT as historical, and added docs/DEMO.md. It also removed "future" from two source module docstrings and updated the requirements comment. Runtime logic, dependency pins, and all tests were preserved. An initial delete/add patch was rejected because both operations targeted the same files; a replacement using update operations applied successfully. No files changed in the rejected attempt.
- Git inspected tracked/non-ignored files, status, whitespace, and ignore rules. Python parsed all 12 candidate Python files and checked Markdown fences/local links, whitespace, generated-artifact names, and common GitHub-token/private-key patterns without printing secrets. At review, 23 submission candidates included source, tests, requirements, README, architecture, and project docs; no generated databases/environments/caches or matching credential patterns were found among them. git diff --check passed, with Git's LF-to-CRLF notice for README. Final staging/commit/publication/access remains manual. A request to open docs/DEMO.md in Codex returned queued; a visible editor tab was not verified.

### Fresh environment and setup evidence

The existing .venv was preserved. Test-Path confirmed .venv/verification-m4 did not exist before creation. The setup commands followed README, with only the environment path deliberately substituted to satisfy the separate-clean-environment request:

```powershell
python --version
git --version
python -m venv .venv/verification-m4
Get-Content .venv/verification-m4/pyvenv.cfg
.\.venv\verification-m4\Scripts\python.exe -m pip list
.\.venv\verification-m4\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\verification-m4\Scripts\python.exe -m pip check
.\.venv\verification-m4\Scripts\python.exe -m pytest --version
.\.venv\verification-m4\Scripts\python.exe -m pip list
```

Creation and installation returned exit 0. Before installation, pip list showed only pip 25.1.1; include-system-site-packages was false. After installing only requirements.txt, pip check reported "No broken requirements found" and pytest --version reported pytest 9.1.1. pip reused cached package distributions; the clean environment did not reuse installed packages from the old environment or global site-packages. No pip upgrade, extra dependency, project installation, activation, or execution-policy change was needed.

Versions actually observed:

| Component | Version |
| --- | --- |
| Python | 3.13.5, 64-bit Windows |
| SQLite bundled with Python | 3.49.1 |
| Git | 2.33.0.windows.2 |
| pip | 25.1.1 |
| requests / pytest | 2.34.2 / 9.1.1 |
| certifi / charset-normalizer / idna / urllib3 | 2026.7.22 / 3.5.2 / 3.20 / 2.8.0 |
| colorama / iniconfig / packaging / pluggy / Pygments | 0.4.6 / 2.3.1 / 26.3 / 1.6.0 / 2.21.0 |

Python inspection confirmed sys.executable and sys.prefix under .venv/verification-m4, sys.base_prefix=C:/Python313, requests/pytest loaded from that environment's Lib/site-packages, and github_issue_connector loaded from the project root. With PYTHONPATH unset, these imports all succeeded: the public functions from github_issue_connector and github_issue_connector.connector (identity also checked), fetch_issues from github_issue_connector.github_client, and upsert_issues/read_saved_issues from github_issue_connector.database. Standard argparse and sqlite3 imported. No sys.path injection or global-package dependency was used for these checks.

```powershell
Remove-Item Env:PYTHONPATH -ErrorAction SilentlyContinue
.\.venv\verification-m4\Scripts\python.exe main.py --help
.\.venv\verification-m4\Scripts\python.exe main.py import --help
.\.venv\verification-m4\Scripts\python.exe main.py read --help
.\.venv\verification-m4\Scripts\python.exe -m pytest -q -p no:cacheprovider
```

All help commands displayed the implemented operations/options/default-path behavior. Initial full suite: **157 passed in 1.37s, exit 0**. Final full suite after edits: **157 passed in 1.45s, exit 0**. The exact documented pytest command worked without an additional --basetemp setting. Existing cases include real late-write rollback and independent-process guarded reads.

Environment creation/install, tests, and live-network commands used approved execution outside sandbox restrictions based on the earlier observed ensurepip/pytest temporary-file permissions and restricted network access. There was no blocked attempt in this milestone, no permission change, and no automatic-approval rejection. Ordinary interpreter/help/source checks also ran within the sandbox. Verification is for this Windows/Python version; it does not establish success under the restricted sandbox, older Python versions, or a proxy-dependent network.

### Actual live connector commands and results

The disposable ./milestone4-live.db was confirmed absent before use. A Python driver called subprocess.run with argument lists, the clean sys.executable, main.py, project-root cwd, capture_output=True, UTF-8 text decoding, and PYTHONPATH removed. Each line below was a separate actual CLI child process; import/read were not invoked inside a pytest fixture or runpy wrapper:

```powershell
.\.venv\verification-m4\Scripts\python.exe main.py import pallets/flask --db ./milestone4-live.db
.\.venv\verification-m4\Scripts\python.exe main.py read pallets/flask --db ./milestone4-live.db
.\.venv\verification-m4\Scripts\python.exe main.py import pallets/flask --db ./milestone4-live.db
.\.venv\verification-m4\Scripts\python.exe main.py read pallets/flask --db ./milestone4-live.db
.\.venv\verification-m4\Scripts\python.exe main.py import owner/repo/extra --db ./milestone4-live.db
.\.venv\verification-m4\Scripts\python.exe main.py read pallets/flask --db
```

| Process | Actual result | Elapsed |
| --- | --- | --- |
| First live import | success=true, operation=import, count=1; JSON stdout, stderr empty, exit 0 | 0.682 s |
| First independent read | success=true, operation=read, count=1; JSON stdout, stderr empty, exit 0 | 0.199 s |
| Repeated live import | success=true, operation=import, count=1; JSON stdout, stderr empty, exit 0 | 0.461 s |
| Second independent read | success=true, operation=read, count=1; JSON stdout, stderr empty, exit 0 | 0.220 s |
| Malformed repository import | invalid_repository; JSON stderr, stdout empty, exit 1 | 0.228 s |
| Missing --db value | argparse usage/error text stderr, stdout empty, exit 2 | 0.210 s |

Both imports returned the following exact JSON, apart from the terminal newline. Both reads returned the same object with operation="read":

```json
{"success": true, "operation": "import", "repository": "pallets/flask", "count": 1, "issues": [{"repository": "pallets/flask", "issue_number": 6146, "title": "Add Cloudflare to Flask Hosting Platforms docs?", "url": "https://github.com/pallets/flask/issues/6146"}], "error": null}
```

After each import/read pair, an independent sqlite3 connection opened that file via mode=ro and ran:

```sql
SELECT repository, issue_number, title, url
FROM issues ORDER BY repository, issue_number;

SELECT repository, issue_number, COUNT(*)
FROM issues GROUP BY repository, issue_number HAVING COUNT(*) > 1;

PRAGMA table_info(issues);
PRAGMA integrity_check;
```

Results after both pairs: exactly the displayed saved row; **duplicate groups=[]**; primary-key positions **repository=1, issue_number=2**; **integrity_check=ok**. Each imported key/title/URL was compared to the independently queried stored row, and read count matched those rows. This proves key-based uniqueness and persistence rather than relying on equal counts. SQLite connections were explicitly closed.

Expected operation error, exact JSON on stderr:

```json
{"success": false, "operation": "import", "repository": null, "count": 0, "issues": [], "error": {"code": "invalid_repository", "message": "Use owner/name with letters, digits, dots, underscores, or hyphens; no whitespace, URLs, extra slashes, backslashes, or . / .. components."}}
```

The driver asserted exit 1, empty stdout, and invalid_repository. SHA-256 of the database bytes before/after that invalid input was identical. The separate syntax-error process returned exit 2 and:

```text
usage: main.py read [-h] [--db PATH] owner/repo
main.py read: error: argument --db: expected one argument
```

The complete captured streams/arguments, timings, and SQLite results were written to ignored .venv/verification-m4/live-evidence.json. The concise durable record is this entry; the environment/evidence/database are not submission files. Databases remain locally ignored, and none was staged or committed.

### Demo rehearsal and delivery limits

docs/DEMO.md provides preflight variables, readable PowerShell summaries of actual CLI JSON, direct SQL uniqueness inspection, the expected error/exit code, narration, and a 105-second schedule. Its five PowerShell blocks were extracted in order and executed as authored, substituting only the fresh database filename ./demo-m4-rehearsal.db instead of ./demo-m4.db. PYTHONPATH was unset. The repeated real import/read summary displayed count=1 and issue #6146; the SQL command printed duplicate_groups: []; the error printed actual failure JSON and exit code: 1. A final assertion checked that expected exit code. The rehearsal command returned exit 0; all command execution without narration took **2.116 seconds**. It made two additional real GitHub imports; there were four live connector imports total in this milestone. This is command rehearsal, not a measured narrated 1:45 recording.

README and architecture were reviewed against source: function contract, module responsibilities, whole-page-before-write flow, composite key/upsert, transaction commit/rollback/close, current-directory path rules, retained rows/page versus stored counts, one-page limit, and expected versus argparse/programming errors are documented. Historic starter directions were replaced/labeled without erasing milestone records. Source/tests/dependencies are locally prepared; most files remain untracked because no staging/commit was requested. Generated artifacts are ignored and absent from submission candidates. No functional code or test change was required.

Remaining manual work: review/commit/publish the repository, rehearse and record under two minutes, upload to Google Drive, verify video playback and reviewer access to both links, and reply only to the sender in the original email thread before October 7, 2026, 11:59 p.m. Pacific. No record/upload/access/publication/email action was performed. The comprehension question is offered in BUILD_PLAN.md and is not recorded as answered.

## Final Git review and local commit preparation

Scope: the developer explicitly requested a final review of tracked and untracked files, staging, staged-diff inspection, a descriptive local commit, and the exact publishing command based on configured remotes. Pushing was explicitly excluded. This entry records the review/preparation performed before the final commit command; the delivery response reports the resulting commit identity.

- Codex read the brief/build plan, all 23 submission candidates (including their untracked contents), and Git status/history/configuration. PowerShell and Git inspected the branch, remotes, candidate manifest, README changes, ignore rules, and staged changes. No sub-agents were used. Source/tests/dependencies and unrelated local generated artifacts were preserved; no functional changes were needed.
- The existing clean `.venv/verification-m4` interpreter ran `.\.venv\verification-m4\Scripts\python.exe -m pytest -q -p no:cacheprovider`: **157 passed in 1.54s, exit 0**. Execution outside sandbox restrictions was approved because earlier runs established pytest temporary-directory failures. Existing HTTP guards keep this suite offline. No environment installation or new live import was performed in this review.
- Python parsed all 12 candidate Python files and scanned all 23 candidate contents for trailing whitespace and common GitHub-token, private-key, AWS-key, and credential-literal patterns. Both findings lists were empty; matching values would have been suppressed. This is a focused scan, not a claim that every possible secret format was detected. Content review found no credentials or unrelated submission files.
- `.gitignore` already covered the actual .venv, bytecode/caches, two live/rehearsal databases, SQLite sidecars, and .env names. `git check-ignore -v` verified those rules; no ignore changes were necessary. A Git ignored-files inventory encountered permission warnings inside old ignored temporary/cache directories. Those paths were preserved and remain excluded.
- The first explicit `git add` failed with index.lock Permission denied in the sandbox. The same 23-path add command then succeeded with approved execution outside the sandbox. There was no automatic-approval rejection. `git diff --cached --check` passed; the staged manifest and source/test diffs were inspected. Git emitted LF-to-CRLF notices consistent with existing core.autocrlf=true; no whitespace error was reported.
- apply_patch updated current delivery guidance and this record while preserving historical milestone evidence. The intended local commit packages .gitignore, six package modules plus main.py, five test files, requirements.txt, README.md, Architecture.MD, AGENTS.md, START_HERE.md, CODING_PROMPT.md, and four docs/ files. Generated databases, environments, caches, and secrets are excluded.
- Current branch main tracks origin/main. `git remote -v` and Git configuration identify origin's fetch/push URL as https://github.com/linuswong/GithubIssueConnector.git. The exact publishing command is `git push origin main:main`; it was not executed. No remote configuration, branch history, external access, upload, or email was changed.

Tradeoff: the assessment's build plan, AI-use evidence, demo script, and historical prompt are included because they document this project and its verification. Generated runtime artifacts stay local. Recording, repository publication/access verification, video sharing, and submission remain pending. No developer comprehension response is claimed.
