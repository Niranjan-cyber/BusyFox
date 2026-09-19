"""Orchestrator (Task 21) — wiring Market/Feedback/Competitor -> Synthesis ->
Evidence Check -> Quality Gate -> DynamoDB into one real pipeline run.

Every stage underneath is already unit-tested on its own (Tasks 15-20); this
file exercises the plumbing between them, same fake-collector-injection
style used throughout backend/agents and backend/pipeline.
"""

from __future__ import annotations

from datetime import datetime, timezone

from backend.agents.competitor_agent import RawCompetitorSignal
from backend.agents.synthesis_agent import RawCandidate
from backend.db.dynamo import get_entity, query_children
from backend.fixtures.fixtures import BUSINESS
from backend.orchestrator import persist, run_pipeline
from backend.pipeline.quality_gate import RejectedIdea
from backend.tests.test_dynamo import _FakeTable
from backend.schemas.entities import (
    AgentRuntimeContract,
    Claim,
    ClaimSupport,
    ClaimSupportStatus,
    DynamoKeyPrefix,
    EvidenceConfidence,
    Opportunity,
    Polarity,
    Priority,
    RejectedCandidate,
    Signal,
    SourceKind,
)

_NOW = datetime(2026, 9, 18, tzinfo=timezone.utc)


def _fake_market_collect(contract: AgentRuntimeContract) -> list:
    return []


def _fake_competitor_collect(contract: AgentRuntimeContract) -> list[RawCompetitorSignal]:
    return [
        RawCompetitorSignal(
            competitor_name="Sentry",
            aspect="pricing_pain",
            polarity="negative",
            claim_text="8 public discussions in the last 45 days mention Sentry's pricing change.",
            count=8,
            date_window="last 45 days",
            source_url="https://news.ycombinator.com/item?id=2",
            source_kind=SourceKind.HN,
        )
    ]


def _fake_synthesis_collect(contract: AgentRuntimeContract, signals: list[Signal]) -> list[RawCandidate]:
    competitor_signal = next(s for s in signals if s.produced_by == "competitor_agent")
    strength_signal = next(s for s in signals if s.polarity == Polarity.POSITIVE)
    return [
        RawCandidate(
            opportunity_type="competitive_gap",
            signal_ids=(competitor_signal.id, strength_signal.id),
            mechanism_statement=(
                "Teams frustrated by Sentry's pricing change fit PulseStack's flat-pricing, "
                "low-noise positioning because PulseStack already serves this exact segment."
            ),
            mechanism_shared_segment="small eng teams evaluating alternatives to Sentry",
            mechanism_actionable_because="PulseStack already has a confirmed flat-pricing plan and low-noise reputation",
            why_this="Sentry's pricing change is driving public complaints.",
            why_you="PulseStack's own reviews already praise its low false-alarm rate.",
            why_now="8 discussions about Sentry pricing in the last 45 days.",
            mechanism_holds=True,
            critique_reason="Shared segment and actionable reason are both concrete and evidenced.",
        )
    ]


def _fake_synthesis_collect_no_signals(contract: AgentRuntimeContract, signals: list[Signal]) -> list[RawCandidate]:
    return []


def _fake_semantic_check(claim_text: str, quote: str) -> ClaimSupport:
    return ClaimSupport(status=ClaimSupportStatus.SUPPORTS, confidence=0.9, reason="quote directly supports the claim")


def _run(synthesis_collect=_fake_synthesis_collect):
    return run_pipeline(
        BUSINESS,
        run_id="run_test",
        now=_NOW,
        market_collect=_fake_market_collect,
        competitor_collect=_fake_competitor_collect,
        synthesis_collect=synthesis_collect,
        semantic_check=_fake_semantic_check,
    )


def test_full_run_produces_a_gate_passed_opportunity():
    result = _run()
    assert len(result.ranked) == 1
    assert result.rejected == []
    assert result.ranked[0].evidence_confidence == EvidenceConfidence.HIGH
    assert result.ranked[0].priority == Priority.HIGH


def test_run_carries_competitor_signal_url_and_date_into_evidence():
    """The gap this module exists to close: Signal drops the raw source_url/
    date_window, so Evidence Check couldn't verify freshness without this
    module keeping it alongside the signal."""

    result = _run()
    competitor_evidence = [e for e in result.evidence if e.url == "https://news.ycombinator.com/item?id=2"]
    assert competitor_evidence
    assert all(e.published_at is not None for e in competitor_evidence)


def test_no_candidate_opportunities_yields_empty_run():
    result = _run(synthesis_collect=_fake_synthesis_collect_no_signals)
    assert result.ranked == []
    assert result.blocked == []
    assert result.run.opportunities_produced == 0


def test_run_entity_records_all_three_agent_invocations():
    result = _run()
    components = {inv.component for inv in result.run.agent_invocations}
    assert components == {"market_agent", "competitor_agent", "synthesis_agent"}


def test_persist_writes_business_run_opportunity_claims_and_evidence():
    result = _run()
    table = _FakeTable()

    persist(table, result)

    assert get_entity(table, DynamoKeyPrefix.BUSINESS, BUSINESS.id, type(BUSINESS)) == BUSINESS
    opportunity = result.ranked[0]
    stored_opportunity = get_entity(table, DynamoKeyPrefix.OPPORTUNITY, opportunity.id, Opportunity)
    assert stored_opportunity is not None
    assert stored_opportunity.id == opportunity.id

    stored_claims = query_children(table, f"OPP#{opportunity.id}", DynamoKeyPrefix.CLAIM)
    assert len(stored_claims) == 4

    one_claim = get_entity(table, DynamoKeyPrefix.CLAIM, opportunity.claim_ids[0], Claim)
    stored_evidence = query_children(table, f"CLAIM#{one_claim.id}", DynamoKeyPrefix.EVIDENCE)
    assert len(stored_evidence) == len(one_claim.evidence_ids)


def test_persist_writes_rejected_candidates():
    result = _run()._replace(
        rejected=[RejectedIdea("opp_x", "competitive_gap", "A rejected idea's title.", "no_verified_evidence", "truth")]
    )
    table = _FakeTable()

    persist(table, result)

    stored = query_children(table, f"BIZ#{BUSINESS.id}", DynamoKeyPrefix.REJECTED_CANDIDATE)
    assert len(stored) == 1
    candidate = RejectedCandidate.model_validate(stored[0])
    assert candidate == RejectedCandidate(
        id="opp_x",
        opportunity_type="competitive_gap",
        title="A rejected idea's title.",
        rejected_because="no_verified_evidence",
        failed_gate="truth",
    )
