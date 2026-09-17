# CLAUDE.md

Opportunity Engine — WeMakeDevs × AWS "First Commit" hackathon (Sept 17–20, 2026). This file is what a fresh session reads before touching anything. Everything here is a pointer or a guardrail; the actual spec, plan, and task state live in the files it points to — read those, don't ask the human to repeat them.

## Non-negotiable guardrails

Full detail: `AGENTS.md`. The four that end the project outright if violated, cached here because they're too expensive to relearn by re-reading:

- Repo history must fall inside 17–20 Sept 2026. No backdating, no pre-event scaffolding.
- No composite opportunity score, ever — evidence confidence, potential value, priority tier stay three separate fields.
- Research agents (Market, Feedback Pipeline, Competitor) emit `signals[]` only — the `opportunities[]` field must not exist in their output schema, not just be unused by convention.
- Every external source (Tavily, GitHub, HN, App Store, Product Hunt) is Live → Cached → Demo Fixture, labelled in the UI, never silently substituted.

## Starting a session to implement a task

1. Read `tasks/todo.md`. Find the next unchecked task in your lane (see below). `tasks/plan.md` has that task's full acceptance criteria, dependencies, and files touched — read only that task's entry, not the whole plan.
2. If the task references a PRD `§` section, read that section of `opportunity_engine_prd_v8.md` by its heading — search for the `§` number, never read the file end to end.
3. If `graphify-out/graph.json` exists, treat any "how does X relate to Y" or "what touches this entity" question as a graphify query first (`graphify query "<question>"`) instead of grepping across files by hand.
4. Route to a skill by task type, not by habit — the phase table lives in `.agents/skills/using-agent-skills/SKILL.md`. The spec and plan already exist, so a task almost never starts at `spec-driven-development`; it starts at `incremental-implementation`, `test-driven-development` (Evidence Check, Quality Gate — these are code, not agents), or `api-and-interface-design` (contract work).
5. Write the task. Ponytail discipline applies by default (`ponytail@ponytail` is enabled in `.claude/settings.json`): reuse before writing, stdlib before a dependency, no abstraction for one caller. If the `Skill` tool doesn't resolve `ponytail` by name, apply its rules from `~/.claude/plugins/cache/ponytail/ponytail/*/skills/ponytail/SKILL.md` directly rather than skipping the discipline.
6. Check the task off in `tasks/todo.md` and commit — small, same-day commits, not a batched dump. This repo's commit history is itself a submission artifact.
7. If anything non-obvious was learned doing the task (a tool's real failure mode, a gap the PRD didn't cover, a decision that could've gone the other way), add one line to today's section of `LEARNING.md`. Not every task needs an entry — most don't.

## Lanes

Contracts-first split, unchanged for all four days — see `tasks/plan.md` for the full breakdown:

| Lane | Owns |
|---|---|
| A — Backend/Agents | Data acquisition, PulseStack, research agents, Synthesis, Evidence Check, Quality Gate, DynamoDB, Step Functions/Lambda, AWS deploy (PRD §7–§14, §17) |
| B — Frontend/UX | The five P0 screens, evidence drawer, Amplify Hosting, design system (PRD §16) |
| C — Floating | Whichever lane isn't blocked: simulator, gold-set labelling, infra scaffolding, eval harness, docs, demo-video prep |

A session infers its lane from the task it's given, not from who's typing — if a task could plausibly belong to either lane, ask before starting rather than guessing.

## Contract (once Task 1/2 land)

Entity + API contract lives in `backend/schemas/`, `frontend/src/types/`, and `docs/contract.md` (human-readable mirror). Code is the source of truth; if `docs/contract.md` and the code ever disagree, the code wins and the doc needs fixing, not the reverse.

## Definition of done

Matches `tasks/plan.md`'s per-task verification steps. Project-wide, on top of that: no P1/P2 work starts while any P0 item is incomplete (hard rule, not a suggestion — see `BUILD_PLAN.md`), and nothing after Day 3, 8pm feature freeze except bug fixes.

## Agent skills

### Issue tracker

Issues are pre-broken-down tasks tracked in `tasks/plan.md` (detail) and `tasks/todo.md` (checkboxes, by Lane A/B/C). See `docs/agents/issue-tracker.md`.

### Triage labels

Default five canonical role labels, unchanged. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context layout (no `CONTEXT.md`/ADRs yet; created lazily by `/domain-modeling`). See `docs/agents/domain.md`.
