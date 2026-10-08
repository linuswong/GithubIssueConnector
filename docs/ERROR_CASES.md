# Manual error cases

Run these one at a time from the project root with .venv activated; [README.md](../README.md#setup) lists shell-specific activation commands. You can also replace `python` with `.\.venv\Scripts\python.exe`. An error test passes when the command fails in the expected way.

| Case | Command | Expected result | Exit code |
| --- | --- | --- | --- |
| Missing owner | `python main.py import flask` | JSON with `error.code="invalid_repository"` | 1 |
| URL instead of owner/name | `python main.py import https://github.com/pallets/flask` | `invalid_repository` | 1 |
| Extra slash | `python main.py import pallets/flask/extra` | `invalid_repository` | 1 |
| Whitespace in repository | `python main.py import "pallets /flask"` | `invalid_repository` | 1 |
| Valid format, nonexistent repository | `python main.py import pallets/connector-error-test-9c371fe6 --db issues.db` | `http_error`, message includes HTTP 404 | 1 |
| Missing repository argument | `python main.py import` | Usage/error text saying a repository is required | 2 |
| Missing value after `--db` | `python main.py read pallets/flask --db` | Usage/error text: `--db: expected one argument` | 2 |
| Unknown command | `python main.py delete pallets/flask` | Usage/error text: invalid command choice | 2 |
| Missing database parent folder | `python main.py read pallets/flask --db error-test-missing-folder/issues.db` | JSON with `error.code="database_error"`; folder stays absent | 1 |
| Directory supplied as database file | `python main.py read pallets/flask --db .` | `database_error` | 1 |

The missing-folder case assumes `error-test-missing-folder` does not exist. The nonexistent-repository case needs internet access; network failures or GitHub rate limits can produce a different expected error. The live request returned HTTP 404 during agent verification on October 7, 2026.

Expected operation errors print JSON on stderr with `success=false`, `count=0`, `issues=[]`, and an error code/message. Argument-parser errors print usage/error text on stderr. Both leave stdout empty. Full error messages may include an absolute database path or platform-specific details.

In **Command Prompt**, immediately after a command check its exit code with:

```bat
echo %ERRORLEVEL%
```

In **PowerShell**, use:

```powershell
$LASTEXITCODE
```

## Check that a failed import preserves saved issues

Read your existing saved issues, run an import that fails, then read again:

```text
python main.py read pallets/flask --db issues.db
python main.py import pallets/connector-error-test-9c371fe6 --db issues.db
python main.py read pallets/flask --db issues.db
```

Compare the complete issues lists from both reads: repository, issue number, title, and URL should match. Existing rows should survive the failed import. This assumes issues.db already contains saved data and no other process changes it during the check.

Reading a missing database in an existing folder is an intentional success with count=0; it does not create a file. It is not an error case.

## Verification evidence

Codex ran all ten listed error commands in separate CLI processes using the existing .venv interpreter. Nine were offline checks; the nonexistent-repository check made one real public GitHub request. Expected exit codes, stderr format, empty stdout, and JSON failure fields were checked. SHA-256 comparisons confirmed issues.db was unchanged after every failure; the missing parent folder stayed absent.

At checklist preparation, the offline suite also passed: `.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider` — **157 passed in 1.46s, exit 0**. Existing automated tests cover simulated timeouts, malformed API data, failed-import preservation, and transaction rollback. The checklist added no test or runtime code. See [AI_NOTES.md](AI_NOTES.md) for historical evidence and the latest full-suite result.
