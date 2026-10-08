# Build plan

Milestones 0–3 and milestone 4's local verification/demo preparation are complete. The optional desktop viewer and styling were added at the developer's request on October 7, 2026. Latest full-suite result: **180 passed, no skips**. Recording and external delivery remain unverified.

Historical results below describe what was checked at that stage. Detailed tools, corrections, commands, and limitations are in [AI_NOTES.md](AI_NOTES.md).

## 0. Initialize and understand — October 6

- [x] Read the instructions and assessment brief; inspect existing files and Git status.
- [x] Create .venv, install requirements, verify isolation/versions, and check ignore rules.
- [x] Agree on function inputs, six result keys, count semantics, and current-directory database paths.
- [x] Make one unauthenticated API exploration without database writes.

Evidence: Python 3.13.5, Git 2.33.0.windows.2, SQLite 3.49.1, requests 2.34.2, and pytest 9.1.1. pip check passed. The API returned four entries: one issue and three PRs. Setup required approved execution outside sandbox temporary-file restrictions. No connector tests existed yet; the final initial pytest run returned exit 5, no tests.

The developer answered the count example and approved the interface with "LGTM."

Review question: How do an API response, Python objects, and saved rows differ?

## 1. GitHub client — October 6

- [x] Validate/normalize owner/name before creating a session.
- [x] Request one page with a finite timeout and check status/JSON.
- [x] Exclude PRs and validate the entire retained page.
- [x] Cover mixed/empty/malformed pages, invalid inputs, and request failures with HTTP mocks.

Evidence: focused suite **92 passed in 0.45s**; full available suite **92 passed in 0.36s**, exit 0. Tests intercept HTTPAdapter.send and forbid unconfigured HTTP. Redirect fixtures were corrected to include PreparedRequest metadata; no SQLite or CLI existed at this stage.

Review question: Why can one API page yield fewer saved issues than its requested page size?

## 2. SQLite storage — October 6

- [x] Implement a composite primary key, transactional upsert, and deterministic local read.
- [x] Close connections explicitly and prove persistence through new connections.
- [x] Verify updates, uniqueness, repository isolation, configured paths, retained omissions, and rollback.

Evidence: focused suite **33 passed in 0.65s**; full available suite **125 passed in 0.76s**, exit 0. A real late-failure trigger observes earlier writes before raising ABORT; independent connections then see the original data. Tests cover read-only access, missing-file/table empty reads, missing parents without fallback, corrupt schemas, bound values, and connection cleanup. Sandbox temporary-directory failures required approved outside-sandbox runs.

Review question: Why does issue number alone fail as the key, and why is deletion based on one page unsafe?

## 3. Reusable connector and CLI — October 6

- [x] Export import_issues and read_issues with consistent success/failure results.
- [x] Add argparse import/read commands, --db, JSON streams, and exit codes.
- [x] Prove local read makes no HTTP call and failed imports preserve saved rows.
- [x] Distinguish per-page import count from total saved read count.

Evidence: focused connector/CLI suite **32 passed in 1.03s**; full suite **157 passed in 1.55s**, exit 0. Real temporary databases and separately guarded CLI processes verify persistence, paths, counts, streams, and errors. Initial help assertions were corrected for argparse line wrapping. No live connector import occurred in this milestone.

Review question: Why should application logic live in reusable functions rather than the CLI?

## 4. Verification and demo preparation — October 6

- [x] Create separate .venv/verification-m4 and install only documented requirements.
- [x] Check package locations with PYTHONPATH unset, pip consistency, help, and the full suite.
- [x] Run real imports and independent CLI reads against fresh disposable databases.
- [x] Inspect composite key positions, duplicate groups, and SQLite integrity.
- [x] Check JSON operation errors, argparse errors, and failed-import file preservation.
- [x] Review source/tests/docs and prepare executable demo commands and narration.

Evidence: the clean environment had include-system-site-packages=false and initially only pip. Setup and all help commands succeeded. Full tests passed **157 in 1.37s**, then **157 in 1.45s** after doc/docstring edits. Four real imports across live verification and command rehearsal returned Flask issue #6146; independent reads matched. Duplicate groups were empty, key positions were repository=1 and issue_number=2, and integrity_check returned ok.

