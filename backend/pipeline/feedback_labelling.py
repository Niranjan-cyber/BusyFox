"""Feedback pipeline (Task 14) — label -> validate -> aggregate -> balance
(PRD §9 diagram, the three stages after Task 13's normalise/dedupe/redact/
spam-filter). Structured-output labelling against the §9.1 `b2b_saas_it`
taxonomy, span+schema validation with one retry, §9.2 theme thresholds, and
a §9.3 sentiment-balance gate before a theme is allowed to become a Signal.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime, timedelta
from difflib import SequenceMatcher
from typing import Callable, NamedTuple

import boto3

from backend.pipeline.feedback_pipeline import RawFeedbackItem
from backend.schemas.entities import (
    ClaimSupport,
    ClaimSupportStatus,
    Evidence,
    Freshness,
    FreshnessStatus,
    Polarity,
    RetrievalMode,
    Signal,
)

# §9.1 label taxonomy (`b2b_saas_it`)
ASPECTS = frozenset(
    {
        "onboarding", "pricing_value", "reliability", "integrations", "support",
        "documentation", "performance", "alert_noise", "ease_of_use",
        "feature_completeness", "migration_friction",
    }
)
LABEL_POLARITIES = frozenset({"positive", "negative", "mixed", "neutral"})
INTENTS = frozenset({"complaint", "request", "praise", "recommendation", "comparison", "churn_signal"})
SEGMENT_HINTS = frozenset({"founder", "backend_engineer", "sre_devops", "on_call_lead", "unknown"})

_FUZZY_MATCH_THRESHOLD = 0.92

# §11.4 has no per-type entry yet for `simulated`/`owner_upload` feedback; using
# the same 180-day limit the PulseStack simulator (Task 10) already applies.
_FRESHNESS_LIMIT_DAYS = 180

# §9.2 — PulseStack's-own-feedback theme threshold row only; the competitor-
# named and cross-competitor rows belong to the Competitor Agent (Task 16),
# which runs this same aggregation shape over its own feed.
_THEME_MIN_ITEMS = 3
_RECENT_WINDOW_DAYS = 90
_THEME_RECENT_SHARE = 0.05
_THEME_GROWTH_RATIO = 0.5

# ponytail: §9.3 names a "sentiment balance check" but gives no numeric ratio
# for "balanced" vs "skewed" — picked dominant-side->=2x-minority as the bar
# for a clear pain/strength signal; a near-50/50 aspect is mixed noise, not a
# signal. Revisit if gold-set labelling (Task 24) shows it's too strict/loose.
_DOMINANT_POLARITY_RATIO = 2.0

_MODEL_ID = "anthropic.claude-haiku-4-5-20251001-v1:0"
_TOOL_NAME = "emit_feedback_labels"


@dataclass(frozen=True)
class RawLabel:
    aspect: str
    polarity: str
    intents: tuple[str, ...]
    segment_hint: str
    evidence_span: str


@dataclass(frozen=True)
class LabelledItem:
    item: RawFeedbackItem
    labels: tuple[RawLabel, ...]


Labeller = Callable[[str], list[RawLabel]]


class FeedbackSignals(NamedTuple):
    evidence: list[Evidence]
    signals: list[Signal]


def _fuzzy_ratio(span: str, text: str) -> float:
    """Best match ratio for `span` against same-length windows of `text` —
    comparing `span` to the whole `text` instead tanks the ratio purely
    from the length mismatch."""

    n = len(span)
    if n == 0 or n > len(text):
        return 0.0
    return max(SequenceMatcher(None, span, text[i : i + n]).ratio() for i in range(len(text) - n + 1))


def _span_found(span: str, text: str) -> bool:
    """Verbatim substring, or fuzzy >=0.92 (§9.1)."""

    if not span:
        return False
    return span in text or _fuzzy_ratio(span, text) >= _FUZZY_MATCH_THRESHOLD


def is_valid_label(label: RawLabel, source_text: str) -> bool:
    return (
        label.aspect in ASPECTS
        and label.polarity in LABEL_POLARITIES
        and bool(label.intents)
        and all(intent in INTENTS for intent in label.intents)
        and label.segment_hint in SEGMENT_HINTS
        and _span_found(label.evidence_span, source_text)
    )


def label_item(item: RawFeedbackItem, labeller: Labeller) -> LabelledItem:
    """Calls `labeller`, validates schema+span (§9.1), retries once if any
    label is invalid, then drops whatever's still invalid after the retry."""

    valid: list[RawLabel] = []
    for _attempt in range(2):
        raw_labels = labeller(item.text)
        valid = [label for label in raw_labels if is_valid_label(label, item.text)]
        if len(valid) == len(raw_labels):
            break
    return LabelledItem(item=item, labels=tuple(valid))


