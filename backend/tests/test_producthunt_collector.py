"""Product Hunt GraphQL collector (Task 11) — launch comments for a named
competitor's product, mapped to Task-1 Signal shape. Network is stubbed
via an injected fetch function; no live HTTP call is made in tests.
"""

from __future__ import annotations

from backend.collectors.producthunt import fetch_producthunt_signals
from backend.schemas.entities import Polarity, Signal, SourceKind

_COMMENTS = {
    "post": {
        "comments": {
            "edges": [
                {"node": {"id": "1", "body": "Can't deploy without it"}},
                {"node": {"id": "2", "body": "Does this work with vanilla JS?"}},
            ]
        }
    }
}


def _fake_fetch(query: str, token: str):
    assert "sentry" in query
    assert token == "fake-token"
    return _COMMENTS


def test_returns_task1_shaped_signals():
    signals = fetch_producthunt_signals("sentry", "Sentry", "run_001", "fake-token", fetch=_fake_fetch)
    assert len(signals) == 2
    for signal in signals:
        Signal.model_validate(signal.model_dump())
        assert signal.source_kind == SourceKind.PRODUCT_HUNT
        assert signal.run_id == "run_001"
        assert signal.polarity == Polarity.POSITIVE
        assert signal.evidence_ids == []


def test_comment_body_lands_in_claim_text():
    signals = fetch_producthunt_signals("sentry", "Sentry", "run_001", "fake-token", fetch=_fake_fetch)
    assert any("Can't deploy without it" in s.claim_text for s in signals)


def test_missing_post_returns_no_signals():
    def _no_post(query: str, token: str):
        return {"post": None}

    signals = fetch_producthunt_signals("unknown-slug", "Unknown", "run_001", "fake-token", fetch=_no_post)
    assert signals == []


def test_signal_ids_are_unique_across_products():
    other_signals = fetch_producthunt_signals(
        "datadog",
        "Datadog",
        "run_001",
        "fake-token",
        fetch=lambda q, t: {"post": {"comments": {"edges": [{"node": {"id": "1", "body": "Same id, different product"}}]}}},
    )
    sentry_signals = fetch_producthunt_signals("sentry", "Sentry", "run_001", "fake-token", fetch=_fake_fetch)

    assert {s.id for s in other_signals}.isdisjoint({s.id for s in sentry_signals})
