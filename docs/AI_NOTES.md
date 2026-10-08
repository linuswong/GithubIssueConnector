# AI and verification notes

This records actual agent work, observations, corrections, and limits. Historical entries describe evidence available at the time. The developer's understanding is not inferred from passing checks; the milestone 0 count answer and "LGTM" approval were explicitly recorded.

The documentation cleanup consolidated repeated command logs. Historical results remain distinct from the latest run. Generated databases, environments, and diagnostic files are ignored.

## Tools actually used

| Tool | Actual use |
| --- | --- |
| ChatGPT/Codex and Cursor | Requirements, explanations, implementation, review, troubleshooting, documentation, and demo preparation |
| PowerShell, rg, Git | File/source searches, shell commands, status/diff/history/configuration, ignore checks, staging, and local commits |
| Python venv and pip | Isolated setup, documented dependency installation, imports, and version/consistency checks |
| requests | Public GitHub exploration/imports; real response preparation/decoding with mocked transport in tests |
| sqlite3 | Storage, schema/key/integrity inspection, independent reads, and real-trigger rollback tests |
| pytest and unittest.mock | Offline HTTP guards, real tmp_path files, CLI and GUI checks |
| subprocess | Independent interpreters, captured streams, exit codes, and persistence verification |
| Web browsing | Primary GitHub, Requests, Python, and SQLite documentation |
| apply_patch and Python file tools | Source/test/documentation edits and structural checks |
| tkinter/ttk and webbrowser | Optional desktop viewer and explicit issue-link action |
| Computer-use skill, node_repl, @oai/sky | Earlier native Windows viewer inspection and repository/issue selection |

No sub-agents were used. No credentials were printed or committed. Publication, recording, reviewer access, and submission remain unverified.

## Milestone 0 — October 6, 2026

Codex read the assessment brief and project instructions, proposed the flat package/public result contract, and explained API objects versus saved rows. Git showed an existing repository at 63eb423; existing changes were preserved.

Fresh .venv setup initially failed during ensurepip with temporary-file PermissionError, including a project-local TEMP/TMP retry. Approved execution outside sandbox restrictions succeeded. Observed versions: Python 3.13.5, Git 2.33.0.windows.2, SQLite 3.49.1, requests 2.34.2, and pytest 9.1.1. Environment isolation/imports were checked and pip check reported no broken requirements. requirements.txt pins those two direct dependency versions.

Initial pytest attempts hit cache/collection permissions. The one generated cache directory was removed only after checking its absolute path and obtaining outside-sandbox execution. The final setup run returned **no tests ran, exit 5**; it was not a passing connector suite.

One unauthenticated GET requested state=open, per_page=100, page=1 with timeout=20, redirects disabled, and trust_env=False. GitHub returned HTTP 200: four entries, one issue and three PRs. Issue #6146 had title "Add Cloudflare to Flask Hosting Platforms docs?" and html_url https://github.com/pallets/flask/issues/6146. No database was written.

