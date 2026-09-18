"""Quality Gate + Ranker (Task 19) — §11 truth/relevance/commerciality/
quality-safety checks, §13.1 rule-table confidence/priority derivation."""

from __future__ import annotations

from datetime import datetime

from backend.pipeline.quality_gate import (
    RejectedIdea,
    check_account_evidence_integrity,
    check_actionable,
    check_attribution_safety,
    check_capability,
    check_claim_evidence_support,
    check_mandatory_fields,
    check_mechanism_present,
    check_verified_evidence,
    compute_evidence_diversity,
    diversity_passes,
    quote_found,
    run_quality_gate,
)
from backend.schemas.entities import (
    Business,
    Capability,
    Claim,
    ClaimStatus,
    ClaimSupport,
    ClaimSupportStatus,
    ClaimType,
    CompetitiveContextItem,
    Evidence,
    EvidenceConfidence,
    EvidenceDiversity,
    Freshness,
    FreshnessStatus,
    Goal,
    MonthlyRange,
    ObservedFact,
    ObservedInferredAssumed,
    Opportunity,
    OpportunityMechanism,
    OpportunityType,
    PainToFix,
    Polarity,
    Priority,
    Pricing,
    RetrievalMode,
    Signal,
    SignalReason,
    SourceKind,
    Target,
    ValueAssumption,
    ValueModel,
)

_NOW = datetime(2026, 9, 18)


def _business(**overrides) -> Business:
    defaults = dict(
        id="biz_1", name="PulseStack", is_simulated=True, industry="observability", playbook_id="p1",
        icp=["eng teams"], pricing=Pricing(team_usd_month=99.0), current_mrr_usd=8000.0,
        goal=Goal(metric="mrr", change_usd=7000, horizon_days=90),
        capabilities=[], named_competitors=["Sentry"], data_assets=[], created_at=_NOW,
    )
    defaults.update(overrides)
    return Business(**defaults)


def _support(status=ClaimSupportStatus.SUPPORTS, confidence=0.9) -> ClaimSupport:
    return ClaimSupport(status=status, confidence=confidence, reason="x")


def _freshness(status=FreshnessStatus.FRESH, age_days=1, limit_days=180) -> Freshness:
    return Freshness(status=status, age_days=age_days, limit_days=limit_days)


def _evidence(**overrides) -> Evidence:
    defaults = dict(
        id="evd_1", source_document_id="src_1", source_kind=SourceKind.HN, retrieval_mode=RetrievalMode.LIVE,
        url="https://news.ycombinator.com/item?id=1", retrieved_at=_NOW, author="alice", published_at=_NOW,
        quote="teams reconsidering pricing", quote_hash="sha256:x",
        claim_support=_support(), freshness=_freshness(),
    )
    defaults.update(overrides)
    return Evidence(**defaults)


def _quote_not_found_evidence(**overrides) -> Evidence:
    overrides.setdefault("claim_support", ClaimSupport(status=ClaimSupportStatus.UNSUPPORTED, confidence=0.0, reason="quote not found in source text"))
    return _evidence(**overrides)


def _claim(claim_id="claim_1", claim_type=ClaimType.WHY_THIS, evidence_ids=("evd_1",), **overrides) -> Claim:
    defaults = dict(id=claim_id, opportunity_id="opp_1", type=claim_type, text=f"{claim_type.value} text", status=ClaimStatus.HYPOTHESIS, evidence_ids=list(evidence_ids))
    defaults.update(overrides)
    return Claim(**defaults)


def _four_claims(evidence_ids=("evd_1",)) -> list[Claim]:
    return [
        _claim("claim_why_this", ClaimType.WHY_THIS, evidence_ids),
        _claim("claim_why_you", ClaimType.WHY_YOU, evidence_ids),
        _claim("claim_why_now", ClaimType.WHY_NOW, evidence_ids),
        _claim("claim_mechanism", ClaimType.MECHANISM, evidence_ids),
    ]


def _opportunity(**overrides) -> Opportunity:
    claims = overrides.pop("claims", None) or _four_claims()
    defaults = dict(
        id="opp_1", type=OpportunityType.COMPETITIVE_GAP, claim_ids=[c.id for c in claims],
        opportunity_mechanism=OpportunityMechanism(statement="Low-noise positioning wins this segment.", shared_segment="small eng teams", actionable_because="already serves this segment"),
        strengths_it_builds_on=[SignalReason(signal_id="sig_1", reason="x")],
        pains_to_fix_first=[], competitive_context=[],
        evidence_diversity=EvidenceDiversity(source_kind_count=0, domain_count=0, author_count=0, underlying_event_risk="unknown"),
        evidence_confidence=EvidenceConfidence.LOW, priority=Priority.LOW,
        value=ValueModel(model="saas_arr", assumptions=[ValueAssumption(key="pending_quality_gate", label=ObservedInferredAssumed.ASSUMED, description="n/a")], monthly_usd=MonthlyRange(low=0.0, high=0.0)),
    )
    defaults.update(overrides)
    return Opportunity(**defaults)


