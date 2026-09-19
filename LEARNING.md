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

**Synthesis Agent (Task 17)**
- The locked Task 1 schema has `Opportunity.claim_ids: list[str]` and §14.6 confirms Claim rows are created before Evidence Check runs (`status: hypothesis` is explicitly "passed with capped confidence," i.e. pre-verification) — but `SynthesisAgentOutput` only had `candidate_opportunities`, no way to hand back the Claim rows those ids point to. Added a `claims: list[Claim]` field to the output schema (and its TS/`docs/contract.md` mirrors) rather than inventing an out-of-band side-channel for them, same as `RawMarketSignal`/`RejectedClaim` stayed local-only in Tasks 15/16 for things that aren't contract entities — the difference here is `Claim` *is* one of the nine, so it couldn't stay local.
- §10.2's own table assigns `evidence_confidence`/priority/value derivation to Quality Gate + Ranker (code, Task 19), not Synthesis — but `Opportunity` has no separate "candidate" shape, so Synthesis still has to put something in those non-optional fields to produce a schema-valid object. Filled them with what the rule tables actually say given zero verified evidence at synthesis time (LOW confidence, Low/Blocked priority off the §13.1 table, a zeroed value model flagged `ASSUMED: pending_quality_gate`) instead of an arbitrary placeholder — Task 19 overwrites these for real, but nothing here required a guess.
- First pass at the mechanism-concreteness check did literal substring matching (statement must contain the exact `shared_segment`/`actionable_because` text) — failed on the module's own demo data because a real paraphrased mechanism never repeats its inputs verbatim. Gate check 7 (§11.2) only says "populated... Missing → reject," which is a presence check, not a semantic one; semantic soundness is what the model's own `mechanism_holds` self-critique verdict is for. Simplified to a pure presence check and let the rubric self-critique field carry the actual judgment — a string-similarity heuristic there would've just taught a future live agent to pad statements with matching keywords, not reason better.

**Evidence Check (Task 18)**
- `Signal` (§14.7) is deliberately trimmed to the public shape research agents may emit — it has no `quote`/`source_url` field, so Market/Competitor Agents' `build_signal` (Tasks 15/16) drops the very quote+URL their `RawMarketSignal`/`RawCompetitorSignal` validated against. By the time a Claim (Task 17) cites a signal, the quote Evidence Check needs to verify no longer exists anywhere in the locked schema. Rather than reopening `Signal` to carry it (which Tasks 14–17 already shipped against), Evidence Check takes a separate `EvidenceCandidate` input the orchestrator (Task 21) will need to build straight from each agent's raw collector output, not from the trimmed `Signal`. Worth flagging now — Task 21 needs to keep raw signal records around per run, not just the final `Signal` list, or it'll hit this gap as a surprise when wiring Synthesis → Evidence Check.
- §12.1's own diagrams give the check order for free: "no verbatim quote found" is rejected without ever asking whether it *supports* the claim — so `build_evidence` checks `quote_exists` in code first and only calls the one Haiku semantic-support call when a quote is actually there, saving a model call on the cases that are already known-losers.
- Reused Task 14's fuzzy-span matcher (`span_found`/`fuzzy_ratio`, promoted from private to public in `feedback_labelling.py`) instead of writing a second verbatim-or-fuzzy quote check — "does this text exist in that text" is the same question whether the text is a feedback item or a live source document.

