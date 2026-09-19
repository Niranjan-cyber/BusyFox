"""Synthesis Agent (Task 17) — Strands agent (Sonnet) combining Market /
Feedback Pipeline / Competitor signals via the §9.3 pattern table into
`candidate_opportunities[]`, each with a mandatory `opportunity_mechanism`
statement (§9.5) that must pass a rubric self-critique before it's emitted.

The only component allowed to emit opportunities, and only from
already-collected signals — never raw research (§10.3): `run_synthesis_agent`
takes a `list[Signal]` as its only source of truth, and every candidate's
cited `signal_ids` are checked against that list, not trusted.

Split the same way Tasks 15/16 split the research agents: pure, testable
logic below (self-critique, §10.3 guardrail, entity assembly) with no
Strands/AWS dependency, reusing Task 15's `RuntimeBudget` for the §10.1a
runtime contract; the real Strands wiring at the bottom is
network/credential-dependent and only smoke-tested here.

`evidence_confidence`/`priority`/`value` on the assembled Opportunity are
provisional (§10.2: their real derivation is Quality Gate + Ranker's job,
Task 19, from verified evidence Task 17 doesn't have yet) — Synthesis fills
them with what the rule tables actually say given zero verified evidence,
not an arbitrary placeholder, so Task 19 overwrites rather than invents.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Callable, NamedTuple

from backend.agents.market_agent import RuntimeBudget, opencode_go_client_args
from backend.schemas.entities import (
    AgentInvocation,
    AgentRuntimeContract,
    Claim,
    ClaimStatus,
    ClaimType,
    CompetitiveContextItem,
    EvidenceConfidence,
    EvidenceDiversity,
    MonthlyRange,
    ObservedInferredAssumed,
    Opportunity,
    OpportunityMechanism,
    OpportunityType,
    PainToFix,
    Polarity,
    Priority,
    Signal,
    SignalReason,
    SynthesisAgentOutput,
    ValueAssumption,
    ValueModel,
)

# See market_agent.py's identical import for why these can't stay local to
# `_build_live_agent`.
from strands.hooks import BeforeModelCallEvent, BeforeToolCallEvent

_COMPONENT = "synthesis_agent"
# See market_agent.py's identical env override and OpenCode Go note. PRD
# names "Claude Sonnet 4.6" (§10.1); using the same OpenCode Go model as
# Market/Competitor instead since Bedrock is unreachable on every available
# AWS account (see opencode_go_client_args).
_MODEL_ID = os.environ.get("SYNTHESIS_AGENT_MODEL_ID", "deepseek-v4.1-flash")

_KNOWN_TYPES = frozenset(t.value for t in OpportunityType)


@dataclass(frozen=True)
class RawCandidate:
    """One candidate exactly as the model's `emit_candidate_opportunity` tool
    call reported it — before §10.3/§9.5 validation and rubric self-critique."""

    opportunity_type: str
    signal_ids: tuple[str, ...]
    mechanism_statement: str
    mechanism_shared_segment: str
    mechanism_actionable_because: str
    why_this: str
    why_you: str
    why_now: str
    mechanism_holds: bool
    critique_reason: str
    pain_severity: int = 0


class RejectedCandidate(NamedTuple):
    """A candidate the schema/self-critique dropped before it ever reached
    the gate. Not part of any entity — the orchestrator logs these, same
    treatment as "Ideas we rejected" (§1.3)."""

    reason: str
    raw: RawCandidate


# ---------------------------------------------------------------------------
# Pure logic — §9.5 mechanism concreteness, rubric self-critique, §10.3
# guardrail. Unit-testable without Strands/AWS.
# ---------------------------------------------------------------------------


def mechanism_is_concrete(raw: RawCandidate) -> bool:
    """§11.2 gate check 7 pre-check, read literally ("populated... Missing
    -> reject"): all three mechanism fields must actually be filled in.
    Whether the statement's reasoning genuinely holds — not just whether
    text is present — is the model's own job, checked by `mechanism_holds`
    below; a string-matching heuristic here would just teach the model to
    game it by repeating words, not to reason better."""

    return bool(raw.mechanism_statement.strip()) and bool(raw.mechanism_shared_segment.strip()) and bool(
        raw.mechanism_actionable_because.strip()
    )


def passes_self_critique(raw: RawCandidate) -> bool:
    """§9.5/§10.1 rubric self-critique — the model's own `mechanism_holds`
    verdict is checked, not just trusted: a model that says "holds" for a
    mechanism that fails the concreteness check is still rejected here."""

    return raw.mechanism_holds and mechanism_is_concrete(raw)


def validate_candidates(
    raw_candidates: list[RawCandidate], *, known_signal_ids: frozenset[str]
) -> tuple[list[RawCandidate], list[RejectedCandidate]]:
    accepted, rejected = [], []
    for raw in raw_candidates:
        if not raw.signal_ids:
            rejected.append(RejectedCandidate(reason="no_signals_cited", raw=raw))
        elif not set(raw.signal_ids) <= known_signal_ids:
            # §10.3 — a candidate can only draw on signals it was actually
            # given, never a signal it invented or recalled from elsewhere.
            rejected.append(RejectedCandidate(reason="cites_uncollected_signal", raw=raw))
        elif raw.opportunity_type not in _KNOWN_TYPES:
            rejected.append(RejectedCandidate(reason="unknown_opportunity_type", raw=raw))
        elif not passes_self_critique(raw):
            rejected.append(RejectedCandidate(reason="failed_self_critique", raw=raw))
        else:
            accepted.append(raw)
    return accepted, rejected


def _competitor_name(claim_text: str) -> str:
    """Competitor Agent signals prefix their claim_text `[Name] ...`
    (§16's build_signal) — reused here instead of asking the model to
    restate a name it can already see."""

    if claim_text.startswith("[") and "]" in claim_text:
        return claim_text[1 : claim_text.index("]")]
    return ""


def _provisional_priority(*, fix_first: bool) -> Priority:
    """§13.1 rule table, applied with the only evidence_confidence Synthesis
    can honestly claim at this stage: LOW (nothing is verified yet)."""

    return Priority.BLOCKED if fix_first else Priority.LOW


def build_opportunity(
    raw: RawCandidate, *, signals_by_id: dict[str, Signal], run_id: str, index: int
) -> tuple[Opportunity, list[Claim]]:
    matched = [signals_by_id[sid] for sid in raw.signal_ids]

    strengths = [
        SignalReason(signal_id=s.id, reason=s.claim_text) for s in matched if s.polarity == Polarity.POSITIVE
    ]
    pains = [
        PainToFix(signal_id=s.id, reason=s.claim_text, severity=raw.pain_severity)
        for s in matched
        # "our pain" only means first-party feedback about our own product —
        # feedback_pipeline_labeller for a real business, pulsestack_simulator
        # for the demo one (orchestrator.run_feedback_stage uses whichever
        # applies; both emit the same Signal/Evidence shape).
        if s.polarity == Polarity.NEGATIVE and s.produced_by in {"feedback_pipeline_labeller", "pulsestack_simulator"}
    ]
    competitive_context = [
        CompetitiveContextItem(
            signal_id=s.id,
            competitor=_competitor_name(s.claim_text),
            pattern=raw.opportunity_type,
        )
        for s in matched
        if s.produced_by == "competitor_agent"
    ]

    opp_id = f"opp_{run_id}_{index}"
    claim_specs = (
        (ClaimType.WHY_THIS, raw.why_this),
        (ClaimType.WHY_YOU, raw.why_you),
        (ClaimType.WHY_NOW, raw.why_now),
        (ClaimType.MECHANISM, raw.mechanism_statement),
    )
    claims = [
        Claim(
            id=f"claim_{run_id}_{index}_{claim_type.value}",
            opportunity_id=opp_id,
            type=claim_type,
            text=text,
            status=ClaimStatus.HYPOTHESIS,  # Evidence Check (Task 18) promotes/rejects this.
            evidence_ids=[],
        )
        for claim_type, text in claim_specs
    ]

    opportunity = Opportunity(
        id=opp_id,
        type=OpportunityType(raw.opportunity_type),
        claim_ids=[c.id for c in claims],
        opportunity_mechanism=OpportunityMechanism(
            statement=raw.mechanism_statement,
            shared_segment=raw.mechanism_shared_segment,
            actionable_because=raw.mechanism_actionable_because,
        ),
        strengths_it_builds_on=strengths,
        pains_to_fix_first=pains,
        competitive_context=competitive_context,
        evidence_diversity=EvidenceDiversity(
            source_kind_count=len({s.source_kind for s in matched}),
            domain_count=0,  # unknown until Evidence Check resolves each signal's Evidence (§12).
            author_count=0,
            underlying_event_risk="unknown",
        ),
        evidence_confidence=EvidenceConfidence.LOW,
        priority=_provisional_priority(fix_first=bool(pains)),
        value=ValueModel(
            model="saas_arr",
            assumptions=[
                ValueAssumption(
                    key="pending_quality_gate",
                    label=ObservedInferredAssumed.ASSUMED,
                    description=(
                        "Not computed at synthesis time; Quality Gate + Ranker (§13.2) "
                        "derives the real estimate from verified evidence and business pricing."
                    ),
                )
            ],
            monthly_usd=MonthlyRange(low=0.0, high=0.0),
        ),
    )
    return opportunity, claims


def assemble_synthesis_output(
    raw_candidates: list[RawCandidate], *, signals: list[Signal], run_id: str, budget: RuntimeBudget
) -> tuple[SynthesisAgentOutput, AgentInvocation, list[RejectedCandidate]]:
    """§10.3/§9.5 validation + §10.1a truncation labelling, all in one place
    — the boundary the real Strands wiring below hands its raw tool-call
    output through, and what tests exercise directly."""

    signals_by_id = {s.id: s for s in signals}
    accepted, rejected = validate_candidates(raw_candidates, known_signal_ids=frozenset(signals_by_id))

    opportunities: list[Opportunity] = []
    claims: list[Claim] = []
    for index, raw in enumerate(accepted):
        opportunity, opp_claims = build_opportunity(raw, signals_by_id=signals_by_id, run_id=run_id, index=index)
        opportunities.append(opportunity)
        claims.extend(opp_claims)

    output = SynthesisAgentOutput(run_id=run_id, candidate_opportunities=opportunities, claims=claims)
    return output, budget.to_invocation(component=_COMPONENT), rejected


# ---------------------------------------------------------------------------
# Real Strands wiring — network/AWS-credential-dependent. Tests inject a
# fake `raw_candidates` producer instead of a live Agent, same treatment as
# Task 15/16's `live_collect`.
# ---------------------------------------------------------------------------

RawCandidateCollector = Callable[[AgentRuntimeContract, list[Signal]], list[RawCandidate]]


def run_synthesis_agent(
    signals: list[Signal], *, run_id: str, contract: AgentRuntimeContract, collect: RawCandidateCollector
) -> tuple[SynthesisAgentOutput, AgentInvocation, list[RejectedCandidate]]:
    """Entry point Task 21's orchestrator calls. `collect` does the actual
    reasoning loop (real Strands agent in production, a fake in tests) and
    returns whatever candidates it proposed before the budget or the model
    itself decided to stop — never anything drawn from outside `signals`."""

    budget = RuntimeBudget(contract)
    raw_candidates = collect(contract, signals)
    return assemble_synthesis_output(raw_candidates, signals=signals, run_id=run_id, budget=budget)


def _signals_prompt(signals: list[Signal]) -> str:
    lines = [
        f"{s.id} | {s.produced_by} | {s.source_kind.value} | {s.aspect} | {s.polarity.value} | {s.claim_text}"
        for s in signals
    ]
    return "\n".join(lines)


def _build_live_agent(contract: AgentRuntimeContract, budget: RuntimeBudget):
    """Wires a real strands.Agent with a single `emit_candidate_opportunity`
    tool and the §10.1a hooks. Imports strands lazily so the pure logic
    above never requires the SDK or AWS credentials to be importable/
    testable. No search tools — §10.3 means Synthesis only ever reasons
    over the signals it's handed, it never goes back out to research."""

    from strands import Agent, tool
    from strands.models.openai import OpenAIModel

    collected: list[RawCandidate] = []

    @tool
    def emit_candidate_opportunity(
        opportunity_type: str,
        signal_ids: list[str],
        mechanism_statement: str,
        mechanism_shared_segment: str,
        mechanism_actionable_because: str,
        why_this: str,
        why_you: str,
        why_now: str,
        mechanism_holds: bool,
        critique_reason: str,
        pain_severity: int = 0,
    ) -> str:
        """Propose one candidate opportunity per §9.3's pattern table,
        combining only signal_ids from the signals you were given. Before
        calling this, self-critique your own mechanism against the rubric
        (does it name a real shared segment, a real reason it's actionable
        now?) and set mechanism_holds honestly — a mechanism that doesn't
        hold gets rejected downstream regardless of what you set here."""

        raw = RawCandidate(
            opportunity_type=opportunity_type,
            signal_ids=tuple(signal_ids),
            mechanism_statement=mechanism_statement,
            mechanism_shared_segment=mechanism_shared_segment,
            mechanism_actionable_because=mechanism_actionable_because,
            why_this=why_this,
            why_you=why_you,
            why_now=why_now,
            mechanism_holds=mechanism_holds,
            critique_reason=critique_reason,
            pain_severity=pain_severity,
        )
        collected.append(raw)
        return "recorded" if passes_self_critique(raw) else "recorded_but_will_likely_be_rejected"

    def _before_model_call(event: BeforeModelCallEvent) -> None:
        if not budget.allow_iteration():
            event.cancel = "runtime contract exhausted (§10.1a)"

    def _before_tool_call(event: BeforeToolCallEvent) -> None:
        if not budget.allow_tool_call():
            event.cancel_tool = "runtime contract exhausted (§10.1a)"

    agent = Agent(
        model=OpenAIModel(
            client_args=opencode_go_client_args(), model_id=_MODEL_ID, params={"max_tokens": contract.max_tokens}
        ),
        tools=[emit_candidate_opportunity],
        system_prompt=(
            "You are the Synthesis Agent. Combine the signals below using the "
            "§9.3 pattern table (competitor pain + our strength -> "
            "competitive_gap; our pain + inbound demand -> unmet_need; our "
            "strength with no demand signal is a proof point, not an "
            "opportunity — don't emit one for it). Every candidate needs a "
            "concrete opportunity_mechanism stating a real shared segment and "
            "a real reason it's actionable now (§9.5) — pain and strength "
            "correlating is not by itself a reason to act. opportunity_type "
            f"must be exactly one of: {', '.join(sorted(_KNOWN_TYPES))} — no "
            "other spelling or variant is accepted. Call "
            "emit_candidate_opportunity once per candidate."
        ),
        hooks=[_before_model_call, _before_tool_call],
    )
    return agent, collected


def live_collect() -> RawCandidateCollector:
    """Returns a `collect` callable that runs a real Strands agent — pass
    this as `run_synthesis_agent`'s `collect` argument in production."""

    def _attempt(contract: AgentRuntimeContract, signals: list[Signal]) -> list[RawCandidate]:
        from strands.types.exceptions import MaxTokensReachedException

        budget = RuntimeBudget(contract)
        agent, collected = _build_live_agent(contract, budget)
        prompt = f"Signals for this run:\n{_signals_prompt(signals)}"
        # ponytail: OpenCode Go's reasoning length is highly variable run to
        # run — a single completion sometimes overruns max_tokens before it
        # finishes. Strands keeps the partial turn in history, so resuming
        # with the same agent picks up where it stopped rather than losing
        # the run; capped at 3 attempts so a genuinely stuck model still
        # surfaces the exception instead of retrying forever.
        for attempt in range(3):
            try:
                agent(prompt)
                break
            except MaxTokensReachedException:
                if attempt == 2:
                    raise
                prompt = "Continue: finish emitting any remaining candidate_opportunity calls, then stop."
        return collected

    def collect(contract: AgentRuntimeContract, signals: list[Signal]) -> list[RawCandidate]:
        # ponytail: distinct failure mode from the max-tokens retry above —
        # the model sometimes rambles through its whole budget without ever
        # calling the tool (no exception, just an empty turn). A fresh agent
        # on a second attempt reliably breaks that specific rut; capped at 2
        # full attempts total.
        for attempt in range(2):
            collected = _attempt(contract, signals)
            if collected or attempt == 1:
                return collected
        return []

    return collect


if __name__ == "__main__":
    from backend.schemas.entities import SourceKind

    _CONTRACT = AgentRuntimeContract(max_tokens=2048)
    _SIGNALS = [
        Signal(
            id="sig_cmp_1",
            run_id="run_demo",
            source_kind=SourceKind.HN,
            aspect="pricing_pain",
            polarity=Polarity.NEGATIVE,
            claim_text="[Sentry] 8 public discussions in the last 45 days mention Sentry's pricing change.",
            evidence_ids=[],
            produced_by="competitor_agent",
        ),
        Signal(
            id="sig_fb_1",
            run_id="run_demo",
            source_kind=SourceKind.SIMULATED,
            aspect="pricing_pain",
            polarity=Polarity.POSITIVE,
            claim_text="6 of 8 recent feedback items praise PulseStack's flat, predictable pricing.",
            evidence_ids=["evd_fb_1"],
            produced_by="feedback_pipeline_labeller",
        ),
    ]

    def _fake_collect(contract: AgentRuntimeContract, signals: list[Signal]) -> list[RawCandidate]:
        return [
            RawCandidate(
                opportunity_type="competitive_gap",
                signal_ids=("sig_cmp_1", "sig_fb_1"),
                mechanism_statement=(
                    "Teams frustrated by Sentry's pricing change can be targeted with PulseStack's flat "
                    "pricing because PulseStack already serves this exact segment at a predictable price."
                ),
                mechanism_shared_segment="teams evaluating alternatives to Sentry on price",
                mechanism_actionable_because="PulseStack already has a confirmed flat-pricing plan to offer",
                why_this="Sentry's pricing change is driving public complaints.",
                why_you="PulseStack's own users already praise its flat, predictable pricing.",
                why_now="8 discussions about Sentry pricing in the last 45 days.",
                mechanism_holds=True,
                critique_reason="Shared segment and actionable reason are both concrete and evidenced.",
            ),
            RawCandidate(
                opportunity_type="competitive_gap",
                signal_ids=("sig_cmp_1",),
                mechanism_statement="This could be a good opportunity for PulseStack.",
                mechanism_shared_segment="",
                mechanism_actionable_because="",
                why_this="x",
                why_you="y",
                why_now="z",
                mechanism_holds=True,  # model over-claims; concreteness check must still catch it
                critique_reason="looks fine",
            ),
        ]

    _output, _invocation, _rejected = run_synthesis_agent(
        _SIGNALS, run_id="run_demo", contract=_CONTRACT, collect=_fake_collect
    )
    assert len(_output.candidate_opportunities) == 1, _output.candidate_opportunities
    assert len(_output.claims) == 4
    assert _output.candidate_opportunities[0].evidence_confidence == EvidenceConfidence.LOW
    assert _output.candidate_opportunities[0].priority == Priority.LOW
    assert len(_rejected) == 1 and _rejected[0].reason == "failed_self_critique"
    assert _invocation.component == "synthesis_agent"
    print("ok")
