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

**App Store + Product Hunt collectors (Task 11)**
- Product Hunt's OAuth app-registration form silently rejects an `http://` redirect URI (`redirect_uri must be an HTTPS/SSL URI`), even though the redirect is never actually used for this read-only, no-browser-flow case — swapping to any syntactically valid `https://` placeholder was enough to create the app.
- The app's **Client Secret** is not a usable API token: sending it as `Authorization: Bearer <secret>` against the v2 GraphQL endpoint returns `401 invalid_oauth_token`. The account-scoped **Developer Token** shown separately on the same app page is the one that actually authenticates — easy to grab the wrong field since both are just opaque strings with no visual distinction.
- Both collectors (App Store RSS, Product Hunt GraphQL) were verified with one real live round-trip each against actual named-competitor data (Datadog reviews, Sentry launch comments) before being marked done — same "prove the failure/success shape once, live" standard as Task 5's Tavily probe, not just unit tests against a fake fetch.

## Day 2 — Sept 18, 2026

**Contract lock (Tasks 1–2)**
- Building the endpoint table for Task 2 surfaced a second, more precise version of the Day-1 gap note: Task 2's own acceptance criteria name screens 1, 3, 4, 5 but not screen 2 (Live investigation) — on inspection that's not an oversight, it's because screen 2 is a streaming view over Run/Signal events, not a list/detail REST shape, so it doesn't belong in a stub-Lambda contract at all. Recorded that exclusion explicitly in `docs/contract.md` rather than silently building an endpoint nobody asked for.
- `Evidence.retrieval_mode` (§12) only has two values, `cached`/`live` — but the resilience ladder in §7.2/§12.2 is three-tier (Live → Cached → Demo Fixture). The third tier isn't a schema field yet; it looks like it belongs on the live-refetch endpoint's response envelope, not the core Evidence entity, but that's a Task 5/evidence-drawer decision, not a Task 1 one. Flagged in `backend/handlers/competitors_stub.py` rather than guessed at now.
- No AWS deployment exists yet (that's Task 6), so Task 2's "curl every stubbed route" verification doesn't literally apply. Invoking each Lambda handler function directly with a fake API Gateway event and validating the response against the Task 1 Pydantic model is the equivalent check pre-deploy — the handler *is* the whole implementation on either side of the API Gateway boundary, so this isn't a weaker test, just an earlier one.

**Lane B — design tokens and screens 1 & 3**
- The brief's palette and WCAG AA disagree in one specific place, and it only showed up once
  the ratios were computed rather than eyeballed: `#456C6F` secondary text on the `#CBD5D4`
  page background is 3.9:1, under the 4.5:1 body-text bar. Fixed by adding one lighter tint of
  the same colour (`#E4EAE9`) as the card surface, which puts the same text at 4.75:1 without
  introducing a hue the brief didn't ask for. `#7EAEA6` as text on the light background is
  1.65:1 — unusable — so the accent is a fill colour on light and a text colour only on dark.
  The token names encode that (`--on-accent`, `--accent-on-dark`) so the failing pairing is
  hard to reach by accident, and the `#/tokens` page recomputes every pairing at load instead
  of trusting the numbers in the design doc.
- The PRD contradicts itself on goal coverage. §13.2 defines it as monthly value × 3 for the
  90-day horizon ÷ goal gap, but §1.3's inbox mock-up compares the monthly sums to the $15k
  MRR goal directly ($6.5k + $4.1k against $15k, no ×3). ×3 is also dimensionally odd, since
  the goal is itself a monthly rate. Built §1.3's version because that's the screen being
  rendered, and left the conflict named in `grouping.ts` rather than quietly picking a side —
  needs a ruling at stand-up.
- §13.1's priority rule table covers HIGH and LOW explicitly but never says which §1.3 section
  MEDIUM belongs to. Grouped it with LOW under "additional hypotheses (lower confidence)",
  since the alternative puts medium-confidence items under a heading that says
  "high-confidence". Also flagged in code rather than settled silently.
- Writing the "no composite score" guardrail as an actual test — asserting no rendered card
  carries a score-shaped field, and that every fixture priority matches the rule table — was
  cheap and caught nothing today, which is the point: it will catch it on Day 3 when someone
  is adding the detail screen at speed. The `signals[]`-only guarantee is enforced the same
  way, as a `@ts-expect-error` that fails the typecheck if the field ever becomes assignable.
- Checking the palette's contrast once, for the light background, was not enough. A review pass
  caught `#456C6F` used as text on the dark nav rail at 2.6:1 — the same colour that is fine on a
  card. The lesson was less "check contrast" than "check it per surface": a token that passes
  somewhere gets reused everywhere. The fix was a second derived step (`--on-slate-muted`) and,
  more usefully, moving the whole contrast table out of a doc and into `npm test`, where it
  parses `theme.css` and fails the build. The page that checks it in a browser only helps when
  somebody opens it.

**Merging Lane B onto the locked contract**
- Lane B's frontend branch was cut before Task 1 landed, so it carried its own hand-written
  `entities.ts` — and left an explicit comment flagging that it needed reconciling. The merge
  conflict on that one file was trivial (`git checkout --ours`); the real work was everything
  downstream that had been built against the invented shape (~60 type errors). Two of those
  turned out to be real contract gaps rather than UI inventions — `RetrievalMode` was missing
  `demo_fixture` even though it's a named guardrail, and `OpportunityType` was missing four
  playbook values its own comment already invited extending — so the canonical schema grew by
  two enums, not zero. Everything else (a `title`, a `fit` checklist, a `what_to_do` string, a
  numeric value-assumption breakdown, a `RejectedIdea` concept) had no source in the canonical
  entities at all; rather than inventing fields to make Lane B's screens compile, those became
  either derived view-model adapters (`frontend/src/lib/viewModels.ts`) built only from data
  the contract actually has, or were dropped/stubbed with the gap named in code. The lesson:
  when two branches diverge across a contract lock, "make it type-check" and "make it correct"
  are different tasks, and the second one needs a human call on which UI assumptions were real
  requirements versus scaffolding that outran the schema.

**Auditing the Day 1 checkpoint before starting Day 2**
- Checking `tasks/todo.md`'s Day 1 checkmarks against actual evidence (not just trusting them)
  found two real gaps a re-read alone wouldn't have caught. First: the GitHub and HN collectors
  had never been exercised live — their own unit tests mock the HTTP call, and unlike Tasks 5
  and 11, nothing in Day 1's own log recorded a real round-trip. Fixed by actually running both
  against real data (`getsentry/sentry`, an HN "Datadog" search) before checking the box.
  Second, and less obvious: `amplify.yml` being committed and Task 7 being checked off was not
  the same thing as a live Amplify Hosting app existing — a buildspec file doesn't create an
  app, and nothing in the repo recorded an App ID or URL. Closed by actually creating the app
  (`aws amplify create-app` with a `gh auth token` for git-connected hosting) and confirming the
  build succeeded and the URL is reachable, not just that the command exited 0. The pattern in
  both: "the task is checked off" and "the thing the task promised is real" can quietly drift
  apart, and the only way to catch it is to go re-verify the artifact, not re-read the checklist.

**Feedback pipeline: normalise/dedupe/redact/spam filter (Task 13)**
- The locked Task 1 schema has no entity for a raw ticket/survey row — `Evidence` already requires `claim_support`, which can't exist until something has been labelled against a claim. §9's diagram puts normalise/dedupe/redact/spam-filter *before* the labeller, so this stage necessarily operates on a pre-`Evidence` shape the contract never defined. Rather than stretching `Evidence` to cover an unlabelled row (or bending the pipeline to consume the simulator's already-labelled `Signal` output, which would skip the stages this task exists to build), added a small `RawFeedbackItem` local to `backend/pipeline/` — deliberately not promoted into `backend/schemas/entities.py`, since it's scaffolding between ingestion and Task 14, not one of the nine contract entities.

**Feedback pipeline: label/validate/aggregate/balance (Task 14)**
- §9.1's fuzzy-span rule ("found verbatim or fuzzy ≥0.92") is easy to implement wrong: comparing the short `evidence_span` against the *whole* source text with `difflib.SequenceMatcher` tanks the ratio purely from the length mismatch (a true positive scored ~0.3). Fixed by sliding a same-length window across the source text and taking the best ratio against that — obvious once seen, but the naive version would have silently dropped every non-exact-substring label as invalid.
- §9.3 is titled "sentiment balance," but its own table is mostly Synthesis-Agent territory (combining Feedback + Competitor signals) except one row ("one-sided evidence") that duplicates the already-schema'd `EvidenceDiversity` object (§11.2, Quality Gate). Read the pipeline diagram's own "BAL" box literally instead: gated theme emission on whether an aspect's pos/neg split is skewed enough to call a signal (dominant side ≥2x the minority) rather than mixed noise. No PRD number exists for that ratio — picked 2x and flagged it `ponytail:` rather than guessing silently, since gold-set labelling (Task 24) is the actual way to validate it later.
- Component #3 in §10.1 is "Lambda pipeline," not "Strands agent in Lambda" like Market/Competitor (#2/#4) — confirmed before writing any code that this stage is a direct Bedrock Converse call with forced tool-choice structured output, not a Strands agent loop with the §10.1a runtime-contract fields (`max_iterations` etc.). Those apply to Tasks 15/16/17, not this one.

**Market Agent (Task 15)**
- No project-scoped Python environment existed before this task — `pip install strands-agents` landed in the shared Anaconda base env by default, which pip flagged as leaving several unrelated already-installed tools (spyder, streamlit, aws-sam-cli) with unmet dependency constraints. Caught before building on top of it; fixed by creating `backend/.venv` and reinstalling there. Worth remembering for Tasks 16/17/18 too — nothing after this should touch the global env again.
- The real Strands Agents SDK (1.56, confirmed by reading its installed source, not assumed from training data) genuinely supports §10.1a's "enforced by code around the agent loop, not a prompt instruction" requirement: `BeforeModelCallEvent.cancel` and `BeforeToolCallEvent.cancel_tool` let a hook stop the loop mid-invocation and hand back whatever was already produced. A bare function with a type-hinted `event:` parameter registers itself via inference (`Agent(hooks=[fn])`) — no `HookProvider` subclass needed for a simple budget check. Confirmed by reading `Agent.__init__`'s actual hook-registration branch, not the docs.
- Split the module the same way Task 14 split the feedback labeller: §9.4 claim validation and §10.1a budget tracking are pure Python, unit-tested with a fake clock and a fake tool-call collector; the real `Agent`/`BedrockModel`/`@tool` wiring is network/AWS-credential-dependent and only smoke-tested, never exercised in the test suite. Kept the live path importable-but-untested rather than mocking `strands` itself, which would test the mock, not the integration.

**Competitor Agent (Task 16)**
- Reused Task 15's `RuntimeBudget` by importing it rather than re-implementing §10.1a budget tracking a second time — it was already generic over the component name via `to_invocation(component=...)`, so the only genuinely new logic was §18.4's named-competitor scope check (`competitor_name in named_competitors`), which structurally stops the agent from inventing or disparaging a company the business never named, on top of §9.4's existing count/date/source rule.

## Day 3 — Sept 19, 2026

*(Not yet written.)*

## Day 4 — Sept 20, 2026

*(Not yet written.)*
