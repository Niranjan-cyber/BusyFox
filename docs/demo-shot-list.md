# Demo video shot list

Maps PRD §21's scene table to what actually exists in the deployed app today, so recording
doesn't stall on "wait, does that screen show that." Checked against the live app
(https://main.dw3gwg5t169l9.amplifyapp.com/, business `biz_pulsestack`) and the frontend
fixtures (`frontend/src/fixtures/`) as of 2026-09-20.

Legend: **LIVE** = record straight off the deployed app · **FIXTURE** = record with no backend
configured (`VITE_API_BASE_URL` unset), which serves the committed fixtures · **GAP** = the
asset the script names doesn't exist yet — needs a decision, not just a recording.

| Time | Scene (§21) | Record this | Source | Status |
|---|---|---|---|---|
| 0:00–0:15 | PulseStack's goal, "Simulated · real competitors" badge | Screen 1 (`#/business`) header + Goal card | LIVE | Ready — `BusinessScreen.tsx` renders the simulated-business note and goal card from live data |
| 0:15–0:30 | Narration line, no UI | — | n/a | Ready (voiceover only) |
| 0:30–0:50 | Business & feedback screen; a real competitor review snippet next to PulseStack's own feedback | Two shots, not one screen: (a) Screen 1 "What customers say" section, then (b) a quick cut to Screen 2's Competitive lane for a real competitor signal card | LIVE | **Verify before recording**: confirm the live Competitive lane actually surfaces a Sentry/Datadog signal (not just any competitor) — Screen 1 itself has no competitor-quote UI, only a "Named competitors" chip list, so the "review snippet" has to come from Screen 2 |
| 0:50–1:10 | Live investigation replay, 3 lanes, labelled "Live run, sped up" | Screen 2 (`#/investigation`) | LIVE | Ready — Task 30/33 verified 3 lanes render live with zero console errors |
| 1:10–1:35 | Inbox → one Competitive Gap opportunity → detail: 4 claims, each with evidence, priority/confidence/value as 3 separate numbers | Screen 3 (`#/inbox`) → Screen 4 (`#/opportunities/{id}`) | **FIXTURE** (`opp_07`) | The only live opportunity, `opp_run_7f023794a99d_0`, is type `unmet_need` (not Competitive Gap) with zero verified strengths — doesn't match the script's "Competitive Gap" framing. `opp_07` in fixtures is built for exactly this beat (4 claims, real evidence set) |
| 1:35–1:55 | Evidence Check diagram live: one accepted, one rejected (missing citation), one rejected (unsupported) | Screen 4's `EvidenceCheckDiagram`, still on `opp_07` | **FIXTURE** | Live opportunity can't show this beat at all — every evidence item on `opp_run_7f023794a99d_0` is `rejected_unsupported` (zero verified strengths, see Task 26/31 notes). `opp_07`'s fixture evidence (`evd_001`=supports, `evd_023`=missing citation, `evd_031`=unsupported-but-cited) is the only asset with all three outcomes |
| 1:55–2:15 | Execution pack: offer/proposal/outreach draft citing a verified proof point, no surveillance framing | Screen 5 (`#/opportunities/opp_07/execution-pack`) | **FIXTURE** | Live opportunity has no outreach draft (same zero-verified-strengths state) — real API correctly renders "No outreach draft yet" instead of crashing, which is *not* the shot the script wants. `opp_07`'s execution pack fixture cites `sig_311`, already on-screen in `strengths_it_builds_on` |
| ~~2:15–2:25~~ | ~~Quick cut to Anveshan Precision~~ | **CUT** | n/a | Decided 2026-09-20: Anveshan Precision doesn't exist anywhere in the system (`BUSINESS_ID` is hardcoded to `biz_pulsestack`, no second scenario ever built) and won't be built on the last day. Beat is dropped; ~10s of slack opens up under the 3:00 cap — spend it on the Evidence Check beat (1:35–1:55) or leave as buffer, don't pad with a new beat |
| 2:15–2:30 | "3 planted opportunities, 2 red herrings" line, qualitative only — no hard numbers | Narration over Screen 3 (inbox) or a rejected-ideas view | LIVE | Decided 2026-09-20: Task 24/29 (gold-set labelling + eval run) stay blocked, per the Day 2 checkpoint's own hard rule — not worth the time cost on the last day. Script drops the three headline-metric numbers and keeps only the qualitative claim: *"We planted opportunities and distractions in this scenario. Here's the inbox — real signal surfaced, distractions rejected with reasons shown."* Point at the rejected-ideas list as the visual proof instead of a metrics card |
| 2:30–2:45 | Architecture diagram, Run details | `docs/architecture-diagram.md` (Mermaid, GitHub-rendered) | Ready | Built 2026-09-20. Two honesty notes baked in per decision: Bedrock is shown as IAM-wired/quota-blocked since Day 3, with OpenCode Go as the actual production inference for all 4 LLM call sites; Step Functions is shown as the deployed Day-1 skeleton (proves wiring), with the real 5-stage pipeline shown running via `scripts/run_live_pipeline.py` instead — both labelled honestly rather than glossed over. Pull real cost/timing numbers from that script's run log before recording |
| 2:45–3:00 | "What we learned"; URL and repo | — | n/a | Ready (voiceover + on-screen URL/repo, pull 1–2 lines from `LEARNING.md`) |

## Gaps — resolved 2026-09-20

All three decisions from the first pass are made; nothing left blocking a recording:

1. **Anveshan Precision** — cut, not built. See row above.
2. **Headline metrics** — qualitative framing only, Task 24/29 stay deferred.
3. **Architecture diagram** — built at `docs/architecture-diagram.md`, including the Bedrock→
   OpenCode Go and Step-Functions-vs-real-pipeline honesty notes surfaced while building it (see
   `LEARNING.md`, Day 4).

Full script now fits at ~2:50 with ~10s of slack under the 3:00 cap.
