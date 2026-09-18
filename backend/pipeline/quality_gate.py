"""Quality Gate + Ranker (Task 19) — code implementing all 14 checks across
the four §11 stages (truth, relevance, commerciality, quality/safety).
Derives `evidence_confidence` and `priority` from the §13.1 rule table only,
never a composite score. Rejected candidates are stored with their reason
and failed-gate stage, for "Ideas we rejected" (frontend's `RejectedIdea`).

Runs after Evidence Check (Task 18): takes each candidate opportunity's
Claims plus the real Evidence Task 18 produced, and decides what's allowed
into the inbox. It also resolves each Claim's final `status`
(verified/hypothesis/unsupported, §14.6) — Evidence Check only fills in
`evidence_ids`, it never touches `status`.

Two things explicitly out of scope here, both flagged rather than faked:
- §13.2's value model (`Opportunity.value`) — scheduled Day 3 (tasks/plan.md
  Phase 3), so `value` passes through untouched from Synthesis's placeholder.
- Gate check 14 (account evidence integrity, §11.4) — it gates a Target's
  `account_fit_inference` against its `observed_facts`, and no Target exists
  yet at this point in the pipeline (Action Agent is Day 3). `check_account_evidence_integrity`
  below is a real, callable check for whenever Targets exist; `run_quality_gate`
  doesn't call it because it has nothing to call it on yet.
"""

from __future__ import annotations

from typing import NamedTuple, Optional
from urllib.parse import urlparse

from backend.schemas.entities import (
    Business,
    Claim,
    ClaimStatus,
    ClaimSupportStatus,
    ClaimType,
    Evidence,
    EvidenceConfidence,
    EvidenceDiversity,
    FreshnessStatus,
    Opportunity,
    PainToFix,
    Priority,
    Signal,
    SourceKind,
    Target,
)

# ponytail: 1-5 scale inferred from the PRD's own worked example
# (§14.8 `"severity": 3`) — no scale is stated explicitly. Revisit against
# Task 24's gold set if this threshold turns out wrong in practice.
_SEVERE_PAIN_THRESHOLD = 4

_NARRATIVE_CLAIM_TYPES = frozenset({ClaimType.WHY_THIS, ClaimType.WHY_YOU, ClaimType.WHY_NOW})
_REQUIRED_CLAIM_TYPES = frozenset({ClaimType.WHY_THIS, ClaimType.WHY_YOU, ClaimType.WHY_NOW, ClaimType.MECHANISM})

_PRIORITY_RANK = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}


class RejectedIdea(NamedTuple):
    """Mirrors frontend `RejectedIdea` (`frontend/src/lib/viewModels.ts`)
    field-for-field except `title`, which is a presentational concern for
    whoever builds the view model, not something the gate computes."""

    opportunity_id: str
    opportunity_type: str
    rejected_because: str
    failed_gate: str


class QualityGateResult(NamedTuple):
    ranked: list[Opportunity]  # High -> Medium -> Low, Blocked excluded (§13.1)
    blocked: list[Opportunity]  # shown separately, never ranked against clear opportunities
    rejected: list[RejectedIdea]
    claims: list[Claim]  # same claims Evidence Check produced, `status` now final


def quote_found(evidence: Evidence) -> bool:
    """§12.1: Evidence Check (Task 18) always emits an Evidence row, even
    when the quote wasn't found — it sets `confidence=0.0` on that exact
    branch (`build_evidence`'s "quote not found" path), never for a real
    model call, so that pairing is a safe proxy for "quote_found=true"
    without Evidence needing a dedicated boolean field of its own."""

    return not (evidence.claim_support.status == ClaimSupportStatus.UNSUPPORTED and evidence.claim_support.confidence == 0.0)


# ---------------------------------------------------------------------------
# §11.1 Truth
# ---------------------------------------------------------------------------


def check_verified_evidence(opp_evidence: list[Evidence]) -> Optional[str]:
    """Check 1: >=1 evidence item with quote_found=true."""

    if not any(quote_found(e) for e in opp_evidence):
        return "no_verified_evidence"
    return None


