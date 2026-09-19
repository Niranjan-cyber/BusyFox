"""Orchestrator (Task 21) — wires Market / Feedback / Competitor -> Synthesis
-> Evidence Check -> Quality Gate + Ranker -> DynamoDB into the real pipeline
Step Functions runs (§10.1, §17.1), replacing Task 6's single stub Lambda.

Every stage is an already-committed, independently-tested Task 15-20
function; this module's only job is data plumbing between them — no new
agent logic, no new gate checks.

One gap it has to bridge: Signal (§14.7) intentionally carries only the
"trimmed public shape" — no raw quote or URL — but Evidence Check needs
both to verify a claim. The Market/Competitor agents' raw tool-call output
(`RawMarketSignal`/`RawCompetitorSignal`) does carry a `source_url` and a
`date_window` string; this module keeps that alongside each accepted
Signal instead of letting it get dropped, by reusing those agents' own
`validate_claims`/`build_signal` rather than their higher-level
`run_*_agent` wrappers (which discard it). Nothing about those agents'
tested behaviour changes.

ponytail: no separate "raw source page text" fetch for Market/Competitor
signals — `quote` and `source_text` are the same string (the claim_text the
agent already asserted), since the collectors don't preserve the original
page text. Evidence Check's quote-exists check is therefore trivially true
for these; its semantic-support check (does this text really support this
specific claim?) is still real. Revisit if a richer collector-level raw-text
cache lands. Feedback-origin signals don't need this: Task 13/14's labeller
and Task 10's PulseStack simulator already produce real Evidence with a
real quote, reused here as-is.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import NamedTuple, Optional

from backend.agents.competitor_agent import (
    RawCompetitorSignal,
    RawSignalCollector as CompetitorCollector,
)
from backend.agents.competitor_agent import build_signal as build_competitor_signal
from backend.agents.competitor_agent import validate_claims as validate_competitor_claims
from backend.agents.market_agent import RawMarketSignal, RuntimeBudget
from backend.agents.market_agent import RawSignalCollector as MarketCollector
from backend.agents.market_agent import build_signal as build_market_signal
from backend.agents.market_agent import validate_claims as validate_market_claims
from backend.agents.synthesis_agent import RawCandidateCollector, run_synthesis_agent
from backend.db.dynamo import put_entity
from backend.pipeline.evidence_check import EvidenceCandidate, SemanticSupportChecker, run_evidence_check
from backend.pipeline.quality_gate import QualityGateResult, run_quality_gate
from backend.schemas.entities import (
    AgentInvocation,
    AgentRuntimeContract,
    Business,
    DynamoKeyPrefix,
    Evidence,
    Opportunity,
    RejectedCandidate,
    RetrievalMode,
    Run,
    RunStatus,
    Signal,
)
from backend.simulator.pulsestack import PulseStackFeedback, generate_pulsestack_feedback, load_scenario

_DAYS_RE = re.compile(r"(\d+)\s*days?")


def _published_at(date_window: str, *, now: datetime) -> Optional[datetime]:
    """Best-effort recovery of a real date from a raw signal's date_window
    string (e.g. "last 45 days") — None (treated as always-fresh by
    `evidence_check.check_freshness`) when it isn't parseable."""

    match = _DAYS_RE.search(date_window)
    return now - timedelta(days=int(match.group(1))) if match else None


class _Provenance(NamedTuple):
    url: str
    published_at: Optional[datetime]


@dataclass
class ResearchStageResult:
    signals: list[Signal]
    invocation: AgentInvocation
    provenance: dict[str, _Provenance]  # signal_id -> where its quote/date came from


def run_market_stage(
    *, run_id: str, contract: AgentRuntimeContract, collect: MarketCollector, now: datetime
) -> ResearchStageResult:
    budget = RuntimeBudget(contract)
    raw_signals = collect(contract)
    accepted, _rejected = validate_market_claims(raw_signals)
    signals = [build_market_signal(raw, run_id=run_id, index=i) for i, raw in enumerate(accepted)]
    provenance = {
        signal.id: _Provenance(raw.source_url, _published_at(raw.date_window, now=now))
        for signal, raw in zip(signals, accepted)
    }
    return ResearchStageResult(signals=signals, invocation=budget.to_invocation(), provenance=provenance)


def run_competitor_stage(
    *,
    run_id: str,
    named_competitors: list[str],
    contract: AgentRuntimeContract,
    collect: CompetitorCollector,
    now: datetime,
) -> ResearchStageResult:
    budget = RuntimeBudget(contract)
    raw_signals = collect(contract)
    accepted, _rejected = validate_competitor_claims(raw_signals, named_competitors=named_competitors)
    signals = [build_competitor_signal(raw, run_id=run_id, index=i) for i, raw in enumerate(accepted)]
    provenance = {
        signal.id: _Provenance(raw.source_url, _published_at(raw.date_window, now=now))
        for signal, raw in zip(signals, accepted)
    }
    return ResearchStageResult(
        signals=signals, invocation=budget.to_invocation(component="competitor_agent"), provenance=provenance
    )