**Quality Gate + Ranker (Task 19)**
- §13.1 names *what* evidence_confidence answers ("verified-item count, source-kind diversity, contradiction flags") but never gives the actual HIGH/MEDIUM/LOW derivation as a formula — unlike priority, which is a literal table. Built it from the two explicit rules the gate checks already state (check 6: diversity failure caps confidence at LOW; check 4: a contradiction costs one tier) rather than inventing a scoring function: diversity-fail -> LOW outright, else contradiction -> MEDIUM, else HIGH. Worth a second look once Task 24's gold set exists.
- Gate check 5 (capability) and check 14 (account evidence integrity) both assume structure the schema doesn't have yet: check 5 wants to know which `Business.capabilities` an opportunity's mechanism depends on, but `OpportunityMechanism` is free text with no capability-key field; check 14 gates a `Target.account_fit_inference` against `observed_facts`, but Target isn't produced until the Action Agent (Day 3). Rather than expanding the locked Task 1 schema mid-Day-2 for one gate check, check 5 does a keyword match against unconfirmed capability keys in the mechanism text (same heuristic-with-a-`ponytail:`-comment treatment as Task 18's `freshness_limit_days`), and check 14 is a real, tested, callable function that `run_quality_gate` simply never calls yet — there's nothing to call it on. Whoever wires the Action Agent should call `check_account_evidence_integrity` per Target before it's shown.
- `Opportunity` needed a place for the three non-rejecting flags §11 describes (stale evidence, contradiction/one-sided evidence, fix-first risk) — none of the 14 checks' outcomes fit into `evidence_confidence`/`priority` alone. Added `flags: list[str]` to the entity (Python default `[]`, TS `flags?: string[]` to avoid breaking existing fixture literals) rather than inventing an out-of-band side channel, same reasoning as Task 17's `claims` field addition.
- Confirmed from `tasks/plan.md`'s own Task 19 line (no mention of `value`) and `todo.md`'s Day 3 list ("value model" appears there, not Day 2) that §13.2's value model is out of scope here — Quality Gate passes `Opportunity.value` through untouched from Synthesis's placeholder rather than half-implementing it.

**DynamoDB table + writes (Task 20)**
- No entity in the locked Task 1 schema carries its own parent id (`Opportunity` has no `run_id`/`business_id`, `ExecutionPack`/`Claim` have no back-pointer beyond `opportunity_id` one level up) — but the API's list endpoints (`/businesses/{id}/opportunities`, `/opportunities/{id}/claims`) need exactly that to query. Rather than adding parent-id fields the Pydantic/TS contract doesn't need, `to_item()` writes the caller-supplied `parent_key` only into `GSI1PK`/`GSI1SK` (not into the entity's own fields), and pydantic v2's default `extra="ignore"` means reading a `GSI1PK`-carrying item back through `Model.model_validate(item)` drops it silently — the contract stays untouched and the query key still works.
- Testing the GSI1 query path without moto (not a project dependency) meant faking `table.query(KeyConditionExpression=...)`, but that argument is a real `boto3.dynamodb.conditions` object (`Key(...).eq(...) & Key(...).begins_with(...)`), not a callable — its `_values`/`.name` fields are undocumented/private but stable enough to walk recursively for a same-process fake. Cheaper than adding moto for one test file; revisit if more Dynamo tests show up and the private-attribute walk gets fragile.

**Orchestrator wiring (Task 21)**
- `Signal` (§14.7) is deliberately the "trimmed public shape" — no raw quote or URL — but Evidence Check needs both to verify a claim. The Market/Competitor agents' raw tool-call output (`RawMarketSignal`/`RawCompetitorSignal`) does carry a `source_url` and a `date_window` string; `run_market_agent`/`run_competitor_agent` throw both away on the way to building a `Signal`. Rather than changing those already-tested Task 15/16 files, the orchestrator calls their lower-level `validate_claims`/`build_signal` directly and keeps its own signal_id → (url, parsed date) map alongside. Net: Evidence Check gets a real URL and a best-effort real date for Market/Competitor evidence, with zero changes to committed agent code.
- A second, smaller gap: `Synthesis` only treats a negative signal as `pains_to_fix_first` when `produced_by == "feedback_pipeline_labeller"` (Task 17), but the PulseStack simulator (Task 10) stamps its signals `produced_by="pulsestack_simulator"` — a negative simulated signal silently can't become a fix-first pain today. Not fixed here (it's a cross-task naming mismatch, not an orchestrator wiring bug), but the demo pipeline was built to route around it — competitor-agent pain + simulator strength → `competitive_gap`, the same pattern Task 17's own self-check already uses — rather than quietly special-casing produced_by strings in new code. Worth a one-line fix (either name) before Task 24's gold-set run depends on fix-first opportunities showing up from simulated data.
- Wiring the P0 GET handlers to read real DynamoDB rows (asked for explicitly, beyond the minimum "orchestrator wiring" scope) almost shipped a real regression: swallowing `Exception` from `boto3.resource("dynamodb")` calls to fall back to the fixture is correct, but with zero AWS credentials configured (normal local dev/test state), boto3's credential-resolution chain takes ~3.4 real seconds to fail before that except-block ever runs — turning every handler call, and the whole test suite, into a multi-second hang. Fixed by gating the DynamoDB attempt on `AWS_LAMBDA_FUNCTION_NAME` (set automatically inside a real Lambda) instead of just try/except, so local/test calls skip straight to the fixture in effectively zero time. The lesson: "catch the error and fall back" and "detect you don't need to try" are different fixes, and only one of them is fast.
**Screens 1 and 3 against the real API (Tasks 22–23)**
- The frontend had been calling `/businesses/{id}/claims`, which exists in neither
  `docs/contract.md` nor the deployed stage — it 404s. Nothing caught it, because with
  `VITE_API_BASE_URL` unset the client never makes the request and the fixture fallback renders
  a perfectly good screen. A fallback ladder hides integration bugs by design: the same code
  path that keeps the demo alive when Tavily has a bad five minutes also keeps a wrong URL
  looking fine forever. The fix was a test that asserts the *requested URL* against the
  contract table, not just that the screen renders.
