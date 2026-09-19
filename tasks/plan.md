# Implementation Plan: Opportunity Engine — Day 1 (remainder) → Day 4

## Overview

Eligibility, registrations, repo creation and Bedrock access confirmation (BUILD_PLAN.md Day 1, steps 1–4) are done. What's left before any lane can build independently is a locked contract — the nine core entities (PRD §14) and the API surface (PRD §15) — because every screen and every agent output shape depends on it. This plan sequences the remaining Day 1 work as a blocking contract phase followed by three parallel lanes, then gives Day 2–4 as milestone-level phases to be re-broken-down each morning once the prior day's actual state is known.

## Architecture decisions (already locked — do not relitigate)

See `AGENTS.md` for the full list. The ones that constrain this plan directly:

- Agents: Bedrock via Strands Agents SDK, in Lambda; Step Functions orchestrates. Frontend: React on Amplify Hosting. State: DynamoDB + S3.
- Research agents (Market, Feedback Pipeline, Competitor) are schema-limited to `signals[]` — no `opportunities` field exists for them to fill. Only Synthesis emits `candidate_opportunities[]`.
- Evidence Check and Quality Gate are code, not agents. No composite score — evidence confidence, potential value and priority tier stay three separate fields.
- Every external source uses Live → Cached → Demo Fixture, each labelled in the UI.

## Dependency graph

```
Core entities (§14) ── shared schema (Pydantic + TS types)
      │
      ├── API contract (§15) ── stub Lambda handlers (fixture data) ── frontend API client
      │         │                                                            │
      │         │                                                            └── Screen shells (1 & 3)
      │         │
      │         └── DynamoDB table design (keys: OPP#, etc.)
      │
      └── PulseStack simulator output shape (must match Signal/Evidence schema)
                │
                └── GitHub / HN / Tavily collectors (must emit the same Signal shape)
```

Nothing below "Core entities" can be built with confidence until that box is committed. That's why Tasks 1–2 are the only strictly sequential, all-hands work in this plan — everything after is parallel by lane.

## Task List

### Phase 0: Contract lock (blocking — both people, same session)

#### Task 1: Core entity schema (the nine entities + provenance chain)

**Description:** Encode Business, Competitor, Run, SourceDocument, Evidence, Claim, Signal, Opportunity, Target/Account, and ExecutionPack (PRD §14.1–14.10) as a shared schema both lanes read from — Pydantic models for the backend, generated or hand-mirrored TypeScript types for the frontend. Include the `OPP#`-style key prefixes and the Observed/Inferred/Assumed label as a shared enum, since it's applied everywhere a claim reaches the UI (§13.3).

**Acceptance criteria:**
- [x] All nine entities from §14 exist as Pydantic models with every field named in the PRD, including `evidence_diversity`, `opportunity_mechanism`, and the runtime-contract fields on Run (§14.3)
- [x] Matching TypeScript interfaces exist for the frontend, field-for-field
- [x] Research-agent output types have no `opportunities` field anywhere in their schema (§10.1a) — this must be true structurally, not by convention
- [x] Committed to the repo, not left in chat/notes

**Verification:**
- [ ] Both people read the committed file together before moving on — this is the one artifact where a silent misunderstanding costs a full day later
- [x] Manual check: pick one entity (e.g. Opportunity) and trace it against §14.8 line by line — done programmatically, see `backend/tests/test_stub_handlers.py` round-trip validation against the PRD's worked `opp_001` example

**Dependencies:** None

**Files likely touched:**
- `backend/schemas/entities.py` (or equivalent per your chosen structure)
- `frontend/src/types/entities.ts`
- `docs/contract.md` (human-readable mirror, linked from both)

**Estimated scope:** Medium

---

#### Task 2: API surface for the five P0 screens

**Description:** Define the request/response shape for every endpoint the five P0 screens need (§15, plus the implied list/detail endpoints for screens 1, 3, 4, 5), using Task 1's entities as the payload types. Stub each as a Lambda handler returning fixture data — not real logic yet, just the shape, so the frontend can build against it today.

