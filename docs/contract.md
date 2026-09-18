# Contract: entities and API surface

Human-readable mirror of the code. **The code is the source of truth** — if
this file and `backend/schemas/entities.py` / `frontend/src/types/entities.ts`
ever disagree, the code wins and this file needs fixing (CLAUDE.md).

- Backend types: `backend/schemas/entities.py` (Pydantic)
- Frontend types: `frontend/src/types/entities.ts` (TypeScript, field-for-field mirror)
- Full field-level rationale: PRD §14 (`opportunity_engine_prd_v8.md`)

## Provenance chain (§14.0)

```
SourceDocument → Evidence → Claim → Signal ──┐
                                              ↓
                                         Opportunity → Target → ExecutionPack
```

Business and Run are the containing entities: a Business runs many Runs; a
Run produces SourceDocuments, Signals and Opportunities.

## The nine core entities + Competitor

| Entity | PRD § | Id prefix | DynamoDB key prefix | Notes |
|---|---|---|---|---|
| Business | §14.1 | `biz_` | `BIZ#` | One per hackathon demo: `biz_pulsestack` |
| Run | §14.3 | `run_` | `RUN#` | Carries `agent_invocations[]` — actual usage against the §10.1a contract |
| SourceDocument | §14.4 | `src_` | `SRC#` | One doc can back many Evidence items |
| Evidence | §14.5 / §12 | `evd_` | `EVD#` | `quote_hash`, `claim_support`, `freshness` live on the item itself |
| Claim | §14.6 | `claim_` | `CLAIM#` | `type` ∈ `why_this \| why_you \| why_now \| mechanism`; one evidence item can support many claims |
| Signal | §14.7 | `sig_` | `SIG#` | The **only** shape a research agent may emit (§10.1a) |
| Opportunity | §14.8 | `opp_` | `OPP#` | No composite score (§13.1) — `evidence_confidence`, `priority`, `value` stay separate |
| Target | §14.9 | `tgt_` | `TGT#` | `observed_facts[]` always rendered before `account_fit_inference` |
| ExecutionPack | §14.10 | `pack_` | `PACK#` | Only generated from a gate-passed Opportunity (§10.3) |
| Competitor | §14.2 | `cmp_` | `CMP#` | Thin supporting entity — a labelled view over SourceDocuments/Evidence for one named competitor, not a tenth core entity |

## Shared enum: Observed / Inferred / Assumed (§13.3)

`OBSERVED | INFERRED | ASSUMED` — the one label every claim-bearing field
must visibly carry when rendered. Concretely typed on each `ValueAssumption`
in `Opportunity.value.assumptions[]` (§13.2); applied by rendering
convention elsewhere (e.g. a Claim's `why_this/why_you/why_now` types are
OBSERVED, `mechanism` is INFERRED — see §13.3 for the worked example).

## Research agents vs. Synthesis agent (§10.1a) — structurally enforced

- `ResearchAgentOutput` (Market / Feedback Pipeline / Competitor agents): `{ run_id, produced_by, signals: Signal[], truncated }` — **no `opportunities` field exists on this type**, not just unused by convention.
- `SynthesisAgentOutput` (Synthesis agent only): `{ run_id, candidate_opportunities: Opportunity[], claims: Claim[] }` — `claims` carries the Claim rows `claim_ids` resolve to, `status: hypothesis` and `evidence_ids: []` until later stages fill them in. Evidence Check (Task 18) attaches the real `evidence_ids` and populates each Evidence item's `claim_support`/`freshness`; Quality Gate (Task 19) reads those to set the Claim's final `status` (`verified` if its evidence supports it and the opportunity's evidence diversity check passes, `hypothesis` if supported but diversity-capped, `unsupported` otherwise).
- Quality Gate + Ranker (Task 19, `backend/pipeline/quality_gate.py`) is the only component that overwrites an `Opportunity`'s `evidence_diversity`/`evidence_confidence`/`priority`/`flags` for real (Synthesis only fills them provisionally, §10.2). It returns three buckets — ranked (High/Medium/Low, not Blocked), blocked (shown separately, §13.1), and rejected (`{opportunity_id, opportunity_type, reason, stage}`, feeding "Ideas we rejected"/`RejectedIdea`) — never a fourth "merged" bucket; a losing duplicate (check 11) is rejected with reason `duplicate_merged_into:<id>`. `value` is left untouched — the §13.2 value model is Day 3 scope, not this task's.

## API surface (§15 + implied screen endpoints)

Every endpoint returns a Task-1-shaped payload (types above) and is backed
today by a stub Lambda returning fixture data — no real research/synthesis
logic yet (that's Day 2). §15 names four endpoints explicitly; the other
five are the gap PRD §15 leaves implicit for screens 1, 3, 4, 5 (flagged in
`tasks/plan.md` Task 2's acceptance criteria rather than discovered later).

| Method | Path | Purpose | Screen | Response type | Source |
|---|---|---|---|---|---|
| GET | `/businesses/{id}` | Business profile: name, capability chips, ICP, goal | 1 | `Business` | implied |
| GET | `/businesses/{id}/feedback-summary` | "What customers love / complain about" — signals from the business's own feedback, by polarity | 1 | `Signal[]` | implied |
| GET | `/businesses/{id}/opportunities` | Opportunity Inbox list (goal bar + cards by type + rejected ideas) | 3 | `Opportunity[]` | implied |
| GET | `/opportunities/{id}` | Opportunity detail: mechanism, strengths, pains, competitive context, evidence diversity, confidence, priority, value | 4 | `Opportunity` | implied |
| GET | `/opportunities/{id}/claims` | List an opportunity's Claims, each with `evidence_ids` | 4 | `Claim[]` | §15 |
| GET | `/claims/{id}/evidence` | Resolve one Claim's full evidence chain (Evidence → SourceDocument) | 4 | `Evidence[]` | §15 |
| GET | `/opportunities/{id}/execution-pack` | Offer, proposal, outreach drafts | 5 | `ExecutionPack` | implied |
| GET | `/competitors` | Named competitors + sentiment summaries | — | `Competitor[]` | §15 |
| GET | `/competitors/{id}/evidence/{evidenceId}/live` | Re-fetch/re-verify a competitor quote; falls back Live → Cached → Demo Fixture (§7.2/§12.2) | 4 (evidence drawer) | `Evidence` | §15 |

Screen 2 (Live investigation) is intentionally excluded — it's a streaming
view over Run/Signal events, not a simple REST list/detail shape, and is
Day 2 pipeline work, not part of Task 2's stub contract.

Stub Lambda handlers: `backend/handlers/*_stub.py`. Fixture data:
`backend/fixtures/fixtures.py` (single source, built from the Task 1 models
so a fixture can never drift from the schema without failing to import).

## Verification

- `backend/tests/test_stub_handlers.py` invokes every handler directly and
  validates its response body against the matching Pydantic model — the
  `curl`-equivalent check for a repo with no live AWS deployment yet
  (deployment is Task 6).
- API Gateway route definitions: `infra/api-gateway.yaml` (SAM template —
  routes exist in code now; Task 6 deploys them for real).
