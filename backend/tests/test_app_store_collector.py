"""App Store RSS collector (Task 11) — reviews for a named competitor's
mobile app, mapped to Task-1 Signal shape. Network is stubbed via an
injected fetch function; no live HTTP call is made in tests.
"""

from __future__ import annotations

from backend.collectors.app_store import fetch_app_store_signals
from backend.schemas.entities import Polarity, Signal, SourceKind

_URL = "https://itunes.apple.com/us/rss/customerreviews/id=1391380318/sortBy=mostRecent/json"

_FEED = {
    "feed": {
        "entry": [
            {
                "id": {"label": "111"},
                "title": {"label": "Great dashboards"},
                "im:rating": {"label": "5"},
            },
            {
                "id": {"label": "222"},
                "title": {"label": "Crashes constantly"},
                "im:rating": {"label": "1"},
            },
            {
                "id": {"label": "333"},
                "title": {"label": "It's fine I guess"},
                "im:rating": {"label": "3"},
            },
            {
                "id": {"label": "444"},
                "title": {"label": "App summary entry, not a review"},
            },
        ]
    }
}


def _fake_fetch(url: str):
    if url == _URL:
        return _FEED
    raise AssertionError(f"unexpected URL: {url}")


def test_returns_task1_shaped_signals():
    signals = fetch_app_store_signals("1391380318", "Datadog", "run_001", fetch=_fake_fetch)
    assert len(signals) == 2
    for signal in signals:
        Signal.model_validate(signal.model_dump())
        assert signal.source_kind == SourceKind.APP_STORE
        assert signal.run_id == "run_001"
        assert signal.evidence_ids == []


def test_high_rating_becomes_a_positive_signal():
    signals = fetch_app_store_signals("1391380318", "Datadog", "run_001", fetch=_fake_fetch)
    positive = [s for s in signals if s.polarity == Polarity.POSITIVE]
    assert len(positive) == 1
    assert "Great dashboards" in positive[0].claim_text


def test_low_rating_becomes_a_negative_signal():
    signals = fetch_app_store_signals("1391380318", "Datadog", "run_001", fetch=_fake_fetch)
    negative = [s for s in signals if s.polarity == Polarity.NEGATIVE]
    assert len(negative) == 1
    assert "Crashes constantly" in negative[0].claim_text


def test_mid_rating_and_missing_rating_are_dropped():
    signals = fetch_app_store_signals("1391380318", "Datadog", "run_001", fetch=_fake_fetch)
    assert all("fine I guess" not in s.claim_text for s in signals)
    assert all("summary entry" not in s.claim_text for s in signals)
