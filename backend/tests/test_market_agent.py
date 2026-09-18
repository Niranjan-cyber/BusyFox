"""Market Agent (Task 15) — §9.4 claim validation, §10.1a runtime contract.

Only the pure logic is exercised here; the real Strands/Bedrock wiring in
`_build_live_agent`/`live_collect` is network/credential-dependent and not
unit-tested, same treatment as Task 5's `tavily.probe` and Task 14's
`bedrock_labeller`.
"""

from __future__ import annotations

from backend.agents.market_agent import (
    RawMarketSignal,
    RuntimeBudget,
    assemble_research_output,
    build_signal,
    is_valid_market_claim,
    run_market_agent,
    validate_claims,
)
from backend.schemas.entities import AgentRuntimeContract, Polarity, Signal, SourceKind


def _raw(**overrides) -> RawMarketSignal:
    defaults = dict(
        aspect="market_timing",
        polarity="positive",
        claim_text="7 public discussions in the last 60 days mention reconsidering monitoring costs.",
        count=7,
        date_window="last 60 days",
        source_url="https://news.ycombinator.com/item?id=1",
        source_kind=SourceKind.HN,
    )
    defaults.update(overrides)
    return RawMarketSignal(**defaults)


def test_valid_claim_accepted():
    assert is_valid_market_claim(_raw())


def test_generic_claim_missing_count_rejected():
    assert not is_valid_market_claim(_raw(count=0))


def test_generic_claim_missing_date_window_rejected():
    assert not is_valid_market_claim(_raw(date_window=""))


def test_generic_claim_missing_source_rejected():
    assert not is_valid_market_claim(_raw(source_url="not-a-url"))


def test_claim_outside_allowed_source_kinds_rejected():
    assert not is_valid_market_claim(_raw(source_kind=SourceKind.SIMULATED))


def test_build_signal_is_schema_valid():
    signal = build_signal(_raw(), run_id="run1", index=0)
    Signal.model_validate(signal.model_dump())
    assert signal.source_kind == SourceKind.HN
    assert signal.polarity == Polarity.POSITIVE
    assert signal.produced_by == "market_agent"
    assert signal.evidence_ids == []


def test_validate_claims_splits_accepted_and_rejected():
    accepted, rejected = validate_claims([_raw(), _raw(count=0, date_window="", source_url="bad")])
    assert len(accepted) == 1
    assert len(rejected) == 1
    assert rejected[0].reason == "rejected_generic_market_claim"


def test_runtime_budget_stops_after_max_iterations():
    contract = AgentRuntimeContract(max_iterations=2, max_tool_calls=10, max_runtime_seconds=60, max_tokens=100)
    budget = RuntimeBudget(contract, clock=lambda: 0.0)
    assert budget.allow_iteration()
    assert budget.allow_iteration()
    assert not budget.allow_iteration()
    assert budget.truncated


def test_runtime_budget_stops_after_max_tool_calls():
    contract = AgentRuntimeContract(max_iterations=10, max_tool_calls=1, max_runtime_seconds=60, max_tokens=100)
    budget = RuntimeBudget(contract, clock=lambda: 0.0)
    assert budget.allow_tool_call()
    assert not budget.allow_tool_call()
    assert budget.truncated


def test_runtime_budget_stops_after_wall_clock_limit():
    times = iter([0.0, 0.0, 100.0])  # __post_init__, then two allow_iteration() elapsed checks
    contract = AgentRuntimeContract(max_iterations=10, max_tool_calls=10, max_runtime_seconds=5, max_tokens=100)
    budget = RuntimeBudget(contract, clock=lambda: next(times))
    assert budget.allow_iteration()
    assert not budget.allow_iteration()
    assert budget.truncated


def test_runtime_budget_not_truncated_within_limits():
    contract = AgentRuntimeContract(max_iterations=3, max_tool_calls=6, max_runtime_seconds=60, max_tokens=100)
    budget = RuntimeBudget(contract, clock=lambda: 0.0)
    assert budget.allow_iteration()
    assert budget.allow_tool_call()
    assert not budget.truncated
    invocation = budget.to_invocation()
    assert invocation.iterations == 1
    assert invocation.tool_calls == 1
    assert invocation.truncated is False


def test_assemble_research_output_drops_generic_claims():
    contract = AgentRuntimeContract(max_iterations=3, max_tool_calls=6, max_runtime_seconds=60, max_tokens=100)
    budget = RuntimeBudget(contract, clock=lambda: 0.0)
    output, invocation, rejected = assemble_research_output(
        [_raw(), _raw(aspect="market_growth", polarity="positive", claim_text="The market is growing.", count=0, date_window="", source_url="bad")],
        run_id="run1",
        budget=budget,
    )
    assert len(output.signals) == 1
    assert output.signals[0].claim_text.startswith("7 public discussions")
    assert output.truncated is False
    assert invocation.component == "market_agent"
    assert len(rejected) == 1


def test_assemble_research_output_has_no_opportunities_field():
    """§10.1a — structurally enforced, not just unused by convention."""
    contract = AgentRuntimeContract(max_iterations=3, max_tool_calls=6, max_runtime_seconds=60, max_tokens=100)
    output, _, _ = assemble_research_output([_raw()], run_id="run1", budget=RuntimeBudget(contract, clock=lambda: 0.0))
    assert not hasattr(output, "opportunities")
    assert not hasattr(output, "candidate_opportunities")


def test_run_market_agent_end_to_end_with_fake_collector():
    contract = AgentRuntimeContract(max_iterations=3, max_tool_calls=6, max_runtime_seconds=60, max_tokens=100)

    def fake_collect(_contract: AgentRuntimeContract) -> list[RawMarketSignal]:
        return [_raw(), _raw(aspect="dup", count=0, date_window="", source_url="bad")]

    output, invocation, rejected = run_market_agent(
        "PulseStack", run_id="run1", contract=contract, collect=fake_collect
    )
    assert len(output.signals) == 1
    assert len(rejected) == 1
    assert invocation.component == "market_agent"