- The bigger find: no endpoint says how it was retrieved. `retrieval_mode` is on
  `SourceDocument` and `Evidence` only (§14.4/§14.5), so a `Business` or `Opportunity` response
  carries no provenance at all — and the client's old behaviour was to assume `cached` when a
  payload didn't declare one. That is a §7.2 violation in the direction nobody looks for:
  the guardrail is written as "never show a fixture as live", so a conservative-sounding
  default reads as safe, when it is still the product asserting a provenance it cannot support
  over what is currently stub-Lambda fixture data served on HTTP 200. Replaced with an explicit
  "provenance not stated" state and an `X-Retrieval-Mode` header proposed to Lane A — a header
  rather than an envelope field because four contract endpoints return a bare array with
  nowhere to put one.
- Fetching the inbox's claims exposed a rule the screen would otherwise get wrong silently: if
  the opportunity list is live and a claims call fails, falling back to the committed fixture
  claims attaches evidence to opportunities nobody ever wrote it about. Consistency between two
  endpoints' fallbacks is part of the ladder, not a detail — so the pairing lives in the client
  (`fetchInbox`) where it can be tested, and fixture claims are only ever served beside fixture
  opportunities.
- With no chrome-devtools MCP configured, the browser pass ran on headless Chrome directly:
  `--dump-dom` for content, and a ~40-line CDP script over Node 24's global `WebSocket` for
  device-metrics emulation, real `Input.dispatchKeyEvent` Tab presses and overflow measurement.
  Two things that would have produced false results: `--window-size` does not set the layout
  viewport, so a screenshot looked clipped at 390px when the page was actually fine (device
  metrics must be emulated via CDP); and `Page.navigate` to a URL differing only in its hash
  does not reload, so a "full outage" check silently re-reported the previous run's live data
  until a cache-busting query string was added.

**Merging Lane B, and clearing its blockers (frontend/README.md)**
- Two of the frontend's five named blockers (retrieval-mode header, `opp_001`'s fixture priority)
  turned out to be one-line backend fixes once traced to source — the header just needed
  `ok()` to accept an optional param, and the priority bug was a hand-authored Task 2 fixture
  that had simply never been run through `run_quality_gate`'s real rule table. Worth noting
  that "known blocker documented by the other lane" and "hard to fix" are not the same thing;
  the value was in the other lane's precise write-up, not in the fix itself.
- The CORS blocker exposed a second, unrelated failure: `sam build` for `infra/api-gateway.yaml`
  is broken, and has been since Task 15 added `strands-agents` to `backend/requirements.txt` —
  nobody had rebuilt this template since. `strands-agents` pulls in `mcp`, which lists
  `pywin32>=311; sys_platform == 'win32'` as a dependency; SAM's local (non-container) pip
  resolver runs on the host platform and tries to satisfy that marker even though the Lambda
  target is Linux, and fails resolving the wheel. `sam build --use-container` targets the
  correct platform and gets past that, but then fails `CopySource` on `.claude/skills/...`:
  those are symlinks to an absolute host path, and even though `.samignore` lists `.claude/`,
  the container-build copy step doesn't honor it before trying to follow the symlink — which
  then doesn't resolve inside the container's mount. Neither failure has anything to do with
  the CORS change that surfaced them.
