"""Market Agent (Task 15) — Strands agent (Haiku) over web/HN/GitHub
producing claim-level, count/date/source-anchored signals (§9.4), bound by
the §10.1a runtime contract. Output is structurally `signals[]`-only:
ResearchAgentOutput has no `opportunities` field for this component to fill.

Split the same way Task 14 split the feedback labeller: pure, testable
logic below (claim validation, budget enforcement, output assembly) with no
Strands/AWS dependency; the real Strands wiring at the bottom is
network/credential-dependent and only smoke-tested here, same as
`backend/pipeline/feedback_labelling.py`'s `bedrock_labeller`.
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from typing import Callable, NamedTuple

from backend.schemas.entities import (
    AgentInvocation,
    AgentRuntimeContract,
    Polarity,
    ResearchAgentOutput,
    Signal,
    SourceKind,
)

# Hoisted out of `_build_live_agent`: `from __future__ import annotations`
# makes every hook callback's `event:` annotation a string, and
# `strands`' hook registry resolves it via `typing.get_type_hints`, which
# looks the name up in the callback's *module* globals — a name imported
# inside the function's own local scope is invisible there and fails with
# "cannot infer event type" the first time a real strands.Agent is built.
from strands.hooks import BeforeModelCallEvent, BeforeToolCallEvent

_COMPONENT = "market_agent"
# MARKET_AGENT_MODEL_ID lets this be swapped without a code change. Default is
# an OpenCode Go model id (see opencode_go_client_args below), not a Bedrock one.
_MODEL_ID = os.environ.get("MARKET_AGENT_MODEL_ID", "deepseek-v4.1-flash")

# §9.4 — tool sources this agent is allowed to draw claims from.
_ALLOWED_SOURCE_KINDS = frozenset({SourceKind.WEB_PUBLIC, SourceKind.HN, SourceKind.GITHUB})


@dataclass(frozen=True)
class RawMarketSignal:
    """One candidate claim exactly as the model's `emit_market_signal` tool
    call reported it — before §9.4 validation."""

    aspect: str
    polarity: str
    claim_text: str
    count: int
    date_window: str
    source_url: str
    source_kind: SourceKind


class RejectedClaim(NamedTuple):
    """A claim the schema dropped before Synthesis ever saw it (§9.4).
    Not part of any entity — the orchestrator logs these, nothing more."""

    reason: str
    raw: RawMarketSignal


# ---------------------------------------------------------------------------
# Pure logic — §9.4 schema validation, unit-testable without Strands/AWS.
# ---------------------------------------------------------------------------


def is_valid_market_claim(raw: RawMarketSignal) -> bool:
    """§9.4: a signal missing a concrete count, date window, or source
    reference fails validation — "the market is growing" has none of the
    three and is rejected here, not passed on labelled generic."""

    return (
        bool(raw.aspect)
        and raw.polarity in ("positive", "negative")
        and raw.count > 0
        and bool(raw.date_window.strip())
        and (raw.source_url.startswith("http://") or raw.source_url.startswith("https://"))
        and raw.source_kind in _ALLOWED_SOURCE_KINDS
    )


def build_signal(raw: RawMarketSignal, *, run_id: str, index: int) -> Signal:
    return Signal(
        id=f"sig_mkt_{run_id}_{index}",
        run_id=run_id,
        source_kind=raw.source_kind,
        aspect=raw.aspect,
        polarity=Polarity.POSITIVE if raw.polarity == "positive" else Polarity.NEGATIVE,
        claim_text=raw.claim_text,
        evidence_ids=[],
        produced_by=_COMPONENT,
    )


def validate_claims(raw_signals: list[RawMarketSignal]) -> tuple[list[RawMarketSignal], list[RejectedClaim]]:
    accepted, rejected = [], []
    for raw in raw_signals:
        if is_valid_market_claim(raw):
            accepted.append(raw)
        else:
            rejected.append(RejectedClaim(reason="rejected_generic_market_claim", raw=raw))
    return accepted, rejected


# ---------------------------------------------------------------------------
# §10.1a runtime contract — enforced by code, not left as a prompt
# instruction. Pure counter/clock logic; Strands hooks below just call it.
# ---------------------------------------------------------------------------


@dataclass
class RuntimeBudget:
    contract: AgentRuntimeContract
    clock: Callable[[], float] = time.monotonic
    _started_at: float = field(init=False, default=0.0)
    _iterations: int = field(init=False, default=0)
    _tool_calls: int = field(init=False, default=0)
    _truncated: bool = field(init=False, default=False)

    def __post_init__(self) -> None:
        self._started_at = self.clock()

    def _elapsed(self) -> float:
        return self.clock() - self._started_at

    def allow_iteration(self) -> bool:
        """Call before each model turn. False means the contract is already
        exhausted — the caller must stop instead of taking another turn."""

        if self._iterations >= self.contract.max_iterations or self._elapsed() > self.contract.max_runtime_seconds:
            self._truncated = True
            return False
        self._iterations += 1
        return True

    def allow_tool_call(self) -> bool:
        """Call before each tool invocation. False means stop; the caller
        must not run the tool."""

        if self._tool_calls >= self.contract.max_tool_calls or self._elapsed() > self.contract.max_runtime_seconds:
            self._truncated = True
            return False
        self._tool_calls += 1
        return True

    @property
    def truncated(self) -> bool:
        return self._truncated

    def to_invocation(self, *, component: str = _COMPONENT) -> AgentInvocation:
        return AgentInvocation(
            component=component,
            iterations=self._iterations,
            tool_calls=self._tool_calls,
            runtime_seconds=round(self._elapsed(), 3),
            truncated=self._truncated,
        )


def assemble_research_output(
    raw_signals: list[RawMarketSignal], *, run_id: str, budget: RuntimeBudget
) -> tuple[ResearchAgentOutput, AgentInvocation, list[RejectedClaim]]:
    """§9.4 validation + §10.1a truncation labelling, all in one place — the
    boundary the real Strands wiring below hands its raw tool-call output
    through, and what tests exercise directly."""

    accepted, rejected = validate_claims(raw_signals)
    signals = [build_signal(raw, run_id=run_id, index=i) for i, raw in enumerate(accepted)]
    output = ResearchAgentOutput(run_id=run_id, produced_by=_COMPONENT, signals=signals, truncated=budget.truncated)
    return output, budget.to_invocation(), rejected


# ---------------------------------------------------------------------------
# Real Strands wiring — network/AWS-credential-dependent. Tests inject a
# fake `raw_signals` producer instead of a live Agent (mirrors Task 5's
# `probe()` / Task 14's `bedrock_labeller`, neither unit-tested against a
# live network call).
# ---------------------------------------------------------------------------

RawSignalCollector = Callable[[AgentRuntimeContract], list[RawMarketSignal]]


def run_market_agent(
    business_context: str, *, run_id: str, contract: AgentRuntimeContract, collect: RawSignalCollector
) -> tuple[ResearchAgentOutput, AgentInvocation, list[RejectedClaim]]:
    """Entry point Task 21's orchestrator calls. `collect` does the actual
    tool-calling loop (real Strands agent in production, a fake in tests)
    and returns whatever candidate claims it produced before the budget or
    the model itself decided to stop."""

    budget = RuntimeBudget(contract)
    raw_signals = collect(contract)
    return assemble_research_output(raw_signals, run_id=run_id, budget=budget)


def _build_live_agent(contract: AgentRuntimeContract, budget: RuntimeBudget):
    """Wires a real strands.Agent with the web/HN/GitHub tools and the
    §10.1a hooks. Imports strands lazily so the pure logic above never
    requires the SDK or AWS credentials to be importable/testable."""

    from strands import Agent, tool
    from strands.models.openai import OpenAIModel

    from backend.collectors.github import fetch_github_signals
    from backend.collectors.hn import fetch_hn_signals
    from backend.collectors.tavily import probe as tavily_probe

    collected: list[RawMarketSignal] = []

    @tool
    def search_web(query: str) -> str:
        """Search the public web for market/timing signals about `query`."""
        report = tavily_probe(query, api_key=_tavily_api_key())
        return str(report)[: 4000]

    @tool
    def search_hn(query: str) -> str:
        """Search Hacker News discussions matching `query`."""
        hits = fetch_hn_signals(query, run_id="probe")[: contract.max_results]
        return "\n".join(h.claim_text for h in hits)

    @tool
    def search_github(owner: str, repo: str) -> str:
        """Look up recent release/issue activity for owner/repo on GitHub."""
        hits = fetch_github_signals(owner, repo, run_id="probe")[: contract.max_results]
        return "\n".join(h.claim_text for h in hits)

    @tool
    def emit_market_signal(
        aspect: str, polarity: str, claim_text: str, count: int, date_window: str, source_url: str, source_kind: str
    ) -> str:
        """Record one claim-level market signal. `count` and `date_window`
        must be concrete (e.g. count=7, date_window="last 60 days") — a
        generic claim with no count/date/source is rejected, not recorded."""

        raw = RawMarketSignal(
            aspect=aspect,
            polarity=polarity,
            claim_text=claim_text,
            count=count,
            date_window=date_window,
            source_url=source_url,
            source_kind=SourceKind(source_kind),
        )
        collected.append(raw)
        return "recorded" if is_valid_market_claim(raw) else "rejected_generic_market_claim"

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
        tools=[search_web, search_hn, search_github, emit_market_signal],
        system_prompt=(
            "You are the Market Agent. Find claim-level, count/date/source-anchored "
            "market and timing signals — never a bare summary like 'the market is "
            "growing'. Call emit_market_signal once per claim you want recorded."
        ),
        hooks=[_before_model_call, _before_tool_call],
    )
    return agent, collected


def opencode_go_client_args() -> dict:
    """This agent (and Competitor, Synthesis, Evidence Check) call an LLM
    through OpenCode Go's OpenAI-compatible gateway (https://opencode.ai/docs/go/)
    rather than Bedrock — AWS Bedrock's real-time inference quota is 0
    requests/minute on every account available to this project (confirmed
    against Anthropic's and Amazon's own models alike, 2026-09-19), so
    nothing on Bedrock is actually callable regardless of which model is
    chosen there.

    Go requires an `x-opencode-session` header on every request ("Request is
    missing x-opencode-session and cannot be routed efficiently") — a fresh
    id per client is fine, it's for Go's own routing/caching, not something
    this project needs to track or reuse across calls."""

    key = os.environ.get("OPENCODE_GO_API_KEY")
    if not key:
        raise RuntimeError("OPENCODE_GO_API_KEY not set")

    import uuid

    return {
        "api_key": key,
        "base_url": "https://opencode.ai/zen/go/v1",
        "default_headers": {"x-opencode-session": str(uuid.uuid4())},
    }


def _tavily_api_key() -> str:
    import os

    key = os.environ.get("TAVILY_API_KEY")
    if not key:
        raise RuntimeError("TAVILY_API_KEY not set")
    return key


def live_collect(business_context: str) -> RawSignalCollector:
    """Returns a `collect` callable that runs a real Strands agent —
    pass this as `run_market_agent`'s `collect` argument in production."""

    def collect(contract: AgentRuntimeContract) -> list[RawMarketSignal]:
        budget = RuntimeBudget(contract)
        agent, collected = _build_live_agent(contract, budget)
        agent(business_context)
        return collected

    return collect


if __name__ == "__main__":
    _CONTRACT = AgentRuntimeContract(max_tokens=1024)

    def _fake_collect(contract: AgentRuntimeContract) -> list[RawMarketSignal]:
        return [
            RawMarketSignal(
                aspect="market_timing",
                polarity="positive",
                claim_text="7 public discussions in the last 60 days mention teams reconsidering monitoring costs.",
                count=7,
                date_window="last 60 days",
                source_url="https://news.ycombinator.com/item?id=1",
                source_kind=SourceKind.HN,
            ),
            RawMarketSignal(
                aspect="market_growth",
                polarity="positive",
                claim_text="The observability market is growing.",
                count=0,
                date_window="",
                source_url="not-a-url",
                source_kind=SourceKind.WEB_PUBLIC,
            ),
        ]

    _output, _invocation, _rejected = run_market_agent(
        "PulseStack, an alerting SaaS for SRE teams", run_id="run_demo", contract=_CONTRACT, collect=_fake_collect
    )
    assert len(_output.signals) == 1, _output.signals
    assert _output.signals[0].aspect == "market_timing"
    assert len(_rejected) == 1 and _rejected[0].reason == "rejected_generic_market_claim"
    assert _invocation.component == "market_agent"
    print("ok")