def check_claim_evidence_support(opp_evidence: list[Evidence]) -> Optional[str]:
    """Check 2: of the quotes that were found, at least one must actually
    support its claim — not merely exist in a source."""

    found = [e for e in opp_evidence if quote_found(e)]
    if found and not any(e.claim_support.status != ClaimSupportStatus.UNSUPPORTED for e in found):
        return "citation_exists_but_unsupported"
    return None


def compute_evidence_diversity(opp_evidence: list[Evidence]) -> EvidenceDiversity:
    """§11.2 check 6 — measured, not asserted. `underlying_event_risk` stays
    "unknown" by design (§11.2): detecting shared-underlying-event risk
    reliably is out of scope, so the field says so rather than guessing."""

    return EvidenceDiversity(
        source_kind_count=len({e.source_kind for e in opp_evidence}),
        domain_count=len({urlparse(e.url).netloc for e in opp_evidence if e.url}),
        author_count=len({e.author for e in opp_evidence if e.author}),
        underlying_event_risk="unknown",
    )


def diversity_passes(diversity: EvidenceDiversity) -> bool:
    return diversity.source_kind_count >= 2


# ---------------------------------------------------------------------------
# §11.2 Relevance
# ---------------------------------------------------------------------------


def check_capability(opportunity: Opportunity, business: Business) -> Optional[str]:
    """Check 5. No structured link exists yet between an Opportunity and the
    Business.capabilities it depends on (§9.5's mechanism is free text) — so
    this is a keyword match against unconfirmed capability keys in the
    mechanism, same treatment as Evidence Check's `freshness_limit_days`
    heuristic (`backend/pipeline/evidence_check.py`).
    ponytail: text-match heuristic, not a real capability graph; revisit if
    gold-set labelling (Task 24) shows the mechanism text doesn't carry the
    capability key literally."""

    unconfirmed = {c.key for c in business.capabilities if not c.confirmed}
    if not unconfirmed:
        return None

    mechanism = opportunity.opportunity_mechanism
    text = f"{mechanism.statement} {mechanism.actionable_because}".lower()
    mentioned = sorted(key for key in unconfirmed if key.lower() in text)
    if mentioned:
        return f"depends_on_unconfirmed_capability:{','.join(mentioned)}"
    return None


def check_mechanism_present(opportunity: Opportunity) -> Optional[str]:
    """Check 7 — defensive re-check; Synthesis's own self-critique
    (`mechanism_is_concrete`, Task 17) already enforces this before a
    candidate exists, but the gate is the deterministic component of
    record (§11 intro) and shouldn't just trust its caller."""

    mechanism = opportunity.opportunity_mechanism
    if not (mechanism.statement.strip() and mechanism.shared_segment.strip() and mechanism.actionable_because.strip()):
        return "mechanism_missing"
    return None


# ---------------------------------------------------------------------------
# §11.3 Commerciality
# ---------------------------------------------------------------------------


def check_mandatory_fields(opportunity: Opportunity, claims_by_id: dict[str, Claim]) -> Optional[str]:
    """Check 8 — the four required claim types (§14.8), each non-empty; plus
    a value model, always present as a non-optional field on Opportunity."""

    opp_claims = [claims_by_id[cid] for cid in opportunity.claim_ids if cid in claims_by_id]
    present_types = {c.type for c in opp_claims}
    if present_types != _REQUIRED_CLAIM_TYPES or any(not c.text.strip() for c in opp_claims):
        return "incomplete_opportunity"
    return None


def check_actionable(opportunity: Opportunity, narrative_claims_verified: bool) -> Optional[str]:
    """Check 9 — a concrete next step exists, and the narrative claims all
    cleared Evidence Check (verified or capped-confidence hypothesis, i.e.
    not `unsupported` — see the module docstring on claim status)."""

    has_next_step = bool(opportunity.pains_to_fix_first or opportunity.competitive_context or opportunity.strengths_it_builds_on)
    if not has_next_step or not narrative_claims_verified:
        return "not_actionable"
    return None


# ---------------------------------------------------------------------------
# §11.4 Quality and safety
# ---------------------------------------------------------------------------


