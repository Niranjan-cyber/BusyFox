# Learning Log — Opportunity Engine

Kept from Day 1 per the event rules (learning is a scored judging criterion). One entry per day, added as it happens — not reconstructed from memory on Day 4.

## Day 1 — Sept 17, 2026

**Eligibility & registration**
- Confirmed both teammates meet the eligibility bar (university students in India, 18+) before any other work started.
- Registered and verified student status on WeMakeDevs and AWS Builder Center.
- *(Fill in: any friction hit during verification — e.g. delay between account creation and verification clearing, which step took longest. Whoever did this step knows the specifics; worth a line here since "learning demonstrated" is explicitly judged.)*

**AWS/Bedrock access**
- Confirmed Bedrock model access for both Claude Haiku 4.5 and Sonnet 4.6, in `eu-north-1` — that's the region the account's IAM Identity Center (SSO) permission set defaults to, so it's also the region the Task 6 skeleton deployed into. Both models showed "Access granted" on the first check, no request/approval wait.

**Planning & tooling**
- Locked the two-person workflow before writing any product code: split by architectural layer (backend/agents vs. frontend/screens) rather than by day, with a third floating lane for the extra AI subscription — the PRD's own Part B already argues for a contracts-first split, so this wasn't a novel idea, just a deliberate decision to follow it rather than default to a day-based split.
- Writing `tasks/plan.md` before touching code surfaced a gap the PRD doesn't spell out: §15 names four API endpoints, but the five P0 screens need more than that (business profile, opportunity list, opportunity detail, execution pack aren't explicitly listed). Better to find that gap during planning than mid-Day-2 when the frontend is already blocked on it.
- Running `/graphify` on the whole repo (rather than scoping it) pulled in the vendored engineering-skill library twice over (`.agents/skills/` and `.claude/skills/`, same content) — 62 of 73 detected files were generic skill docs, not product content. Scoping the run to the 7 project-specific files was the actual lesson: a knowledge-graph tool is only as useful as the corpus you point it at.
- The `ponytail` plugin was enabled in project settings but didn't resolve through the Skill tool mid-session — a reminder that enabling a plugin and having it actually usable in the current session aren't the same event; worth checking early rather than assuming.

**Collectors (Tasks 3–4)**
- The GitHub collector gets `Signal.polarity` for free from the API shape (release = positive, open issue = negative). HN Algolia's `/search` response has no equivalent structural split — a story surfacing is just a story, no sentiment field. Rather than inventing a title-keyword classifier to fake a pain/praise split, the HN collector marks every hit POSITIVE (attention on the query) and leaves sentiment splitting to a later pass, flagged with a `ponytail:` comment. Could've gone the other way; recording why it didn't.

**Tavily live round-trip (Task 5)**
- Clean search+extract on two different queries (a normal one, a gibberish one) both succeeded — Tavily's search doesn't return `empty_results` even for nonsense input (`"xqzplonkfribbet zzyx nonsense query 928471"` still returned 5 results); an empty-results failure mode may be rare enough that we can't assume the demo will ever hit it live.
- A bad API key surfaces as `http_error:search:401`, confirming `probe()`'s HTTP-error branch is reachable and correctly labelled.
- Extract on a URL Tavily can't fetch (tried a PDF) doesn't come back as an HTTP error — it's a 200 with `results: []` and a separate `failed_results: [...]` list carrying the reason. `probe()`'s existing `if not extracted` check already catches this correctly as `malformed_extract`, but it's worth flagging: a naive implementation checking only for an HTTP error would have missed this failure shape entirely.
- Net: of the three named failure modes (empty results, timeout, malformed extract), two are confirmed reachable and correctly handled; timeout wasn't triggered live (not something we can force on demand) but the code path (`urllib.error.URLError`/`TimeoutError`) is exercised by existing unit tests with a fake `post`.

