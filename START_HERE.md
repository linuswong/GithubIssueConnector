# Start here

Start with [README.md](README.md) to set up the environment, import/read issues, launch the optional viewer, and run tests.

| Document | Use |
| --- | --- |
| [Architecture.MD](Architecture.MD) | Interfaces, components, flow, schema, transactions, configuration, errors, and tradeoffs |
| [sysDes.mmd](sysDes.mmd) | Mermaid diagram of the CLI import/read flow |
| [docs/PROJECT_BRIEF.md](docs/PROJECT_BRIEF.md) | Assessment requirements and chosen design decisions |
| [docs/BUILD_PLAN.md](docs/BUILD_PLAN.md) | Completed milestones, verification, and remaining delivery work |
| [docs/AI_NOTES.md](docs/AI_NOTES.md) | Actual AI/tool use, results, corrections, and limits |
| [docs/DEMO.md](docs/DEMO.md) | 1:45 recording script and manual delivery checklist |
| [docs/ERROR_CASES.md](docs/ERROR_CASES.md) | Manual failure commands and expected exit codes |
| [AGENTS.md](AGENTS.md) | Instructions for coding agents |
| [CODING_PROMPT.md](CODING_PROMPT.md) | Historical milestone 0 request |

Source lives in main.py, viewer.py, and github_issue_connector/; tests live in tests/. requirements.txt pins the two tested direct dependencies. .gitignore excludes databases, virtual environments, caches, and credential files.

The connector and optional viewer are implemented. Fresh setup and real CLI imports/reads have been verified; the latest full suite passed **180 tests with no skips**. The initial implementation is recorded in local commit cd75207. Publication, recording, sharing, access verification, and submission remain unverified.

The assessment deadline is **October 7, 2026, at 11:59 p.m. Pacific**.
