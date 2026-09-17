# Issue tracker: project task list (tasks/plan.md + tasks/todo.md)

Issues for this repo are pre-broken-down for the whole event, not filed one at a time.
Full task detail lives in `tasks/plan.md`; what's done is tracked in `tasks/todo.md`.
There's no per-feature directory like `.scratch/<feature>/` — one task list covers
Phase 0-4 / Day 1-4.

## Conventions

- Each task entry in `tasks/plan.md` carries: Description, Acceptance criteria
  (checkboxes), Verification (checkboxes), Dependencies (task numbers), Files likely
  touched, Estimated scope.
- `tasks/todo.md` is the single source of "what's checked off" — check a box there
  only after both the acceptance criteria and verification steps in `tasks/plan.md`
  are actually satisfied, then commit.
- Tasks are grouped by lane (Lane A — Backend/Agents, Lane B — Frontend/UX, Lane C —
  Floating; see `CLAUDE.md`). A session infers its lane from the task it's given.
- Day 2-4 are re-broken-down each morning stand-up (`BUILD_PLAN.md`) rather than
  planned upfront in full detail — treat those phase-level bullets in `tasks/todo.md`
  as milestone placeholders until that day's stand-up expands them into
  `tasks/plan.md`-style entries.

## When a skill says "publish to the issue tracker"

Add a new task entry to `tasks/plan.md` (Description/Acceptance/Verification/
Dependencies/Files/Scope) and a corresponding unchecked checkbox to `tasks/todo.md`
under the right Phase/Lane heading.

## When a skill says "fetch the relevant ticket"

Read that task's entry in `tasks/plan.md` by its `Task N` heading — don't read the
whole file (`CLAUDE.md` already says this).

## Blocking

A task's `Dependencies` line in `tasks/plan.md` names the task(s) it's blocked by
(e.g. "Dependencies: Task 1"). A task is unblocked once every task it depends on is
checked off in `tasks/todo.md`.

## Frontier

Scan `tasks/todo.md` for the next unchecked box in your lane whose `Dependencies`
(per `tasks/plan.md`) are already checked off.

## PRs as a request surface

Off. The repo has a GitHub remote, but work isn't routed through GitHub
Issues/PRs — this file, not GitHub, is what skills read. Edit this section if
that changes later.
