# Opportunity Engine — frontend

React + TypeScript + Vite. Lane B owns this directory: the five P0 screens (PRD §16.1), the
evidence drawer, the design system and the Amplify Hosting pipeline.

## Commands

| Command | What it does |
| --- | --- |
| `npm install` | Install dependencies |
| `npm run dev` | Dev server with HMR |
| `npm run lint` | oxlint |
| `npm test` | vitest — rule-table, guardrail and render tests |
| `npm run build` | `tsc -b` then `vite build` — the gate Amplify runs |
| `npm run preview` | Serve the production build locally |

## Layout

```
src/
  api/          API client; fixture fallback when no live endpoint is configured
  components/
    common/     Shared primitives (labels, chips, meters, cards, buttons)
    layout/     App shell and navigation
    inbox/      Screen 3 components
    polarity/   Polarity split bar (screen 1's signature moment)
  fixtures/     Committed fixture payloads, shaped per PRD §14
  screens/      One folder per P0 screen
  styles/       theme.css — the design tokens every screen imports
  types/        Entity + API types mirroring PRD §14
```

## Routes

Hash routing, so Amplify needs no rewrite rule for deep links.

| Route | Screen |
| --- | --- |
| `#/business` | Screen 1 — Business & feedback (default) |
| `#/inbox` | Screen 3 — Opportunity inbox |
| `#/tokens` | Design-token reference. Not a product screen; it computes the palette's contrast ratios at load, so a token change that breaks a pairing shows up as a FAIL |

Screens 2, 4 and 5 are listed in the nav as not built yet rather than linking nowhere.

## Configuration

`VITE_API_BASE_URL` points the client at the deployed API Gateway stage. When it is unset the
client serves committed fixtures instead — and the UI labels them `DEMO FIXTURE`, per the
Live → Cached → Demo Fixture ladder in PRD §7.2. Fixture data is never shown as if it were live.

`VITE_DEV_API_ORIGIN` turns on the dev-server proxy (`vite.config.ts`). It exists because the
deployed stage sends no CORS headers, so a browser on `localhost` cannot call it directly. To
run the screens against real data locally, copy `.env.example` to `.env.local` and set:

```
VITE_DEV_API_ORIGIN=https://vx59qs2osl.execute-api.eu-north-1.amazonaws.com
VITE_API_BASE_URL=/api
```

`.env.local` is gitignored. The proxy is a local affordance, not the fix — see below.

## Known blockers

All resolved as of 2026-09-19 — Tasks 22 and 23 are checked off in `tasks/todo.md`. Kept here as
the record of what each one actually was and how it was found.