**Acceptance criteria:**
- [x] Every endpoint in §15 is listed with method, path, request, response
- [x] Additionally listed: whatever GET endpoints screens 1, 3, 4, 5 need that §15 doesn't spell out (business profile, opportunity list, opportunity detail, execution pack) — the PRD names four explicit endpoints but the screens need more; make the gap explicit rather than discovering it mid-Day-2
- [x] Each stub Lambda returns a fixture payload matching Task 1's types exactly
- [x] API Gateway routes exist (even if pointing at stub Lambdas) so the frontend can hit real URLs, not mocks — `infra/api-gateway.yaml` (SAM template); real deploy is Task 6

**Verification:**
- [x] `curl` or Postman hits every stubbed route and gets a Task-1-shaped response back — no live deploy yet (Task 6), so verified as `backend/tests/test_stub_handlers.py`: invokes every handler directly and validates the response body against its Task-1 model
- [ ] Frontend dev confirms they can build screen 1 and 3 against these stubs without asking backend anything

**Dependencies:** Task 1

**Files likely touched:**
- `infra/api-gateway.*` (routes)
- `backend/handlers/*_stub.py`
- `docs/contract.md` (extended with endpoint table)

**Estimated scope:** Medium

### Checkpoint: Contract locked
- [x] Tasks 1–2 committed
- [ ] Both people can point at the same file and agree it's the source of truth
- [ ] Lanes below start only after this checkpoint

---

### Phase 1: Day 1 remainder (parallel by lane)

#### Lane A — Backend/Agents

**Task 3 — GitHub REST collector.** Fetch repo/release/issue activity for a named competitor; emit output in the Task-1 `Signal` shape. *(Small, 1–2 files, depends on Task 1)*

**Task 4 — HN Algolia collector.** Search HN for a competitor/topic; emit `Signal`-shaped output. *(Small, depends on Task 1)*

**Task 5 — One live Tavily round-trip.** Single search+extract call against a real query; log latency and every observed failure mode (empty results, timeout, malformed extract) — this is the PRD's named top technical risk (§7.2), so the goal today is characterizing how it fails, not just proving it can succeed once. *(Small, depends on Task 1)*

**Task 6 — Skeleton AWS deploy.** Amplify Hosting + API Gateway (from Task 2) + Step Functions + one stub Lambda wired end to end, so "deployed on Day 1" is true. *(Medium, depends on Task 2)*

#### Lane B — Frontend/UX

**Task 7 — React app scaffold + Amplify Hosting pipeline.** Deploys on push, even showing a placeholder. *(Small)*

**Task 8 — Design tokens.** Run the `frontend-design` skill once; commit the resulting palette/type/layout tokens as a theme file all five screens will import. *(Small, no dependency — can start immediately, in parallel with Task 1–2)*

**Task 9 — Screen 1 & 3 shells.** Business & Feedback and Opportunity Inbox, wired to Task 2's stub endpoints, rendering fixture data through Task 8's theme. *(Medium, depends on Tasks 2 and 8)*

#### Lane C — Floating

**Task 10 — PulseStack simulator.** Scenario file, generator, fixed seed; output must already match Task 1's `Signal`/`Evidence` shape so Lane A doesn't have to reconcile it later. *(Medium, depends on Task 1)*

**Task 11 — App Store RSS fetch + Product Hunt token.** One real competitor's RSS feed parsed; PH developer token registered. *(Small, P1-priority — do this only after Task 10 or if a person is free before Lane A needs help)*

**Task 12 — Start LEARNING.md.** First real entry (not a placeholder) — required from Day 1, scored criterion. *(XS)*

### Checkpoint: End of Day 1
- [ ] Repo has real, visible commits across the day (not one dump)
- [ ] GitHub + HN collectors return real signals
- [ ] One Tavily round-trip's failure modes are known, not assumed
- [ ] Simulator committed with its seed
- [ ] Skeleton deployed and reachable at a live Amplify URL
- [ ] Design tokens committed; screens 1 & 3 render fixture data through them
- [ ] LEARNING.md has a real entry

