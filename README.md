# BusyFox — Opportunity Engine

Built for **First Commit** (WeMakeDevs × AWS, Bharat Builds Tour), Sept 17–20, 2026.

**Opportunity Engine finds where a competitor's customers are unhappy about something the
business is already good at, backs that claim with evidence code can verify, estimates what
it's worth against the owner's stated goal, and hands the owner an execution pack they
control.** Research agents only ever propose `signals[]`; a deterministic Evidence Check and
Quality Gate — not another LLM call — decide what's allowed into the inbox. Full product spec:
`opportunity_engine_prd_v8.md`.

Try it live: https://main.dw3gwg5t169l9.amplifyapp.com/ (`#/business` → `#/investigation` →
`#/inbox` → an opportunity card → `.../execution-pack`).

## Submission docs

- [`WRITEUP.md`](WRITEUP.md) — problem, build, AWS integration, AI tools used
- [`CREDITS.md`](CREDITS.md) — third-party licences and simulated-vs-real data policy
- [`LEARNING.md`](LEARNING.md) — daily learning log kept since Day 1
- [`docs/architecture-diagram.md`](docs/architecture-diagram.md) — what's actually deployed, drift from plan labelled honestly
- [`docs/contract.md`](docs/contract.md) — entity + API contract (human-readable mirror of the code)

## Tools we used

Built with **Claude Code**, driven from a committed task list (`tasks/plan.md`, `tasks/todo.md`)
and repo instructions (`CLAUDE.md`, `AGENTS.md`). The deployed product's agent pipeline runs on
**OpenCode Go** (`deepseek-v4.1-flash`), substituting for the originally-planned Amazon Bedrock
calls after every AWS account hit a 0 req/min real-time inference quota (see `WRITEUP.md` and
`LEARNING.md` for the full story). Full AI-tool disclosure: `WRITEUP.md`.

## Live deployments

| What | URL | Region |
|---|---|---|
| Frontend (Amplify Hosting, app `dw3gwg5t169l9`, branch `main`) | https://main.dw3gwg5t169l9.amplifyapp.com/ | eu-north-1 |
| API Gateway (Task 6 skeleton, stack `opportunity-engine-skeleton`) | https://vx59qs2osl.execute-api.eu-north-1.amazonaws.com/ | eu-north-1 |

The Amplify app is git-connected to `main` with auto-build enabled, so every push to `main` redeploys the frontend from `amplify.yml`. `VITE_API_BASE_URL` is set as an Amplify app-level environment variable (`https://vx59qs2osl.execute-api.eu-north-1.amazonaws.com`, no trailing slash) as of 2026-09-20 — the deployed frontend hits the live API and only falls back to `DEMO FIXTURE` on a real failure, never silently. Changing this value requires a manual redeploy of the branch (Amplify Console → Hosting → `main` → latest job → Redeploy this version) — a new env var alone does not trigger a build.

## Deploy the Task 6 skeleton

`scripts/task6-deploy-wizard.sh` walks through AWS CLI/SAM CLI setup, credentials, confirming Bedrock model access, and `sam deploy` for `infra/api-gateway.yaml`. Run it from a bash shell (Git Bash on Windows): `bash scripts/task6-deploy-wizard.sh`.