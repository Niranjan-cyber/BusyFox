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

**Collectors (Tasks 3–4)**
- The GitHub collector gets `Signal.polarity` for free from the API shape (release = positive, open issue = negative). HN Algolia's `/search` response has no equivalent structural split — a story surfacing is just a story, no sentiment field. Rather than inventing a title-keyword classifier to fake a pain/praise split, the HN collector marks every hit POSITIVE (attention on the query) and leaves sentiment splitting to a later pass, flagged with a `ponytail:` comment. Could've gone the other way; recording why it didn't.

## Day 2 — Sept 18, 2026

**Contract lock (Tasks 1–2)**
- Building the endpoint table for Task 2 surfaced a second, more precise version of the Day-1 gap note: Task 2's own acceptance criteria name screens 1, 3, 4, 5 but not screen 2 (Live investigation) — on inspection that's not an oversight, it's because screen 2 is a streaming view over Run/Signal events, not a list/detail REST shape, so it doesn't belong in a stub-Lambda contract at all. Recorded that exclusion explicitly in `docs/contract.md` rather than silently building an endpoint nobody asked for.
- `Evidence.retrieval_mode` (§12) only has two values, `cached`/`live` — but the resilience ladder in §7.2/§12.2 is three-tier (Live → Cached → Demo Fixture). The third tier isn't a schema field yet; it looks like it belongs on the live-refetch endpoint's response envelope, not the core Evidence entity, but that's a Task 5/evidence-drawer decision, not a Task 1 one. Flagged in `backend/handlers/competitors_stub.py` rather than guessed at now.
- No AWS deployment exists yet (that's Task 6), so Task 2's "curl every stubbed route" verification doesn't literally apply. Invoking each Lambda handler function directly with a fake API Gateway event and validating the response against the Task 1 Pydantic model is the equivalent check pre-deploy — the handler *is* the whole implementation on either side of the API Gateway boundary, so this isn't a weaker test, just an earlier one.

## Day 3 — Sept 19, 2026

*(Not yet written.)*

## Day 4 — Sept 20, 2026

*(Not yet written.)*
