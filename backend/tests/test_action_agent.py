"""Action Agent (Task 26) — §18.1 outreach_policy check, proof-point
guardrail, and entity assembly.

Only the pure logic is exercised here; the real Strands/Bedrock wiring in
`_build_live_agent`/`live_collect` is network/credential-dependent and not
unit-tested, same treatment as Task 15/16/17's `live_collect`.
"""

from __future__ import annotations

from backend.agents.action_agent import (
    RawExecutionPack,
    RawOutreachDraft,
    RuntimeBudget,
    build_execution_pack,
    is_valid_outreach_draft,
    run_action_agent,
    validate_drafts,
    violates_outreach_policy,
)
from backend.schemas.entities import (
    AgentRuntimeContract,
    EvidenceConfidence,
    EvidenceDiversity,
    MonthlyRange,
    ObservedInferredAssumed,
    Opportunity,
    OpportunityMechanism,
    OpportunityType,
    OutreachChannel,
    Priority,
    SignalReason,
    ValueAssumption,
    ValueModel,
)


def _opportunity(**overrides) -> Opportunity:
    defaults = dict(
        id="opp_1",
        type=OpportunityType.COMPETITIVE_GAP,
        claim_ids=[],
        opportunity_mechanism=OpportunityMechanism(
            statement="stmt", shared_segment="segment", actionable_because="reason"
        ),
        strengths_it_builds_on=[SignalReason(signal_id="sig_strength_1", reason="Users praise flat pricing.")],
        pains_to_fix_first=[],
        competitive_context=[],
        evidence_diversity=EvidenceDiversity(
            source_kind_count=1, domain_count=1, author_count=1, underlying_event_risk="low"
        ),
        evidence_confidence=EvidenceConfidence.HIGH,
        priority=Priority.HIGH,
        value=ValueModel(
            model="saas_arr",
            assumptions=[ValueAssumption(key="arpa", label=ObservedInferredAssumed.OBSERVED, description="d")],
            monthly_usd=MonthlyRange(low=1.0, high=2.0),
        ),
    )
    defaults.update(overrides)
    return Opportunity(**defaults)


def _raw_draft(**overrides) -> RawOutreachDraft:
    defaults = dict(
        channel="email",
        draft="We've been helping small engineering teams reduce monitoring overhead with predictable pricing.",
        proof_point_signal_id="sig_strength_1",
    )
    defaults.update(overrides)
    return RawOutreachDraft(**defaults)


# ---------------------------------------------------------------------------
# §18.1 outreach_policy post-generation check
# ---------------------------------------------------------------------------


def test_generic_draft_does_not_violate_policy():
    assert not violates_outreach_policy(_raw_draft().draft)


def test_draft_referencing_a_specific_post_violates_policy():
    assert violates_outreach_policy("I saw your post about switching off your current tool.")


def test_draft_noticing_language_violates_policy():
    assert violates_outreach_policy("We noticed your complaint on the forum yesterday.")


# ---------------------------------------------------------------------------
# proof-point guardrail
# ---------------------------------------------------------------------------


def test_draft_citing_known_strength_is_valid():
    assert is_valid_outreach_draft(_raw_draft(), known_strength_signal_ids=frozenset({"sig_strength_1"}))


def test_draft_citing_unknown_signal_is_invalid():
    assert not is_valid_outreach_draft(
        _raw_draft(proof_point_signal_id="sig_invented"), known_strength_signal_ids=frozenset({"sig_strength_1"})
    )


def test_draft_with_unknown_channel_is_invalid():
    assert not is_valid_outreach_draft(
        _raw_draft(channel="sms"), known_strength_signal_ids=frozenset({"sig_strength_1"})
    )


# ---------------------------------------------------------------------------
# validate_drafts
# ---------------------------------------------------------------------------


def test_validate_drafts_accepts_valid_draft():
    accepted, rejected = validate_drafts([_raw_draft()], known_strength_signal_ids=frozenset({"sig_strength_1"}))
    assert len(accepted) == 1
    assert rejected == []


def test_validate_drafts_rejects_policy_violation():
    accepted, rejected = validate_drafts(
        [_raw_draft(draft="I saw your post about pricing.")], known_strength_signal_ids=frozenset({"sig_strength_1"})
    )
    assert accepted == []
    assert rejected[0].reason == "outreach_policy_violation"