- Given a broken build, the actual fix was applied straight to the live resource
  (`aws apigatewayv2 update-api --cors-configuration ...`) rather than through `sam deploy`,
  with the same config also committed to the template so a future successful deploy confirms
  rather than drifts it. Verified with a real `OPTIONS` preflight against the deployed API
  from the Amplify origin, not just a template review — the same "prove it live" standard as
  Tasks 5/11's collector probes.

**Actually fixing `sam build` (blocker 6)**
- `.samignore` never did anything. `.git`/`.pytest_cache`/`.venv`/etc. being excluded from the
  build artifact was `aws_lambda_builders`' own hardcoded `EXCLUDED_FILES` tuple, not our file —
  it isn't referenced anywhere in the installed `samcli`/`aws_lambda_builders` packages. It
  looked like it was working because the things it claimed to exclude (`.git`, `graphify-out`,
  `.claude`) either matched the hardcoded list by coincidence (`.git`) or simply never broke
  anything by being included (small text files) — until `.claude/skills/*`'s symlinks did, under
  `--use-container`, and there was nothing left to blame but a config file that was always inert.
- The real fix for the `pywin32` failure was smaller than it looked: none of the 10 deployed
  functions import `strands-agents`/`mcp` at all (checked by grepping every handler's imports) —
  it's only needed by `backend/agents/*.py`, none of which are wired into this template. Pointing
  `sam build` at a `pydantic`+`boto3`-only requirements file sidesteps the whole platform-marker
  problem, no container needed, and confirmed correct by checking the built `pydantic_core`
  wheel's tag was `manylinux_2_17_x86_64`, not a Windows one — cross-platform pip resolution for
  the Lambda target does work locally on Windows; it just can't tolerate a Windows-only marker in
  the dependency graph, container or not.
- Tried to also stop `frontend/node_modules` (~90MB) from riding into every package, by pointing
  `CodeUri` at a small directory containing a symlink to the real `backend/`. Reverted: this
  repo's `git config core.symlinks` is `false` (git-for-windows default), so `git add` silently
  dereferenced the symlink and staged a full second copy of `backend/` as real files — the exact
  drift risk this whole exercise was trying to avoid, just relocated. Checking `git ls-files -s`
  on an existing symlinked path (`.claude/skills/*`) before committing anything symlink-shaped
  would have caught this in seconds; the packaging bloat itself (128MB, under Lambda's 250MB
  unzipped limit) turned out not to be a real problem worth solving today.

## Day 3 — Sept 19, 2026

**Rejected-candidate route + first real deploy (blockers 2–3)**
- SAM's `Globals.Function` section rejects `Policies` outright (`InvalidGlobalsSectionException`,
  not a silent no-op) — it only accepts a fixed property list that doesn't include IAM policies.
  `Environment` is fine at the Globals level; per-function `DynamoDBReadPolicy` has to go on each
  function individually. Caught by `sam validate` before a wasted deploy, not by reading docs.
- The real find: deploying `OpportunityEngineTable` for the first time did **not** make any
  handler's "live" response actually live. `backend/handlers/_common.py::dynamo_get` defaults
  `DYNAMO_TABLE_NAME` to a hardcoded fallback name that was never the CloudFormation-generated
  one, and no function had `dynamodb:GetItem`/`Query` permission either way — both failures are
  caught by the same broad `except Exception: return None` that also covers "no credentials in
  local dev," so a handler with a wrong table name and a handler with a missing table look
  identical: both just fall back to the fixture, silently. The deploy would have "succeeded" and
  every screen would have kept rendering fixtures under a `LIVE`-capable header. Caught only by
  writing a throwaway item straight into the table and invoking the deployed Lambda directly to
  check the header actually flipped to `live` — a green `UPDATE_COMPLETE` and a reachable URL
  are not the same claim as "the wiring between them is correct."
