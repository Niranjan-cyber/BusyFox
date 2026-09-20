# BusyFox — Opportunity Engine

<p>
  <img alt="Hackathon" src="https://img.shields.io/badge/First%20Commit-WeMakeDevs%20%C3%97%20AWS-232F3E?style=flat-square">
  <img alt="Built on AWS" src="https://img.shields.io/badge/Built%20on-AWS-FF9900?style=flat-square&logo=amazonaws&logoColor=white">
  <img alt="Frontend" src="https://img.shields.io/badge/Frontend-React%20%2B%20Amplify-149eca?style=flat-square&logo=react&logoColor=white">
  <img alt="Status" src="https://img.shields.io/badge/Status-live-2ea44f?style=flat-square">
</p>

Built in four days for **First Commit** (WeMakeDevs × AWS, Bharat Builds Tour), Sept 17–20, 2026.

> **Opportunity Engine finds where a competitor's customers are unhappy about something the
> business is already good at, backs that claim with evidence code can verify, estimates what
> it's worth against the owner's stated goal, and hands the owner an execution pack they
> control.**
>
> Research agents only ever propose `signals[]`. A deterministic Evidence Check and Quality
> Gate — not another LLM call — decide what's allowed into the inbox. **Agents discover. Code
> verifies. Humans decide.**

**Live app:** [main.dw3gwg5t169l9.amplifyapp.com](https://main.dw3gwg5t169l9.amplifyapp.com/)
— walk it in order: `#/business` → `#/investigation` → `#/inbox` → an opportunity card →
`.../execution-pack`.

Full product spec: [`opportunity_engine_prd_v8.md`](opportunity_engine_prd_v8.md).

---

## At a glance

| | |
|---|---|
| **Flagship business** | PulseStack — simulated B2B SaaS (lightweight monitoring), competing against real named tools (Sentry, Datadog, …) |
| **Frontend** | React on Amplify Hosting — five screens: business, live investigation, inbox, opportunity detail, execution pack |
| **Backend** | API Gateway → 13 Lambda functions → DynamoDB (single table) + S3 |
| **Agents** | Strands Agents SDK; Market / Feedback / Competitor research agents, Synthesis, Action — running on OpenCode Go (see [Tools we used](#tools-we-used)) |
| **Data sources** | Tavily, GitHub REST, HN Algolia, App Store RSS, Product Hunt — every response labelled Live → Cached → Demo Fixture, never silently substituted |

## Submission docs

| Doc | What's in it |
|---|---|
| [`WRITEUP.md`](WRITEUP.md) | Problem, build, AWS integration, AI tools used |
| [`CREDITS.md`](CREDITS.md) | Third-party licences and the simulated-vs-real data policy |
| [`LEARNING.md`](LEARNING.md) | Daily learning log, kept since Day 1 |
| [`docs/architecture-diagram.md`](docs/architecture-diagram.md) | What's actually deployed — drift from plan labelled honestly, not glossed over |
| [`docs/contract.md`](docs/contract.md) | Entity + API contract (human-readable mirror of the code) |

## Tools we used

Built with **Claude Code**, driven from a committed task list (`tasks/plan.md`, `tasks/todo.md`)
and repo instructions (`CLAUDE.md`, `AGENTS.md`) so every session picked up the same contract and
guardrails.

The deployed product's agent pipeline runs on **OpenCode Go** (`deepseek-v4.1-flash`),
substituting for the originally-planned Amazon Bedrock calls after every AWS account hit a
0 req/min real-time inference quota — the reasoning architecture didn't change, only which model
answers the call. Full story: [`WRITEUP.md`](WRITEUP.md), [`LEARNING.md`](LEARNING.md).

## Live deployments

| What | URL | Region |
|---|---|---|
| Frontend (Amplify Hosting, app `dw3gwg5t169l9`, branch `main`) | https://main.dw3gwg5t169l9.amplifyapp.com/ | eu-north-1 |
| API Gateway (stack `opportunity-engine-skeleton`) | https://vx59qs2osl.execute-api.eu-north-1.amazonaws.com/ | eu-north-1 |

The Amplify app is git-connected to `main` with auto-build enabled, so every push to `main`
redeploys the frontend from `amplify.yml`. `VITE_API_BASE_URL` is set as an Amplify app-level
environment variable (`https://vx59qs2osl.execute-api.eu-north-1.amazonaws.com`, no trailing
slash) — the deployed frontend hits the live API and only falls back to `DEMO FIXTURE` on a real
failure, never silently.

> Changing that value requires a manual redeploy of the branch (Amplify Console → Hosting →
> `main` → latest job → Redeploy this version) — a new env var alone does not trigger a build.

## Deploy the backend skeleton

`scripts/task6-deploy-wizard.sh` walks through AWS CLI/SAM CLI setup, credentials, confirming
Bedrock model access, and `sam deploy` for `infra/api-gateway.yaml`. Run it from a bash shell
(Git Bash on Windows):

```bash
bash scripts/task6-deploy-wizard.sh
```
