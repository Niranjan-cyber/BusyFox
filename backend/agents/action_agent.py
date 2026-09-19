"""Action Agent (Task 26) — Strands agent (Sonnet) producing an
`ExecutionPack` (offer, proposal, `outreach_drafts[]`) for one gate-passed
`Opportunity` (ranked or blocked), per §14.10/§18.

`outreach_policy` (§6.1, §18.1: `never_reveal_surveillance_source`,
`never_quote_private_or_sensitive_information`,
`use_public_evidence_only_as_internal_reasoning`) is enforced twice — stated
in the system prompt, and re-checked here by a keyword/phrase scan for
leaked-source language — belt-and-suspenders, same treatment as Synthesis's
`mechanism_holds` (§9.5/§10.1). A draft that fails the check never reaches
the pack; `outreach_policy_checked=True` is only ever set on a draft that
actually passed.

A `proof_point_signal_id` must name one of the opportunity's own verified
strengths (`strengths_it_builds_on`) — never an invented or pain signal —
mirroring Synthesis's §10.3 guardrail against citing signals it wasn't
given.

Split the same way Tasks 15/17 split: pure, testable logic below with no
Strands/AWS dependency; the real Strands wiring at the bottom is
network/credential-dependent and only smoke-tested here.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Callable, NamedTuple

from backend.agents.market_agent import RuntimeBudget, opencode_go_client_args
from backend.schemas.entities import (
    AgentInvocation,
    AgentRuntimeContract,
    ExecutionPack,
    ExecutionPackStatus,
    Opportunity,
    OutreachChannel,
    OutreachDraft,
)

from strands.hooks import BeforeModelCallEvent, BeforeToolCallEvent

_COMPONENT = "action_agent"
_MODEL_ID = os.environ.get("ACTION_AGENT_MODEL_ID", "deepseek-v4.1-flash")

_KNOWN_CHANNELS = frozenset(c.value for c in OutreachChannel)

# ponytail: keyword/phrase scan, not a semantic classifier — §18.1 names this
# exact belt-and-suspenders shape ("prompt and a post-generation regex/
# keyword check"). Ceiling: a draft that leaks the surveillance source
# without ever using one of these phrasings slips through; upgrade to a
# semantic-support-style LLM check (like evidence_check's) if that's ever
# observed in practice.
_SURVEILLANCE_PHRASES = (
    "i saw",
    "i noticed",
    "we saw",
    "we noticed",
    "saw your",
    "noticed your",
    "spotted your",
    "your post",
    "your review",
    "your complaint",
    "your comment",
    "your thread",
    "your discussion",
    "you posted",
    "you wrote",
    "you mentioned",
    "you complained",
)


@dataclass(frozen=True)
class RawOutreachDraft:
    """One draft exactly as the model's `emit_outreach_draft` tool call
    reported it — before §18.1 policy validation."""

    channel: str
    draft: str
    proof_point_signal_id: str


@dataclass(frozen=True)
class RawExecutionPack:
    """The model's `set_offer_and_proposal` + `emit_outreach_draft` tool
    calls, collected — before validation/assembly."""

    offer: str
    proposal: str
    outreach_drafts: tuple[RawOutreachDraft, ...]


class RejectedDraft(NamedTuple):
    """A draft the schema/policy check dropped before it ever reached the
    pack. Not part of any entity — the orchestrator logs these."""

    reason: str
    raw: RawOutreachDraft


# ---------------------------------------------------------------------------
# Pure logic — §18.1 outreach_policy check, proof-point guardrail, entity
# assembly. Unit-testable without Strands/AWS.
# ---------------------------------------------------------------------------


def violates_outreach_policy(draft_text: str) -> bool:
    """§18.1's post-generation check: does this draft read as if it's
    referencing a specific surveilled post/comment, rather than the public
    insight in general terms?"""

    lowered = draft_text.lower()
    return any(phrase in lowered for phrase in _SURVEILLANCE_PHRASES)


def is_valid_outreach_draft(raw: RawOutreachDraft, *, known_strength_signal_ids: frozenset[str]) -> bool:
    return (
        bool(raw.draft.strip())
        and raw.channel in _KNOWN_CHANNELS
        and raw.proof_point_signal_id in known_strength_signal_ids
        and not violates_outreach_policy(raw.draft)
    )


def validate_drafts(
    raw_drafts: list[RawOutreachDraft], *, known_strength_signal_ids: frozenset[str]
) -> tuple[list[RawOutreachDraft], list[RejectedDraft]]:
    accepted, rejected = [], []
    for raw in raw_drafts:
        if raw.channel not in _KNOWN_CHANNELS:
            rejected.append(RejectedDraft(reason="unknown_channel", raw=raw))
        elif raw.proof_point_signal_id not in known_strength_signal_ids:
            # §10.3-style guardrail — a proof point can only be a signal this
            # opportunity actually cites as a verified strength.
            rejected.append(RejectedDraft(reason="proof_point_not_a_known_strength", raw=raw))
        elif violates_outreach_policy(raw.draft):
            rejected.append(RejectedDraft(reason="outreach_policy_violation", raw=raw))
        elif not raw.draft.strip():
            rejected.append(RejectedDraft(reason="empty_draft", raw=raw))
        else:
            accepted.append(raw)
    return accepted, rejected


def build_execution_pack(raw: RawExecutionPack, *, opportunity: Opportunity) -> tuple[ExecutionPack, list[RejectedDraft]]:
    known_strength_signal_ids = frozenset(s.signal_id for s in opportunity.strengths_it_builds_on)
    accepted, rejected = validate_drafts(list(raw.outreach_drafts), known_strength_signal_ids=known_strength_signal_ids)

    outreach_drafts = [
        OutreachDraft(
            channel=OutreachChannel(d.channel),
            draft=d.draft,
            proof_point_signal_id=d.proof_point_signal_id,
            outreach_policy_checked=True,  # only ever set on a draft that passed the check above
        )
        for d in accepted
    ]

    pack = ExecutionPack(
        id=f"pack_{opportunity.id}",
        opportunity_id=opportunity.id,
        offer=raw.offer,
        proposal=raw.proposal,
        outreach_drafts=outreach_drafts,
        status=ExecutionPackStatus.DRAFT,
    )
    return pack, rejected


# ---------------------------------------------------------------------------
# Real Strands wiring — network/AWS-credential-dependent. Tests inject a
# fake `raw_pack` producer instead of a live Agent, same treatment as
# Task 15/16/17's `live_collect`.
# ---------------------------------------------------------------------------

RawExecutionPackCollector = Callable[[AgentRuntimeContract, Opportunity], RawExecutionPack]


def run_action_agent(
    opportunity: Opportunity, *, contract: AgentRuntimeContract, collect: RawExecutionPackCollector
) -> tuple[ExecutionPack, AgentInvocation, list[RejectedDraft]]:
    """Entry point Task 21's orchestrator calls for each gate-passed (ranked
    or blocked) Opportunity. `collect` does the actual reasoning loop (real
    Strands agent in production, a fake in tests)."""

    budget = RuntimeBudget(contract)
    raw_pack = collect(contract, opportunity)
    pack, rejected = build_execution_pack(raw_pack, opportunity=opportunity)
    return pack, budget.to_invocation(component=_COMPONENT), rejected


def _build_live_agent(contract: AgentRuntimeContract, budget: RuntimeBudget, opportunity: Opportunity):
    """Wires a real strands.Agent with the offer/proposal/draft tools and
    the §10.1a hooks. Imports strands lazily so the pure logic above never
    requires the SDK or AWS credentials to be importable/testable."""

    from strands import Agent, tool

    from strands.models.openai import OpenAIModel

    offer_and_proposal: list[tuple[str, str]] = []
    collected_drafts: list[RawOutreachDraft] = []

    @tool
    def set_offer_and_proposal(offer: str, proposal: str) -> str:
        """Record the offer and proposal text for this opportunity's
        execution pack. Call this exactly once, before any outreach draft."""

        offer_and_proposal.append((offer, proposal))
        return "recorded"

    @tool
    def emit_outreach_draft(channel: str, draft: str, proof_point_signal_id: str) -> str:
        """Record one outreach draft. `proof_point_signal_id` must be one of
        the opportunity's own verified strength signal ids listed in the
        prompt — never invented. The draft must reference the public insight
        in general terms only, never a specific post/comment/complaint you
        're referencing — see the outreach_policy bad/good examples above."""

        raw = RawOutreachDraft(channel=channel, draft=draft, proof_point_signal_id=proof_point_signal_id)
        collected_drafts.append(raw)
        known = frozenset(s.signal_id for s in opportunity.strengths_it_builds_on)
        if is_valid_outreach_draft(raw, known_strength_signal_ids=known):
            return "recorded"
        if violates_outreach_policy(raw.draft):
            return "rejected_outreach_policy_violation: rewrite without referencing a specific surveilled post"
        return "rejected: invalid channel or unknown proof_point_signal_id"

    def _before_model_call(event: BeforeModelCallEvent) -> None:
        if not budget.allow_iteration():
            event.cancel = "runtime contract exhausted (§10.1a)"

    def _before_tool_call(event: BeforeToolCallEvent) -> None:
        if not budget.allow_tool_call():
            event.cancel_tool = "runtime contract exhausted (§10.1a)"

    strengths_prompt = "\n".join(
        f"{s.signal_id} | {s.reason}" for s in opportunity.strengths_it_builds_on
    ) or "(no verified strengths on this opportunity)"

    agent = Agent(
        model=OpenAIModel(
            client_args=opencode_go_client_args(), model_id=_MODEL_ID, params={"max_tokens": contract.max_tokens}
        ),
        tools=[set_offer_and_proposal, emit_outreach_draft],
        system_prompt=(
            "You are the Action Agent. Given a gate-passed opportunity, write "
            "an offer, a proposal, and outreach_drafts (channel=email) that "
            "each cite one proof_point_signal_id from this opportunity's "
            "verified strengths below — never a signal not listed here:\n"
            f"{strengths_prompt}\n\n"
            "outreach_policy (§18.1) is mandatory: never_reveal_surveillance_"
            "source, never_quote_private_or_sensitive_information, "
            "use_public_evidence_only_as_internal_reasoning. A draft must use "
            "the insight without exposing that it was found by watching a "
            "specific public post.\n"
            "Bad: \"I saw you're frustrated with Sentry's pricing...\"\n"
            "Good: \"We've been helping small engineering teams reduce "
            "monitoring overhead...\"\n"
            "Call set_offer_and_proposal once, then emit_outreach_draft once "
            "per draft."
        ),
        hooks=[_before_model_call, _before_tool_call],
    )
    return agent, offer_and_proposal, collected_drafts


