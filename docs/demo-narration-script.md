# Demo video — narration script (Task 40)

Word-for-word lines + exact on-screen actions for `docs/demo-shot-list.md`'s resolved timing.
Total runtime ≈2:50, under the 3:00 hard cap. Read this once through before recording — every
beat below is either **LIVE** (record straight off the deployed app) or **FIXTURE** (record the
same deployed app at a URL that 404s from the real API and falls back to the committed fixture,
labelled `DEMO FIXTURE` on screen — no local dev server needed, see note below each fixture beat).

## Before you hit record

1. Open **https://main.dw3gwg5t169l9.amplifyapp.com/#/business** in a fresh/incognito window —
   avoids any stale cached state from earlier testing sessions.
2. Confirm the top banner reads **LIVE RESEARCH**, not `DEMO FIXTURE` — if it doesn't, the
   Amplify env var may have reverted; check before recording, not after.
3. Quickly click through `#/opportunities/opp_07` and `#/opportunities/opp_07/execution-pack`
   once to confirm the fixture fallback still renders (banner should read `DEMO FIXTURE`, not a
   blank/error screen).
4. Mute Windows notifications (Focus Assist on, or Win+A → Focus toggle) so nothing pops mid-take.
5. Recording tool: **Win+Alt+R** (Xbox Game Bar, built into Windows 11, records the active
   window) — no install needed. Record the browser window only, not the full desktop.
6. Zoom the browser to ~100–110% so text is legible at 1080p; close other tabs.

---

## Script

**0:00–0:15 — Screen 1, `#/business`**
Show the header + Goal card ($15k additional MRR / 90 days) and the "Simulated company · real
competitors and market" badge.
> "This is PulseStack — a simulated business, with a real goal: $15,000 in new MRR in 90 days.
> Its competitors are real companies."

**0:15–0:30 — no UI, just the business screen sitting on screen**
> "A general AI can research your market. Watch what ours rejects."

**0:30–0:50 — Screen 1 feedback section, then cut to Screen 2's Competitive lane**
Show PulseStack's own customer feedback on Screen 1, then switch to `#/investigation` and point
at one real competitor signal card in the Competitive lane (verify it's a Sentry/Datadog card,
not another lane, before recording — see shot-list note).
> "It reads the business's own customer feedback — and real, live-retrieved reviews from named
> competitors, side by side."

**0:50–1:10 — `#/investigation`, all three lanes**
Let all three lanes (Market / Feedback / Competitive) visibly populate. Speed this clip up in
edit and caption it.
> **On-screen caption: "Live run, sped up."**
> "Three research agents run in parallel — market signals, customer feedback, and competitor
> activity — each one only ever proposing raw signals, never a finished opportunity."

**1:10–1:35 — `#/inbox` → `#/opportunities/opp_07`** *(FIXTURE — 404s from the real API,
falls back to the committed fixture, labelled `DEMO FIXTURE` on screen)*
Open the inbox, click into opportunity `opp_07`. Show its four claims (why this / why you / why
now / mechanism), each with its own evidence, and the three separate numbers: priority, evidence
confidence, potential value.
> "Every opportunity has to answer four questions, each backed by its own evidence — and notice
> there's no single score. Priority, evidence confidence, and potential value are three separate,
> editable numbers. We deliberately never combine them into one."

**1:35–1:55 — same screen, `EvidenceCheckDiagram`** *(FIXTURE, same page)*
Walk the diagram: one claim accepted, one rejected for a missing citation, one rejected because
the quote exists but doesn't actually support the claim.
> "This is the check that matters. Code verifies the quote exists. A separate, constrained model
> call verifies the quote actually supports the claim — not just that the words appear somewhere.
> Here's one that passes, one rejected for no citation, and one rejected because the citation
> doesn't back up what it's cited for."

**1:55–2:15 — `#/opportunities/opp_07/execution-pack`** *(FIXTURE, same fallback)*
Show the offer, proposal, and one outreach draft. Point at the cited proof point.
> "Once an opportunity clears every check, it becomes an execution pack — an offer, a proposal,
> and outreach drafts, each one citing a verified strength. The human sends it. Nothing here
> exposes how the system found what it found."

**2:15–2:30 — `#/inbox`, "Ideas we rejected"** *(LIVE)*
Scroll to or click the rejected-ideas list; show the real rejected idea with its reason
(`no_verified_evidence`).
> "We planted opportunities and distractions in this scenario. Here's the inbox — real signal
> surfaced, distractions rejected with the reason shown. The engine's IAM role never sees the
> answer key."

**2:30–2:45 — `docs/architecture-diagram.md` on GitHub**
Scroll the rendered Mermaid diagram: Amplify → API Gateway → Lambda → DynamoDB/S3, and the two
honestly-labelled gaps (Bedrock IAM-wired but quota-blocked, real inference via OpenCode Go;
Step Functions deployed as the Day 1 skeleton, real pipeline run via a local script).
> "Deployed on AWS: Amplify Hosting, API Gateway, thirteen Lambda functions, DynamoDB, and S3.
> Two honest notes on here too — Bedrock access is wired and approved, but every account we
> tried hit a zero-request-per-minute quota, so live model calls run on OpenCode Go instead. And
> the orchestrator you're seeing wired is today's deployed skeleton; the full five-stage pipeline
> that produced this data ran through a local script, not yet through Step Functions. We'd rather
> show that honestly than hide it."

**2:45–3:00 — Amplify URL + repo link on screen**
> "The biggest thing we learned: we verified every screen against local dev and the API
> directly — and never actually loaded the public URL a judge would open, until Day 4. It was
> quietly serving demo fixtures the whole time, correctly labelled, just never checked. Lesson:
> verify the one surface that combines everything, not each piece in isolation.
> That's Opportunity Engine — agents discover, code verifies, humans decide."

---

## After recording

- Trim to ≤3:00 total (script lands ~2:50 as written; the 0:50–1:10 lane clip is the one place
  with slack if you're over).
- Export, upload per the submission form's required host/format.
- Move on to Task 43 (submit + confirm registration).