def check_attribution_safety(opportunity: Opportunity, signals_by_id: dict[str, Signal]) -> Optional[str]:
    """Check 10 — competitors are always real (§18.1); no competitive claim
    may trace back to PulseStack's own simulated data, and no competitive
    claim may cite a signal that was never actually collected."""

    for item in opportunity.competitive_context:
        signal = signals_by_id.get(item.signal_id)
        if signal is None:
            return "invented_competitor_claim"
        if signal.source_kind == SourceKind.SIMULATED:
            return "simulated_claim_attributed_to_competitor"
    return None


def _signal_ids(opportunity: Opportunity) -> set[str]:
    return (
        {s.signal_id for s in opportunity.strengths_it_builds_on}
        | {p.signal_id for p in opportunity.pains_to_fix_first}
        | {c.signal_id for c in opportunity.competitive_context}
    )


def _merge_duplicates(survivors: list[Opportunity]) -> tuple[list[Opportunity], list[RejectedIdea]]:
    """Check 11 — same type, >=50% overlapping signals with a stronger
    opportunity, merges into it. "Stronger" ranks by evidence_confidence;
    ties keep the earlier candidate, since the §13.2 value-model tie-break
    the PRD describes doesn't exist yet (Day 3 scope, see module docstring)."""

    confidence_rank = {EvidenceConfidence.HIGH: 2, EvidenceConfidence.MEDIUM: 1, EvidenceConfidence.LOW: 0}
    dropped: set[str] = set()
    rejected: list[RejectedIdea] = []

    for i, a in enumerate(survivors):
        if a.id in dropped:
            continue
        a_signals = _signal_ids(a)
        for b in survivors[i + 1 :]:
            if b.id in dropped or b.type != a.type or not a_signals:
                continue
            b_signals = _signal_ids(b)
            if not b_signals:
                continue
            overlap = len(a_signals & b_signals) / min(len(a_signals), len(b_signals))
            if overlap < 0.5:
                continue
            weaker, stronger = (b, a) if confidence_rank[a.evidence_confidence] >= confidence_rank[b.evidence_confidence] else (a, b)
            dropped.add(weaker.id)
            rejected.append(RejectedIdea(weaker.id, weaker.type.value, f"duplicate_merged_into:{stronger.id}", "quality_safety"))

    return [o for o in survivors if o.id not in dropped], rejected


def check_account_evidence_integrity(target: Target) -> Optional[str]:
    """Check 14 — a target's `account_fit_inference` is never shown without
    its `observed_facts`. Not called by `run_quality_gate` (no Target exists
    at this stage of the pipeline, see module docstring); ready for whenever
    Action Agent (Day 3) starts producing Targets."""

    if not target.observed_facts:
        return "account_fit_inference_without_observed_facts"
    return None


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------


def _priority_from_rule_table(confidence: EvidenceConfidence, fix_first: bool) -> Priority:
    """§13.1 — a rule table, not arithmetic. Mirrors the shape of Synthesis's
    own provisional `_provisional_priority` (Task 17), now with the real,
    Quality-Gate-derived confidence instead of a fixed LOW."""

    if fix_first:
        return Priority.BLOCKED
    return {EvidenceConfidence.HIGH: Priority.HIGH, EvidenceConfidence.MEDIUM: Priority.MEDIUM, EvidenceConfidence.LOW: Priority.LOW}[
        confidence
    ]