| # | Blocker | Owner | What it stops |
|---|---|---|---|
| 1 | ~~No endpoint states its retrieval mode.~~ **Resolved.** Every handler now sends `X-Retrieval-Mode: live \| cached \| demo_fixture` (`backend/handlers/_common.py::ok()`); `LIVE` for a real DynamoDB row, `DEMO_FIXTURE` for the Task 2 fallback. See `docs/contract.md` gap 1. | Lane A | — |
| 2 | ~~No rejected-candidate route.~~ **Resolved.** `RejectedCandidate` (`backend/schemas/entities.py`) + `list_rejected_ideas` handler + `/businesses/{id}/rejected-ideas` route now exist, wired into `orchestrator.persist`. See `docs/contract.md` gap 2. | Lane A, Task 19 | — |
| 3 | ~~The deployed stack has no DynamoDB table at all.~~ **Resolved.** `sam deploy` shipped the Task 20 table and all current Lambda code (stack `opportunity-engine-skeleton`, `UPDATE_COMPLETE`, 2026-09-19). A first deploy also silently deployed handlers no read path to the table — `Globals.Function.Environment.DYNAMO_TABLE_NAME` and a per-function `DynamoDBReadPolicy` were missing from `infra/api-gateway.yaml`, so every "live" response would have fallen back to the fixture regardless. Fixed, rebuilt, redeployed; verified with a real `put-item`/Lambda-invoke/`delete-item` round trip against `GetBusiness` — the header came back `live` with the written row's real content. The table was still empty after this — that turned out to need six more, separate fixes (below) before a live run would actually persist an opportunity. | Lane A | — |
| 7 | ~~The table was empty — no pipeline run had ever persisted anything.~~ **Resolved.** `scripts/run_live_pipeline.py` had a stale import from the Bedrock→OpenCode Go rename; Windows' `cp1252` stdout crashed on the model's own reasoning text; `boto3` rejects native `float` (needs `Decimal`); OpenCode Go's response length is flaky enough to blow past any fixed `max_tokens` (fixed with a resume-then-restart retry in `synthesis_agent.live_collect`); the Synthesis prompt described `opportunity_type` in prose instead of stating the literal enum values, so the model invented a variant the schema rejected; and `build_opportunity`'s "our pain" filter only recognized `feedback_pipeline_labeller`, silently dropping every negative-polarity signal from the demo business's own PulseStack-simulator feedback (`produced_by="pulsestack_simulator"`). First real gate-passed opportunity: `opp_run_7f023794a99d_0`. See `LEARNING.md`, Day 3. | Lane A | — |
| 4 | ~~The deployed `AWS::Serverless::HttpApi` has no `CorsConfiguration`.~~ **Resolved.** `infra/api-gateway.yaml` now declares `CorsConfiguration` (GET, wildcard origin, `ExposeHeaders: X-Retrieval-Mode` — without that, browsers drop blocker 1's header before JS sees it). Applied to the live API directly via `aws apigatewayv2 update-api` (verified with a real `OPTIONS` preflight from the Amplify origin: `204`, correct headers) rather than a `sam deploy`, since `sam build` for this template is separately broken — see next line. Template and live config now match, so a future successful deploy won't drift it. | Lane A / infra | — |
| 6 | ~~`sam build` for `infra/api-gateway.yaml` fails.~~ **Resolved.** None of these 10 functions import `strands-agents`/`mcp`, but `sam build` was resolving deps from the repo's full `backend/requirements.txt` (which does need it, for the agent modules) anyway — `mcp`'s Windows-only `pywin32` dependency broke local pip resolution for the Lambda (Linux) target. Root `requirements.txt` now points at `backend/requirements-lambda.txt` (pydantic + boto3 only). `.samignore` is deleted — it never did anything; `aws_lambda_builders` has no such feature, only a fixed internal exclude list. The ~90MB of `frontend/node_modules` still rides along into every package (128MB total, under Lambda's 250MB unzipped limit) — a `CodeUri` pointed at a smaller symlinked directory was tried and reverted: this repo's git-for-windows has `core.symlinks=false`, so committing it would have silently duplicated all of `backend/` into git as real, driftable files. | Lane A / infra | — |
| 5 | ~~`opp_001` comes back with `priority: "High"` despite a non-empty `pains_to_fix_first`.~~ **Resolved.** The Task 2 fixture (`backend/fixtures/fixtures.py`) had drifted from §13.1's rule table — never actually run through `run_quality_gate`. Corrected to `"Blocked"`; see `test_get_opportunity_fixture_priority_matches_the_rule_table`. | Lane A | — |

## Rendering rules that are not optional

These come from `AGENTS.md` and the PRD; a change that breaks one of them is a bug, not a preference.

- No composite opportunity score. Evidence confidence, potential value and priority render as
  three visually separate fields (§13.1).
- Every claim reaching the UI carries an `OBSERVED` / `INFERRED` / `ASSUMED` label (§13.3).
- Every source carries its retrieval level: `LIVE RESEARCH` / `CACHED VERIFIED SOURCE` /
  `DEMO FIXTURE` (§7.2). Never substitute silently.
- Potential value is always a range with its assumptions visible and editable (§13.2).
- The provenance chain SourceDocument → Evidence → Claim → Opportunity stays clickable.
