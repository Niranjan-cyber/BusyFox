"""Competitor Agent (Task 16) — Strands agent (Haiku) over web/HN/GitHub
(P0) plus App Store/Product Hunt (P1 enrichment) identifying relevant named
competitors' public signals, claim-level and count/date/source-anchored the
same way §9.4 requires of the Market Agent. Output is structurally
`signals[]`-only: ResearchAgentOutput has no `opportunities` field for this
component to fill (§10.1a).

Split the same way Task 15 split the Market Agent: pure, testable logic
below (claim validation, output assembly) with no Strands/AWS dependency,
reusing Task 15's `RuntimeBudget` rather than re-implementing §10.1a budget
tracking; the real Strands wiring at the bottom is network/credential-
dependent and only smoke-tested here.

§18.1/§18.4 guardrail: a claim is only accepted if `competitor_name` is one
of the business's own `named_competitors` (§8.1) — the agent enriches
competitors the business owner already identified, it doesn't invent or
go digging up ones nobody asked about. Source kinds are real-only (never
SIMULATED), so gate check 10 (§11.4 — no simulated claim ever attributed to
a real competitor) can't be violated structurally.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, NamedTuple

from backend.agents.market_agent import RuntimeBudget
from backend.schemas.entities import (
    AgentInvocation,
    AgentRuntimeContract,
    Polarity,
    ResearchAgentOutput,
    Signal,
    SourceKind,
)

# See market_agent.py's identical import for why these can't stay local to
# `_build_live_agent`.
from strands.hooks import BeforeModelCallEvent, BeforeToolCallEvent

_COMPONENT = "competitor_agent"
_MODEL_ID = "anthropic.claude-haiku-4-5-20251001-v1:0"

# §7 S1-S3 (P0) plus S4-S5 (P1 enrichment) — never SIMULATED (§18.1/gate check 10).
_ALLOWED_SOURCE_KINDS = frozenset(
    {SourceKind.WEB_PUBLIC, SourceKind.HN, SourceKind.GITHUB, SourceKind.APP_STORE, SourceKind.PRODUCT_HUNT}
)


@dataclass(frozen=True)
class RawCompetitorSignal:
    """One candidate claim exactly as the model's `emit_competitor_signal`
    tool call reported it — before §9.4/§18.4 validation."""

    competitor_name: str
    aspect: str
    polarity: str
    claim_text: str
    count: int
    date_window: str
    source_url: str
    source_kind: SourceKind


class RejectedClaim(NamedTuple):
    """A claim the schema dropped before Synthesis ever saw it. Not part of
    any entity — the orchestrator logs these, nothing more."""

    reason: str
    raw: RawCompetitorSignal


# ---------------------------------------------------------------------------
# Pure logic — §9.4 schema validation + §18.4 named-competitor scope, unit-
# testable without Strands/AWS.
# ---------------------------------------------------------------------------


def is_valid_competitor_claim(raw: RawCompetitorSignal, *, named_competitors: frozenset[str]) -> bool:
    """§9.4: a signal missing a concrete count, date window, or source
    reference fails validation, same rule as the Market Agent. §18.4: a
    competitor name outside the business's own `named_competitors` list
    fails too — this agent enriches named competitors, it doesn't pick
    its own."""

    return (
        raw.competitor_name in named_competitors
        and bool(raw.aspect)
        and raw.polarity in ("positive", "negative")
        and raw.count > 0
        and bool(raw.date_window.strip())
        and (raw.source_url.startswith("http://") or raw.source_url.startswith("https://"))
        and raw.source_kind in _ALLOWED_SOURCE_KINDS
    )


def build_signal(raw: RawCompetitorSignal, *, run_id: str, index: int) -> Signal:
    return Signal(
        id=f"sig_cmp_{run_id}_{index}",
        run_id=run_id,
        source_kind=raw.source_kind,
        aspect=raw.aspect,
        polarity=Polarity.POSITIVE if raw.polarity == "positive" else Polarity.NEGATIVE,
        claim_text=f"[{raw.competitor_name}] {raw.claim_text}",
        evidence_ids=[],
        produced_by=_COMPONENT,
    )


def validate_claims(
    raw_signals: list[RawCompetitorSignal], *, named_competitors: list[str]
) -> tuple[list[RawCompetitorSignal], list[RejectedClaim]]:
    allowed = frozenset(named_competitors)
    accepted, rejected = [], []
    for raw in raw_signals:
        if is_valid_competitor_claim(raw, named_competitors=allowed):
            accepted.append(raw)
        else:
            rejected.append(RejectedClaim(reason="rejected_generic_competitor_claim", raw=raw))
    return accepted, rejected


def assemble_research_output(
    raw_signals: list[RawCompetitorSignal],
    *,
    run_id: str,
    named_competitors: list[str],
    budget: RuntimeBudget,
) -> tuple[ResearchAgentOutput, AgentInvocation, list[RejectedClaim]]:
    """§9.4/§18.4 validation + §10.1a truncation labelling, all in one place
    — the boundary the real Strands wiring below hands its raw tool-call
    output through, and what tests exercise directly."""

    accepted, rejected = validate_claims(raw_signals, named_competitors=named_competitors)
    signals = [build_signal(raw, run_id=run_id, index=i) for i, raw in enumerate(accepted)]
    output = ResearchAgentOutput(run_id=run_id, produced_by=_COMPONENT, signals=signals, truncated=budget.truncated)
    return output, budget.to_invocation(component=_COMPONENT), rejected


# ---------------------------------------------------------------------------
# Real Strands wiring — network/AWS-credential-dependent. Tests inject a
# fake `raw_signals` producer instead of a live Agent, same treatment as
# Task 15's `market_agent.live_collect`.
# ---------------------------------------------------------------------------

RawSignalCollector = Callable[[AgentRuntimeContract], list[RawCompetitorSignal]]


def run_competitor_agent(
    business_context: str,
    *,
    run_id: str,
    named_competitors: list[str],
    contract: AgentRuntimeContract,
    collect: RawSignalCollector,
) -> tuple[ResearchAgentOutput, AgentInvocation, list[RejectedClaim]]:
    """Entry point Task 21's orchestrator calls. `collect` does the actual
    tool-calling loop (real Strands agent in production, a fake in tests)
    and returns whatever candidate claims it produced before the budget or
    the model itself decided to stop."""

    budget = RuntimeBudget(contract)
    raw_signals = collect(contract)
    return assemble_research_output(raw_signals, run_id=run_id, named_competitors=named_competitors, budget=budget)


def _build_live_agent(contract: AgentRuntimeContract, budget: RuntimeBudget, named_competitors: list[str]):
    """Wires a real strands.Agent with the web/HN/GitHub/App Store/Product
    Hunt tools and the §10.1a hooks. Imports strands lazily so the pure
    logic above never requires the SDK or AWS credentials to be
    importable/testable."""

    from strands import Agent, tool
    from strands.models import BedrockModel

    from backend.collectors.app_store import fetch_app_store_signals
    from backend.collectors.github import fetch_github_signals
    from backend.collectors.hn import fetch_hn_signals
    from backend.collectors.producthunt import fetch_producthunt_signals
    from backend.collectors.tavily import probe as tavily_probe

    collected: list[RawCompetitorSignal] = []
    allowed = frozenset(named_competitors)

    @tool
    def search_web(query: str) -> str:
        """Search the public web for signals about a named competitor."""
        report = tavily_probe(query, api_key=_tavily_api_key())
        return str(report)[:4000]

    @tool
    def search_hn(query: str) -> str:
        """Search Hacker News discussions matching query (e.g. a competitor name)."""
        hits = fetch_hn_signals(query, run_id="probe")[: contract.max_results]
        return "\n".join(h.claim_text for h in hits)

    @tool
    def search_github(owner: str, repo: str) -> str:
        """Look up recent release/issue activity for a competitor's owner/repo on GitHub."""
        hits = fetch_github_signals(owner, repo, run_id="probe")[: contract.max_results]
        return "\n".join(h.claim_text for h in hits)

    @tool
    def search_app_store(app_id: str, app_name: str) -> str:
        """P1 enrichment: recent App Store customer reviews for a competitor's
        app. Skips cleanly (empty result) if this competitor has no app or the
        lookup fails — enrichment must never block the run (§7.4/§8.2)."""
        try:
            hits = fetch_app_store_signals(app_id, app_name, "probe")[: contract.max_results]
        except Exception:
            return ""
        return "\n".join(h.claim_text for h in hits)

    @tool
    def search_producthunt(slug: str, product_name: str) -> str:
        """P1 enrichment: recent Product Hunt launch comments for a competitor's
        product. Skips cleanly (empty result) if there's no token or the
        lookup fails — enrichment must never block the run (§7.4/§8.2)."""
        try:
            hits = fetch_producthunt_signals(slug, product_name, "probe", _producthunt_token())[: contract.max_results]
        except Exception:
            return ""
        return "\n".join(h.claim_text for h in hits)

    @tool
    def emit_competitor_signal(
        competitor_name: str,
        aspect: str,
        polarity: str,
        claim_text: str,
        count: int,
        date_window: str,
        source_url: str,
        source_kind: str,
    ) -> str:
        """Record one claim-level signal about a named competitor.
        `competitor_name` must be one of the business's own named
        competitors; `count` and `date_window` must be concrete — a generic
        claim, or one about a competitor nobody named, is rejected, not
        recorded."""

        raw = RawCompetitorSignal(
            competitor_name=competitor_name,
            aspect=aspect,
            polarity=polarity,
            claim_text=claim_text,
            count=count,
            date_window=date_window,
            source_url=source_url,
            source_kind=SourceKind(source_kind),
        )
        collected.append(raw)
        return "recorded" if is_valid_competitor_claim(raw, named_competitors=allowed) else "rejected_generic_competitor_claim"

    def _before_model_call(event: BeforeModelCallEvent) -> None:
        if not budget.allow_iteration():
            event.cancel = "runtime contract exhausted (§10.1a)"

    def _before_tool_call(event: BeforeToolCallEvent) -> None:
        if not budget.allow_tool_call():
            event.cancel_tool = "runtime contract exhausted (§10.1a)"

    agent = Agent(
        model=BedrockModel(model_id=_MODEL_ID, max_tokens=contract.max_tokens),
        tools=[search_web, search_hn, search_github, search_app_store, search_producthunt, emit_competitor_signal],
        system_prompt=(
            "You are the Competitor Agent. Named competitors in scope: "
            f"{', '.join(named_competitors)}. Find claim-level, count/date/"
            "source-anchored public signals about these competitors only — "
            "never a bare summary, never a competitor not in that list, and "
            "never a disparaging claim about a named company (pattern-level "
            "only, §18). Call emit_competitor_signal once per claim you want "
            "recorded."
        ),
        hooks=[_before_model_call, _before_tool_call],
    )
    return agent, collected