- `sam deploy --config-file infra/samconfig.toml` (relative path) failed with "Config file...
  does not exist or could not be read" from a cwd where the file plainly does exist — an
  absolute path fixed it immediately. Never root-caused (didn't burn time on a SAM CLI internals
  rabbit hole with a working alternative one flag away), but worth remembering the symptom
  doesn't mean what it says.
- The harness itself (not a normal permission prompt) hard-blocks `sam deploy` as a "Blind Apply"
  Bash action regardless of prior conversational approval — it has to be run by the human, with
  the `!` prefix, in their own terminal. Budgeted for that up front instead of retrying the same
  blocked call.

**Bedrock was never coming back — root cause, then a real fix (Market/Competitor/Synthesis, Evidence Check)**
- Day 1's log says Bedrock access was confirmed ("Access granted", no wait) — that checked the
  model-access *grant*, not the account's actual invoke *quota*, and those are different things.
  `aws bedrock list-foundation-models` showing a model as `ACTIVE` proves nothing about whether a
  call will succeed. The only real proof is an actual `Converse`/`InvokeModel` call; every attempt
  today returned `ValidationException: Operation not allowed`, on both this account and a second,
  genuinely different teammate account, for Claude *and* Amazon's own Nova — ruling out a
  per-model or per-provider access gate. `aws service-quotas list-service-quotas --service-code
  bedrock` found the actual cause: every real-time inference quota (on-demand and cross-region,
  requests/min and tokens/min, every model) was a hard 0 — the default for a new AWS account,
  unrelated to which model or which account. Two independent accounts hitting the identical wall
  is what made this diagnosable instead of "maybe try a third profile."
- Rather than wait on an AWS quota increase with no ETA, switched all four Bedrock call sites
  (three agents' `Agent(model=BedrockModel(...))`, plus Evidence Check's raw `boto3` Converse call
  for semantic claim support) to OpenCode Go, an already-paid-for $10/mo subscription, via its
  OpenAI-compatible gateway. `strands-agents` 1.56 already ships `strands.models.openai.OpenAIModel`
  with a `client_args` escape hatch for a custom `base_url` — no new agent framework needed, just a
  different model provider underneath the same `Agent`/`@tool` code.
- Getting there needed two more real, only-discoverable-by-calling-it fixes: Go 400s with
  `MissingSessionID` unless every request carries an `x-opencode-session` header (undocumented as
  a hard requirement, mentioned only in passing as a caching optimization); and Go's models run in
  "thinking mode," which rejects a forced `tool_choice` (`{"type": "function", ...}`) outright —
  `tool_choice="auto"` gets the identical real tool call in practice, verified live, not assumed.
  Also unrelated to Go specifically: `strands.models.openai.OpenAIModel` doesn't take `max_tokens`
  as a constructor kwarg the way `BedrockModel` did — it's silently dropped with a `UserWarning`
  unless passed inside `params={"max_tokens": ...}}`, a fix that would've been easy to miss without
  actually reading stderr on a real run rather than just checking the tool call succeeded.
- Asked an LLM (via WebFetch) to summarize OpenCode Go's model catalog from its docs page before
  the real API key existed to check it against — got back a suspiciously large, neatly-formatted
  table of model IDs. Flagged it as possibly partly invented rather than trusting it, and once a
  real key existed, fetched `/v1/models` directly instead: the real list differed from the
  summarized one in several entries. A page-summarizer asked "list every X with its exact ID" will
  produce something that looks authoritative whether or not the source page actually said all of
  it — worth the extra live call before hardcoding anything from it.

**First real end-to-end pipeline run — the table wasn't empty because of one bug, it was five**
- `scripts/run_live_pipeline.py` still imported `bedrock_semantic_support_checker`, a name the
  Bedrock→OpenCode Go rename (above) missed — caught immediately by the import error, cheap fix.
