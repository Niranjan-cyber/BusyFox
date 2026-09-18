"""Synthesis Agent (Task 17) — §10.3 guardrail, §9.5 mechanism concreteness,
rubric self-critique, and entity assembly.

Only the pure logic is exercised here; the real Strands/Bedrock wiring in
`_build_live_agent`/`live_collect` is network/credential-dependent and not
unit-tested, same treatment as Task 15/16's `live_collect`.
"""

from __future__ import annotations

from backend.agents.market_agent import RuntimeBudget
from backend.agents.synthesis_agent import (
    RawCandidate,
    assemble_synthesis_output,
    build_opportunity,
    mechanism_is_concrete,
    passes_self_critique,
    run_synthesis_agent,
    validate_candidates,
)
from backend.schemas.entities import (
    AgentRuntimeContract,
    ClaimStatus,
    ClaimType,
    EvidenceConfidence,
    Opportunity,
    Polarity,
    Priority,
    Signal,
    SourceKind,
)


def _signal(**overrides) -> Signal:
    defaults = dict(
        id="sig_1",
        run_id="run1",
        source_kind=SourceKind.HN,
        aspect="pricing_pain",
        polarity=Polarity.NEGATIVE,
        claim_text="[Sentry] 8 discussions in 45 days mention pricing.",
        evidence_ids=[],
        produced_by="competitor_agent",
    )
    defaults.update(overrides)
    return Signal(**defaults)


def _raw(**overrides) -> RawCandidate:
    defaults = dict(
        opportunity_type="competitive_gap",
        signal_ids=("sig_1", "sig_2"),
        mechanism_statement="Teams evaluating alternatives on price fit PulseStack's flat pricing plan.",
        mechanism_shared_segment="teams evaluating alternatives on price",
        mechanism_actionable_because="PulseStack already has a flat pricing plan to offer",
        why_this="Sentry's pricing change is driving complaints.",
        why_you="Our users already praise flat pricing.",
        why_now="8 discussions in the last 45 days.",
        mechanism_holds=True,
        critique_reason="Segment and reason are both concrete.",
    )
    defaults.update(overrides)
    return RawCandidate(**defaults)


def _signals_by_id() -> dict[str, Signal]:
    return {
        "sig_1": _signal(),
        "sig_2": _signal(
            id="sig_2",
            source_kind=SourceKind.SIMULATED,
            polarity=Polarity.POSITIVE,
            claim_text="Our users praise flat pricing.",
            produced_by="feedback_pipeline_labeller",
        ),
    }


# ---------------------------------------------------------------------------
# §9.5 mechanism concreteness
# ---------------------------------------------------------------------------


def test_concrete_mechanism_accepted():
    assert mechanism_is_concrete(_raw())


def test_mechanism_missing_shared_segment_rejected():
    assert not mechanism_is_concrete(_raw(mechanism_shared_segment=""))


def test_mechanism_whitespace_only_field_rejected():
    assert not mechanism_is_concrete(_raw(mechanism_actionable_because="   "))


# ---------------------------------------------------------------------------
# Rubric self-critique
# ---------------------------------------------------------------------------


def test_self_critique_holds_and_concrete_passes():
    assert passes_self_critique(_raw())


def test_self_critique_false_fails_even_if_concrete():
    assert not passes_self_critique(_raw(mechanism_holds=False))


def test_model_overclaiming_holds_still_fails_if_not_concrete():
    assert not passes_self_critique(_raw(mechanism_holds=True, mechanism_shared_segment=""))


# ---------------------------------------------------------------------------
# §10.3 guardrail — only already-collected signals
# ---------------------------------------------------------------------------


def test_candidate_citing_uncollected_signal_rejected():
    accepted, rejected = validate_candidates(
        [_raw(signal_ids=("sig_1", "sig_unknown"))], known_signal_ids=frozenset({"sig_1", "sig_2"})
    )
    assert accepted == []
    assert rejected[0].reason == "cites_uncollected_signal"


def test_candidate_with_no_signals_rejected():
    accepted, rejected = validate_candidates([_raw(signal_ids=())], known_signal_ids=frozenset({"sig_1"}))
    assert accepted == []
    assert rejected[0].reason == "no_signals_cited"


def test_unknown_opportunity_type_rejected():
    accepted, rejected = validate_candidates(
        [_raw(opportunity_type="not_a_real_type")], known_signal_ids=frozenset({"sig_1", "sig_2"})
    )
    assert accepted == []
    assert rejected[0].reason == "unknown_opportunity_type"


def test_valid_candidate_accepted():
    accepted, rejected = validate_candidates([_raw()], known_signal_ids=frozenset({"sig_1", "sig_2"}))
    assert len(accepted) == 1
    assert rejected == []


# ---------------------------------------------------------------------------
# Entity assembly
# ---------------------------------------------------------------------------


