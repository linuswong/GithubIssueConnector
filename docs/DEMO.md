# Demo script — target 1 minute 45 seconds

The walkthrough uses real GitHub data and local SQLite. The original command blocks were executed with the clean verification interpreter and a fresh rehearsal database on October 6, 2026; command time was 2.116 seconds without narration. This guide now uses the standard .venv path from [README.md](../README.md) and includes the revised diagram narration. Recording, narration timing, and sharing remain unverified. Aim for 1:45, leaving 15 seconds before the two-minute limit.

## Before recording

Open PowerShell in the project root after setup. Use a large readable font, keep the window wide enough for summary tables, and hide unrelated windows. Prepare these variables before starting the timer:

```powershell
$python = (Resolve-Path .\.venv\Scripts\python.exe).Path
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
| 0:00–0:05 | Introduce the project | "This connector imports GitHub issues and keeps a local SQLite snapshot." |
| 0:05–0:40 | Show [sysDes.mmd](../sysDes.mmd) as a rendered diagram | Use the architecture narration below, pointing to each path as you explain it. |
| 0:40–1:00 | Run A; show the summary and issue | "This is a real unauthenticated import from pallets/flask. Import count is the number of issues processed in this page, including updates." |
| 1:00–1:10 | Run B | "This separate process reads the saved issues locally. Read count includes all stored issues for this repository." |
| 1:10–1:30 | Run C; pause on duplicate_groups: [] | "I import and read again. This SQL query finds no duplicate repository and issue-number groups. Equal counts alone would not prove that." |
| 1:30–1:45 | Run D; show JSON and exit 1 | "An extra slash is invalid input. The command returns an error before HTTP or database work. Existing saved issues are preserved." |

## Explaining sysDes.mmd

Aim for about 35 seconds. This is a suggested allocation; the revised narration has not been rehearsed or timed in a recording.

> "This diagram shows the two commands. main.py reads the operation, repository, and database path. Import requests one page from GitHub, removes pull requests, and validates the issues before saving them. SQLite uses repository and issue number together as the key, so repeated imports update records without duplicates. The batch commits together or rolls back if saving fails. Read retrieves saved issues directly from SQLite. Finally, the command prints JSON. Success exits with zero; expected operation errors exit with one."

Point to these labels as you speak:

1. `main.py` and argparse: the inputs are import/read, owner/name, and --db.
2. `import_issues → fetch_issues → GitHub REST API → filtering/validation`: one API page becomes sorted issue records before any writes.
3. `upsert_issues → transaction → database`: the composite key prevents duplicates; upsert inserts new records or updates title/URL; a failed batch rolls back its writes.
4. `read_issues → read_saved_issues`: reads use SQLite only and return records in issue-number order.
5. `_result → JSON output`: public functions build the result, and main.py prints it. Expected API/database errors pass through ConnectorError to that result.

The diagram is simplified: repository validation happens before either operation's HTTP/database work, argparse syntax errors exit with two, and issues.db represents the default file (the actual path is configurable). If asked why the key has two columns, explain that issue number 1 can exist in several repositories. If asked what one page means, the API request explicitly uses page=1 and per_page=100; the website can display a different number per page. Previously saved rows absent from a later page are retained because that page cannot establish closure or deletion.

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
- [x] Review and commit the initial connector locally as cd75207. Generated databases/environments/caches/credentials are excluded; later viewer/documentation changes receive a separate commit review.
- [ ] Publish the reviewed local commit when ready. Check that the required source, tests, dependencies, README, and architecture are visible in the published repository.
- [ ] Upload the video to Google Drive.
- [ ] Grant the reviewer viewer access to the video and appropriate repository access. Test both links from a separate signed-out/private session or the intended reviewer context; verify the video actually plays and the source is visible. Access has not been checked by this milestone.
- [ ] Reply only to the sender in the original email thread with the repository and demo links by October 7, 2026, 11:59 p.m. Pacific. Sending the reply remains your task.

Codex has not recorded a video, uploaded it, changed sharing, published the repository, or sent the submission. These remain manual and unverified; see [BUILD_PLAN.md](BUILD_PLAN.md#remaining-delivery-work).
