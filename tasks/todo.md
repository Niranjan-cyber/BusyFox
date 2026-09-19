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
- [ ] Task 24: **Deferred 2026-09-19, deferral confirmed 2026-09-20** — Label F1 (§19.2) lives in
  the full metrics table, which is explicitly P1 ("if P0 done by Day 3, 4pm" — PRD §19.2 intro).
  It's not part of the Day 2 checkpoint either. Per `CLAUDE.md`'s hard rule, no
  P1 starts while Day 3's P0 (Action Agent, screens 2/4/5) is open, so 100-row
  manual labelling is on hold until P0 lands. Corpus + blank sheets are ready
  (`tasks/gold_set/labels_{niranjan,swarali}.csv`, `scripts/build_gold_set.py`)
  whenever it's picked back up. Re-confirmed on Day 4 while closing Task 34's shot-list gaps:
  with the demo needed today, staying deferred for good (not "picked back up") — the video runs
  the qualitative "planted opportunities + red herrings" narrative without the three headline
  numbers instead. See `docs/demo-shot-list.md`.
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
- [x] Task 26: Action Agent + ExecutionPack generation, `outreach_policy` enforced in prompt
  and post-generation check — code + 15 unit tests committed
  (`backend/agents/action_agent.py`, `backend/tests/test_action_agent.py`); orchestrator gained
  `run_action_stage`/`persist_execution_pack`, handler reads DynamoDB first
  (`backend/handlers/opportunities_stub.py`). Live-run-verified 2026-09-19 via
  `scripts/run_action_agent_live.py` against `opp_run_7f023794a99d_0`: correctly refused to
  emit any outreach draft (that opportunity has zero verified strengths, so no valid
  `proof_point_signal_id` exists — working as designed; the policy-violation reject path still
  needs a rehearsal against a ranked opportunity with a real strength, not yet covered live).
  Pack `pack_opp_run_7f023794a99d_0` persisted and, after a second real bug (`GetExecutionPack`
  was missing the `DynamoDBReadPolicy` every sibling handler already had — IAM gap, not a code
  gap), confirmed live via `GET /opportunities/opp_run_7f023794a99d_0/execution-pack` returning
  `200`, `X-Retrieval-Mode: live`, the real pack (both `sam deploy`s run by the human; harness
  auto-mode won't script past the changeset confirmation). See `LEARNING.md`, Day 3.
- [x] Task 27: Real value model computation (§13.2 formula, editable labelled range) —
  replaces Synthesis's placeholder `ValueModel`. `compute_value_model` in
  `backend/pipeline/quality_gate.py`, applied to every surviving opportunity; 5 new tests
  (PRD worked example: 24 signals × $99 → $5,940–$17,820). Not yet re-verified against a fresh
  live pipeline run — `opp_run_7f023794a99d_0`'s persisted `value` is still the old placeholder
  until `scripts/run_live_pipeline.py` is re-run. Assumption *values* live in each
  `ValueAssumption.description` string, so the "editable" UI in Task 31 will need either
  structured values on the schema or client-side recompute.
- [x] Task 28: Evidence drawer Level 2 (Cached) fallback, rehearsed with a real forced
  failure — this closes out Day 2 checkpoint's unfinished Tavily risk-watch item, don't
  track it twice. `GET /competitors/{id}/evidence/{evidenceId}/live` now does live Tavily
  re-verify -> S3 cache (`backend/db/evidence_cache.py`) -> fixture; body and
  `X-Retrieval-Mode` always name the rung served; labels render §7.2's exact strings; 9 unit
  tests. Rehearsed against the deployed stack 2026-09-19 (real key -> `live`, bad key ->
  `cached`, cache emptied -> `demo_fixture`, key restored -> `live`; all PASS, log in
  `docs/rehearsals/task28-evidence-fallback.txt`). Rehearsal needed a new real fixture
  (`evd_hn_31781473`) — see `LEARNING.md`, Day 3. Nothing in the frontend calls this route
  yet; the drawer wiring is Task 31.
- [ ] Task 29: Evaluation run vs. gold set — **blocked on Task 24 (deferred)**, do not start

### Lane B — Frontend/UX
- [x] Task 30: Screen 2 — Live investigation (3 streaming research lanes) — closed the
  contract.md gap Task 2 left open (Screen 2 had no endpoint): added
  `GET /businesses/{id}/signals` (unfiltered `Signal[]`, same DynamoDB-first/fixture-fallback
  pattern as every other handler) plus its SAM route. Frontend polls it every 4s
  (`InvestigationScreen.tsx`, no websockets — acceptance criteria allow polling) and groups by
  lane via `lib/viewModels.ts::signalLane` (`produced_by` → Market/Feedback/Competitive). Each
  signal card carries its own `SourceLabel`, not just the screen banner. Manually verified in a
  browser (Playwright): 3 lanes render, no console errors, nav/labels correct. 9 new backend
  tests, 3 new frontend tests (client + lane classification), all passing (202 backend / 122
  frontend). See `LEARNING.md`, Day 3.
- [x] Task 31: Screen 4 — Opportunity detail + live Evidence Check diagram (§21's named
  best differentiator — real design attention, not a placeholder chart). New
  `frontend/src/screens/OpportunityDetail/` reached from an opportunity card's
  "View evidence chain" link (`#/opportunities/{id}`), wired to the three
  already-live routes (`/opportunities/{id}`, `/opportunities/{id}/claims`,
  `/claims/{id}/evidence` — all built in Task 21/26, nothing new on the backend).
  New `EvidenceCheckDiagram` (`components/evidence-check/`) replays each claim's
  real per-evidence `claim_support` into the three PRD §21 outcomes (accepted /
  rejected-missing-citation / rejected-unsupported) via
  `lib/viewModels.ts::evidenceCheckResult`, which detects the missing-citation
  case off the exact literal string `backend/pipeline/evidence_check.py`
  hardcodes ("quote not found in source text") since Evidence carries no
  separate `quote_exists` boolean. New frontend fixture evidence set
  (`fixtures/evidence.ts`) deliberately includes both reject shapes so the
  diagram has real data to walk even with no backend configured — the backend's
  own demo fixture (`backend/fixtures/fixtures.py`) has zero reject examples.
  Value-model range is editable (`EditableValueRange`, session-only, not
  persisted — no route exists to save it, Task 27's note that `ValueAssumption`
  has no numeric fields to recompute from still stands). `EvidenceDiversityReadout`
  extracted out of `OpportunityCard` so the inbox card and detail screen share
  one readout. 12 new component/client tests (frontend now 136 passing);
  `npm run build`/`lint` clean. Manually verified in a browser (Playwright)
  against fixtures (all three Evidence Check outcomes render, editable inputs
  work) and against the deployed API for the real `opp_run_7f023794a99d_0`
  (LIVE banner, real claim/evidence text, diagram correctly shows every
  evidence item as `rejected_unsupported` — consistent with that run's known
  zero-verified-strengths state, Task 26's note); no console errors either way.
- [x] Task 32: Screen 5 — Execution pack. New `frontend/src/screens/ExecutionPack/`
  (`#/opportunities/{id}/execution-pack`, reached from a new "View execution pack" link at the
  bottom of screen 4), wired to the already-live `/opportunities/{id}/execution-pack` route
  (Task 26 — no new backend work needed). Offer/proposal/outreach-drafts rendering lives in a
  pure `components/execution-pack/ExecutionPackBody.tsx`, same fetch/presentation split as
  screen 4's `EvidenceCheckDiagram`. Each outreach draft's `proof_point_signal_id` is looked up
  against the opportunity's own `strengths_it_builds_on` (already on screen, no second fetch)
  and rendered as its reason text, linking back to `#/opportunities/{id}`; `outreach_policy_checked`
  (§18.1) is shown per draft with a ✓/✗. New frontend fixture (`fixtures/executionPacks.ts`)
  deliberately cites `sig_311`, a real signal already on `opp_07`'s `strengths_it_builds_on`, so
  the proof-point trace has a genuine cross-reference to render even with no backend configured.
  9 new component/client tests (frontend now 142 total, 1 existing AppShell test updated to
  match the nav's new copy — see LEARNING.md). Manually verified in a browser (Playwright) both
  ways: against fixtures
  (`opp_07`, real fallback triggered by a 404 from the deployed API, proof-point link resolves
  correctly) and against the deployed API for the real `opp_run_7f023794a99d_0` — LIVE banner,
  real Action-Agent-generated offer/proposal text, and the "No outreach draft yet" empty state
  correctly rendered rather than crashing (that opportunity has zero verified strengths, Task
  26's known state); no console errors either way. `npm run build`/`lint` clean. (3 tests fail
  locally with "no backend configured" assertions tripped by a developer `.env.local` setting
  `VITE_API_BASE_URL` — pre-existing on `main` too, not introduced here; see LEARNING.md.)
- [x] Task 33: `browser-testing-with-devtools` pass on all 5 screens (after 30–32) — all
  five clean. Screens 1, 3, 4, 5: LIVE data end to end (`opp_run_7f023794a99d_0` through
  business → inbox → detail → execution pack), zero console errors, all network calls
  200. Fixed one real bug found along the way: `App.tsx`'s `UnavailableScreen` copy
  ("lands later on day 3. Screens 1, 2 and 3 are built") was stale now that 4/5 exist —
  reworded to explain screens 4/5 need an opportunity id. Screen 2 (`/investigation`)
  initially 404'd on `GET /businesses/{id}/signals` — Task 30 added the route to
  `infra/api-gateway.yaml`/handler code (commit `2fa0e4c`) but never `sam deploy`ed it.
  Deploying it surfaced the real `CodeUri` bloat (see LEARNING.md, Day 3): `.aws-sam/`
  from every prior build was riding along inside `CodeUri: ../`, snowballing to a 1.18GB
  upload. Fixed with `rm -rf .aws-sam` before a clean rebuild (125MB, back to Day 1's
  documented baseline) — **not** a `.samignore` file, which is confirmed inert for this
  project (tried it, checked the build output, `frontend/`/`docs/`/`graphify-out/` were
  still in there). Deployed via the built template (`.aws-sam/build/template.yaml`, not
  the raw source, which re-packages unfiltered and blows the 250MB Lambda limit) with
  `--resolve-s3 --capabilities CAPABILITY_IAM`. Live-verified 2026-09-19 20:08 UTC:
  `X-Retrieval-Mode: live`, real signal data, Screen 2 renders with zero console errors,
  every 4s poll returns 200.

### Lane C — Floating
- [x] Task 34: Demo-video shot list against §21's scene table — `docs/demo-shot-list.md`.
  Maps every scene to what's actually recordable today: most beats are live off the deployed
  app or the committed `opp_07` fixture (the only live opportunity has zero verified strengths,
  so it can't carry the 1:35–2:15 beats — those need `opp_07`). Found 3 real gaps needing a
  decision before recording, not just recording work: Anveshan Precision (2:15–2:25) doesn't
  exist anywhere in the system (`BUSINESS_ID` is hardcoded to `biz_pulsestack`), the three
  headline metrics (2:25–2:40, §19.1) are uncomputed since Task 24/29 are still blocked, and no
  architecture diagram exists yet for 2:40–2:50.
- [ ] Task 35: Anveshan Precision clip — **conditional**, only if Tasks 26–28/30–33 done by 4pm

### Everyone, before 8pm
- [x] Task 36: `code-review-and-quality` + `code-simplification` + `ponytail-review` pass,
  time-boxed to finish by 8pm — done 2026-09-20 (Day 4), two parallel reviews (backend/scripts,
  frontend), all three lenses combined, explicit check against the four CLAUDE.md guardrails
  (all clear — no composite score, agents structurally emit `signals[]` only, retrieval-mode
  labelling never silently substituted). 6 real findings fixed:
  - **Security:** `backend/collectors/producthunt.py` built its GraphQL query by raw f-string
    interpolation of `slug` (sourced from an LLM tool call) — a `"` or newline could break out
    of the query. Fixed with `json.dumps(slug)`.
  - **Correctness/production bug:** `backend/pipeline/feedback_labelling.py`'s `bedrock_labeller`
    was the one component never migrated off Bedrock in the 2026-09-19 sweep (every AWS account
    has 0 req/min real-time inference quota, see MEMORY.md) — would hang/fail on any real
    uploaded-data business. Migrated to OpenCode Go, same pattern as
    `evidence_check.opencode_go_semantic_support_checker`, renamed to `opencode_go_labeller`.
  - **Correctness:** `frontend/src/screens/Business/BusinessScreen.tsx` called `exactUsd()` on
    `Pricing`'s optional fields without a null check — a business missing one pricing tier
    rendered `$NaN/mo`. Filtered undefined entries before mapping.
  - **Guardrail-adjacent:** `OpportunityDetailScreen.tsx`'s `ServedBanner` only tracked
    Opportunity + Claims `Served` sources, not each claim's evidence fetch — the top banner
    could read "LIVE" while the evidence chain underneath had silently fallen back to
    `demo_fixture`, exactly the per-screen version of the labelling guardrail. Added each
    claim's evidence `Served` to the banner's `sources`.
  - **Simplification:** `CLAIM_HEADING`/`CLAIM_ORDER` were duplicated verbatim in
    `OpportunityCard.tsx` and `OpportunityDetailScreen.tsx`; moved to `lib/viewModels.ts`, one
    source of truth. `orchestrator._matched_signal_ids` duplicated
    `quality_gate._signal_ids`; made the latter public (`signal_ids`) and imported it instead.
  - **Dead code:** deleted unused `EntityIdPrefix` enum from `backend/schemas/entities.py` (zero
    references; ids are built with raw f-strings everywhere).
  Verified: `npm run build`/lint clean, frontend 139/142 (3 pre-existing `.env.local` failures,
  unchanged from Task 32's note), backend 202/202 passing. One low-likelihood nit flagged but
  left alone per freeze (`quality_gate.quote_found`'s sentinel-pairing assumption has no schema
  enforcement) — not worth a schema change this late.

### Checkpoint: Feature freeze — Day 3, 8pm
- [x] Golden path runs start to finish — closed 2026-09-20 (Day 4), not Day 3: the deployed
  Amplify app had never actually had `VITE_API_BASE_URL` set (flagged in `README.md` on Day 1,
  never followed up), so every prior "LIVE-verified" screen (Tasks 22/23/30/31/32/33) was
  checked against local dev or the API directly — the public URL anyone would open, including
  for the demo video, was serving `DEMO FIXTURE` on every screen the whole time. Fixed by
  setting the env var as an Amplify app-level variable and redeploying (human-run, no AWS creds
  in the harness). Re-verified live via Playwright straight after redeploy, clicking the full
  path on `https://main.dw3gwg5t169l9.amplifyapp.com/`: `#/business` → `#/investigation` →
  `#/inbox` → `#/opportunities/opp_run_7f023794a99d_0` → `.../execution-pack`. Every screen
  `LIVE RESEARCH`, every network call 200, zero console errors throughout. See `LEARNING.md`.
- [x] No new features after this point — holding since Task 36; today's work is bug fixes only

## Phase 4 — Day 4 (broken down into tasks 2026-09-20; full detail: `tasks/plan.md`, Phase 4)

### Day 4 — Ship (no lane split, single critical path)
- [x] Task 37: `rm -rf .aws-sam infra/.aws-sam` added right before `sam build` in
  `scripts/task6-deploy-wizard.sh` (Stage 5) — Day 3's Task 33 deploy took ~90 min because every
  build re-zips its own prior `.aws-sam/` output into the next one (1.5GB → 1.18GB upload for a
  one-route change; confirmed both a root-level and `infra/`-level `.aws-sam` exist depending on
  how `sam build` was invoked, 1.5GB/1.6GB respectively on disk right now). Did **not** scope
  `CodeUri` down (tried and reverted Day 1 — Windows `git core.symlinks=false` turns the symlink
  workaround into a real, driftable second copy of `backend/`) or add a `.samignore` (confirmed
  inert twice now, Day 1 and Day 3 — see `LEARNING.md`). Re-verified on a real `sam deploy`
  2026-09-20: the rebuilt `.aws-sam` still measured 1.6GB (13 functions × `CodeUri: ../` each,
  no dedup at build time — expected, not a regression), but the actual S3 upload was ~47MB
  because every function shares one identical content hash, so `sam deploy` uploads it once and
  skips the rest as "File with same data already exists." Separately hit and fixed the exact
  Day 3 `--template-file <source>.yaml` gotcha again (repackages from scratch, ignoring
  `sam build`'s output) — deploying `.aws-sam/build/template.yaml` instead is what actually used
  the small artifact. `LEARNING.md` had this written down already; worth grepping it before
  handing over a deploy command, not just before writing code.
- [x] Task 38: Deadline re-confirmed — **8pm, 2026-09-20** — unchanged from the earlier check.
- [x] Task 39: Polish pass across all 5 screens, live on Amplify — found and fixed 2 real bugs:
  - Screen 3 (inbox), "Ideas we rejected" (the screen's named signature moment) rendered raw
    backend slugs verbatim (`truth`, `no_verified_evidence`) instead of readable text — the
    fixture data used polished prose but the live pipeline never did. Added a label map in
    `frontend/src/lib/viewModels.ts` (`rejectionGateLabel`/`rejectionReasonLabel`), same pattern
    as the existing `CLAIM_HEADING` map, with a humanize-slug fallback for anything unmapped
    (including the dynamic `duplicate_merged_into:<id>` case). Live-verified: now reads "Evidence
    Check" / "No claim in this idea has verified evidence backing it."
  - Screen 4 (opportunity detail), `GET /claims/{id}/evidence` (`backend/handlers/claims_stub.py`)
    never set `X-Retrieval-Mode` — the one handler that skipped the label every sibling handler
    sets — so the `ServedBanner` reported every evidence fetch as `PROVENANCE NOT STATED` even
    when served live from DynamoDB, directly undermining the §7.2 labelling guardrail on the
    PRD's named best-differentiator screen. Fixed by passing `retrieval_mode=LIVE`/`DEMO_FIXTURE`
    like every other handler. Live-verified: banner now reads "LIVE RESEARCH" throughout.
  - Both fixes: 202/202 backend tests, 139/142 frontend (3 pre-existing unrelated `.env.local`
    failures per Task 32's note), `npm run build`/lint clean. Committed (`dd0913a`), pushed,
    frontend redeployed via Amplify's build-on-push, backend redeployed via `sam deploy`
    (human-run, no AWS creds in the harness — see Task 37 note above for what that deploy hit).
  - Screens 1, 2, 5 checked clean, no bugs found.
- [ ] Task 40: Record demo video ≤3:00 per §21 script
- [x] Task 41: Write the writeup (problem, build, AWS integration, AI tools used) —
  `WRITEUP.md`, covers all four required sections including the honest Bedrock→OpenCode Go
  substitution
- [x] Task 42: Finalise README.md, CREDITS.md, LEARNING.md — `README.md` gained a product
  intro, submission-docs index, and the "Tools we used" AI-disclosure section AGENTS.md has
  required since Day 1 but nobody had written; `CREDITS.md` created from scratch (didn't exist
  before); `LEARNING.md` Day 4 entry added noting the gap. See `LEARNING.md`, Day 4.
- [ ] Task 43: Submit; confirm registration went through

### Checkpoint: Submission complete
- [x] Deadline hour confirmed (Task 38) and everything below landed before it
- [x] Golden path still holds live on Amplify after Task 39's fixes
- [ ] Demo video, writeup, and docs (Tasks 40–42) all committed
- [ ] Submission + registration both confirmed (Task 43)