---

### Phase 2: Day 2 (parallel by lane, broken down at Day 2 morning stand-up)

Goal per BUILD_PLAN.md: a full run produces ≥1 gate-passed opportunity, visible in a real inbox, with claims traceable to evidence. Broken down below now that Day 1's actual contract, collector output and merged frontend state are known.

#### Lane A — Backend/Agents

**Task 13 — Feedback pipeline: normalise → dedupe → redact → spam filter.** Pure code, no LLM call — takes PulseStack's simulated/uploaded feedback and runs it through the first four §9 pipeline stages. Testable without any Bedrock call, so it lands before Task 14 adds one. *(Medium, depends on Tasks 1, 10)*

**Task 14 — Feedback pipeline: label → validate → aggregate → balance.** Adds the Haiku structured-output labeller against the §9.1 taxonomy (aspect/polarity/intents/segment_hints), span+schema validation with one retry, theme aggregation against the §9.2 thresholds, and the §9.3 sentiment-balance check. Completes the "Feedback Pipeline" component (§10.1 #3). *(Medium, depends on Task 13)*

**Task 15 — Market Agent.** Strands agent (Haiku) over web/HN/GitHub producing claim-level, count/date/source-anchored signals (§9.4) — a generic market claim (e.g. "the market is growing") fails schema validation and is dropped as `rejected_generic_market_claim`, never reaching Synthesis. Bound by the §10.1a runtime contract; output is structurally `signals[]`-only. *(Medium, depends on Tasks 1, 3, 4, 5)*

**Task 16 — Competitor Agent.** Strands agent (Haiku) identifying relevant named competitors and their public signals (web/HN/GitHub P0, App Store/Product Hunt enrichment where available), same runtime contract and `signals[]`-only shape as Task 15. *(Medium, depends on Tasks 1, 3, 4, 11)*

**Task 17 — Synthesis Agent.** Strands agent (Sonnet) combining signals via the §9.3 pattern table into `candidate_opportunities[]`, with a mandatory `opportunity_mechanism` statement (§9.5) and rubric self-critique. The only component allowed to emit opportunities, and only from already-collected signals — never raw research (§10.3). *(Medium, depends on Tasks 14, 15, 16)*

**Task 18 — Evidence Check.** Code, plus one lightweight model call for semantic claim support (§12.1): quote-exists, quote-supports-claim, freshness against the §11.4 per-type limits, contradiction detection. Populates `Evidence.claim_support` and `Evidence.freshness` exactly as shaped in §12. *(Medium, depends on Task 17)*

**Task 19 — Quality Gate + Ranker.** Code implementing all 14 checks across the four §11 stages (truth, relevance — including the computed `evidence_diversity` object, not a single heuristic — commerciality, quality/safety). Derives confidence and priority from the rule table only, never a composite score. Rejected candidates are stored with their reason and failed-gate stage, for "Ideas we rejected" (frontend's `RejectedIdea` — see `frontend/src/lib/viewModels.ts` and today's `LEARNING.md` entry on why that's not a canonical entity yet). *(Medium, depends on Task 18)*

**Task 20 — DynamoDB table design + writes.** Table(s) keyed on the Task 1 prefixes (`BIZ#`, `RUN#`, `OPP#`, etc., §17.2) for every core entity: Business, Run, SourceDocument, Evidence, Claim, Signal, Opportunity, Target, ExecutionPack. *(Medium, depends on Task 1; can start in parallel with Tasks 13–19)*

**Task 21 — Orchestrator wiring.** Step Functions runs Market/Feedback/Competitor in parallel → S3 → Synthesis → Evidence Check → Quality Gate + Ranker → DynamoDB, replacing Task 6's single stub Lambda with the real graph (§17.1). A full run produces at least one gate-passed opportunity end to end — this is the Day 2 goal, made real. *(Large, depends on Tasks 15–20)*

#### Lane B — Frontend/UX

**Task 22 — Screen 1 on real data.** Point `fetchBusiness`/`fetchFeedbackSignals` (`frontend/src/api/client.ts`) at the real API Gateway routes once Task 20/21 exposes real rows; confirm the Live/Cached/Demo Fixture banner reflects what actually happened on that request rather than always reading `demo_fixture`. *(Medium, depends on Task 20 or 21, whichever exposes real business/signal data first)*

**Task 23 — Screen 3 on real data.** Same treatment for `fetchOpportunities`/`fetchClaims`; confirm "Ideas we rejected" renders Task 19's real rejected-candidate output instead of the empty stub (`fetchRejectedIdeas` currently always resolves `[]`), and that the inbox groups/ranks real gate-passed opportunities correctly. *(Medium, depends on Tasks 19, 20/21)*

#### Lane C — Floating

**Task 24 — Gold-set labelling.** 80 simulated feedback items (balanced positive/negative/mixed) + 20 real competitor snippets, labelled independently by both teammates against the §9.1 taxonomy before either sees the other's labels — this is what the §19.2 label-F1 (≥ 0.75 macro) target gets measured against. *(Medium, depends on Task 10 for the simulated half)*

**Task 25 — Re-run `/graphify`.** Against the day's actual codebase, scoped to the project-specific files rather than the whole tree — Day 1's `LEARNING.md` entry already flagged that an unscoped run pulls in the vendored skill library twice over. Run before the evening stand-up. *(XS)*

### Checkpoint: End of Day 2
- [ ] A full run produces at least one gate-passed opportunity
- [ ] Visible in the real inbox screen
- [ ] Claims traceable to evidence
- [ ] Named risk watch: if Tavily is returning nothing usable under real conditions, fall back to Level 2/3 rather than debugging search quality under time pressure

---

### Phase 3: Day 3 — broken down at the Day 3 morning stand-up (2026-09-19)

Goal: opportunity-to-action works end to end; feature freeze at 8pm. Nothing here starts before Day 2's checkpoint items land (it did, minus the Tavily fallback rehearsal — see Task 28, which absorbs that unfinished item rather than duplicating it).

#### Lane A — Backend/Agents

##### Task 26: Action Agent + ExecutionPack generation

**Description:** New `backend/agents/action_agent.py` (Strands, Sonnet), same shape as `synthesis_agent.py`: a live-agent path plus a pure `build_execution_pack`-style function tests can call directly. Takes one gate-passed `Opportunity` (ranked or blocked) and produces an `ExecutionPack` (offer, proposal, `outreach_drafts[]`) per §14.10/§18. `outreach_policy` (`never_reveal_surveillance_source`, `never_quote_private_or_sensitive_information`, `use_public_evidence_only_as_internal_reasoning`) is enforced twice: stated in the system prompt, and checked again after generation (keyword/regex scan for leaked source language) — belt-and-suspenders per §18.1, matching how Synthesis's `mechanism_holds` is both asked-for and independently re-checked. Each `OutreachDraft` must set `proof_point_signal_id` and `outreach_policy_checked=true` only after the post-generation check actually passes.

**Acceptance criteria:**
- [ ] `run_action_agent`/`build_execution_pack` produces a real `ExecutionPack` from a real `Opportunity` (no hardcoded fixture)
- [ ] A draft that would leak `never_reveal_surveillance_source` language is caught by the post-generation check and rejected/retried, not just relied on the prompt
- [ ] `GET /opportunities/{id}/execution-pack` (already routed to `opportunities_stub.get_execution_pack`, currently fixture-only) returns a real, persisted pack for `opp_run_7f023794a99d_0`

**Verification:**
- [ ] Unit tests: `backend/tests/test_action_agent.py` (new), same fake-collector pattern as `test_synthesis_agent.py`
- [ ] Manual check: run against the live opportunity persisted 2026-09-19, confirm the pack shows up via the deployed API with `X-Retrieval-Mode: live`

**Dependencies:** Task 21 (orchestrator; a real Opportunity to act on already exists)

**Files likely touched:** `backend/agents/action_agent.py`, `backend/handlers/opportunities_stub.py`, `backend/orchestrator.py` (persist the pack), `backend/tests/test_action_agent.py`

**Estimated scope:** Medium

##### Task 27: Real value model computation

**Description:** Replace Synthesis's placeholder `ValueModel` (`monthly_usd=0.0/0.0`, assumption `pending_quality_gate`) with §13.2's actual formula: `estimated_monthly_value = estimated_qualified_accounts × expected_conversion × ARPA`, each variable labelled `OBSERVED`/`INFERRED`/`ASSUMED` per `ValueAssumption`, always rendered as a `MonthlyRange` (low/high), never a single point number. Runs as part of Quality Gate + Ranker (Task 19's module), not Synthesis — Synthesis still shouldn't claim a real number before the gate has verified evidence.

**Acceptance criteria:**
- [ ] `run_quality_gate` (or a new function it calls) replaces the placeholder `ValueModel` on every surviving `Opportunity` with a real range and per-variable assumption labels
- [ ] At least one assumption is `OBSERVED` when business pricing data is available (`Business.current_mrr_usd` etc. already on the schema), `ASSUMED` otherwise — never silently defaulting to a made-up number with no label
- [ ] No composite score anywhere near this — value stays a separate field from priority/confidence (AGENTS.md hard rule)

**Verification:**
- [ ] Unit tests in `backend/tests/test_quality_gate.py`: assert the range and assumption labels for a known input
- [ ] Manual check: confirm `opp_run_7f023794a99d_0`'s persisted `value` field is no longer the placeholder after a fresh pipeline run

**Dependencies:** None (Quality Gate already exists; this extends it)

**Files likely touched:** `backend/pipeline/quality_gate.py`, `backend/tests/test_quality_gate.py`

**Estimated scope:** Small–Medium

##### Task 28: Evidence drawer Level 2 (Cached) fallback — closes out Day 2's unfinished risk-watch item

**Description:** The resilience ladder (§7.2/§12.2) only has two of its three levels implemented — every handler returns `LIVE` or `DEMO_FIXTURE`, `CACHED` doesn't exist anywhere (confirmed by grep 2026-09-19). Build the missing middle level: an S3-backed cache of prior live evidence fetches, checked before falling all the way to the fixture. `GET /competitors/{id}/evidence/{evidenceId}/live` (already routed, currently fixture-only) tries live → falls back to the S3 cache if the live call fails → falls back to the fixture if the cache is also empty, each labelled exactly per §7.2 ("LIVE RESEARCH" / "CACHED VERIFIED SOURCE · collected earlier in this run" / "DEMO FIXTURE · pre-collected and verified, not this run's live search"). This *is* the Day 2 checkpoint's unfinished "Tavily risk watch" item — don't track it twice.

**Acceptance criteria:**
- [x] `CACHED` is a real, reachable `RetrievalMode` for at least the evidence-drawer live-refetch path
- [x] The fallback is **rehearsed at least once with a real forced failure** (e.g. a bad Tavily key or a deliberately broken endpoint), not just unit-tested — screenshot or note the result
- [x] UI label text matches §7.2's exact three strings, word for word

**Verification:**
- [x] Unit tests: cache-hit, cache-miss-falls-to-fixture, live-succeeds-skips-cache
- [x] Manual rehearsal: force a live failure against the deployed stack, confirm the drawer shows `CACHED` or `DEMO FIXTURE` correctly instead of erroring

**Dependencies:** Task 20 (DynamoDB/S3 wiring), Task 5 (Tavily failure modes already characterized)

**Files likely touched:** `backend/handlers/competitors_stub.py`, new `backend/db/evidence_cache.py` (S3), `infra/api-gateway.yaml` (S3 permissions), `frontend/src/lib/viewModels.ts` (label strings)

**Estimated scope:** Medium

##### Task 29: Evaluation run against the gold set — blocked

**Description:** §19.2's Label F1 metric needs Task 24's gold set, which is deferred (P1, per 2026-09-19 decision — not required before Day 3's P0 work). This task is a placeholder, not active work: do not start it before Task 24 unblocks. If Day 3's P0 (Tasks 26–28, 30–33) lands well before 8pm, revisit deferring Task 24 first.

**Acceptance criteria:** N/A while blocked.

**Dependencies:** Task 24 (deferred)

**Estimated scope:** N/A — blocked

#### Lane B — Frontend/UX

##### Task 30: Screen 2 — Live investigation

**Description:** Per §16.1: three streaming research lanes (Market / Feedback / Competitive) showing signals arriving in real time, feeding into candidate opportunity cards as Synthesis produces them. Greenfield — only Screens 1 (`Business`) and 3 (`Inbox`) exist today.

**Acceptance criteria:**
- [ ] Three visually distinct lanes, each showing its own signals as they arrive (poll or stream — polling is fine for a hackathon demo, don't build websockets for this)
- [ ] Uses Task 8's theme, consistent with Screens 1 & 3
- [ ] Retrieval-mode labelling (§7.2 exact strings) shown per signal, not just per screen

**Verification:**
- [ ] Component tests alongside existing `frontend/src/screens/*` test pattern
- [ ] Manual check in a browser against the deployed stage with a real run in flight

**Dependencies:** Task 9 (screen-shell pattern), Task 22 (live data wiring already proven on Screens 1/3)

**Files likely touched:** `frontend/src/screens/Investigation/` (new), `frontend/src/lib/viewModels.ts`

**Estimated scope:** Medium

##### Task 31: Screen 4 — Opportunity detail + live Evidence Check diagram

**Description:** Per §16.1/§21: claims shown with their evidence, priority/confidence/value as three visually separate fields (never composited — AGENTS.md hard rule), evidence grouped by polarity and source diversity, editable value-model assumptions (Task 27), and the **live accept/reject Evidence Check diagram** — §21 names this the single best differentiator, "demonstrated not asserted." Real design attention here, not a placeholder chart.

**Acceptance criteria:**
- [ ] Every claim shows its `OBSERVED`/`INFERRED`/`ASSUMED` label (§13.3)
- [ ] Evidence confidence, potential value, priority render as three separate UI elements, never combined into one score
- [ ] The Evidence Check diagram actually animates/replays a real accept or reject decision from `run_evidence_check`'s output, not a static mock
- [ ] Value-model range (Task 27) is editable in the UI, assumptions visible

**Verification:**
- [ ] Component tests
- [ ] Manual check: load `opp_run_7f023794a99d_0`, confirm the diagram reflects its real evidence/claim data

**Dependencies:** Task 22/23 (live data wiring), Task 27 (real value model), Task 18 (Evidence Check output already exists)

**Files likely touched:** `frontend/src/screens/OpportunityDetail/` (new), evidence-diagram component (new)

**Estimated scope:** Large — if it doesn't split cleanly into diagram + rest-of-screen sub-tasks once started, split it then rather than build it as one sitting

##### Task 32: Screen 5 — Execution pack

**Description:** Per §16.1: offer, proposal, and outreach drafts, each outreach draft showing its cited `proof_point_signal_id` traceably. Can be built against the fixture first and re-pointed at Task 26's real data once that lands — don't block Screen 5 on Action Agent being finished if Lane A is still mid-task.

**Acceptance criteria:**
- [ ] Offer/proposal/outreach drafts all rendered, each outreach draft's proof point clickable back to its source signal
- [ ] Works against fixture data even before Task 26 is done; swaps to live data with no UI change once it is

**Verification:**
- [ ] Component tests against fixture data
- [ ] Manual check against Task 26's real pack once available

**Dependencies:** Task 9/22 pattern; Task 26 for real (not fixture) data

**Files likely touched:** `frontend/src/screens/ExecutionPack/` (new)

**Estimated scope:** Medium

##### Task 33: `browser-testing-with-devtools` pass, all five screens

**Description:** Once Screens 2/4/5 exist, run the devtools skill across all five P0 screens — console errors, network requests, visual output — not just the two that existed before today.

**Acceptance criteria:**
- [ ] All five screens pass with no console errors on the golden path
- [ ] Any real bugs found get fixed, not just logged

**Dependencies:** Tasks 30, 31, 32

**Estimated scope:** Small, but only after 30–32 land

#### Lane C — Floating

##### Task 34: Demo-video shot list

**Description:** Draft the shot list against §21's 10-scene table now, independent of P0 completion — the shot list is a planning artifact, not a recording. Flag scene 1:35–1:55 (the live Evidence Check diagram) as depending on Task 31.

**Acceptance criteria:**
- [ ] One shot per §21 scene, with which screen/state each needs
- [ ] Notes which shots are blocked on Lane A/B tasks above vs. already shootable

**Dependencies:** None to start; individual shots depend on 30–32

**Files likely touched:** `docs/demo-shot-list.md` (new)

**Estimated scope:** XS

##### Task 35: Anveshan Precision clip — conditional

**Description:** Only if all of Lane A/B's P0 tasks (26–28, 30–33) are done by 4pm. Do not start early at the cost of P0 work — CLAUDE.md's hard rule (no P1/P2 while P0 is open) applies here too.

**Dependencies:** Tasks 26–28, 30–33 all complete

**Estimated scope:** Small, conditional

#### Everyone, before 8pm

##### Task 36: Quality pass — `code-review-and-quality` + `code-simplification` + `ponytail-review`

**Description:** Across both lanes' Day 3 diffs, before feature freeze. Not a rewrite pass — findings get fixed if small, ticketed as Day 4 polish if not.

**Acceptance criteria:**
- [ ] All three passes run against today's diff
- [ ] Findings triaged: fixed now, or explicitly deferred to Day 4 with a one-line reason

**Dependencies:** Tasks 26–33 substantially done

**Estimated scope:** Medium (time-boxed — this must finish by 8pm, not run until it's perfect)

### Checkpoint: Feature freeze, Day 3, 8pm
- [ ] Golden path runs start to finish: goal → investigation → inbox → detail → execution pack
- [ ] No new features accepted after this point — bug fixes and rehearsal only

---

### Phase 4: Day 4 — milestone level

- [ ] Re-check the official schedule page for the actual submission deadline hour first thing
- [ ] Polish all five screens; fix Day 3 rehearsal bugs
- [ ] Record demo video ≤3:00 per §21's script, showing AWS visibly
- [ ] Write the writeup as a first-class deliverable (problem, build, AWS integration, AI tools used)
- [ ] Finalise README.md, CREDITS.md, LEARNING.md
- [ ] Submit; confirm registration before the deadline window closes

---

## Risks and mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Contract phase (Tasks 1–2) runs long and eats into Lane kickoff time | High — delays both lanes equally | Timebox it: if it's not done in ~90 minutes, lock what you have and treat gaps as fast-follow tasks rather than blocking further |
| Tavily fails in a way not yet characterized | High (named top risk, §7.2) | Task 5 exists specifically to surface failure modes today, not discover them on Day 3 |
| Lane B builds ahead of a contract field that changes later | Medium | Any change to Task 1/2's committed schema gets announced in the next stand-up before anyone assumes it's stable |
| Simulator output shape doesn't match what Lane A's pipeline expects | Medium | Task 10 explicitly depends on Task 1, not built independently |

## Open questions

- Exact submission deadline hour — unpublished as of Day 1 per PRD §22; re-check schedule page daily.
- Whether `docs/contract.md` or the code files themselves are the source of truth if they ever drift — recommend: code is truth, `docs/contract.md` is a generated/manually-synced mirror, checked at each stand-up.
