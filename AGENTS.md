# AGENTS.md

Repo for **Opportunity Engine** (dir/repo name is `BusyFox`; the product name is a placeholder and may be renamed). As of Day 1 (17 Sept 2026) there is **no application code** — only a placeholder `README.md` and the product spec. There is no build, test, lint, or typecheck tooling yet.

## Spec of record
- `opportunity_engine_prd_v8.md` (~1,400 lines) is the single source of truth for what to build. It is large — search it by `§`-numbered section rather than reading end to end.
- Highest-value sections: §10 agent/service architecture, §10.1a agent runtime contract, §11 quality gate, §12 evidence model, §13 prioritisation/value, §14 data models, §16 screens, §17 AWS architecture, §21 demo script, §22 risks, and **Part B** (two-person workflow).
- Older PRD versions (v5–v7) are discussed in the text but not committed.

## Hard event constraints (disqualification risk — do not violate)
- Commit history must fall inside the event window (17–20 Sept 2026). Never backdate, rewrite, or fabricate history.
- Work must be new once the clock starts. Reused code needs a credit plus licence in `CREDITS.md`.
- List AI coding tools in the submission writeup (and mirror in `README.md`).
- Maintain `LEARNING.md` from Day 1 — "Learning" is a scored judging criterion.
- Submission is exactly three artifacts: public repo, demo video ≤ 3:00 that visibly shows AWS integration, and a short writeup. Submission after the deadline is impossible.
- Every member must be a university student in India, 18+, verified on WeMakeDevs and AWS Builder Center (student status).

## Locked technical decisions (from the spec — don't relitigate)
- Agents: **Amazon Bedrock via the Strands Agents SDK**, each running inside Lambda; **Step Functions** orchestrates. Frontend: React on **Amplify Hosting**. State: DynamoDB + S3.
- Web search/extraction is **Tavily** (not Exa). Other P0 sources: GitHub REST API and Hacker News (Algolia). Business feedback is our own seeded simulator (PulseStack), not scraped.
- Research agents are schema-limited to `signals[]`; no `opportunities` field exists for them. Only the Synthesis Agent emits `candidate_opportunities[]`.
- Every agent is bounded by the five-field runtime contract in §10.1a; hitting a limit returns `truncated: true` instead of failing the run.
- Evidence Check and Quality Gate are code, not agents. There is deliberately **no composite opportunity score** (§13.1): show evidence confidence, potential value, and a rule-based priority tier separately.
- Data acquisition is the named top technical risk (§7.2). Every external source uses a Live → Cached → Demo Fixture ladder, each level labelled in the UI. Never substitute silently.

## Modelling conventions
- Provenance chain: `SourceDocument → Evidence → Claim → Opportunity`, and it must be clickable in the UI.
- Every claim reaching the UI is labelled **Observed / Inferred / Assumed** (§13.3).
- Stable prefixes: `opp_` and DynamoDB keys like `OPP#`. Generated simulator data is committed with its generator and fixed seed.
- PulseStack is simulated; its named competitors (Sentry, Datadog, etc.) are real. Never invent claims about a real company (§3.3).

## Working cadence
- Part B defines contracts-first repo setup, daily stand-up/integration/demo, and the P0 → P1 → P2 scope discipline; §20 lists MVP scope; feature freeze is Day 3, 8pm.