The authored demo command blocks ran in **2.116 seconds without narration**. That does not establish recording length. The revised diagram narration targets 1:45 and has not been timed in a recording.

Review question: Why do equal counts after repeated imports fail to prove uniqueness?

## Local Git review

The requested initial local commit was created as **cd75207**, "Add GitHub issue snapshot connector with SQLite persistence." All 23 initial submission candidates were reviewed; the offline suite passed **157 tests in 1.54s** before staging. Ignore checks excluded generated files, and staged whitespace checks passed. No push was performed during that review.

Review question: Why does git diff alone miss never-tracked files?

## Follow-ups — October 7

| Work | Completed behavior and evidence |
| --- | --- |
| Interpreter troubleshooting | Global Python lacked requests; .venv imported it. Direct CLI import/read succeeded, pip check passed, and the suite passed 157 in 1.40s. |
| Shell activation guidance | Agent PowerShell and Command Prompt processes selected .venv and ran help successfully. The developer's terminal activation was not observed. |
| API page-size explanation | Parsed the developer's count=100 result and checked per_page=100 in source/docs. Website row count remained the developer's observation. |
| Manual errors | All ten checklist commands produced expected failures: nine offline and one live HTTP 404. Database SHA-256 stayed unchanged; full suite passed 157 in 1.46s. |
| Diagram narration | Compared sysDes.mmd to implementation and revised the 1:45 schedule; narration remains unrecorded. |

See [ERROR_CASES.md](ERROR_CASES.md) and [DEMO.md](DEMO.md).

Review question: Why do syntax errors exit 2 with usage text while operation failures exit 1 with JSON?

## Optional desktop viewer — October 7

The developer explicitly requested a GUI, overriding the original no-UI scope for this extension.

- [x] Add a thin launcher, database dropdown/Browse, repository counts, and ordered issue display.
- [x] Add local search, full details, Copy URL, and explicit browser opening.
- [x] Reuse read-only storage and report errors without creating files.
- [x] Check real Tk events, temporary databases, switching/refresh, offline behavior, file preservation, and layout.
- [x] Inspect the Windows viewer and correct clipped bottom controls.
- [x] Apply the requested GitHub-inspired dark theme and tighten minimum-size spacing.

Evidence: no new dependency was installed; existing Tk 8.6/Tcl 8.6.15 worked. Repeated Tk initialization was corrected to one module-level interpreter and separate test windows. Focused storage/GUI tests passed **56 in 1.88s**; full suite passed **180 in 2.82s**, no skips. Styling checks passed **14 in 1.56s**, then the full suite **180 in 2.77s**. Geometry tests require a full visible issue row at 900×640 and 1180×780.

Limits: stored snapshots only, synchronous reads, no viewer imports/polling. File-picker/browser boundaries are mocked; their native actions and other operating systems are not manually verified. The final compact layout passed tests; a final preview launch was not inspected after the user's Escape stop.

Review question: Why can the repository's saved row count differ from its latest import count?

## Documentation cleanup and commit review — October 7

- [x] Review every project Markdown file and pending source/test/diagram changes.
- [x] Consolidate repeated evidence, fix stale staged-state claims, and align docs with the viewer.
- [x] Run the full offline suite: **180 passed in 2.64s, exit 0**, no skips.
- [x] Check all ten Markdown files, 44 local links/anchors, code fences, whitespace, and all 15 Python files' syntax.
- [x] Review the 16-file staged manifest/diffs and pass git diff --cached --check.

The first sandbox run failed on pytest temporary-file permissions; the approved retry used a fresh ignored basetemp and passed. pip check and CLI/viewer help also succeeded. The requested local commit includes the cleaned docs and existing viewer/storage/test/diagram changes; its identity is recorded in Git history and the delivery response. Existing fresh-setup/live-import evidence was retained; no new environment, installation, live request, or GUI inspection was performed in this cleanup.

Review question: How would you show that the documentation's import/read count descriptions match the code?

## Remaining delivery work

- [ ] Rehearse narration, record the real demo, and verify the finished video is under two minutes.
- [ ] Publish the reviewed source and verify repository access.
- [ ] Upload the video to Google Drive and verify reviewer access and playback.
- [ ] Reply only to the sender in the original email thread with repository/demo links by October 7, 2026, 11:59 p.m. Pacific.

Recording, publication, access changes, and submission are not implied by a local commit.