**Unfamiliar API detail:** the Issues endpoint includes PRs. Codex proposed excluding objects by pull_request key presence and saving html_url rather than the API url. [GitHub's repository issues reference](https://docs.github.com/en/rest/issues/issues#list-repository-issues) and the observed response supported that choice. Tests came in milestone 1.

The developer answered that import count is 1 while the saved read count may be 10 or 11, then approved the function inputs/result keys with "LGTM."

## Milestone 1 — October 6, 2026

Implemented only the client, shared repository validation, expected error type, and mocked-HTTP tests. No SQLite or CLI was added. Before coding, Codex explained inputs/outputs, whole-page validation, failure handling, and one-page/timeout tradeoffs.

| Run | Actual result |
| --- | --- |
| Initial client tests | 2 failed, 88 passed in 0.76s; cache warnings; exit 1 |
| Corrected redirect fixture and added credential guard | 90 passed in 0.39s; exit 0 |
| Final focused suite, including URL-port cases | 92 passed in 0.45s; exit 0 |
| Full available suite | 92 passed in 0.36s; exit 0 |

**Correction:** the fake Response lacked PreparedRequest metadata. Requests still prepares redirect bookkeeping even when redirect following is disabled. Adding response.request and response.url corrected the fixture while retaining the one-transport-call assertion. See [Requests advanced usage](https://requests.readthedocs.io/en/latest/user/advanced/).

Tests cover request/query/headers, PR markers with null/empty/false values, html_url mapping, field validation, malformed later entries, ordering, URL structure/ports, status/timeout/network errors, empty pages, invalid input before session creation, and unexpected-error propagation. HTTPAdapter.send is mocked and unconfigured sends fail. No live request occurred in this milestone.

## Milestone 2 — October 6, 2026

Implemented SQLite storage and real-file tests, preserving client/public-interface decisions. Codex explained composite identity, file versus connection, explicit transactions, read-only URIs, and path behavior before implementation.

Two sandboxed runs failed on pytest temporary-directory setup/cleanup; no passing storage result was claimed. Approved outside-sandbox runs used fresh absolute basetemp paths under ignored .venv:

- Focused: **33 passed in 0.65s, exit 0**.
- Full available suite: **125 passed in 0.76s, exit 0**.

**Unfamiliar database behavior:** a failed statement can leave earlier statements pending. The connection context commits/rolls back but does not open a transaction or close the connection. Codex used explicit BEGIN before schema/batch work, the context for commit/rollback, and finally for close.

A real BEFORE INSERT trigger checks that issue 7 was updated and issue 8 inserted before rejecting issue 99 with RAISE(ABORT). New connections then see the original issue 7, no 8/99, and the other repository unchanged. This verifies late-write rollback rather than relying on a mock or pre-write error. Primary references: [Python connection contexts](https://docs.python.org/3.13/library/sqlite3.html#how-to-use-the-connection-context-manager), [SQLite transactions](https://www.sqlite.org/lang_transaction.html), and [SQLite triggers](https://www.sqlite.org/lang_createtrigger.html).

Other cases verify persistence, duplicate-free updates, repository isolation, bound values, omitted-row retention, str/Path/current-directory paths, Unicode/# filenames, missing-file/table reads without creation, missing parents without fallback, corrupt schemas, and connection closure. HTTP/session guards keep tests offline. No public orchestration or CLI existed yet.

## Milestone 3 — October 6, 2026

Added reusable functions/package exports, thin argparse CLI, integration tests, and documentation. Codex explained application coordination versus CLI parsing/printing before implementation.

The first focused run had **2 failed, 30 passed in 1.12s, exit 1** because help assertions assumed an unwrapped phrase. Normalizing whitespace fixed the assertions without changing argparse output. Final focused suite: **32 passed in 1.03s**. Full suite: **157 passed in 1.55s, exit 0**.

Real Requests decoding and real tmp_path databases verify import/read, PR exclusion, updates, retained omissions, page count versus saved count, failed-import preservation, paths, validation-before-access, and error propagation. Independent CLI processes use child-local HTTP/session guards; a parent monkeypatch is not assumed to apply in children.

**Boundary decision:** argparse syntax errors keep usage text/exit 2, while expected operation failures use JSON/exit 1. [argparse](https://docs.python.org/3.13/library/argparse.html) and [subprocess](https://docs.python.org/3.13/library/subprocess.html) documentation informed parser and process checks. No live connector import occurred here.

## Milestone 4 — October 6, 2026

Verified fresh setup, actual CLI imports/reads, uniqueness, errors, docs, and demo commands. No functional change or new test was needed; two stale module docstrings and the requirements comment were updated.

### Fresh setup

Confirmed .venv/verification-m4 did not exist, then ran:

```powershell
python -m venv .venv/verification-m4
.\.venv\verification-m4\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\verification-m4\Scripts\python.exe -m pip check
.\.venv\verification-m4\Scripts\python.exe -m pytest --version
```

Creation/install exited 0. The environment initially contained only pip 25.1.1 and had include-system-site-packages=false. After installing only requirements.txt, pip check passed. Python package locations, sys.prefix/base_prefix, and public imports were inspected with PYTHONPATH unset; the package resolved from the project root.

| Component | Observed version |
| --- | --- |
| Python / SQLite / Git / pip | 3.13.5 / 3.49.1 / 2.33.0.windows.2 / 25.1.1 |
| requests / pytest | 2.34.2 / 9.1.1 |
| certifi / charset-normalizer / idna / urllib3 | 2026.7.22 / 3.5.2 / 3.20 / 2.8.0 |
| colorama / iniconfig / packaging / pluggy / Pygments | 0.4.6 / 2.3.1 / 26.3 / 1.6.0 / 2.21.0 |

All three main.py help commands succeeded. The clean interpreter ran `python -m pytest -q -p no:cacheprovider`: **157 passed in 1.37s**, then **157 in 1.45s** after documentation/docstring edits, exit 0. Setup/tests/live networking used approved outside-sandbox execution based on previous permission failures.

### Live import and persistence

A subprocess driver used the clean interpreter, project-root cwd, argument lists, UTF-8 captured streams, and no PYTHONPATH. Each command was a separate actual CLI process:

```powershell
.\.venv\verification-m4\Scripts\python.exe main.py import pallets/flask --db ./milestone4-live.db
.\.venv\verification-m4\Scripts\python.exe main.py read pallets/flask --db ./milestone4-live.db
.\.venv\verification-m4\Scripts\python.exe main.py import pallets/flask --db ./milestone4-live.db
.\.venv\verification-m4\Scripts\python.exe main.py read pallets/flask --db ./milestone4-live.db
.\.venv\verification-m4\Scripts\python.exe main.py import owner/repo/extra --db ./milestone4-live.db
.\.venv\verification-m4\Scripts\python.exe main.py read pallets/flask --db
```

The first four returned success JSON on stdout, empty stderr, exit 0, and count=1 with issue #6146; [README.md](../README.md#example-output) preserves the actual data. Timings were 0.682s, 0.199s, 0.461s, and 0.220s respectively.

Independent mode=ro SQLite queries compared stored fields, grouped by repository/issue_number for duplicates, inspected table_info, and checked integrity. After both pairs: duplicate groups=[], key positions repository=1 and issue_number=2, integrity_check=ok.

The malformed repository returned invalid_repository JSON on stderr, empty stdout, exit 1, with identical database SHA-256 before/after. Missing --db returned argparse text on stderr, empty stdout, exit 2. Timings were 0.228s and 0.210s. Captured arguments/streams/results were written to ignored .venv/verification-m4/live-evidence.json.

### Demo commands and review

The five authored PowerShell blocks were executed in order with a fresh rehearsal filename. Two additional real imports, independent reads, duplicate_groups: [], and the expected JSON/exit 1 succeeded. Total command time was **2.116 seconds without narration**. This milestone therefore made four live connector imports; it did not measure a narrated recording.

All 23 initial submission candidates were read, Python files parsed, Markdown fences/local links checked, and ignore/whitespace/common-credential patterns inspected. No matching credentials or unwanted generated candidates were found; this was a focused scan, not proof against every secret format.

## Initial local commit

The developer requested review, staging, a descriptive local commit, and the configured publishing command. The existing clean interpreter passed **157 tests in 1.54s, exit 0**. An initial sandboxed git add failed on index.lock permissions; approved outside-sandbox staging succeeded. The staged manifest/diffs and whitespace were reviewed.

Git history confirms **cd75207 — Add GitHub issue snapshot connector with SQLite persistence**. Branch main tracks origin/main; origin is https://github.com/linuswong/GithubIssueConnector.git. The publishing command `git push origin main:main` was documented but not run during that review.

## Dependency troubleshooting — October 7, 2026

The reported missing-requests error came from global C:/Python313/python.exe; find_spec returned None there. Existing .venv imported requests 2.34.2, pip check passed, and help succeeded.

Using .venv directly performed one real import into issues.db and a separate read: count=1, issue #6146, exit 0. The full offline suite passed **157 in 1.40s, exit 0**. No dependency install or new environment was needed.

Shell follow-up: the developer pasted Activate.ps1 source opened in Notepad. Agent Command Prompt and PowerShell processes used their respective activation scripts, selected .venv, imported requests, and ran help successfully. No execution policy was changed. The developer's actual terminal activation was not observed. [venv activation documentation](https://docs.python.org/3.13/library/venv.html#how-venvs-work) informed the guidance.

### API page-size explanation

Parsed the developer's openai/codex JSON: import count=100 and len(issues)=100. Source uses per_page=100/page=1; primary GitHub docs confirm configurable page size. The website's 25 rows were the developer's observation, not an independently counted agent result. No new live connector call or database write occurred.

## Manual error checklist — October 7, 2026

Prepared [ERROR_CASES.md](ERROR_CASES.md) and checked all ten commands in independent CLI processes. Nine checks were offline; one real nonexistent-repository request returned HTTP 404. Expected codes/streams/envelopes passed, database SHA-256 stayed unchanged after every failure, and the missing parent stayed absent. Full offline suite: **157 passed in 1.46s, exit 0**.

No runtime code or new test was needed. Live request/tests used approved outside-sandbox execution; offline command checks ran in the sandbox.

## Diagram narration preparation — October 7, 2026

Compared sysDes.mmd with main.py, connector, client, storage, and architecture. Added 35-second narration and label pointers to [DEMO.md](DEMO.md), retaining a 105-second target. Documented early validation, configurable paths, argparse exit 2, composite identity, page size, and retained rows. The user-created diagram was preserved. No Mermaid rendering, narration timing, live request, or runtime test occurred.

## Desktop database viewer — October 7, 2026

The developer explicitly requested a GUI, overriding the original no-UI scope. Codex explained local file input, repository/issue display, read-only behavior, and Tkinter tradeoffs before implementation.

Added root/package viewer modules, grouped repository counts, shared read-only query handling, and storage/GUI tests. Existing .venv and clean verification environment provided Tk 8.6/Tcl 8.6.15; no dependency was installed. A read-only query found openai/codex=100 and pallets/flask=1 in issues.db. A hidden-window selection showed full Flask details; database SHA-256 was unchanged.

**Corrections and evidence:**

- A sandboxed focused run failed on temporary-file permissions. Outside-sandbox runs initially reported 52 passed/2 skipped and a diagnostic 11 passed/1 skipped. Repeated Tk initialization intermittently failed on init.tcl; one module-level interpreter with separate Toplevel windows resolved it.
- Corrected focused tests passed 54 in 1.24s, no skips. The first clean-environment full run passed 178 in 2.21s before layout corrections.
- Earlier computer-use inspection found clipped bottom controls. Reserving grid rows corrected them; native clicks selected pallets/flask and issue #6146, with full details and enabled actions visible.
- Layout regression checks were added at 900×640 and 1180×780. Final focused storage/GUI suite passed **56 in 1.88s**; full suite **180 in 2.82s**, exit 0, no skips.

Tests use real Tk events and real tmp_path files; session/HTTP guards reject networking. File-dialog and browser boundaries are mocked. Viewer help succeeded. Native Browse and real browser launching were not manually exercised.

Primary references: [Tkinter](https://docs.python.org/3.13/library/tkinter.html), [ttk virtual events](https://docs.python.org/3.13/library/tkinter.ttk.html#virtual-events), [native file dialogs](https://docs.python.org/3.13/library/dialog.html#native-load-save-dialogs), and [SQLite read-only URIs](https://docs.python.org/3.13/library/sqlite3.html#how-to-work-with-sqlite-uris).

## GitHub-inspired viewer styling — October 7, 2026

The developer requested a GitHub-like appearance. Added shared COLORS/apply_theme, dark header and drawn issue icon, blue links, green action, bordered panels, dark inputs, and compact spacing. Storage/API behavior and dependencies were unchanged.

Initial focused GUI tests passed **14 in 1.00s**. A geometry check found only 27 pixels for the table at 900×640. Tightened spacing and strengthened the existing regression to require a complete visible issue row. Focused tests then passed **14 in 1.56s**; full suite **180 in 2.77s**, exit 0, no skips.

Computer-use inspection showed the initial dark version with actual database content. The final compact spacing is covered by event/geometry tests. A close/reload attempt stopped on the user's physical Escape; an already-running cell subsequently launched the final preview, which was not inspected. No further Computer Use calls followed the stop. Browser-open status in the preview came from user activity, not an agent click.

## Documentation cleanup — October 7, 2026

The developer requested cleanup of all Markdown files and a local commit. Codex read every project Markdown file, the pending viewer/storage/tests, diagram, Git history/status, and the brief/build plan. Existing source/test/diagram work was preserved for review.

Consolidated repeated evidence, removed stale staged-state claims, aligned current docs with the viewer, standardized links/code formatting, and retained the historical setup prompt. This entry records current actions; earlier browser/computer-use work was not repeated.

Current full-suite command used the existing clean interpreter:

```powershell
.\.venv\verification-m4\Scripts\python.exe -m pytest -q -rs -p no:cacheprovider --basetemp .venv/pytest-docs-cleanup-20261007-f92cb874 --tb=short
```

The first sandbox run, using a different basetemp, failed on temporary-directory permissions and exited 1. An approved outside-sandbox retry with a checked-unused path passed **180 tests in 2.64s, exit 0**, no skips. All automated tests remained offline.

Structural checks passed for **10 Markdown files, 44 local links/anchors, and 15 Python files**: no missing local targets/headings, unclosed fences, trailing whitespace, newline errors, or Python syntax errors. pip check reported no broken requirements; CLI and viewer help succeeded. Ignore checks confirmed environment/database/cache/credential paths stay excluded.

Explicit staging used approved outside-sandbox execution for Git metadata writes. The 16-file staged manifest and diffs were reviewed, and git diff --cached --check passed. Commit scope is the ten cleaned Markdown files plus the existing storage helper, viewer launchers, storage/GUI tests, and user-created diagram. Git history and the delivery response record the resulting local commit identity.

An oversized shell write command was rejected by Windows before execution; patch/file tools then applied the documentation edits. No project source logic changed during cleanup. No new environment, installation, live import, native GUI inspection, push, recording, or submission occurred.

## Reference index and limits

Previously consulted primary references also include [Requests quickstart](https://requests.readthedocs.io/en/latest/user/quickstart/), [netrc authentication](https://requests.readthedocs.io/en/latest/user/authentication/#netrc-authentication), [SQLite UPSERT](https://www.sqlite.org/lang_upsert.html), [URI paths](https://www.sqlite.org/uri.html), [table constraints](https://www.sqlite.org/lang_createtable.html), [pytest tmp_path](https://docs.pytest.org/en/stable/how-to/tmp_path.html), and [monkeypatch](https://docs.pytest.org/en/stable/how-to/monkeypatch.html).

Verification covers the recorded Windows/Python environment. Other Python versions, proxy-dependent networking, native file-picker/browser actions, and final compact-layout visual confirmation remain unverified. Narration, video duration/playback, publication, reviewer access, and email submission remain manual. No developer comprehension is claimed beyond the recorded milestone 0 response.