def test_build_opportunity_produces_four_claims_resolving_claim_ids():
    opportunity, claims = build_opportunity(_raw(), signals_by_id=_signals_by_id(), run_id="run1", index=0)
    Opportunity.model_validate(opportunity.model_dump())
    assert {c.id for c in claims} == set(opportunity.claim_ids)
    assert {c.type for c in claims} == {ClaimType.WHY_THIS, ClaimType.WHY_YOU, ClaimType.WHY_NOW, ClaimType.MECHANISM}
    assert all(c.status == ClaimStatus.HYPOTHESIS and c.evidence_ids == [] for c in claims)


def test_build_opportunity_splits_strengths_and_pains_by_polarity():
    opportunity, _ = build_opportunity(_raw(), signals_by_id=_signals_by_id(), run_id="run1", index=0)
    assert [s.signal_id for s in opportunity.strengths_it_builds_on] == ["sig_2"]
    assert opportunity.pains_to_fix_first == []  # sig_1 is a competitor signal, not our own pain


def test_build_opportunity_derives_competitive_context_from_competitor_signal():
    opportunity, _ = build_opportunity(_raw(), signals_by_id=_signals_by_id(), run_id="run1", index=0)
    assert len(opportunity.competitive_context) == 1
    assert opportunity.competitive_context[0].competitor == "Sentry"
    assert opportunity.competitive_context[0].signal_id == "sig_1"


def test_build_opportunity_evidence_confidence_is_low_pending_quality_gate():
    opportunity, _ = build_opportunity(_raw(), signals_by_id=_signals_by_id(), run_id="run1", index=0)
    assert opportunity.evidence_confidence == EvidenceConfidence.LOW


def test_build_opportunity_priority_blocked_when_own_pain_present():
    signals = _signals_by_id()
    signals["sig_3"] = _signal(
        id="sig_3", polarity=Polarity.NEGATIVE, produced_by="feedback_pipeline_labeller", claim_text="Own pain."
    )
    raw = _raw(signal_ids=("sig_1", "sig_2", "sig_3"), pain_severity=4)
    opportunity, _ = build_opportunity(raw, signals_by_id=signals, run_id="run1", index=0)
    assert opportunity.pains_to_fix_first[0].severity == 4
    assert opportunity.priority == Priority.BLOCKED


def test_build_opportunity_priority_low_when_no_own_pain():
    opportunity, _ = build_opportunity(_raw(), signals_by_id=_signals_by_id(), run_id="run1", index=0)
    assert opportunity.priority == Priority.LOW


def test_build_opportunity_evidence_diversity_counts_distinct_source_kinds():
    opportunity, _ = build_opportunity(_raw(), signals_by_id=_signals_by_id(), run_id="run1", index=0)
    assert opportunity.evidence_diversity.source_kind_count == 2  # HN + SIMULATED


# ---------------------------------------------------------------------------
# assemble_synthesis_output / run_synthesis_agent end-to-end
# ---------------------------------------------------------------------------


def test_assemble_synthesis_output_drops_failed_self_critique():
    signals = list(_signals_by_id().values())
    budget = RuntimeBudget(AgentRuntimeContract(max_tokens=100), clock=lambda: 0.0)
    output, invocation, rejected = assemble_synthesis_output(
        [_raw(), _raw(mechanism_holds=False)], signals=signals, run_id="run1", budget=budget
    )
    assert len(output.candidate_opportunities) == 1
    assert len(output.claims) == 4
    assert len(rejected) == 1
    assert invocation.component == "synthesis_agent"


def test_synthesis_output_has_no_bare_opportunities_field():
    """SynthesisAgentOutput is the *only* place opportunities may appear
    (§10.1a) — this pins the field name so it can't quietly drift."""
    signals = list(_signals_by_id().values())
    budget = RuntimeBudget(AgentRuntimeContract(max_tokens=100), clock=lambda: 0.0)
    output, _, _ = assemble_synthesis_output([_raw()], signals=signals, run_id="run1", budget=budget)
    assert hasattr(output, "candidate_opportunities")
    assert not hasattr(output, "opportunities")


def test_run_synthesis_agent_end_to_end_with_fake_collector():
    signals = list(_signals_by_id().values())
    contract = AgentRuntimeContract(max_iterations=3, max_tool_calls=6, max_runtime_seconds=60, max_tokens=100)

    def fake_collect(_contract, _signals):
        return [_raw(), _raw(signal_ids=("sig_unknown",))]

    output, invocation, rejected = run_synthesis_agent(signals, run_id="run1", contract=contract, collect=fake_collect)
    assert len(output.candidate_opportunities) == 1
    assert len(rejected) == 1
    assert rejected[0].reason == "cites_uncollected_signal"
    assert invocation.component == "synthesis_agent"
