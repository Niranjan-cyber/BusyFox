# Opportunity Engine — Task List

Full detail and rationale for each task: `tasks/plan.md`. Check items off here as they land; commit this file as you go — it doubles as a visible, dated record of progress for the repo-history requirement.

## Phase 0 — Contract lock (blocking, both people together)

- [x] **Task 1:** Core entity schema — nine entities + provenance chain (Pydantic + TS types), committed
- [x] **Task 2:** API surface for the five P0 screens — endpoint table + stub Lambdas returning fixture data

### Checkpoint: Contract locked
- [x] Tasks 1–2 committed
- [ ] Both people agree the committed file is the source of truth

## Phase 1 — Day 1 remainder

### Lane A — Backend/Agents
- [x] Task 3: GitHub REST collector → `Signal`-shaped output
- [x] Task 4: HN Algolia collector → `Signal`-shaped output
- [x] Task 5: One live Tavily round-trip — characterize failure modes
- [x] Task 6: Skeleton AWS deploy (API Gateway + Step Functions + stub Lambda live in eu-north-1; Amplify Hosting deferred to Task 7)

### Lane B — Frontend/UX
- [x] Task 7: React app scaffold + Amplify Hosting pipeline
- [x] Task 8: Design tokens via `frontend-design` skill, committed as a theme file
- [x] Task 9: Screen 1 & 3 shells on fixture data, using Task 8's theme

### Lane C — Floating
- [x] Task 10: PulseStack simulator (scenario + generator + seed), `Signal`/`Evidence`-shaped output
- [x] Task 11: App Store RSS fetch (one competitor) + Product Hunt token registered
- [x] Task 12: LEARNING.md — first real entry

### Checkpoint: End of Day 1
- [~] Real, visible commits across the day — true for Lane A/C (19 commits, 09:15-23:59 Sept 17); Lane B's Tasks 7-9 landed as one commit dated Sept 18 12:52, flagged to teammate
- [x] GitHub + HN collectors return real signals — live-verified 2026-09-18 against getsentry/sentry and an HN "Datadog" search (not exercised live before; their unit tests mock the HTTP call)
- [x] Tavily failure modes known
- [x] Simulator committed with its seed
- [x] Skeleton deployed, live Amplify URL reachable — https://main.dw3gwg5t169l9.amplifyapp.com/ (created 2026-09-18; `amplify.yml` alone wasn't a live app until now, see README.md)
- [x] Screens 1 & 3 render fixture data through committed theme
- [x] LEARNING.md has a real entry

## Phase 2 — Day 2

### Lane A — Backend/Agents
- [x] Task 13: Feedback pipeline — normalise/dedupe/redact/spam filter (code only)
- [x] Task 14: Feedback pipeline — label/validate/aggregate/balance (Haiku labeller)
- [x] Task 15: Market Agent (Strands, Haiku) → `signals[]`
- [x] Task 16: Competitor Agent (Strands, Haiku) → `signals[]`
- [x] Task 17: Synthesis Agent (Strands, Sonnet) → `candidate_opportunities[]` w/ mechanism
- [x] Task 18: Evidence Check (quote-exists + quote-supports-claim + freshness)
- [x] Task 19: Quality Gate + Ranker (14 checks, rule-table priority, no composite score)
- [x] Task 20: DynamoDB table design + writes for all core entities
- [x] Task 21: Orchestrator wiring — full pipeline end to end. First real live run
  2026-09-19 via `scripts/run_live_pipeline.py`, persisting `opp_run_7f023794a99d_0`
  (`unmet_need`, priority `Blocked`, `LOW` confidence) to the deployed table. Getting
  there fixed six real bugs (stale rename, Windows stdout encoding, DynamoDB float/Decimal,
  flaky OpenCode Go token budgets, `opportunity_type` prompt/schema mismatch, and a
  `produced_by` gap that silently dropped every "our pain" signal for the simulated
  business) — see `LEARNING.md`, Day 3.

### Lane B — Frontend/UX
- [x] Task 22: Screen 1 on real data — client wired to the contract routes and verified in a
  browser against the deployed stage; blockers 1 (retrieval-mode header), 3 (table deployed +
  wired), and 4 (CORS) resolved. Table is no longer empty — `scripts/run_live_pipeline.py`
  persisted a real gate-passed opportunity 2026-09-19 (see Task 21 note below); verified live via
  `GET /businesses/biz_pulsestack/opportunities` returning it with `X-Retrieval-Mode: live`.
- [x] Task 23: Screen 3 on real data — inbox groups and ranks the live opportunity with its
  claims off `/opportunities/{id}/claims`; blockers 1, 2 (rejected-candidate route, Task 19), 3,
  and 5 resolved. Same fix as Task 22 unblocks this: `GET /opportunities/{id}/claims` returns real
  claims, each with populated `evidence_ids`.