def label_items(items: list[RawFeedbackItem], labeller: Labeller) -> list[LabelledItem]:
    return [label_item(item, labeller) for item in items]


def _quote_hash(quote: str) -> str:
    return f"sha256:{hashlib.sha256(quote.encode()).hexdigest()}"


def _evidence_for(item: RawFeedbackItem, label: RawLabel, now: datetime) -> Evidence:
    exact = label.evidence_span in item.text
    ratio = 1.0 if exact else _fuzzy_ratio(label.evidence_span, item.text)
    age_days = max((now - item.published_at).days, 0)
    return Evidence(
        id=f"evd_fb_{item.id}",
        source_document_id=f"src_fb_{item.id}",
        source_kind=item.source_kind,
        retrieval_mode=RetrievalMode.CACHED,
        url=f"feedback://{item.source_kind.value}/{item.id}",
        retrieved_at=now,
        author=item.author,
        published_at=item.published_at,
        quote=item.text,
        quote_hash=_quote_hash(item.text),
        claim_support=ClaimSupport(
            status=ClaimSupportStatus.SUPPORTS,
            confidence=round(ratio, 2),
            reason=(
                "Evidence span matched verbatim in source text."
                if exact
                else f"Evidence span matched fuzzily (ratio {ratio:.2f}) in source text."
            ),
        ),
        freshness=Freshness(
            status=FreshnessStatus.STALE if age_days > _FRESHNESS_LIMIT_DAYS else FreshnessStatus.FRESH,
            age_days=age_days,
            limit_days=_FRESHNESS_LIMIT_DAYS,
        ),
    )


@dataclass(frozen=True)
class _AspectItem:
    item: RawFeedbackItem
    label: RawLabel


def _aspect_groups(labelled_items: list[LabelledItem]) -> dict[str, list[_AspectItem]]:
    groups: dict[str, list[_AspectItem]] = {}
    for labelled in labelled_items:
        for label in labelled.labels:
            groups.setdefault(label.aspect, []).append(_AspectItem(labelled.item, label))
    return groups


def _passes_theme_threshold(candidates: list[_AspectItem], *, total_items: int, now: datetime) -> bool:
    if len(candidates) < _THEME_MIN_ITEMS:
        return False
    recent_cutoff = now - timedelta(days=_RECENT_WINDOW_DAYS)
    prior_cutoff = now - timedelta(days=2 * _RECENT_WINDOW_DAYS)
    recent = [c for c in candidates if c.item.published_at >= recent_cutoff]
    prior = [c for c in candidates if prior_cutoff <= c.item.published_at < recent_cutoff]
    recent_share = len(recent) / total_items if total_items else 0.0
    if prior:
        growth = (len(recent) - len(prior)) / len(prior)
    else:
        growth = float("inf") if recent else 0.0
    return recent_share >= _THEME_RECENT_SHARE or growth >= _THEME_GROWTH_RATIO


def _dominant_polarity(candidates: list[_AspectItem]) -> list[_AspectItem] | None:
    """§9.3 sentiment balance check — only a clearly one-sided aspect (see
    `_DOMINANT_POLARITY_RATIO`) becomes a directional pain/strength signal;
    mixed/neutral labels and a near-even pos/neg split produce no signal."""

    positive = [c for c in candidates if c.label.polarity == "positive"]
    negative = [c for c in candidates if c.label.polarity == "negative"]
    dominant, other = (positive, negative) if len(positive) >= len(negative) else (negative, positive)
    if not dominant:
        return None
    if other and len(dominant) < _DOMINANT_POLARITY_RATIO * len(other):
        return None
    return dominant