def _signal(**overrides) -> Signal:
    defaults = dict(id="sig_1", run_id="run_1", source_kind=SourceKind.HN, aspect="pricing_pain", polarity=Polarity.NEGATIVE, claim_text="[Sentry] pricing pain", evidence_ids=[], produced_by="competitor_agent")
    defaults.update(overrides)
    return Signal(**defaults)


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------


def test_quote_found_true_for_real_support_call():
    assert quote_found(_evidence())


def test_quote_found_false_for_task18_no_quote_sentinel():
    assert not quote_found(_quote_not_found_evidence())


def test_check_verified_evidence_rejects_when_no_quote_found():
    assert check_verified_evidence([_quote_not_found_evidence()]) == "no_verified_evidence"


def test_check_verified_evidence_passes_with_one_found_quote():
    assert check_verified_evidence([_evidence()]) is None


def test_check_claim_evidence_support_rejects_when_found_but_unsupported():
    evidence = [_evidence(claim_support=_support(status=ClaimSupportStatus.UNSUPPORTED, confidence=0.7))]
    assert check_claim_evidence_support(evidence) == "citation_exists_but_unsupported"


def test_check_claim_evidence_support_passes_with_one_supporting_item():
    evidence = [_evidence(claim_support=_support(status=ClaimSupportStatus.UNSUPPORTED, confidence=0.7)), _evidence(id="evd_2")]
    assert check_claim_evidence_support(evidence) is None


def test_compute_evidence_diversity_counts_kinds_domains_authors():
    evidence = [
        _evidence(source_kind=SourceKind.HN, url="https://news.ycombinator.com/item?id=1", author="alice"),
        _evidence(id="evd_2", source_kind=SourceKind.GITHUB, url="https://github.com/x/y/issues/1", author="bob"),
    ]
    diversity = compute_evidence_diversity(evidence)
    assert diversity.source_kind_count == 2
    assert diversity.domain_count == 2
    assert diversity.author_count == 2
    assert diversity.underlying_event_risk == "unknown"


def test_diversity_passes_requires_two_source_kinds():
    assert not diversity_passes(EvidenceDiversity(source_kind_count=1, domain_count=1, author_count=1, underlying_event_risk="unknown"))
    assert diversity_passes(EvidenceDiversity(source_kind_count=2, domain_count=1, author_count=1, underlying_event_risk="unknown"))


def test_check_capability_passes_when_no_unconfirmed_capability_mentioned():
    business = _business(capabilities=[Capability(key="sso", confirmed=False)])
    opp = _opportunity()
    assert check_capability(opp, business) is None


def test_check_capability_rejects_when_mechanism_depends_on_unconfirmed_capability():
    business = _business(capabilities=[Capability(key="sso", confirmed=False)])
    opp = _opportunity(opportunity_mechanism=OpportunityMechanism(statement="Needs sso to close.", shared_segment="enterprise", actionable_because="sso unlocks the deal"))
    result = check_capability(opp, business)
    assert result == "depends_on_unconfirmed_capability:sso"


def test_check_mechanism_present_rejects_blank_field():
    opp = _opportunity(opportunity_mechanism=OpportunityMechanism(statement="x", shared_segment="", actionable_because="y"))
    assert check_mechanism_present(opp) == "mechanism_missing"


def test_check_mandatory_fields_rejects_when_a_claim_type_is_missing():
    claims = _four_claims()[:3]  # drop mechanism claim
    opp = _opportunity(claims=claims, claim_ids=[c.id for c in claims])
    claims_by_id = {c.id: c for c in claims}
    assert check_mandatory_fields(opp, claims_by_id) == "incomplete_opportunity"


def test_check_actionable_rejects_with_no_next_step():
    opp = _opportunity(strengths_it_builds_on=[], pains_to_fix_first=[], competitive_context=[])
    assert check_actionable(opp, narrative_claims_verified=True) == "not_actionable"