def run_quality_gate(
    candidates: list[Opportunity],
    claims: list[Claim],
    evidence: list[Evidence],
    contradictions: dict[str, bool],
    signals: list[Signal],
    business: Business,
) -> QualityGateResult:
    """Entry point Task 21's orchestrator calls between Evidence Check and
    DynamoDB persistence."""

    claims_by_id = {c.id: c for c in claims}
    evidence_by_id = {e.id: e for e in evidence}
    signals_by_id = {s.id: s for s in signals}

    rejected: list[RejectedIdea] = []
    survivors: list[Opportunity] = []
    final_claims: dict[str, Claim] = dict(claims_by_id)

    for opp in candidates:
        opp_claims = [claims_by_id[cid] for cid in opp.claim_ids if cid in claims_by_id]
        opp_evidence = [evidence_by_id[eid] for c in opp_claims for eid in c.evidence_ids if eid in evidence_by_id]

        failure = check_verified_evidence(opp_evidence) or check_claim_evidence_support(opp_evidence)
        if failure:
            rejected.append(RejectedIdea(opp.id, opp.type.value, failure, "truth"))
            continue

        failure = check_capability(opp, business) or check_mechanism_present(opp)
        if failure:
            rejected.append(RejectedIdea(opp.id, opp.type.value, failure, "relevance"))
            continue

        diversity = compute_evidence_diversity(opp_evidence)
        passes_diversity = diversity_passes(diversity)

        flags: list[str] = []
        why_now_all_stale = False
        for claim in opp_claims:
            claim_evidence = [evidence_by_id[eid] for eid in claim.evidence_ids if eid in evidence_by_id]
            verified = any(e.claim_support.status != ClaimSupportStatus.UNSUPPORTED for e in claim_evidence)
            status = (
                ClaimStatus.UNSUPPORTED
                if not verified
                else (ClaimStatus.HYPOTHESIS if not passes_diversity else ClaimStatus.VERIFIED)
            )
            final_claims[claim.id] = claim.model_copy(update={"status": status})

            stale = bool(claim_evidence) and all(e.freshness.status == FreshnessStatus.STALE for e in claim_evidence)
            if stale:
                if "stale_evidence" not in flags:
                    flags.append("stale_evidence")
                if claim.type == ClaimType.WHY_NOW:
                    why_now_all_stale = True

        if why_now_all_stale:
            # §11.4: stale evidence can never be the sole support for a "why now" claim.
            rejected.append(RejectedIdea(opp.id, opp.type.value, "why_now_rests_solely_on_stale_evidence", "truth"))
            continue

        narrative_verified = _NARRATIVE_CLAIM_TYPES <= {c.type for c in opp_claims} and all(
            final_claims[c.id].status != ClaimStatus.UNSUPPORTED for c in opp_claims if c.type in _NARRATIVE_CLAIM_TYPES
        )

        failure = (
            check_mandatory_fields(opp, claims_by_id)
            or check_actionable(opp, narrative_verified)
            or check_attribution_safety(opp, signals_by_id)
        )
        if failure:
            stage = "quality_safety" if failure in {"invented_competitor_claim", "simulated_claim_attributed_to_competitor"} else "commerciality"
            rejected.append(RejectedIdea(opp.id, opp.type.value, failure, stage))
            continue

        if any(contradictions.get(c.id, False) for c in opp_claims):
            flags.append("contradiction_present")
            confidence = EvidenceConfidence.MEDIUM if passes_diversity else EvidenceConfidence.LOW
        else:
            confidence = EvidenceConfidence.HIGH if passes_diversity else EvidenceConfidence.LOW

        if any(p.severity >= _SEVERE_PAIN_THRESHOLD for p in opp.pains_to_fix_first):
            flags.append("fix_first_risk")

        priority = _priority_from_rule_table(confidence, fix_first=bool(opp.pains_to_fix_first))

        survivors.append(
            opp.model_copy(
                update={
                    "evidence_diversity": diversity,
                    "evidence_confidence": confidence,
                    "priority": priority,
                    "flags": flags,
                }
            )
        )

    survivors, dup_rejected = _merge_duplicates(survivors)
    rejected.extend(dup_rejected)

    ranked = sorted((o for o in survivors if o.priority != Priority.BLOCKED), key=lambda o: _PRIORITY_RANK[o.priority])
    blocked = [o for o in survivors if o.priority == Priority.BLOCKED]

    return QualityGateResult(ranked=ranked, blocked=blocked, rejected=rejected, claims=list(final_claims.values()))