### Lane C — Floating
- [ ] Task 24: **Deferred 2026-09-19** — Label F1 (§19.2) lives in the full metrics
  table, which is explicitly P1 ("if P0 done by Day 3, 4pm" — PRD §19.2 intro).
  It's not part of the Day 2 checkpoint either. Per `CLAUDE.md`'s hard rule, no
  P1 starts while Day 3's P0 (Action Agent, screens 2/4/5) is open, so 100-row
  manual labelling is on hold until P0 lands. Corpus + blank sheets are ready
  (`tasks/gold_set/labels_{niranjan,swarali}.csv`, `scripts/build_gold_set.py`)
  whenever it's picked back up.
- [x] Task 25: Re-run `/graphify` before evening stand-up — scoped via
  `.graphifyignore` (`.agents/`, `.claude/`) this time, per Day 1's own
  lesson. 112 files, 1237 nodes, 87 communities. Health check flagged 96
  dangling-endpoint edges and ~326 collapsed multi-relation edges (mostly
  benign AST multi-edge collapse) — see `graphify-out/GRAPH_REPORT.md`.

### Checkpoint: End of Day 2
- [x] ≥1 gate-passed opportunity visible in real inbox, claims traceable to evidence — met
  2026-09-19 (Day 3), not Day 2 itself; `opp_run_7f023794a99d_0` live via the deployed API,
  every claim's `evidence_ids` populated. See Task 21 note.
- [ ] Risk watch: if Tavily unusable live, fall back to Level 2/3 rather than debug under pressure

## Phase 3 — Day 3 (broken down at Day 3 morning stand-up, 2026-09-19)

Full detail for every task below: `tasks/plan.md`, Phase 3.

### Lane A — Backend/Agents
- [~] Task 26: Action Agent + ExecutionPack generation, `outreach_policy` enforced in prompt
  and post-generation check — code + 15 unit tests committed
  (`backend/agents/action_agent.py`, `backend/tests/test_action_agent.py`); orchestrator gained
  `run_action_stage`/`persist_execution_pack`, handler reads DynamoDB first
  (`backend/handlers/opportunities_stub.py`). Live-run-verified 2026-09-19 via
  `scripts/run_action_agent_live.py` against `opp_run_7f023794a99d_0`: correctly refused to
  emit any outreach draft (that opportunity has zero verified strengths, so no valid
  `proof_point_signal_id` exists — working as designed, not yet a rehearsal of the
  policy-violation reject path, which needs a ranked opportunity with a real strength).
  Pack `pack_opp_run_7f023794a99d_0` persisted to the live table. Blocked on: `sam deploy` for
  the updated `GetExecutionPack` Lambda — harness auto-mode won't script past the changeset
  confirmation prompt, needs a human to run
  `sam deploy --config-file infra/samconfig.toml` interactively before the deployed API
  reflects the new handler (currently still serving the old fixture-only code). See
  `LEARNING.md`, Day 3.
- [ ] Task 27: Real value model computation (§13.2 formula, editable labelled range) —
  replaces Synthesis's placeholder `ValueModel`
- [ ] Task 28: Evidence drawer Level 2 (Cached) fallback, rehearsed with a real forced
  failure — this closes out Day 2 checkpoint's unfinished Tavily risk-watch item, don't
  track it twice
- [ ] Task 29: Evaluation run vs. gold set — **blocked on Task 24 (deferred)**, do not start

### Lane B — Frontend/UX
- [ ] Task 30: Screen 2 — Live investigation (3 streaming research lanes)
- [ ] Task 31: Screen 4 — Opportunity detail + live Evidence Check diagram (§21's named
  best differentiator — real design attention, not a placeholder chart)
- [ ] Task 32: Screen 5 — Execution pack (can build against fixture first, re-point at
  Task 26 once real)
- [ ] Task 33: `browser-testing-with-devtools` pass on all 5 screens (after 30–32)

### Lane C — Floating
- [ ] Task 34: Demo-video shot list against §21's scene table — start now, not blocked
- [ ] Task 35: Anveshan Precision clip — **conditional**, only if Tasks 26–28/30–33 done by 4pm

### Everyone, before 8pm
- [ ] Task 36: `code-review-and-quality` + `code-simplification` + `ponytail-review` pass,
  time-boxed to finish by 8pm

### Checkpoint: Feature freeze — Day 3, 8pm
- [ ] Golden path runs start to finish
- [ ] No new features after this point

## Phase 4 — Day 4

- [ ] Re-check official schedule for actual deadline hour
- [ ] Polish all 5 screens, fix Day 3 bugs
- [ ] Record demo video ≤3:00 per §21 script
- [ ] Write the writeup (problem, build, AWS integration, AI tools used)
- [ ] Finalise README.md, CREDITS.md, LEARNING.md
- [ ] Submit; confirm registration went through