def test_check_actionable_rejects_when_narrative_claims_unverified():
    opp = _opportunity()
    assert check_actionable(opp, narrative_claims_verified=False) == "not_actionable"


def test_check_attribution_safety_rejects_simulated_signal():
    opp = _opportunity(competitive_context=[CompetitiveContextItem(signal_id="sig_1", competitor="Sentry", pattern="competitive_gap")])
    signals_by_id = {"sig_1": _signal(source_kind=SourceKind.SIMULATED)}
    assert check_attribution_safety(opp, signals_by_id) == "simulated_claim_attributed_to_competitor"


def test_check_attribution_safety_rejects_invented_signal():
    opp = _opportunity(competitive_context=[CompetitiveContextItem(signal_id="sig_missing", competitor="Sentry", pattern="competitive_gap")])
    assert check_attribution_safety(opp, {}) == "invented_competitor_claim"


def test_check_attribution_safety_passes_for_real_signal():
    opp = _opportunity(competitive_context=[CompetitiveContextItem(signal_id="sig_1", competitor="Sentry", pattern="competitive_gap")])
    assert check_attribution_safety(opp, {"sig_1": _signal()}) is None


def test_check_account_evidence_integrity_rejects_missing_observed_facts():
    from backend.schemas.entities import AccountFitInference, SuggestedContact

    target = Target(
        id="tgt_1", opportunity_id="opp_1", organisation="Acme", observed_facts=[],
        derived_signals=[], account_fit_inference=AccountFitInference(statement="good fit", confidence="medium"),
        suggested_contact=SuggestedContact(role="eng lead", reason="owns the pain"),
    )
    assert check_account_evidence_integrity(target) == "account_fit_inference_without_observed_facts"


# ---------------------------------------------------------------------------
# run_quality_gate — end to end
# ---------------------------------------------------------------------------


def test_run_quality_gate_rejects_opportunity_with_no_verified_evidence():
    evidence = [_quote_not_found_evidence()]
    claims = _four_claims()
    opp = _opportunity(claims=claims)

    result = run_quality_gate([opp], claims, evidence, contradictions={}, signals=[_signal()], business=_business())

    assert result.ranked == []
    assert result.rejected == [RejectedIdea("opp_1", "competitive_gap", "no_verified_evidence", "truth")]


def test_run_quality_gate_single_source_kind_caps_confidence_low_not_rejected():
    evidence = [_evidence()]
    claims = _four_claims()
    opp = _opportunity(claims=claims, competitive_context=[CompetitiveContextItem(signal_id="sig_1", competitor="Sentry", pattern="competitive_gap")])

    result = run_quality_gate([opp], claims, evidence, contradictions={}, signals=[_signal()], business=_business())

    assert result.rejected == []
    assert len(result.ranked) == 1
    assert result.ranked[0].evidence_confidence == EvidenceConfidence.LOW
    assert result.ranked[0].priority == Priority.LOW
    assert all(c.status == ClaimStatus.HYPOTHESIS for c in result.claims)


def test_run_quality_gate_two_source_kinds_no_contradiction_is_high_confidence():
    evidence = [_evidence(source_kind=SourceKind.HN, url="https://a.example/1"), _evidence(id="evd_2", source_kind=SourceKind.GITHUB, url="https://b.example/1")]
    claims = _four_claims(evidence_ids=("evd_1", "evd_2"))
    opp = _opportunity(claims=claims, competitive_context=[CompetitiveContextItem(signal_id="sig_1", competitor="Sentry", pattern="competitive_gap")])

    result = run_quality_gate([opp], claims, evidence, contradictions={c.id: False for c in claims}, signals=[_signal()], business=_business())

    assert result.ranked[0].evidence_confidence == EvidenceConfidence.HIGH
    assert result.ranked[0].priority == Priority.HIGH
    assert all(c.status == ClaimStatus.VERIFIED for c in result.claims)


def test_run_quality_gate_contradiction_downgrades_high_to_medium_and_flags():
    evidence = [_evidence(source_kind=SourceKind.HN, url="https://a.example/1"), _evidence(id="evd_2", source_kind=SourceKind.GITHUB, url="https://b.example/1")]
    claims = _four_claims(evidence_ids=("evd_1", "evd_2"))
    opp = _opportunity(claims=claims, competitive_context=[CompetitiveContextItem(signal_id="sig_1", competitor="Sentry", pattern="competitive_gap")])
    contradictions = {c.id: False for c in claims}
    contradictions["claim_why_this"] = True

    result = run_quality_gate([opp], claims, evidence, contradictions=contradictions, signals=[_signal()], business=_business())

    assert result.ranked[0].evidence_confidence == EvidenceConfidence.MEDIUM
    assert result.ranked[0].priority == Priority.MEDIUM
    assert "contradiction_present" in result.ranked[0].flags


