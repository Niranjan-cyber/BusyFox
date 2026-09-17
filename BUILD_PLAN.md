# Build Plan

Opportunity Engine — WeMakeDevs × AWS First Commit (17–20 Sept 2026)

## Day 1

Nothing below counts as "the build" until step 0 is done — eligibility and repo history are the two rules that can end participation before the product matters at all.

**Scope discipline, stated once so it doesn't need repeating each day:**

| Priority | Scope |
| --- | --- |
| P0 | Live/cached/demo-fixture acquisition; Market/Feedback/Competitor research agents; Synthesis; Evidence Check; Quality Gate + Ranker; DynamoDB persistence; all five P0 screens; execution pack; the AWS deployment itself |
| P1 | App Store + Product Hunt enrichment; the four overlay screens (Competitor lens, Targets, Pipeline, Run details); Anveshan Precision playbook |
| P2 | Evidence graph overlay; Koa Studio (evaluation set only); any further polish |

**Rule: if any P0 item is incomplete, no P1 or P2 work starts.** This is the guardrail against spending a spare afternoon polishing something attractive but non-load-bearing while a P0 piece is still shaky.

1. **Eligibility gate, before anything else.** Confirm both teammates are university students in India, 18+. No code, no registration, nothing until this is confirmed.
2. Both members register and get **verified student status** on WeMakeDevs and AWS Builder Center. Budget real time — account creation and verification can be two separate delays.
3. **Create the public repo now.** The clock started when the hackathon opened, not when the repo is created — create it now, as the literal first commit, so the repo's own history matches that start rather than predating it. No pre-event scaffolding beyond notes in `LEARNING.md`.
4. Confirm Bedrock model access/quota for both Haiku 4.5 and Sonnet 4.6; switch inference profile/region immediately if blocked.
5. Stand up **GitHub REST** and **HN Algolia Search** integrations first — deliberately ahead of Tavily, since they're the reliable P0 sources (unauthenticated or lightly authenticated, no rate-limit surprises).
6. Get **one full live Tavily round-trip working** and start the **Level-3 demo fixture** set for PulseStack's primary named competitor (Sentry). This is the PRD's top-named technical risk — it needs to be tested today, not discovered on Day 3.
7. Get one App Store RSS fetch working for a real competitor and register a Product Hunt developer token (P1 enrichment, lower priority than the above).
8. Build and commit the **PulseStack simulator** (scenario file, seed, generator) — seeded sampling of tickets/survey items, planted truths, planted strengths, red herrings.
9. Deploy a skeleton end-to-end: Amplify Hosting + API Gateway + Step Functions + one stub Lambda, so "deployed on Day 1" is true before any agent logic exists.

**End of Day 1:** eligibility confirmed, repo live with real commits, GitHub/HN working, one Tavily round-trip proven, simulator committed with its seed, skeleton deployed on AWS.

## Day 2

Goal: evidence-backed opportunities actually reach the inbox, end to end, once today.

1. Build the **Feedback/Competitor-signal pipeline**: normalise → dedupe → redact → spam filter → Haiku labeller → span/schema validation → theme aggregation by polarity → sentiment balance check.
2. Build the **Market**, **Feedback Pipeline** and **Competitor** agents under the runtime contract (`max_iterations`, `max_tool_calls`, `max_runtime_seconds`, `max_results`, `max_tokens`) — verify they can only emit `signals[]`, never `opportunities[]`.
3. Build the **Synthesis Agent**: apply the sentiment-balance/combination rules, and require a stated **opportunity mechanism** on every candidate — this field is non-negotiable, not a nicety.
4. Build the **Evidence Check**: quote-exists (code) + quote-supports-claim (one structured Haiku call, logged and shown) + source/date/attribution validity + evidence diversity.
5. Build the **Quality Gate + Ranker**: the four-group check sequence (truth, relevance, commerciality, quality/safety), mandatory-fields gate, and the rule-based **priority table** (evidence confidence × fix-first flag) — no composite score, no weighted sum.
6. Wire DynamoDB writes for Business, Run, SourceDocument, Evidence, Claim, Signal, Opportunity.
7. Start the **five P0 screens**: at minimum, Business & Feedback (screen 1) and Opportunity Inbox (screen 3) should render real data by end of day.
8. Label the gold set: 80 simulated feedback items + 20 real competitor snippets, labelled independently by both teammates.

