"""PulseStack business simulator (Task 10) — scenario file + seeded
generator, mapped straight to the Task-1 Signal/Evidence shape (§14.5,
§14.7) so Lane A's pipeline doesn't have to reconcile the format later.

An effect tagged "(real)" in the scenario describes something the live
collectors (GitHub/HN/Tavily/App Store) are expected to find on their own —
this generator only emits PulseStack's own simulated feedback.

# ponytail: no Bedrock-authored text/personas/typo injection (PRD §8.2) and
# no full ticket_count/survey_response_count volume — nothing consumes that
# volume yet (the normalise/dedupe/spam-filter pipeline is Day 2 Lane A).
# This emits the planted truths/strengths/red-herring plus a small spam
# sample; add bulk noise generation once that pipeline needs volume to
# filter against.
"""

from __future__ import annotations

import hashlib
import json
import random
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import NamedTuple

from backend.schemas.entities import (
    ClaimSupport,
    ClaimSupportStatus,
    Evidence,
    Freshness,
    FreshnessStatus,
    Polarity,
    RetrievalMode,
    Signal,
    SourceDocument,
    SourceKind,
)

_SCENARIO_PATH = Path(__file__).parent / "scenario_pulsestack_v1.json"
_PERSONAS = ["founder", "backend_engineer", "sre", "on_call_rotation_lead"]
_NEGATIVE_KEYWORDS = ("complain", "confus", "alternative", "churn", "frustrat", "blocks")
_FRESHNESS_LIMIT_DAYS = 180
_BASE_TIME = datetime(2026, 9, 17, tzinfo=timezone.utc)


class PulseStackFeedback(NamedTuple):
    evidence: list[Evidence]
    signals: list[Signal]


def load_scenario(path: Path = _SCENARIO_PATH) -> dict:
    return json.loads(path.read_text())


def _quote_hash(quote: str) -> str:
    return f"sha256:{hashlib.sha256(quote.encode()).hexdigest()}"


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def _polarity_for(text: str) -> Polarity:
    lowered = text.lower()
    if any(keyword in lowered for keyword in _NEGATIVE_KEYWORDS):
        return Polarity.NEGATIVE
    return Polarity.POSITIVE


def generate_pulsestack_feedback(scenario: dict, run_id: str, seed: int) -> PulseStackFeedback:
    """Deterministic Evidence + Signal pairs for one PulseStack scenario.

    Same seed + same scenario always produces identical ids/dates/personas —
    required so a re-run doesn't reshuffle what Lane C already gold-labelled.
    """

    rng = random.Random(seed)
    scenario_id = scenario["scenario_id"]
    evidence: list[Evidence] = []
    signals: list[Signal] = []
    counter = 0

    def add_item(
        *,
        aspect: str,
        text: str,
        age_days: int,
        support_status: ClaimSupportStatus = ClaimSupportStatus.SUPPORTS,
        confidence: float = 0.9,
        support_reason: str = "Simulated feedback item generated directly from the scenario's planted content.",
    ) -> None:
        nonlocal counter
        counter += 1
        item_id = f"{scenario_id}_{counter:04d}"
        persona = rng.choice(_PERSONAS)
        freshness_status = FreshnessStatus.STALE if age_days > _FRESHNESS_LIMIT_DAYS else FreshnessStatus.FRESH

        source_document = SourceDocument(
            id=f"src_sim_{item_id}",
            run_id=run_id,
            source_kind=SourceKind.SIMULATED,
            retrieval_mode=RetrievalMode.CACHED,
            url=f"simulated://{scenario_id}/{item_id}",
            fetched_at=_BASE_TIME,
            raw_text_s3_key=f"sim/{scenario_id}/{item_id}.txt",
            expires_at=_BASE_TIME + timedelta(days=30),
        )

        evidence_item = Evidence(
            id=f"evd_sim_{item_id}",
            source_document_id=source_document.id,
            source_kind=SourceKind.SIMULATED,
            retrieval_mode=RetrievalMode.CACHED,
            url=source_document.url,
            retrieved_at=_BASE_TIME,
            author=persona,
            published_at=_BASE_TIME - timedelta(days=age_days),
            quote=text,
            quote_hash=_quote_hash(text),
            claim_support=ClaimSupport(status=support_status, confidence=confidence, reason=support_reason),
            freshness=Freshness(status=freshness_status, age_days=age_days, limit_days=_FRESHNESS_LIMIT_DAYS),
        )
        evidence.append(evidence_item)

        signals.append(
            Signal(
                id=f"sig_sim_{item_id}",
                run_id=run_id,
                source_kind=SourceKind.SIMULATED,
                aspect=aspect,
                polarity=_polarity_for(text),
                claim_text=text,
                evidence_ids=[evidence_item.id],
                produced_by="pulsestack_simulator",
            )
        )

    def add_effects(aspect_source: str, effects: list[str], *, stale: bool = False) -> None:
        aspect = _slug(aspect_source)
        for effect in effects:
            if effect.startswith("(real)"):
                continue
            age_days = 270 if stale and "stale" in effect.lower() else rng.randint(1, 60)
            add_item(aspect=aspect, text=effect, age_days=age_days)

    for truth in scenario.get("planted_truths", []):
        add_effects(truth["opportunity"], truth.get("generator_effects", []))

    for strength in scenario.get("planted_strengths", []):
        add_effects(strength["strength"], strength.get("generator_effects", []))

    for herring in scenario.get("red_herrings", []):
        add_effects(herring["idea"], herring.get("generator_effects", []), stale=True)

    spam_count = scenario.get("noise", {}).get("spam_or_low_signal", 0)
    for i in range(spam_count):
        add_item(
            aspect="low_signal",
            text=f"low-signal filler item #{i + 1} — no actionable content.",
            age_days=rng.randint(1, 90),
            support_status=ClaimSupportStatus.UNSUPPORTED,
            confidence=round(rng.uniform(0.05, 0.3), 2),
            support_reason="Generic filler noise item; not tied to any planted opportunity.",
        )

    return PulseStackFeedback(evidence=evidence, signals=signals)