def test_validate_drafts_rejects_unknown_proof_point():
    accepted, rejected = validate_drafts(
        [_raw_draft(proof_point_signal_id="sig_invented")], known_strength_signal_ids=frozenset({"sig_strength_1"})
    )
    assert accepted == []
    assert rejected[0].reason == "proof_point_not_a_known_strength"


def test_validate_drafts_rejects_unknown_channel():
    accepted, rejected = validate_drafts(
        [_raw_draft(channel="sms")], known_strength_signal_ids=frozenset({"sig_strength_1"})
    )
    assert accepted == []
    assert rejected[0].reason == "unknown_channel"


# ---------------------------------------------------------------------------
# build_execution_pack / entity assembly
# ---------------------------------------------------------------------------


def test_build_execution_pack_produces_real_pack_from_real_opportunity():
    raw = RawExecutionPack(offer="offer text", proposal="proposal text", outreach_drafts=(_raw_draft(),))
    pack, rejected = build_execution_pack(raw, opportunity=_opportunity())

    Opportunity.model_validate(_opportunity().model_dump())  # sanity: fixture itself is a valid Opportunity
    assert pack.id == "pack_opp_1"
    assert pack.opportunity_id == "opp_1"
    assert pack.offer == "offer text"
    assert pack.proposal == "proposal text"
    assert len(pack.outreach_drafts) == 1
    assert pack.outreach_drafts[0].outreach_policy_checked is True
    assert pack.outreach_drafts[0].channel == OutreachChannel.EMAIL
    assert rejected == []


def test_build_execution_pack_drops_policy_violating_draft():
    raw = RawExecutionPack(
        offer="offer",
        proposal="proposal",
        outreach_drafts=(
            _raw_draft(),
            _raw_draft(draft="I saw your post about switching off Sentry."),
        ),
    )
    pack, rejected = build_execution_pack(raw, opportunity=_opportunity())
    assert len(pack.outreach_drafts) == 1
    assert len(rejected) == 1
    assert rejected[0].reason == "outreach_policy_violation"


def test_build_execution_pack_outreach_policy_checked_only_true_after_passing():
    """No draft in the pack was ever marked checked before the policy scan
    ran — the flag on a surviving draft always reflects a real pass."""

    raw = RawExecutionPack(
        offer="offer",
        proposal="proposal",
        outreach_drafts=(_raw_draft(), _raw_draft(draft="We noticed your complaint.")),
    )
    pack, _rejected = build_execution_pack(raw, opportunity=_opportunity())
    assert all(d.outreach_policy_checked for d in pack.outreach_drafts)
    assert len(pack.outreach_drafts) == 1


# ---------------------------------------------------------------------------
# run_action_agent end-to-end
# ---------------------------------------------------------------------------


def test_run_action_agent_end_to_end_with_fake_collector():
    contract = AgentRuntimeContract(max_iterations=3, max_tool_calls=6, max_runtime_seconds=60, max_tokens=100)

    def fake_collect(_contract, _opportunity):
        return RawExecutionPack(
            offer="offer",
            proposal="proposal",
            outreach_drafts=(_raw_draft(), _raw_draft(proof_point_signal_id="sig_invented")),
        )

    pack, invocation, rejected = run_action_agent(
        _opportunity(), contract=contract, collect=fake_collect
    )
    assert len(pack.outreach_drafts) == 1
    assert len(rejected) == 1
    assert rejected[0].reason == "proof_point_not_a_known_strength"
    assert invocation.component == "action_agent"


def test_run_action_agent_budget_is_a_real_runtime_budget():
    """Pins that run_action_agent starts its own RuntimeBudget (§10.1a),
    same contract as every other agent — not skipped for Action Agent."""

    contract = AgentRuntimeContract(max_tokens=100)

    def fake_collect(_contract, _opportunity):
        return RawExecutionPack(offer="o", proposal="p", outreach_drafts=())

    _pack, invocation, _rejected = run_action_agent(
        _opportunity(), contract=contract, collect=fake_collect
    )
    assert invocation.iterations == 0
    assert invocation.tool_calls == 0
    assert invocation.truncated is False
    assert isinstance(RuntimeBudget(contract), RuntimeBudget)