def live_collect() -> RawExecutionPackCollector:
    """Returns a `collect` callable that runs a real Strands agent — pass
    this as `run_action_agent`'s `collect` argument in production."""

    def collect(contract: AgentRuntimeContract, opportunity: Opportunity) -> RawExecutionPack:
        budget = RuntimeBudget(contract)
        agent, offer_and_proposal, collected_drafts = _build_live_agent(contract, budget, opportunity)
        agent(f"Opportunity mechanism: {opportunity.opportunity_mechanism.statement}")
        offer, proposal = offer_and_proposal[-1] if offer_and_proposal else ("", "")
        return RawExecutionPack(offer=offer, proposal=proposal, outreach_drafts=tuple(collected_drafts))

    return collect


if __name__ == "__main__":
    from backend.schemas.entities import (
        ClaimStatus,
        EvidenceConfidence,
        EvidenceDiversity,
        MonthlyRange,
        ObservedInferredAssumed,
        OpportunityMechanism,
        OpportunityType,
        Priority,
        SignalReason,
        ValueAssumption,
        ValueModel,
    )

    _OPPORTUNITY = Opportunity(
        id="opp_demo_0",
        type=OpportunityType.COMPETITIVE_GAP,
        claim_ids=[],
        opportunity_mechanism=OpportunityMechanism(
            statement="Teams evaluating alternatives on price fit PulseStack's flat pricing plan.",
            shared_segment="teams evaluating alternatives on price",
            actionable_because="PulseStack already has a flat pricing plan to offer",
        ),
        strengths_it_builds_on=[SignalReason(signal_id="sig_fb_1", reason="Users praise flat, predictable pricing.")],
        pains_to_fix_first=[],
        competitive_context=[],
        evidence_diversity=EvidenceDiversity(source_kind_count=2, domain_count=1, author_count=1, underlying_event_risk="low"),
        evidence_confidence=EvidenceConfidence.HIGH,
        priority=Priority.HIGH,
        value=ValueModel(
            model="saas_arr",
            assumptions=[ValueAssumption(key="arpa", label=ObservedInferredAssumed.OBSERVED, description="from pricing")],
            monthly_usd=MonthlyRange(low=100.0, high=500.0),
        ),
    )

    def _fake_collect(contract: AgentRuntimeContract, opportunity: Opportunity) -> RawExecutionPack:
        return RawExecutionPack(
            offer="A flat, predictable-pricing monitoring plan for small eng teams.",
            proposal="30-day pilot at your current alert volume, flat monthly price, no surprise overage.",
            outreach_drafts=(
                RawOutreachDraft(
                    channel="email",
                    draft="We've been helping small engineering teams reduce monitoring overhead with predictable pricing.",
                    proof_point_signal_id="sig_fb_1",
                ),
                RawOutreachDraft(
                    channel="email",
                    draft="I saw your post about switching off your current tool over pricing.",
                    proof_point_signal_id="sig_fb_1",
                ),
                RawOutreachDraft(
                    channel="email",
                    draft="Generic pitch citing an unknown signal.",
                    proof_point_signal_id="sig_not_a_real_strength",
                ),
            ),
        )

    _CONTRACT = AgentRuntimeContract(max_tokens=2048)
    _pack, _invocation, _rejected = run_action_agent(_OPPORTUNITY, contract=_CONTRACT, collect=_fake_collect)
    assert len(_pack.outreach_drafts) == 1, _pack.outreach_drafts
    assert _pack.outreach_drafts[0].outreach_policy_checked is True
    assert _pack.outreach_drafts[0].proof_point_signal_id == "sig_fb_1"
    assert {r.reason for r in _rejected} == {"outreach_policy_violation", "proof_point_not_a_known_strength"}
    assert _pack.id == "pack_opp_demo_0"
    assert _pack.status == ExecutionPackStatus.DRAFT
    assert _invocation.component == "action_agent"
    print("ok")
