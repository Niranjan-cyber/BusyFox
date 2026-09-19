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
| 2:15–2:25 | Quick cut to Anveshan Precision running the same engine | — | **GAP** | Anveshan Precision doesn't exist anywhere in the running system. `BUSINESS_ID` is hardcoded to `biz_pulsestack` in `App.tsx` ("the business is fixed for the hackathon scope... when a second one exists it becomes part of the route, not a constant") — there is no second business, scenario, or fixture set for it. Needs a decision now: build a second scenario, cut this beat, or replace it with something that exists |
| 2:25–2:40 | "3 planted opportunities, 2 red herrings" line + three headline metrics (opportunity recall, evidence validity, noise rejection, §19.1) | — | **GAP** | Blocked on Task 24 (gold-set labelling, deferred) and Task 29 (eval run, blocked on 24) per `tasks/todo.md`. No computed numbers exist. Needs a decision: unblock Task 24/29 before recording, or soften this beat to qualitative framing without hard numbers |
| 2:40–2:50 | Architecture diagram, Run details cost panel | — | **GAP** | No architecture diagram file exists in the repo. No cost/run-details panel is built in the UI (PRD §19.1's own note says this is fine as a video-only overlay, not a dedicated screen) — diagram needs to be made, cost numbers pulled from a real run's logs/DynamoDB record |
| 2:50–3:00 | "What we learned"; URL and repo | — | n/a | Ready (voiceover + on-screen URL/repo, pull 1–2 lines from `LEARNING.md`) |

## Decisions needed before recording (blocking, in priority order)

1. **Anveshan Precision (2:15–2:25)** — build it, cut it, or substitute. Cutting it loses the
   "generality" beat entirely; the PRD doesn't offer a fallback.
2. **Headline metrics (2:25–2:40)** — decide whether Task 24/29 get unblocked today given the
   feature-freeze checkpoint is already open, or the beat runs qualitative-only.
3. **Architecture diagram (2:40–2:50)** — smallest lift of the three gaps; can be built directly
   from `infra/` (API Gateway, Step Functions, Lambda, DynamoDB, S3, Amplify are all already
   deployed, just not drawn).

Everything else on the table is recordable today, either live or against the committed `opp_07`
fixture — no code changes needed for those beats.