def _theme_signal(
    aspect: str, candidates: list[_AspectItem], *, total_items: int, run_id: str, now: datetime
) -> tuple[Signal, list[Evidence]] | None:
    if not _passes_theme_threshold(candidates, total_items=total_items, now=now):
        return None
    dominant = _dominant_polarity(candidates)
    if not dominant:
        return None

    polarity = Polarity.POSITIVE if dominant[0].label.polarity == "positive" else Polarity.NEGATIVE
    example = dominant[0].label.evidence_span
    claim_text = (
        f"{len(dominant)} of {len(candidates)} recent feedback items flag "
        f"{aspect} ({polarity.value}) — e.g. {example!r}."
    )
    evidence = [_evidence_for(c.item, c.label, now) for c in dominant]
    signal = Signal(
        id=f"sig_fb_{run_id}_{aspect}_{polarity.value}",
        run_id=run_id,
        source_kind=dominant[0].item.source_kind,
        aspect=aspect,
        polarity=polarity,
        claim_text=claim_text,
        evidence_ids=[e.id for e in evidence],
        produced_by="feedback_pipeline_labeller",
    )
    return signal, evidence


def aggregate_and_balance(labelled_items: list[LabelledItem], *, run_id: str, now: datetime) -> FeedbackSignals:
    groups = _aspect_groups(labelled_items)
    signals: list[Signal] = []
    evidence: list[Evidence] = []
    for aspect, aspect_items in groups.items():
        candidates = list({ai.item.id: ai for ai in aspect_items}.values())  # one vote per item per aspect
        result = _theme_signal(aspect, candidates, total_items=len(labelled_items), run_id=run_id, now=now)
        if result:
            signal, ev = result
            signals.append(signal)
            evidence.extend(ev)
    return FeedbackSignals(evidence=evidence, signals=signals)


def run_labelling_pipeline(
    items: list[RawFeedbackItem], labeller: Labeller, *, run_id: str, now: datetime
) -> FeedbackSignals:
    return aggregate_and_balance(label_items(items, labeller), run_id=run_id, now=now)


# ---------------------------------------------------------------------------
# Real labeller — Bedrock Converse, Claude Haiku 4.5, forced structured output.
# Network/credential-dependent; tests inject a fake `Labeller` instead.
# ---------------------------------------------------------------------------

_TOOL_SCHEMA = {
    "type": "object",
    "properties": {
        "labels": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "aspect": {"type": "string", "enum": sorted(ASPECTS)},
                    "polarity": {"type": "string", "enum": sorted(LABEL_POLARITIES)},
                    "intents": {"type": "array", "items": {"type": "string", "enum": sorted(INTENTS)}},
                    "segment_hint": {"type": "string", "enum": sorted(SEGMENT_HINTS)},
                    "evidence_span": {"type": "string"},
                },
                "required": ["aspect", "polarity", "intents", "segment_hint", "evidence_span"],
            },
        }
    },
    "required": ["labels"],
}


def bedrock_labeller(client=None, model_id: str = _MODEL_ID) -> Labeller:
    bedrock = client or boto3.client("bedrock-runtime")

    def labeller(text: str) -> list[RawLabel]:
        response = bedrock.converse(
            modelId=model_id,
            messages=[{"role": "user", "content": [{"text": text}]}],
            toolConfig={
                "tools": [{"toolSpec": {"name": _TOOL_NAME, "inputSchema": {"json": _TOOL_SCHEMA}}}],
                "toolChoice": {"tool": {"name": _TOOL_NAME}},
            },
        )
        for block in response["output"]["message"]["content"]:
            if "toolUse" in block:
                entries = block["toolUse"]["input"].get("labels", [])
                return [
                    RawLabel(
                        aspect=entry["aspect"],
                        polarity=entry["polarity"],
                        intents=tuple(entry.get("intents", [])),
                        segment_hint=entry["segment_hint"],
                        evidence_span=entry["evidence_span"],
                    )
                    for entry in entries
                ]
        return []

    return labeller


if __name__ == "__main__":
    from backend.schemas.entities import SourceKind

    _NOW = datetime(2026, 9, 18)
    _ITEMS = [
        RawFeedbackItem(f"a{i}", "Alerts are way too noisy, paging us every night.", "sre", _NOW - timedelta(days=5 * i), SourceKind.SIMULATED)
        for i in range(4)
    ]

    def _fake_labeller(text: str) -> list[RawLabel]:
        return [
            RawLabel(
                aspect="alert_noise",
                polarity="negative",
                intents=("complaint",),
                segment_hint="sre_devops",
                evidence_span="way too noisy",
            )
        ]

    _result = run_labelling_pipeline(_ITEMS, _fake_labeller, run_id="run_demo", now=_NOW)
    assert len(_result.signals) == 1, _result.signals
    assert _result.signals[0].aspect == "alert_noise"
    assert _result.signals[0].polarity == Polarity.NEGATIVE
    assert len(_result.evidence) == 4
    print("ok")
