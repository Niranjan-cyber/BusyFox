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
- [x] Task 21: Orchestrator wiring — full pipeline end to end

### Lane B — Frontend/UX
- [~] Task 22: Screen 1 on real data — client wired to the contract routes and verified in a
  browser against the deployed stage; blockers 1 (retrieval-mode header) and 4 (CORS) resolved.
  Still **blocked** on 3 (real pipeline data behind the stage). See `frontend/README.md`,
  "Known blockers"
- [~] Task 23: Screen 3 on real data — inbox groups and ranks the live opportunity with its
  claims off `/opportunities/{id}/claims`; blockers 1 and 5 resolved. Still **blocked** on 2 (no
  rejected-candidate route, Task 19) and 3. See `frontend/README.md`, "Known blockers"

### Lane C — Floating
- [~] Task 24: Gold-set labelling (80 sim + 20 real, independent) — corpus built
  and blank sheets ready (`tasks/gold_set/labels_{niranjan,swarali}.csv`,
  `scripts/build_gold_set.py`). Still needs: both of you actually labelling
  independently, then reconciling into one agreed gold set.
- [ ] Task 25: Re-run `/graphify` before evening stand-up

### Checkpoint: End of Day 2
- [ ] ≥1 gate-passed opportunity visible in real inbox, claims traceable to evidence
- [ ] Risk watch: if Tavily unusable live, fall back to Level 2/3 rather than debug under pressure

## Phase 3 — Day 3 (re-break-down at Day 3 morning stand-up)

- [ ] Lane A: Action Agent + ExecutionPack w/ `outreach_policy` enforcement; value model; evidence drawer fallback rehearsed at least once; evaluation run vs. gold set
- [ ] Lane B: screens 2, 4, 5 feature-complete; Evidence Check diagram polish; devtools pass on all 5 screens
- [ ] Lane C: Anveshan Precision clip (if P0 done by 4pm); demo-video shot list started
- [ ] Everyone: code-review-and-quality + code-simplification + ponytail-review pass before 8pm

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