def run_feedback_stage(*, run_id: str, seed: int = 1) -> PulseStackFeedback:
    """PulseStack's own feedback, for the simulated demo business (§18.1:
    always labelled simulated). A real, uploaded-data business would call
    Task 13/14's `feedback_pipeline`/`feedback_labelling` here instead —
    both return the same `evidence`+`signals` shape this module consumes."""

    return generate_pulsestack_feedback(load_scenario(), run_id, seed)


def _matched_signal_ids(opportunity: Opportunity) -> set[str]:
    """Every signal Synthesis cited when building this opportunity — mirrors
    `quality_gate._signal_ids`, duplicated rather than imported since that
    helper is private to its own module."""

    return (
        {s.signal_id for s in opportunity.strengths_it_builds_on}
        | {p.signal_id for p in opportunity.pains_to_fix_first}
        | {c.signal_id for c in opportunity.competitive_context}
    )


def _candidates_for_claim(
    claim_id: str,
    signal_ids: set[str],
    *,
    now: datetime,
    signals_by_id: dict[str, Signal],
    provenance: dict[str, _Provenance],
    feedback_evidence_by_signal: dict[str, list[Evidence]],
) -> list[EvidenceCandidate]:
    candidates: list[EvidenceCandidate] = []
    for signal_id in signal_ids:
        signal = signals_by_id.get(signal_id)
        if signal is None:
            continue

        feedback_evidence = feedback_evidence_by_signal.get(signal_id)
        if feedback_evidence:
            for evidence in feedback_evidence:
                candidates.append(
                    EvidenceCandidate(
                        claim_id=claim_id,
                        source_document_id=evidence.source_document_id,
                        source_kind=evidence.source_kind,
                        retrieval_mode=evidence.retrieval_mode,
                        url=evidence.url,
                        retrieved_at=evidence.retrieved_at,
                        quote=evidence.quote,
                        source_text=evidence.quote,
                        aspect=signal.aspect,
                        polarity=signal.polarity,
                        produced_by=signal.produced_by,
                        author=evidence.author,
                        published_at=evidence.published_at,
                    )
                )
            continue

        prov = provenance.get(signal_id)
        candidates.append(
            EvidenceCandidate(
                claim_id=claim_id,
                source_document_id=f"src_{signal_id}",
                source_kind=signal.source_kind,
                retrieval_mode=RetrievalMode.LIVE,
                url=prov.url if prov else "",
                retrieved_at=now,
                quote=signal.claim_text,
                source_text=signal.claim_text,
                aspect=signal.aspect,
                polarity=signal.polarity,
                produced_by=signal.produced_by,
                author=None,
                published_at=prov.published_at if prov else None,
            )
        )
    return candidates


class PipelineResult(NamedTuple):
    run: Run
    business: Business
    signals: list[Signal]
    claims: list
    evidence: list[Evidence]
    ranked: list[Opportunity]
    blocked: list[Opportunity]
    rejected: list
    synthesis_rejected: list  # candidates Synthesis itself dropped (§10.3), never reaching the gate


def run_pipeline(
    business: Business,
    *,
    run_id: str,
    now: datetime,
    market_collect: MarketCollector,
    competitor_collect: CompetitorCollector,
    synthesis_collect: RawCandidateCollector,
    semantic_check: SemanticSupportChecker,
    seed: int = 1,
    market_contract: AgentRuntimeContract = AgentRuntimeContract(max_tokens=1024),
    competitor_contract: AgentRuntimeContract = AgentRuntimeContract(max_tokens=1024),
    synthesis_contract: AgentRuntimeContract = AgentRuntimeContract(max_tokens=4096),
) -> PipelineResult:
    """Entry point Step Functions' orchestrator Lambda calls (§10.1): the
    Day-2 goal, made real — a full run producing at least one gate-passed
    opportunity end to end."""

    market = run_market_stage(run_id=run_id, contract=market_contract, collect=market_collect, now=now)
    competitor = run_competitor_stage(
        run_id=run_id,
        named_competitors=business.named_competitors,
        contract=competitor_contract,
        collect=competitor_collect,
        now=now,
    )
    feedback = run_feedback_stage(run_id=run_id, seed=seed)

    all_signals = market.signals + competitor.signals + feedback.signals
    provenance = {**market.provenance, **competitor.provenance}
    feedback_evidence_by_id = {e.id: e for e in feedback.evidence}
    feedback_evidence_by_signal = {
        s.id: [feedback_evidence_by_id[eid] for eid in s.evidence_ids if eid in feedback_evidence_by_id]
        for s in feedback.signals
    }

    synthesis_output, synthesis_invocation, synth_rejected = run_synthesis_agent(
        all_signals, run_id=run_id, contract=synthesis_contract, collect=synthesis_collect
    )

    signals_by_id = {s.id: s for s in all_signals}
    candidates: list[EvidenceCandidate] = []
    for opportunity in synthesis_output.candidate_opportunities:
        matched = _matched_signal_ids(opportunity)
        for claim_id in opportunity.claim_ids:
            candidates.extend(
                _candidates_for_claim(
                    claim_id,
                    matched,
                    now=now,
                    signals_by_id=signals_by_id,
                    provenance=provenance,
                    feedback_evidence_by_signal=feedback_evidence_by_signal,
                )
            )

    evidence_result = run_evidence_check(
        synthesis_output.claims, candidates, all_signals, semantic_check=semantic_check, now=now
    )

    gate_result: QualityGateResult = run_quality_gate(
        synthesis_output.candidate_opportunities,
        evidence_result.claims,
        evidence_result.evidence,
        evidence_result.contradictions,
        all_signals,
        business,
    )

    run = Run(
        id=run_id,
        business_id=business.id,
        started_at=now,
        finished_at=now,
        status=RunStatus.SUCCEEDED,
        agent_invocations=[market.invocation, competitor.invocation, synthesis_invocation],
        opportunities_produced=len(gate_result.ranked) + len(gate_result.blocked),
        opportunities_rejected=len(gate_result.rejected),
        estimated_cost_usd=0.0,
    )

    return PipelineResult(
        run=run,
        business=business,
        signals=all_signals,
        claims=gate_result.claims,
        evidence=evidence_result.evidence,
        ranked=gate_result.ranked,
        blocked=gate_result.blocked,
        rejected=gate_result.rejected,
        synthesis_rejected=synth_rejected,
    )