- Windows' console defaults `sys.stdout` to `cp1252`; strands' callback handler `print()`s the
  model's raw reasoning text, and OpenCode Go's model uses non-ASCII characters (e.g. `→`) in its
  chain-of-thought often enough that every live run crashed on it. `sys.stdout.reconfigure(encoding=
  "utf-8")` at the top of the script fixed it — a Windows-only failure mode that unit tests (which
  don't print model reasoning) never would have caught.
- `boto3`'s DynamoDB `Table.put_item` rejects native Python `float` outright ("Use Decimal types
  instead") — `backend/db/dynamo.py::to_item` used `model.model_dump(mode="json")`, which keeps
  floats as floats. Fixed by round-tripping through `json.loads(model.model_dump_json(),
  parse_float=Decimal)` instead — converts every float in the tree in one pass, stdlib only.
- OpenCode Go's model is dramatically more verbose in tool-call reasoning than Bedrock's was, and
  its response length is highly variable run to run — the same `max_tokens` that worked once threw
  `MaxTokensReachedException` on the next attempt, and sometimes the model burned its whole budget
  narrating without ever calling the tool (no exception, just an empty turn — a different failure
  mode from hitting the cap). Fixed with two independent retries in `synthesis_agent.live_collect`:
  resume the same agent on `MaxTokensReachedException` (strands keeps the partial turn in history),
  and restart with a fresh agent if a full attempt produces zero tool calls at all.
- The Synthesis system prompt described the §9.3 pattern table in prose ("unmet need with a
  fix-first step") but never stated the literal `opportunity_type` enum values the tool parameter
  must equal — the model reasonably paraphrased it to `"unmet_need_fix_first"`, which
  `validate_candidates` silently rejected as `unknown_opportunity_type`. Only surfaced because
  `orchestrator.run_pipeline` was discarding synthesis-level rejections into a `_`-prefixed
  variable — added `synthesis_rejected` to `PipelineResult` so this class of failure is visible
  in the pipeline output instead of just showing up as "zero opportunities, no explanation."
- The real bug once all of the above were visible: `synthesis_agent.build_opportunity`'s
  "our pain" filter only recognized `produced_by == "feedback_pipeline_labeller"` (Task 13/14's
  real-business pipeline), but the demo business's own feedback signals come from
  `run_feedback_stage` → PulseStack simulator, `produced_by="pulsestack_simulator"`. Every
  negative-polarity signal about our own product was silently dropped from
  `pains_to_fix_first` for the simulated business specifically — the one business this repo can
  actually demo against live. Same gap existed in `evidence_check.freshness_limit_days`. A
  produced_by check like this needs to be written against "what are all the producers of
  first-party feedback," not just the one that existed when the line was first written.
- Net effect of chasing all five root causes instead of raising `max_tokens` and moving on: the
  first real opportunity (`opp_run_7f023794a99d_0`, `unmet_need`, priority `Blocked`) is now live
  in DynamoDB, reachable through the deployed API (`X-Retrieval-Mode: live`), with every claim
  carrying real `evidence_ids` — Day 2's checkpoint, made real on Day 3 rather than left as a
  known gap into Day 3's own feature work.
- Task 26 (Action Agent): the first live run against `opp_run_7f023794a99d_0` refused to emit any
  outreach draft at all — that opportunity has zero verified strengths (`priority=Blocked`,
  `evidence_confidence=Low`), so there's no signal id the `proof_point_signal_id` guardrail can
  legitimately accept, and the model correctly declined to invent one rather than fabricate a
  proof point. Working as designed, not a bug — but it means the live rehearsal of the
  policy-violation reject path (§18.1) still needs a *ranked* opportunity with a real strength to
  actually exercise, not just the one persisted opportunity this repo currently has.
- Real bug, caught by the first live run: `build_execution_pack` originally took a separate
  `run_id` and built the pack id as `pack_{run_id}_{opportunity.id}`, mirroring Synthesis's
  `opp_{run_id}_{index}` scheme. But a pack is 1:1 with its opportunity (unlike synthesis, which
  emits several opportunities per run and needs the index for uniqueness) — the live script
  passed `opportunity.id` as `run_id` for lack of anything better, producing
  `pack_opp_run_7f023794a99d_0_opp_run_7f023794a99d_0`. Dropped `run_id` entirely; `pack_{opportunity.id}`
  is both simpler and can't collide.
- `.env`'s `API_BASE_URL` pointed at a stale API Gateway id (`oy52dx5ygl`) that no longer resolves
  — the stack's actual current endpoint (`aws apigatewayv2 get-apis`) is `vx59qs2osl`. Likely
  drifted after an earlier stack recreation; nothing rewrites `.env` on redeploy. Fixed locally;
  worth checking `SKELETON_ORCHESTRATOR_ARN` for the same drift before it's next needed.
- Deploying the fixed `GetExecutionPack` handler needed `sam deploy`, which prompts an interactive
  changeset confirmation — the harness's own auto-mode classifier blocks any attempt to script
  past that prompt (`--no-confirm-changeset`, piping `y`) as a "blind apply," even with the
  human's prior go-ahead to deploy. Correct behavior: a live infra change gets a human looking at
  the actual changeset, not a pre-committed yes. Left for the human to run interactively.
- After that first deploy, the live endpoint still 404'd with the exact same message the old
  fixture-only code produced — a false negative on "code didn't ship." Real cause:
  `GetExecutionPack` was defined in `infra/api-gateway.yaml` back when it was permanently
  fixture-only (Task 2/6) and never got a `DynamoDBReadPolicy`, unlike every sibling handler that
  already reads the table. Once Task 26 made it call `dynamo_children`, the Lambda's IAM role had
  no `dynamodb:Query` permission — `_common.py`'s blanket `except Exception: return None` (added
  so local dev/test never hangs on missing credentials) swallowed the AccessDenied and looked
  identical to "table has no rows yet." Fixed by adding the same `DynamoDBReadPolicy` the other
  read handlers already have; second `sam deploy` confirmed it — `GET .../execution-pack` now
  returns `200`, `X-Retrieval-Mode: live`, the real pack. Lesson: that broad exception swallow is
  exactly right for the local-dev case it was built for, but it means a live IAM gap on a *new*
  DynamoDB-reading handler looks like an empty table from the outside — worth an explicit CloudWatch
  check, not just a curl, whenever a handler gains its first real Dynamo read.

- Task 28's rehearsal failed its first dry run for a reason no unit test could see: `evd_001` and
  `evd_002` (Task 2 fixtures) point at a real HN item that has nothing to do with the quote they
  carry — the quote was invented. So a genuine live re-verify ("is the quote still at the URL?")
  can never pass on them, and §7.2's Level 3 promise ("manually verified real evidence") isn't
  actually met by those two. Found by running Tavily's extract on the URL and grepping for the
  quote, *before* deploying. Added one genuinely real fixture, `evd_hn_31781473` (verbatim HN
  comment about Sentry's noise, confirmed present in Tavily's extract), which is what the
  rehearsal used. Still open: the golden-path demo's fixtures should be replaced with real
  quotes the same way, before the video.
- Rehearsal result (deployed stack, 2026-09-19): real key -> `live`; bad key -> `cached` with the
  *original* `retrieved_at` (14:52Z, not now — the cache re-serves an earlier real fetch, it
  doesn't re-stamp it); cache emptied -> `demo_fixture`; key restored -> `live`. The fixture
  record itself is stored with `retrieval_mode="live"`, so the handler has to overwrite it to
  `demo_fixture` on the way out or it would be served under the wrong label.
- `Timeout: 10` in `Globals` would have killed this Lambda before it could fall back: Tavily's own
  HTTP timeout is 10s, so the function needed 20s. Any handler whose fallback runs *after* a slow
  external call needs a timeout longer than that call, or the fallback never gets to run.

- Task 30 (Screen 2): `docs/contract.md`'s Task-2-era note excluding Screen 2 from the API table
  ("streaming, not a simple REST shape, Day 2 work") had gone stale — by Day 3 the pipeline
  persists Signal rows per business already (Task 20/21), so the real gap was just a missing
  *route*, not missing data. Closed it the same way Tasks 22/23 closed their gaps: one more
  DynamoDB-first/fixture-fallback handler (`GET /businesses/{id}/signals`, unfiltered), not a new
  mechanism. Cheaper to notice a stale exclusion note than to build the websocket the old note
  implied was necessary.
- Reused `feedbackSignals` (the Task 8/9 fixture that expands each theme into one entry per
  mention count, for §1's polarity totals) as the Feedback lane's fixture data and only caught the
  bug by actually loading the screen in a browser: 170 near-duplicate cards, not signals arriving.
  Component tests (`toEqual(investigationSignals)`) couldn't have caught this — they'd pass either
  way, since they only check the client returns whatever the fixture array contains. A fixture
  shaped for one screen's aggregate math isn't automatically right for another screen's per-item
  list; the type checker and unit tests agreed it was fine, and it wasn't. Fixed by deduping to one
  representative signal per theme before rendering.

- Task 31 (Screen 4): Evidence has no `quote_exists` boolean of its own — quote-exists is a
  check `backend/pipeline/evidence_check.py::build_evidence` runs *before* ever calling the
  semantic-support model, and when it fails, the only trace left in the response is the exact
  literal string `"quote not found in source text"` in `claim_support.reason`. The frontend has
  to string-match that exact reason to tell "missing citation" apart from "quote exists but
  doesn't support the claim" — two outcomes §21's demo beat both needs. Documented the coupling
  in `lib/viewModels.ts::evidenceCheckResult` rather than hiding it, since a backend wording
  change would silently break the diagram's rejection labelling with no type error to catch it.
- Backend's own demo fixture (`backend/fixtures/fixtures.py::EVIDENCE_BY_ID`) has zero reject
  examples — every evidence item there is `status: supports`. §21's signature diagram beat
  (accept + two distinct reject shapes) can't actually be demoed off that fixture alone. Didn't
  touch Lane A's file for this; added both reject shapes to the *frontend's own* fixture set
  instead (`frontend/src/fixtures/evidence.ts`), which is enough to prove the diagram's logic
  end-to-end and to demo it with no backend configured. Someone still needs to add a real reject
  example to the backend fixture (or get one from a live run) before the actual recorded demo,
  since a judge asking to see it against the live API today would only see accepts and
  `rejected_unsupported` — worth flagging before §21 shot-list recording (Task 34).
- Verified the diagram against the real deployed API's `opp_run_7f023794a99d_0`, not just
  fixtures: every one of its evidence items comes back `rejected_unsupported` (quote exists,
  semantic check says no) — consistent with Task 26's note that this run has zero verified
  strengths. A live run that fails Evidence Check cleanly is itself a useful thing to have
  actually seen happen, not just unit-tested.
- Task 32 (Screen 5): checked the last P0 screen against the real deployed
  `opp_run_7f023794a99d_0` and it produced the cleanest possible confirmation of Task 26's
  `outreach_policy` enforcement — a real Action-Agent-written offer and proposal, but zero
  outreach drafts, because that opportunity has no verified strength to cite. The screen had to
  render that as a real empty state rather than assume `outreach_drafts` is always non-empty.
  If the frontend build had happened before Task 26's live run instead of after, the empty case
  would have been easy to miss and ship as a silent blank block.
- Local dev has a `.env.local` with `VITE_API_BASE_URL=/api`, which `vitest` also picks up (Vite
  loads `.env.local` for every mode, not just `dev`). Any test asserting "no fetch call happens
  with no backend configured" silently starts hitting the network in this environment even
  though it's `vi.stubEnv`-free — three such tests fail locally (two pre-existing, one added by
  Task 32) but would pass in CI/a clean checkout. Didn't chase a fix since it's a local-only
  false negative, not a real bug; flagging so a future session doesn't burn time re-diagnosing
  the same three failures as a regression.
- Task 33 (devtools pass, all 5 screens): a route can be fully committed — SAM template,
  handler, frontend client, unit tests, todo.md note — and still 404 live, because `sam deploy`
  is a separate, human-confirmed step from `git commit` in this repo. Screen 2's
  `/businesses/{id}/signals` (added in Task 30, commit `2fa0e4c`) fell back to its fixture on
  every real browser check today, not because of a frontend bug but because that commit's SAM
  changes were never deployed. `curl` straight at the API Gateway origin (bypassing the vite
  dev proxy) is the fast way to tell "not deployed" apart from "deployed but broken" — the
  proxy's own 404 looks identical either way. Worth a standing habit: after any task that edits
  `infra/api-gateway.yaml`, curl the new route directly before checking the task off, not just
  the unit tests.

## Day 4 — Sept 20, 2026

*(Not yet written.)*
