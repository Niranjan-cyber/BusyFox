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
- [ ] Task 6: Skeleton AWS deploy (Amplify + API Gateway + Step Functions + stub Lambda) — IaC written, live deploy pending AWS credentials

### Lane B — Frontend/UX
- [ ] Task 7: React app scaffold + Amplify Hosting pipeline
- [ ] Task 8: Design tokens via `frontend-design` skill, committed as a theme file
- [ ] Task 9: Screen 1 & 3 shells on fixture data, using Task 8's theme

### Lane C — Floating
- [ ] Task 10: PulseStack simulator (scenario + generator + seed), `Signal`/`Evidence`-shaped output
- [ ] Task 11: App Store RSS fetch (one competitor) + Product Hunt token registered
- [ ] Task 12: LEARNING.md — first real entry

### Checkpoint: End of Day 1
- [ ] Real, visible commits across the day
- [ ] GitHub + HN collectors return real signals
- [ ] Tavily failure modes known
- [ ] Simulator committed with its seed
- [ ] Skeleton deployed, live Amplify URL reachable
- [ ] Screens 1 & 3 render fixture data through committed theme
- [ ] LEARNING.md has a real entry

## Phase 2 — Day 2 (re-break-down at Day 2 morning stand-up)

- [ ] Lane A: feedback/competitor pipeline; Market/Feedback/Competitor agents under runtime contract; Synthesis Agent w/ mechanism statement; Evidence Check; Quality Gate + Ranker; DynamoDB writes
- [ ] Lane B: Screens 1 & 3 on real data
- [ ] Lane C: gold-set labelling (80 sim + 20 real); re-run `/graphify` before evening stand-up

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