def persist(table, result: PipelineResult) -> None:
    """DynamoDB writes for a completed run (Task 20's DAO; Task 21's job per
    docs/contract.md). Parent keys follow the chain the P0 API surface (Task
    2/22/23) actually queries by: Business -> Run/Signal/Opportunity ->
    Claim -> Evidence — Signal and Opportunity parent to the Business
    (not the Run) because `/businesses/{id}/opportunities` and
    `/businesses/{id}/feedback-summary` list by business, not by run."""

    biz_key = f"{DynamoKeyPrefix.BUSINESS.value}{result.business.id}"

    put_entity(table, result.business)
    put_entity(table, result.run, parent_key=biz_key)
    for signal in result.signals:
        put_entity(table, signal, parent_key=biz_key)
    for opportunity in (*result.ranked, *result.blocked):
        put_entity(table, opportunity, parent_key=biz_key)
    for rejected in result.rejected:
        candidate = RejectedCandidate(
            id=rejected.opportunity_id,
            opportunity_type=rejected.opportunity_type,
            title=rejected.title,
            rejected_because=rejected.rejected_because,
            failed_gate=rejected.failed_gate,
        )
        put_entity(table, candidate, parent_key=biz_key)
    for claim in result.claims:
        put_entity(table, claim, parent_key=f"{DynamoKeyPrefix.OPPORTUNITY.value}{claim.opportunity_id}")

    # Evidence.id doesn't carry its owning claim_id as a field — recovered
    # from whichever claim's evidence_ids lists it (run_evidence_check sets
    # both sides at once, so this always resolves for evidence it produced).
    claims_by_evidence_id = {eid: claim.id for claim in result.claims for eid in claim.evidence_ids}
    for evidence in result.evidence:
        claim_id = claims_by_evidence_id.get(evidence.id)
        parent = f"{DynamoKeyPrefix.CLAIM.value}{claim_id}" if claim_id else None
        put_entity(table, evidence, parent_key=parent)


if __name__ == "__main__":
    from backend.fixtures.fixtures import BUSINESS
    from backend.schemas.entities import (
        ClaimSupport,
        ClaimSupportStatus,
        EvidenceConfidence,
        Polarity,
        Priority,
        SourceKind,
    )
    from datetime import timezone

    from backend.agents.synthesis_agent import RawCandidate

    _NOW = datetime(2026, 9, 18, tzinfo=timezone.utc)

    def _fake_market_collect(contract: AgentRuntimeContract) -> list[RawMarketSignal]:
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

    def _fake_semantic_check(claim_text: str, quote: str) -> ClaimSupport:
        return ClaimSupport(status=ClaimSupportStatus.SUPPORTS, confidence=0.9, reason="quote directly supports the claim")

    _result = run_pipeline(
        BUSINESS,
        run_id="run_demo",
        now=_NOW,
        market_collect=_fake_market_collect,
        competitor_collect=_fake_competitor_collect,
        synthesis_collect=_fake_synthesis_collect,
        semantic_check=_fake_semantic_check,
    )

    assert len(_result.ranked) == 1, _result.ranked
    assert _result.rejected == [], _result.rejected
    assert _result.ranked[0].evidence_confidence == EvidenceConfidence.HIGH
    assert _result.ranked[0].priority == Priority.HIGH
    assert _result.run.opportunities_produced == 1
    assert _result.run.opportunities_rejected == 0
    print("ok — gate-passed opportunity produced end to end")
