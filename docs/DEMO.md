# Demo script — target 1 minute 45 seconds

The commands use real GitHub data and local SQLite. All PowerShell blocks were executed successfully using a fresh rehearsal database on October 6, 2026. Command execution took 2.116 seconds without narration; recording and sharing are still pending. Rehearse with a stopwatch and aim for 1:45, leaving 15 seconds before the assessment's two-minute limit. Narration timing has not been verified by a recording.

## Before recording

Open PowerShell in the project root. Use a large readable font, keep the window wide enough for the summary tables, and hide unrelated windows. Use the verified clean interpreter below, or the documented .venv interpreter after setup. Prepare these variables before starting the timer:

```powershell
$python = (Resolve-Path .\.venv\verification-m4\Scripts\python.exe).Path
$db = "./demo-m4.db"
if (Test-Path $db) { throw "Choose a new demo filename before recording." }
$checkDuplicates = @'
import sqlite3
import sys
from pathlib import Path

connection = sqlite3.connect(
    Path(sys.argv[1]).absolute().as_uri() + "?mode=ro", uri=True
)
try:
    duplicates = connection.execute(
        "SELECT repository, issue_number, COUNT(*) FROM issues "
        "GROUP BY repository, issue_number HAVING COUNT(*) > 1"
    ).fetchall()
    print("duplicate_groups:", duplicates)
finally:
    connection.close()
'@
```

For another take, choose another unused demo-*.db filename; keep all generated databases out of Git. Do not pre-import into the recording database. Preflight networking with a different disposable file and confirm pallets/flask still returns at least one issue. October 6 verification returned issue #6146, titled "Add Cloudflare to Flask Hosting Platforms docs?"; live data can change. If the chosen repository has no issues or networking fails, resolve that before recording; a mocked import does not satisfy the live-demo requirement.

## Timed walkthrough

| Time | Action | Suggested narration |
| --- | --- | --- |
| 0:00–0:10 | Introduce the terminal/project | "This Python connector saves one page of open GitHub issues to SQLite. I can read that data locally in another process." |
| 0:10–0:35 | Run A; show the summary and issue | "This is a real unauthenticated import from pallets/flask. It excludes pull requests and validates the whole page before committing. Import count is issues processed in this page, including updates." |
| 0:35–0:50 | Run B | "This separate CLI process reads from SQLite. It never contacts GitHub. Read count is all saved rows for this repository." |
| 0:50–1:20 | Run C; pause on duplicate_groups: [] | "I import again and read again. This SQL query finds no duplicate repository and issue-number groups. Equal counts alone would not prove that. Returned titles and URLs update through upsert." |
| 1:20–1:35 | Run D; show JSON and exit 1 | "An extra slash is invalid input. This expected failure prints JSON on stderr and returns exit one before HTTP or database work." |
| 1:35–1:45 | Briefly explain the key | "Issue numbers are local to each repository, so the primary key includes repository and issue number. SQLite enforces uniqueness while upsert updates saved records." |

### A. Real import

```powershell
$imported = & $python main.py import pallets/flask --db $db | ConvertFrom-Json
if ($LASTEXITCODE -ne 0) { throw "Live import failed; restart after resolving it." }
$imported | Select-Object success,operation,repository,count | Format-Table -AutoSize
$imported.issues | Select-Object -First 3 issue_number,title | Format-Table -AutoSize
```

The display shows at most three actual issues; it does not change the saved batch. The summary's count remains the full page's issue count. Do not narrate a fixed count before seeing the live result.

### B. Read in another CLI process

```powershell
$saved = & $python main.py read pallets/flask --db $db | ConvertFrom-Json
if ($LASTEXITCODE -ne 0) { throw "Local read failed." }
$saved | Select-Object success,operation,repository,count | Format-Table -AutoSize
$saved.issues | Select-Object -First 3 issue_number,title | Format-Table -AutoSize
```

### C. Repeat import, separate read, direct duplicate query

```powershell
$again = & $python main.py import pallets/flask --db $db | ConvertFrom-Json
if ($LASTEXITCODE -ne 0) { throw "Repeated live import failed." }
$again | Select-Object success,operation,repository,count | Format-Table -AutoSize
$savedAgain = & $python main.py read pallets/flask --db $db | ConvertFrom-Json
if ($LASTEXITCODE -ne 0) { throw "Repeated read failed." }
$savedAgain | Select-Object success,operation,repository,count | Format-Table -AutoSize
$savedAgain.issues | Select-Object -First 3 issue_number,title | Format-Table -AutoSize
& $python -c $checkDuplicates $db
```

Expected uniqueness output is `duplicate_groups: []`. The query groups by both key columns and looks for groups with more than one row. If GitHub changes between calls, page/read counts may differ: older rows are retained, and only one page is fetched. That does not invalidate the key-based uniqueness check.

### D. Expected error

```powershell
& $python main.py import owner/repo/extra --db $db
"exit code: $LASTEXITCODE"
```

Expected: failure JSON on stderr with code invalid_repository, repository=null, count=0, issues=[], then exit code: 1. Successful commands emit JSON on stdout with exit 0. An argparse syntax error instead emits usage text on stderr with exit 2; explain this distinction if asked, without adding another step to the recording.

## Manual delivery checklist

- [ ] Rehearse the narration with a stopwatch; record the real run with clear terminal output and audible explanation. Verify the finished video is under two minutes and shows all five required elements.
- [x] Review tracked and untracked source/docs/tests, stage the intended submission, and inspect the staged diff for the requested local commit. Generated databases/environments/caches/credentials are excluded.
- [ ] Publish the reviewed local commit when ready. Check that the required source, tests, dependencies, README, and architecture are visible in the published repository.
- [ ] Upload the video to Google Drive.
- [ ] Grant the reviewer viewer access to the video and appropriate repository access. Test both links from a separate signed-out/private session or the intended reviewer context; verify the video actually plays and the source is visible. Access has not been checked by this milestone.
- [ ] Reply only to the sender in the original email thread with the repository and demo links by October 7, 2026, 11:59 p.m. Pacific. Sending the reply remains your task.

No video, upload, sharing change, repository publication, or email submission was performed by Codex.
