"""Evidence Check (Task 18) — quote-exists, semantic claim support, freshness, contradiction."""

from __future__ import annotations

from datetime import datetime

from backend.pipeline.evidence_check import (
    EvidenceCandidate,
    build_evidence,
    check_freshness,
    contradiction_exists,
    freshness_limit_days,
    quote_exists,
    run_evidence_check,
)
from backend.schemas.entities import (
    Claim,
    ClaimStatus,
    ClaimSupport,
    ClaimSupportStatus,
    ClaimType,
    FreshnessStatus,
    Polarity,
    RetrievalMode,
    Signal,
    SourceKind,
)

_NOW = datetime(2026, 9, 18)


def _candidate(**overrides) -> EvidenceCandidate:
    defaults = dict(
        claim_id="claim_1",
        source_document_id="src_1",
        source_kind=SourceKind.HN,
        retrieval_mode=RetrievalMode.LIVE,
        url="https://news.ycombinator.com/item?id=1",
        retrieved_at=_NOW,
        quote="the new pricing tier doubled our bill",
        source_text="Thread: the new pricing tier doubled our bill overnight, we're leaving.",
        aspect="pricing_pain",
        polarity=Polarity.NEGATIVE,
        produced_by="competitor_agent",
        published_at=datetime(2026, 8, 30),
    )
    defaults.update(overrides)
    return EvidenceCandidate(**defaults)


def _claim(**overrides) -> Claim:
    defaults = dict(
        id="claim_1", opportunity_id="opp_1", type=ClaimType.WHY_THIS,
        text="Teams are leaving because of pricing.", status=ClaimStatus.HYPOTHESIS, evidence_ids=[],
    )
    defaults.update(overrides)
    return Claim(**defaults)


def _supports(**overrides) -> ClaimSupport:
    defaults = dict(status=ClaimSupportStatus.SUPPORTS, confidence=0.9, reason="matches")
    defaults.update(overrides)
    return ClaimSupport(**defaults)


def test_quote_exists_verbatim():
    assert quote_exists("doubled our bill", "the new pricing tier doubled our bill overnight")


def test_quote_exists_false_when_absent():
    assert not quote_exists("this text is nowhere in the source", "completely unrelated content")


def test_freshness_limit_days_pricing_aspect_overrides_producer():
    assert freshness_limit_days(aspect="pricing_pain", produced_by="market_agent") == 90


def test_freshness_limit_days_own_feedback():
    assert freshness_limit_days(aspect="alert_noise", produced_by="feedback_pipeline_labeller") == 90


def test_freshness_limit_days_competitor_complaint():
    assert freshness_limit_days(aspect="reliability", produced_by="competitor_agent") == 180


def test_freshness_limit_days_evergreen_capability():
    assert freshness_limit_days(aspect="has_slack_integration", produced_by="market_agent") == 36_500


def test_check_freshness_flags_stale_past_limit():
    result = check_freshness(datetime(2026, 1, 1), now=_NOW, aspect="pricing_pain", produced_by="competitor_agent")
    assert result.status == FreshnessStatus.STALE
    assert result.limit_days == 90


def test_check_freshness_within_limit_is_fresh():
    result = check_freshness(datetime(2026, 9, 1), now=_NOW, aspect="pricing_pain", produced_by="competitor_agent")
    assert result.status == FreshnessStatus.FRESH


def test_contradiction_exists_true_for_opposite_polarity_same_aspect():
    signals = [Signal(id="s1", run_id="r1", source_kind=SourceKind.HN, aspect="pricing_pain", polarity=Polarity.POSITIVE, claim_text="x", evidence_ids=[], produced_by="feedback_pipeline_labeller")]
    assert contradiction_exists(aspect="pricing_pain", polarity=Polarity.NEGATIVE, signals=signals)


def test_contradiction_exists_false_when_no_opposite_signal():
    signals = [Signal(id="s1", run_id="r1", source_kind=SourceKind.HN, aspect="pricing_pain", polarity=Polarity.NEGATIVE, claim_text="x", evidence_ids=[], produced_by="feedback_pipeline_labeller")]
    assert not contradiction_exists(aspect="pricing_pain", polarity=Polarity.NEGATIVE, signals=signals)


def test_build_evidence_rejects_missing_quote_without_calling_model():
    calls = []

    def semantic_check(claim_text: str, quote: str) -> ClaimSupport:
        calls.append((claim_text, quote))
        return _supports()

    candidate = _candidate(quote="nowhere to be found", source_text="totally different text")
    evidence = build_evidence(candidate, claim_text="x", semantic_check=semantic_check, now=_NOW, evidence_id="evd_1")

    assert evidence.claim_support.status == ClaimSupportStatus.UNSUPPORTED
    assert calls == []  # §12.1: no verbatim quote -> semantic check never runs


def test_build_evidence_calls_model_when_quote_found():
    def semantic_check(claim_text: str, quote: str) -> ClaimSupport:
        return _supports(status=ClaimSupportStatus.PARTIAL, reason="topic mismatch")

    evidence = build_evidence(_candidate(), claim_text="x", semantic_check=semantic_check, now=_NOW, evidence_id="evd_1")

    assert evidence.claim_support.status == ClaimSupportStatus.PARTIAL
    assert evidence.quote_hash.startswith("sha256:")


def test_run_evidence_check_populates_claim_evidence_ids():
    claims = [_claim()]
    candidates = [_candidate()]
    result = run_evidence_check(claims, candidates, signals=[], semantic_check=lambda t, q: _supports(), now=_NOW)

    assert len(result.evidence) == 1
    assert result.claims[0].evidence_ids == [result.evidence[0].id]
    assert result.contradictions["claim_1"] is False


def test_run_evidence_check_flags_contradiction():
    claims = [_claim()]
    candidates = [_candidate()]
    signals = [Signal(id="s1", run_id="r1", source_kind=SourceKind.HN, aspect="pricing_pain", polarity=Polarity.POSITIVE, claim_text="x", evidence_ids=[], produced_by="feedback_pipeline_labeller")]

    result = run_evidence_check(claims, candidates, signals=signals, semantic_check=lambda t, q: _supports(), now=_NOW)

    assert result.contradictions["claim_1"] is True


def test_run_evidence_check_claim_with_no_candidates_gets_empty_evidence():
    claims = [_claim()]
    result = run_evidence_check(claims, candidates=[], signals=[], semantic_check=lambda t, q: _supports(), now=_NOW)

    assert result.evidence == []
    assert result.claims[0].evidence_ids == []
    assert result.contradictions["claim_1"] is False