**End of Day 2:** a full run produces at least one gate-passed opportunity, visible in a real (if rough) inbox screen, with its claims traceable to evidence.

Checkpoint: this is also where the biggest fragility — Tavily returning nothing usable — first shows up under real conditions. If Level 1 struggles, lean on Level 2/3 fallback rather than debugging search quality under time pressure.

## Day 3

Goal: opportunity-to-action works end to end, and scope is frozen by tonight.

1. Build the **Action Agent** and **ExecutionPack** generation — offer, proposal, outreach drafts — enforcing `outreach_policy` (`never_reveal_surveillance_source`, `never_quote_private_or_sensitive_information`) in both the prompt and a post-generation check.
2. Finish screens 2, 4 and 5 (Live investigation, Opportunity detail, Execution pack) — all five P0 screens should be feature-complete by end of day.
3. Wire the **value model** (`saas_arr`): `estimated_qualified_accounts` × `expected_conversion` × `ARPA`, shown as an editable range with every assumption labelled OBSERVED/INFERRED/ASSUMED.
4. Wire the **evidence drawer**'s live re-fetch endpoint and its three-level fallback (LIVE RESEARCH → CACHED VERIFIED SOURCE → DEMO FIXTURE) — rehearse this failing over at least once today, don't just code it and hope.
5. Run the evaluation: planted-truth recall, planted-strength recall, red-herring rejection, quote-found rate, quote-supports-claim rate against the gold set from Day 2.
6. If P0 is done by 4pm: Anveshan Precision playbook (20-second "same engine, different business" clip) and, only if screens 1–5 are frozen, the evidence-graph overlay.
7. **Feature freeze at 8pm.** After this point: bug fixes and rehearsal only, no new features.

**End of Day 3:** the full golden path runs start to finish — goal → investigation → inbox → detail → execution pack — on real (or gracefully-fallback) evidence, and the team stops adding scope.

## Day 4

Day 4 is Sunday, Sept 20 — the date is confirmed, the exact deadline hour is not, so **re-check the official schedule/submission page first thing this morning**. Treat "submission-ready by Saturday night" as the team's own internal buffer target, not the real deadline: aim to have everything in a submittable state by the end of Day 3, so all of Day 4 is polish and margin, not last-mile building.

1. Polish UI, fix bugs surfaced in Day 3 rehearsal, sand down rough edges on the five P0 screens.
2. Record the demo video (≤ 3:00) per the script in section 3 — include the live Evidence Check diagram and at least one real AWS-integration beat on screen, not just named in the writeup.
3. Write the **writeup** as a first-class deliverable (problem, build, AWS integration, AI tools used) — not assembled from README scraps in the last hour.
4. Finalise `README.md` ("Tools we used"), `CREDITS.md`, and `LEARNING.md`.
5. Submit the public repo, video and writeup. Confirm the submission actually registered before the deadline window closes.
6. If time remains after submission: Koa Studio evaluation-set pass, extra polish — never new scope.

**Submission checklist:** eligibility + verified registrations done (Day 1); repo history reflects only work done after the clock started on Day 1 (the stated DQ rule), committed as it happens rather than dumped at the end — the rule requires the history to match the dates, not a specific commit cadence; demo video shows AWS visibly, not just names it; writeup covers problem/build/AWS/AI-tools; `CREDITS.md` present for anything reused; no last-minute feature additions after the Day 3, 8pm freeze.