if __name__ == "__main__":
    from datetime import datetime

    from backend.schemas.entities import (
        ClaimSupport,
        CompetitiveContextItem,
        Freshness,
        Goal,
        MonthlyRange,
        ObservedInferredAssumed,
        OpportunityMechanism,
        OpportunityType,
        PainToFix,
        Polarity,
        Pricing,
        RetrievalMode,
        SignalReason,
        ValueAssumption,
        ValueModel,
    )

    _NOW = datetime(2026, 9, 18)
    _BUSINESS = Business(
        id="biz_1", name="PulseStack", is_simulated=True, industry="observability", playbook_id="p1",
        icp=["eng teams"], pricing=Pricing(team_usd_month=99.0), current_mrr_usd=8000.0,
        goal=Goal(metric="mrr", change_usd=7000, horizon_days=90),
        capabilities=[], named_competitors=["Sentry"], data_assets=[], created_at=_NOW,
    )
    _SIGNALS = [Signal(id="sig_1", run_id="run_1", source_kind=SourceKind.HN, aspect="pricing_pain", polarity=Polarity.NEGATIVE, claim_text="[Sentry] teams reconsidering pricing", evidence_ids=[], produced_by="competitor_agent")]
    _CLAIMS = [
        Claim(id="claim_why_this", opportunity_id="opp_1", type=ClaimType.WHY_THIS, text="Teams cite Sentry pricing pain.", status=ClaimStatus.HYPOTHESIS, evidence_ids=["evd_1"]),
        Claim(id="claim_why_you", opportunity_id="opp_1", type=ClaimType.WHY_YOU, text="PulseStack already serves this segment.", status=ClaimStatus.HYPOTHESIS, evidence_ids=["evd_1"]),
        Claim(id="claim_why_now", opportunity_id="opp_1", type=ClaimType.WHY_NOW, text="Complaints are recent.", status=ClaimStatus.HYPOTHESIS, evidence_ids=["evd_1"]),
        Claim(id="claim_mechanism", opportunity_id="opp_1", type=ClaimType.MECHANISM, text="Low-noise positioning fits this segment.", status=ClaimStatus.HYPOTHESIS, evidence_ids=["evd_1"]),
    ]
    _EVIDENCE = [
        Evidence(
            id="evd_1", source_document_id="src_1", source_kind=SourceKind.HN, retrieval_mode=RetrievalMode.LIVE,
            url="https://news.ycombinator.com/item?id=1", retrieved_at=_NOW, author="alice", published_at=_NOW,
            quote="teams reconsidering pricing", quote_hash="sha256:x",
            claim_support=ClaimSupport(status=ClaimSupportStatus.SUPPORTS, confidence=0.9, reason="on point"),
            freshness=Freshness(status=FreshnessStatus.FRESH, age_days=0, limit_days=180),
        )
    ]
    _OPPORTUNITY = Opportunity(
        id="opp_1", type=OpportunityType.COMPETITIVE_GAP, claim_ids=[c.id for c in _CLAIMS],
        opportunity_mechanism=OpportunityMechanism(statement="Low-noise positioning wins this segment.", shared_segment="small eng teams", actionable_because="already serves this segment"),
        strengths_it_builds_on=[SignalReason(signal_id="sig_1", reason="x")],
        pains_to_fix_first=[], competitive_context=[CompetitiveContextItem(signal_id="sig_1", competitor="Sentry", pattern="competitive_gap")],
        evidence_diversity=EvidenceDiversity(source_kind_count=0, domain_count=0, author_count=0, underlying_event_risk="unknown"),
        evidence_confidence=EvidenceConfidence.LOW, priority=Priority.LOW,
        value=ValueModel(model="saas_arr", assumptions=[ValueAssumption(key="pending_quality_gate", label=ObservedInferredAssumed.ASSUMED, description="n/a")], monthly_usd=MonthlyRange(low=0.0, high=0.0)),
    )

    _result = run_quality_gate([_OPPORTUNITY], _CLAIMS, _EVIDENCE, contradictions={cid: False for cid in ["claim_why_this", "claim_why_you", "claim_why_now", "claim_mechanism"]}, signals=_SIGNALS, business=_BUSINESS)
    assert len(_result.ranked) == 1
    assert _result.ranked[0].evidence_confidence == EvidenceConfidence.LOW  # only 1 source kind -> diversity-capped
    assert _result.ranked[0].priority == Priority.LOW
    assert _result.rejected == []
    assert all(c.status == ClaimStatus.HYPOTHESIS for c in _result.claims)  # capped, not unsupported
    print("ok")
