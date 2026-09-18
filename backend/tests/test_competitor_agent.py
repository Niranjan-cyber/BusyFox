"""Competitor Agent (Task 16) — §9.4 claim validation + §18.4 named-
competitor scope, §10.1a runtime contract (reused from Task 15).

Only the pure logic is exercised here; the real Strands/Bedrock wiring in
`_build_live_agent`/`live_collect` is network/credential-dependent and not
unit-tested, same treatment as Task 15's `market_agent`.
"""

from __future__ import annotations

from backend.agents.competitor_agent import (
    RawCompetitorSignal,
    assemble_research_output,
    build_signal,
    is_valid_competitor_claim,
    run_competitor_agent,
    validate_claims,
)
from backend.agents.market_agent import RuntimeBudget
from backend.schemas.entities import AgentRuntimeContract, Polarity, Signal, SourceKind

_NAMED = ["Sentry", "Datadog"]


def _raw(**overrides) -> RawCompetitorSignal:
    defaults = dict(
        competitor_name="Sentry",
        aspect="pricing_pain",
        polarity="negative",
        claim_text="8 public discussions in the last 45 days mention Sentry's pricing change.",
        count=8,
        date_window="last 45 days",
        source_url="https://news.ycombinator.com/item?id=2",
        source_kind=SourceKind.HN,
    )
    defaults.update(overrides)
    return RawCompetitorSignal(**defaults)


def test_valid_claim_accepted():
    assert is_valid_competitor_claim(_raw(), named_competitors=frozenset(_NAMED))


def test_claim_for_unnamed_competitor_rejected():
    assert not is_valid_competitor_claim(_raw(competitor_name="Acme Corp"), named_competitors=frozenset(_NAMED))


def test_generic_claim_missing_count_rejected():
    assert not is_valid_competitor_claim(_raw(count=0), named_competitors=frozenset(_NAMED))


def test_generic_claim_missing_date_window_rejected():
    assert not is_valid_competitor_claim(_raw(date_window=""), named_competitors=frozenset(_NAMED))


def test_generic_claim_missing_source_rejected():
    assert not is_valid_competitor_claim(_raw(source_url="not-a-url"), named_competitors=frozenset(_NAMED))


def test_claim_outside_allowed_source_kinds_rejected():
    assert not is_valid_competitor_claim(_raw(source_kind=SourceKind.SIMULATED), named_competitors=frozenset(_NAMED))


def test_app_store_and_producthunt_are_allowed_enrichment_sources():
    assert is_valid_competitor_claim(_raw(source_kind=SourceKind.APP_STORE), named_competitors=frozenset(_NAMED))
    assert is_valid_competitor_claim(_raw(source_kind=SourceKind.PRODUCT_HUNT), named_competitors=frozenset(_NAMED))


def test_build_signal_is_schema_valid_and_prefixed_with_competitor():
    signal = build_signal(_raw(), run_id="run1", index=0)
    Signal.model_validate(signal.model_dump())
    assert signal.source_kind == SourceKind.HN
    assert signal.polarity == Polarity.NEGATIVE
    assert signal.produced_by == "competitor_agent"
    assert signal.evidence_ids == []
    assert signal.claim_text.startswith("[Sentry]")


def test_validate_claims_splits_accepted_and_rejected():
    accepted, rejected = validate_claims(
        [_raw(), _raw(competitor_name="Acme Corp")], named_competitors=_NAMED
    )
    assert len(accepted) == 1
    assert len(rejected) == 1
    assert rejected[0].reason == "rejected_generic_competitor_claim"


def test_assemble_research_output_drops_out_of_scope_claims():
    contract = AgentRuntimeContract(max_iterations=3, max_tool_calls=6, max_runtime_seconds=60, max_tokens=100)
    budget = RuntimeBudget(contract, clock=lambda: 0.0)
    output, invocation, rejected = assemble_research_output(
        [_raw(), _raw(competitor_name="Acme Corp")],
        run_id="run1",
        named_competitors=_NAMED,
        budget=budget,
    )
    assert len(output.signals) == 1
    assert output.signals[0].claim_text.startswith("[Sentry]")
    assert output.truncated is False
    assert invocation.component == "competitor_agent"
    assert len(rejected) == 1


def test_assemble_research_output_has_no_opportunities_field():
    """§10.1a — structurally enforced, not just unused by convention."""
    contract = AgentRuntimeContract(max_iterations=3, max_tool_calls=6, max_runtime_seconds=60, max_tokens=100)
    output, _, _ = assemble_research_output(
        [_raw()], run_id="run1", named_competitors=_NAMED, budget=RuntimeBudget(contract, clock=lambda: 0.0)
    )
    assert not hasattr(output, "opportunities")
    assert not hasattr(output, "candidate_opportunities")


def test_run_competitor_agent_end_to_end_with_fake_collector():
    contract = AgentRuntimeContract(max_iterations=3, max_tool_calls=6, max_runtime_seconds=60, max_tokens=100)

    def fake_collect(_contract: AgentRuntimeContract) -> list[RawCompetitorSignal]:
        return [_raw(), _raw(competitor_name="Acme Corp")]

    output, invocation, rejected = run_competitor_agent(
        "PulseStack", run_id="run1", named_competitors=_NAMED, contract=contract, collect=fake_collect
    )
    assert len(output.signals) == 1
    assert len(rejected) == 1
    assert invocation.component == "competitor_agent"