def test_run_quality_gate_fix_first_forces_blocked_regardless_of_confidence():
    evidence = [_evidence(source_kind=SourceKind.HN, url="https://a.example/1"), _evidence(id="evd_2", source_kind=SourceKind.GITHUB, url="https://b.example/1")]
    claims = _four_claims(evidence_ids=("evd_1", "evd_2"))
    opp = _opportunity(claims=claims, pains_to_fix_first=[PainToFix(signal_id="sig_1", reason="own pain", severity=2)])

    result = run_quality_gate([opp], claims, evidence, contradictions={c.id: False for c in claims}, signals=[_signal()], business=_business())

    assert result.ranked == []
    assert result.blocked[0].priority == Priority.BLOCKED


def test_run_quality_gate_severe_pain_flags_fix_first_risk():
    evidence = [_evidence(source_kind=SourceKind.HN, url="https://a.example/1"), _evidence(id="evd_2", source_kind=SourceKind.GITHUB, url="https://b.example/1")]
    claims = _four_claims(evidence_ids=("evd_1", "evd_2"))
    opp = _opportunity(claims=claims, pains_to_fix_first=[PainToFix(signal_id="sig_1", reason="own pain", severity=5)])

    result = run_quality_gate([opp], claims, evidence, contradictions={c.id: False for c in claims}, signals=[_signal()], business=_business())

    assert "fix_first_risk" in result.blocked[0].flags


def test_run_quality_gate_why_now_solely_on_stale_evidence_is_rejected():
    stale = _evidence(freshness=_freshness(status=FreshnessStatus.STALE, age_days=400, limit_days=180))
    claims = _four_claims()  # every claim cites "evd_1", the only (stale) evidence item
    opp = _opportunity(claims=claims)

    result = run_quality_gate([opp], claims, [stale], contradictions={}, signals=[_signal()], business=_business())

    assert result.ranked == [] and result.blocked == []
    assert result.rejected[0].rejected_because == "why_now_rests_solely_on_stale_evidence"


def test_run_quality_gate_attribution_safety_rejects_simulated_competitor_claim():
    evidence = [_evidence()]
    claims = _four_claims()
    opp = _opportunity(claims=claims, competitive_context=[CompetitiveContextItem(signal_id="sig_1", competitor="Sentry", pattern="competitive_gap")])
    signals = [_signal(source_kind=SourceKind.SIMULATED)]

    result = run_quality_gate([opp], claims, evidence, contradictions={}, signals=signals, business=_business())

    assert result.rejected[0].rejected_because == "simulated_claim_attributed_to_competitor"
    assert result.rejected[0].failed_gate == "quality_safety"


def test_run_quality_gate_merges_duplicate_into_stronger_opportunity():
    evidence_a = [_evidence(source_kind=SourceKind.HN, url="https://a.example/1"), _evidence(id="evd_2", source_kind=SourceKind.GITHUB, url="https://b.example/1")]
    evidence_b = [_evidence(id="evd_3")]

    claims_a = [c.model_copy(update={"id": f"a_{c.id}"}) for c in _four_claims(evidence_ids=("evd_1", "evd_2"))]
    claims_b = [c.model_copy(update={"id": f"b_{c.id}", "evidence_ids": ["evd_3"]}) for c in _four_claims()]

    opp_a = _opportunity(
        id="opp_a", claims=claims_a, claim_ids=[c.id for c in claims_a],
        strengths_it_builds_on=[SignalReason(signal_id="sig_1", reason="x")],
    )
    opp_b = _opportunity(
        id="opp_b", claims=claims_b, claim_ids=[c.id for c in claims_b],
        strengths_it_builds_on=[SignalReason(signal_id="sig_1", reason="x")],
    )

    claims = claims_a + claims_b
    evidence = evidence_a + evidence_b
    contradictions = {c.id: False for c in claims}

    result = run_quality_gate([opp_a, opp_b], claims, evidence, contradictions=contradictions, signals=[_signal()], business=_business())

    ids = {o.id for o in result.ranked}
    assert ids == {"opp_a"}  # higher confidence (2 source kinds) wins over opp_b (1 source kind)
    assert result.rejected == [RejectedIdea("opp_b", "competitive_gap", "duplicate_merged_into:opp_a", "quality_safety")]
