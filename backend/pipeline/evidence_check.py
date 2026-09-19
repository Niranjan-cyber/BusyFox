"""Evidence Check (Task 18) — code, plus one lightweight model call for
semantic claim support (§12.1): quote-exists, quote-supports-claim,
freshness against the §11.4 per-type limits, contradiction detection.
Populates `Evidence.claim_support` and `Evidence.freshness` exactly as
shaped in §12.

Runs after Synthesis (Task 17): takes each candidate opportunity's Claims
plus the raw quotes their cited signals were built from, and turns them
into real Evidence. Quote-exists is checked first, in code — if the quote
isn't even in the source, the semantic-support model call never happens
(§12.1's "no verbatim quote found" rejection needs no model opinion). Only
a quote that's actually there gets the one Haiku call asking whether it
supports the specific claim, not just that it exists (§12.1's third
diagram — the failure mode v5 didn't catch).

Quality Gate (Task 19) reads `claim_support`/`freshness` off the Evidence
this produces to run its 14 checks; it does not belong here.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, NamedTuple, Optional

from backend.pipeline.feedback_labelling import span_found
from backend.schemas.entities import (
    Claim,
    ClaimSupport,
    ClaimSupportStatus,
    Evidence,
    Freshness,
    FreshnessStatus,
    Polarity,
    RetrievalMode,
    Signal,
    SourceKind,
)

# See backend/agents/market_agent.py's identical env override and OpenCode Go note.
_MODEL_ID = os.environ.get("EVIDENCE_CHECK_MODEL_ID", "deepseek-v4.1-flash")
_TOOL_NAME = "emit_claim_support"

# §11.4's table is a small set of semantic categories, not a field Signal
# carries directly — this bridges aspect/produced_by to that table.
# ponytail: keyword/producer heuristic, not a real classifier; revisit if
# gold-set labelling (Task 24) shows it's misclassifying a real category.
_PRICING_LIMIT_DAYS = 90
_OWN_FEEDBACK_LIMIT_DAYS = 90
_COMPETITOR_COMPLAINT_LIMIT_DAYS = 180
_MARKET_EVENT_LIMIT_DAYS = 180
_NO_STRICT_LIMIT_DAYS = 36_500  # "evergreen capability claims" — always fresh


def freshness_limit_days(*, aspect: str, produced_by: str) -> int:
    if "pricing" in aspect:
        return _PRICING_LIMIT_DAYS
    if "integration" in aspect or "capability" in aspect:
        return _NO_STRICT_LIMIT_DAYS
    if produced_by in {"feedback_pipeline_labeller", "pulsestack_simulator"}:
        return _OWN_FEEDBACK_LIMIT_DAYS
    if produced_by == "competitor_agent":
        return _COMPETITOR_COMPLAINT_LIMIT_DAYS
    return _MARKET_EVENT_LIMIT_DAYS  # market_agent / general news, the default row


def check_freshness(published_at: Optional[datetime], *, now: datetime, aspect: str, produced_by: str) -> Freshness:
    limit_days = freshness_limit_days(aspect=aspect, produced_by=produced_by)
    age_days = max((now - published_at).days, 0) if published_at else 0
    status = FreshnessStatus.STALE if age_days > limit_days else FreshnessStatus.FRESH
    return Freshness(status=status, age_days=age_days, limit_days=limit_days)


def quote_exists(quote: str, source_text: str) -> bool:
    """§12.1 citation verification — reuses Task 14's verbatim-or-fuzzy
    span check (§9.1) since a quote existing in a source is the same
    question as an evidence_span existing in feedback text."""

    return span_found(quote, source_text)


def contradiction_exists(*, aspect: str, polarity: Polarity, signals: list[Signal]) -> bool:
    """§11.1 check 4 — counter-evidence exists: some other signal from this
    run makes the opposite claim about the same aspect."""

    opposite = Polarity.NEGATIVE if polarity == Polarity.POSITIVE else Polarity.POSITIVE
    return any(s.aspect == aspect and s.polarity == opposite for s in signals)


SemanticSupportChecker = Callable[[str, str], ClaimSupport]


@dataclass(frozen=True)
class EvidenceCandidate:
    """One quote Evidence Check must verify, for one Claim. The orchestrator
    (Task 21) builds these from whatever raw quote+source the signal behind
    a claim actually came from — Signal itself only carries the trimmed
    public shape (§14.7), not the source text Evidence Check needs."""

    claim_id: str
    source_document_id: str
    source_kind: SourceKind
    retrieval_mode: RetrievalMode
    url: str
    retrieved_at: datetime
    quote: str
    source_text: str
    aspect: str
    polarity: Polarity
    produced_by: str
    author: Optional[str] = None
    published_at: Optional[datetime] = None


class EvidenceCheckResult(NamedTuple):
    evidence: list[Evidence]
    claims: list[Claim]  # same claims, `evidence_ids` filled in
    contradictions: dict[str, bool]  # claim_id -> counter-evidence exists


def build_evidence(
    candidate: EvidenceCandidate, *, claim_text: str, semantic_check: SemanticSupportChecker, now: datetime, evidence_id: str
) -> Evidence:
    if not quote_exists(candidate.quote, candidate.source_text):
        # §12.1: no verbatim quote found -> rejected without ever asking the
        # model whether it supports the claim, there's nothing to ask about.
        claim_support = ClaimSupport(status=ClaimSupportStatus.UNSUPPORTED, confidence=0.0, reason="quote not found in source text")
    else:
        claim_support = semantic_check(claim_text, candidate.quote)

    freshness = check_freshness(candidate.published_at, now=now, aspect=candidate.aspect, produced_by=candidate.produced_by)

    return Evidence(
        id=evidence_id,
        source_document_id=candidate.source_document_id,
        source_kind=candidate.source_kind,
        retrieval_mode=candidate.retrieval_mode,
        url=candidate.url,
        retrieved_at=candidate.retrieved_at,
        author=candidate.author,
        published_at=candidate.published_at,
        quote=candidate.quote,
        quote_hash=_quote_hash(candidate.quote),
        claim_support=claim_support,
        freshness=freshness,
    )


def _quote_hash(quote: str) -> str:
    import hashlib

    return f"sha256:{hashlib.sha256(quote.encode()).hexdigest()}"


def run_evidence_check(
    claims: list[Claim],
    candidates: list[EvidenceCandidate],
    signals: list[Signal],
    *,
    semantic_check: SemanticSupportChecker,
    now: datetime,
) -> EvidenceCheckResult:
    """Entry point Task 21's orchestrator calls between Synthesis and
    Quality Gate. `semantic_check` does the one Haiku call (real Bedrock in
    production via `opencode_go_semantic_support_checker`, a fake in tests)."""

    claims_by_id = {c.id: c for c in claims}
    candidates_by_claim: dict[str, list[EvidenceCandidate]] = {}
    for candidate in candidates:
        candidates_by_claim.setdefault(candidate.claim_id, []).append(candidate)

    all_evidence: list[Evidence] = []
    updated_claims: list[Claim] = []
    contradictions: dict[str, bool] = {}

    for claim in claims:
        claim_candidates = candidates_by_claim.get(claim.id, [])
        evidence = [
            build_evidence(
                candidate, claim_text=claim.text, semantic_check=semantic_check, now=now, evidence_id=f"evd_{claim.id}_{i}"
            )
            for i, candidate in enumerate(claim_candidates)
        ]
        all_evidence.extend(evidence)
        updated_claims.append(claim.model_copy(update={"evidence_ids": [e.id for e in evidence]}))
        contradictions[claim.id] = any(
            contradiction_exists(aspect=c.aspect, polarity=c.polarity, signals=signals) for c in claim_candidates
        )

    return EvidenceCheckResult(evidence=all_evidence, claims=updated_claims, contradictions=contradictions)


# ---------------------------------------------------------------------------
# Real semantic checker — OpenCode Go (OpenAI-compatible), forced tool
# choice for structured output. Network/credential-dependent; tests inject a
# fake `SemanticSupportChecker` instead, same treatment as Task 14's
# `opencode_go_labeller`. Was a raw Bedrock Converse call until 2026-09-19 —
# every AWS account available to this project has a 0 req/min real-time
# Bedrock inference quota (see backend/agents/market_agent.py::
# opencode_go_client_args), so this now goes through OpenCode Go's gateway
# with the `openai` SDK instead of `boto3`.
# ---------------------------------------------------------------------------

_TOOL_SCHEMA = {
    "type": "object",
    "properties": {
        "status": {"type": "string", "enum": ["supports", "partial", "unsupported"]},
        "confidence": {"type": "number"},
        "reason": {"type": "string"},
    },
    "required": ["status", "confidence", "reason"],
}


def opencode_go_semantic_support_checker(client=None, model_id: str = _MODEL_ID) -> SemanticSupportChecker:
    from backend.agents.market_agent import opencode_go_client_args

    from openai import OpenAI

    oai = client or OpenAI(**opencode_go_client_args())

    def check(claim_text: str, quote: str) -> ClaimSupport:
        prompt = f'Claim: "{claim_text}"\nQuote: "{quote}"\nDoes the quote support the claim: yes/partial/no, one-sentence reason.'
        response = oai.chat.completions.create(
            model=model_id,
            messages=[{"role": "user", "content": prompt}],
            tools=[{"type": "function", "function": {"name": _TOOL_NAME, "parameters": _TOOL_SCHEMA}}],
            # Not a forced tool_choice: Go's "thinking mode" models 400 on
            # `{"type": "function", ...}` ("Thinking mode does not support
            # this tool_choice") — "auto" with a single tool and a directive
            # prompt gets the same real call in practice (verified live).
            tool_choice="auto",
        )
        tool_calls = response.choices[0].message.tool_calls
        if not tool_calls:
            return ClaimSupport(status=ClaimSupportStatus.UNSUPPORTED, confidence=0.0, reason="model returned no tool call")
        data = json.loads(tool_calls[0].function.arguments)
        return ClaimSupport(status=ClaimSupportStatus(data["status"]), confidence=float(data["confidence"]), reason=data["reason"])

    return check


if __name__ == "__main__":
    from backend.schemas.entities import ClaimStatus, ClaimType

    _NOW = datetime(2026, 9, 18)
    _CLAIM = Claim(id="claim_1", opportunity_id="opp_1", type=ClaimType.WHY_THIS, text="Teams are leaving Sentry because of pricing.", status=ClaimStatus.HYPOTHESIS, evidence_ids=[])
    _SIGNALS = [Signal(id="sig_1", run_id="run_1", source_kind=SourceKind.HN, aspect="pricing_pain", polarity=Polarity.NEGATIVE, claim_text="x", evidence_ids=[], produced_by="competitor_agent")]

    _CANDIDATES = [
        EvidenceCandidate(
            claim_id="claim_1",
            source_document_id="src_1",
            source_kind=SourceKind.HN,
            retrieval_mode=RetrievalMode.LIVE,
            url="https://news.ycombinator.com/item?id=1",
            retrieved_at=_NOW,
            quote="we're moving off Sentry, the new pricing tier doubled our bill",
            source_text="Thread: we're moving off Sentry, the new pricing tier doubled our bill overnight.",
            aspect="pricing_pain",
            polarity=Polarity.NEGATIVE,
            produced_by="competitor_agent",
            published_at=datetime(2026, 8, 30),
        ),
        EvidenceCandidate(
            claim_id="claim_1",
            source_document_id="src_2",
            source_kind=SourceKind.HN,
            retrieval_mode=RetrievalMode.LIVE,
            url="https://news.ycombinator.com/item?id=2",
            retrieved_at=_NOW,
            quote="this quote does not appear anywhere in the source",
            source_text="Completely unrelated thread about something else entirely.",
            aspect="pricing_pain",
            polarity=Polarity.NEGATIVE,
            produced_by="competitor_agent",
            published_at=_NOW,
        ),
    ]

    def _fake_semantic_check(claim_text: str, quote: str) -> ClaimSupport:
        return ClaimSupport(status=ClaimSupportStatus.SUPPORTS, confidence=0.9, reason="quote directly names the pricing change as the reason for leaving")

    _result = run_evidence_check([_CLAIM], _CANDIDATES, _SIGNALS, semantic_check=_fake_semantic_check, now=_NOW)
    assert len(_result.evidence) == 2
    assert _result.evidence[0].claim_support.status == ClaimSupportStatus.SUPPORTS
    assert _result.evidence[0].freshness.status == FreshnessStatus.FRESH
    assert _result.evidence[1].claim_support.status == ClaimSupportStatus.UNSUPPORTED  # quote not found -> no model call needed
    assert _result.claims[0].evidence_ids == [_result.evidence[0].id, _result.evidence[1].id]
    assert _result.contradictions["claim_1"] is False  # no opposite-polarity signal for pricing_pain in this run
    print("ok")