**Skeleton AWS deploy (Task 6)**
- The first live deploy returned `500 Internal Server Error` on every route. Root cause: every handler imports as `from backend.X import Y` (matching how the pytest suite runs, from repo root), but the SAM template had `CodeUri: ../backend/`, which deploys `backend/`'s *contents* as the Lambda's own root — so `backend` wasn't an importable package at runtime for any of the 9 functions. Fixed by pointing `CodeUri` at the repo root and prefixing every `Handler:` with `backend.` instead, which also needed a root-level `requirements.txt` (`-r backend/requirements.txt`) so `sam build`'s pip step still finds the dependency list, and a `.samignore` so the wider `CodeUri` doesn't try to bundle `.git`/`graphify-out`/etc. into every function's package. Same class of bug the GitHub Actions "works on my machine" trap is — local pytest and the deployed Lambda need the *same* package root, and nothing catches that mismatch until a real deploy.
- SAM's `sam build` and `sam deploy` are on PATH for the account that ran `pip install aws-sam-cli`, but `aws` (installed via winget) needed a fresh terminal before PowerShell/bash picked it up on PATH — the wizard's own note about this ("reopen this terminal") was necessary, not boilerplate caution.
- Used AWS SSO (`aws configure sso`), not long-lived access keys — `~/.aws/config` ends up with a named profile (e.g. `AdministratorAccess-<account-id>`), and the plain `aws` command with no `--profile` flag fails with `NoCredentials` even after a successful SSO login, since `[default]` in that file has no credential source. Every AWS CLI/SAM call after setup needs `--profile <name>` or `$env:AWS_PROFILE` set.
- A first `sam deploy` run under a mistyped/truncated stack name (`busfox-ske`) left a stray, broken CloudFormation stack once the real one (`opportunity-engine-skeleton`) deployed correctly — cleaned up with `aws cloudformation delete-stack`. Worth double-checking the stack name at the `sam deploy --guided` prompt rather than typing fast.

**PulseStack simulator (Task 10)**
- PRD §8.1's scenario format mixes lines the simulator should generate itself with lines tagged `(real)` that live collectors (GitHub/HN/Tavily) are expected to find independently, inside the *same* `generator_effects` list for one planted truth. Missing that tag would have double-counted signals for the same opportunity (one simulated, one live) once Lane A's pipeline runs both feeds together — worth flagging since it's easy to read the scenario as "everything here is ours to generate."
- Wrote the scenario as JSON instead of the PRD's YAML sample — stdlib `json` covers a static data file with no new dependency (`pyyaml`), and nothing about the format is load-bearing for judging.

## Day 2 — Sept 18, 2026

**Contract lock (Tasks 1–2)**
- Building the endpoint table for Task 2 surfaced a second, more precise version of the Day-1 gap note: Task 2's own acceptance criteria name screens 1, 3, 4, 5 but not screen 2 (Live investigation) — on inspection that's not an oversight, it's because screen 2 is a streaming view over Run/Signal events, not a list/detail REST shape, so it doesn't belong in a stub-Lambda contract at all. Recorded that exclusion explicitly in `docs/contract.md` rather than silently building an endpoint nobody asked for.
- `Evidence.retrieval_mode` (§12) only has two values, `cached`/`live` — but the resilience ladder in §7.2/§12.2 is three-tier (Live → Cached → Demo Fixture). The third tier isn't a schema field yet; it looks like it belongs on the live-refetch endpoint's response envelope, not the core Evidence entity, but that's a Task 5/evidence-drawer decision, not a Task 1 one. Flagged in `backend/handlers/competitors_stub.py` rather than guessed at now.
- No AWS deployment exists yet (that's Task 6), so Task 2's "curl every stubbed route" verification doesn't literally apply. Invoking each Lambda handler function directly with a fake API Gateway event and validating the response against the Task 1 Pydantic model is the equivalent check pre-deploy — the handler *is* the whole implementation on either side of the API Gateway boundary, so this isn't a weaker test, just an earlier one.

## Day 3 — Sept 19, 2026

*(Not yet written.)*

## Day 4 — Sept 20, 2026

*(Not yet written.)*