def _tavily_api_key() -> str:
    import os

    key = os.environ.get("TAVILY_API_KEY")
    if not key:
        raise RuntimeError("TAVILY_API_KEY not set")
    return key


def _producthunt_token() -> str:
    import os

    token = os.environ.get("PRODUCT_HUNT_TOKEN")
    if not token:
        raise RuntimeError("PRODUCT_HUNT_TOKEN not set")
    return token


def live_collect(business_context: str, named_competitors: list[str]) -> RawSignalCollector:
    """Returns a `collect` callable that runs a real Strands agent — pass
    this as `run_competitor_agent`'s `collect` argument in production."""

    def collect(contract: AgentRuntimeContract) -> list[RawCompetitorSignal]:
        budget = RuntimeBudget(contract)
        agent, collected = _build_live_agent(contract, budget, named_competitors)
        agent(business_context)
        return collected

    return collect


if __name__ == "__main__":
    _CONTRACT = AgentRuntimeContract(max_tokens=1024)
    _NAMED = ["Sentry", "Datadog"]

    def _fake_collect(contract: AgentRuntimeContract) -> list[RawCompetitorSignal]:
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
            ),
            RawCompetitorSignal(
                competitor_name="Acme Corp",  # not in _NAMED — must be rejected
                aspect="pricing_pain",
                polarity="negative",
                claim_text="Acme users complain about pricing.",
                count=5,
                date_window="last 30 days",
                source_url="https://news.ycombinator.com/item?id=3",
                source_kind=SourceKind.HN,
            ),
        ]

    _output, _invocation, _rejected = run_competitor_agent(
        "PulseStack, an alerting SaaS for SRE teams",
        run_id="run_demo",
        named_competitors=_NAMED,
        contract=_CONTRACT,
        collect=_fake_collect,
    )
    assert len(_output.signals) == 1, _output.signals
    assert _output.signals[0].claim_text.startswith("[Sentry]")
    assert len(_rejected) == 1 and _rejected[0].reason == "rejected_generic_competitor_claim"
    assert _invocation.component == "competitor_agent"
    print("ok")
