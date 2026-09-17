# Learning Log — Opportunity Engine

Kept from Day 1 per the event rules (learning is a scored judging criterion). One entry per day, added as it happens — not reconstructed from memory on Day 4.

## Day 1 — Sept 17, 2026

**Eligibility & registration**
- Confirmed both teammates meet the eligibility bar (university students in India, 18+) before any other work started.
- Registered and verified student status on WeMakeDevs and AWS Builder Center.
- *(Fill in: any friction hit during verification — e.g. delay between account creation and verification clearing, which step took longest. Whoever did this step knows the specifics; worth a line here since "learning demonstrated" is explicitly judged.)*

**AWS/Bedrock access**
- Confirmed Bedrock model access for both Claude Haiku 4.5 and Sonnet 4.6.
- *(Fill in: which region/inference profile ended up working, and whether the default one was blocked — this is exactly the kind of concrete technical learning judges want to see, and it's only known to whoever ran the check.)*

**Planning & tooling**
- Locked the two-person workflow before writing any product code: split by architectural layer (backend/agents vs. frontend/screens) rather than by day, with a third floating lane for the extra AI subscription — the PRD's own Part B already argues for a contracts-first split, so this wasn't a novel idea, just a deliberate decision to follow it rather than default to a day-based split.
- Writing `tasks/plan.md` before touching code surfaced a gap the PRD doesn't spell out: §15 names four API endpoints, but the five P0 screens need more than that (business profile, opportunity list, opportunity detail, execution pack aren't explicitly listed). Better to find that gap during planning than mid-Day-2 when the frontend is already blocked on it.
- Running `/graphify` on the whole repo (rather than scoping it) pulled in the vendored engineering-skill library twice over (`.agents/skills/` and `.claude/skills/`, same content) — 62 of 73 detected files were generic skill docs, not product content. Scoping the run to the 7 project-specific files was the actual lesson: a knowledge-graph tool is only as useful as the corpus you point it at.
- The `ponytail` plugin was enabled in project settings but didn't resolve through the Skill tool mid-session — a reminder that enabling a plugin and having it actually usable in the current session aren't the same event; worth checking early rather than assuming.

## Day 2 — Sept 18, 2026

*(Not yet written — add as the day happens.)*

## Day 3 — Sept 19, 2026

*(Not yet written.)*

## Day 4 — Sept 20, 2026

*(Not yet written.)*
