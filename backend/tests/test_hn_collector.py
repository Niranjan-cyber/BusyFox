"""HN Algolia collector (Task 4) — story discussion of a competitor/topic,
mapped to Task-1 Signal shape. Network is stubbed via an injected fetch
function; no live HTTP call is made in tests.
"""

from __future__ import annotations

from backend.collectors.hn import fetch_hn_signals
from backend.schemas.entities import Polarity, Signal, SourceKind

_QUERY_URL = "https://hn.algolia.com/api/v1/search?query=acme&tags=story"

_HITS = [
    {"objectID": "1001", "title": "Acme widget silently drops webhooks under load", "points": 42, "num_comments": 18},
    {"objectID": "1002", "title": "Show HN: I built a faster alternative to Acme", "points": 120, "num_comments": 55},
]


def _fake_fetch(url: str):
    if url == _QUERY_URL:
        return _HITS
    raise AssertionError(f"unexpected URL: {url}")


def test_returns_task1_shaped_signals():
    signals = fetch_hn_signals("acme", "run_001", fetch=_fake_fetch)
    assert len(signals) == 2
    for signal in signals:
        Signal.model_validate(signal.model_dump())
        assert signal.source_kind == SourceKind.HN
        assert signal.run_id == "run_001"
        assert signal.evidence_ids == []


def test_story_becomes_a_market_mention_signal():
    signals = fetch_hn_signals("acme", "run_001", fetch=_fake_fetch)
    assert all(s.aspect == "market_mention" for s in signals)
    assert all(s.polarity == Polarity.POSITIVE for s in signals)
    dropped_webhooks = next(s for s in signals if "1001" in s.id)
    assert "silently drops webhooks under load" in dropped_webhooks.claim_text
    assert "42" in dropped_webhooks.claim_text


def test_no_hits_returns_empty_list():
    signals = fetch_hn_signals("nothing_here", "run_001", fetch=lambda url: [])
    assert signals == []


def test_signal_ids_are_stable_per_story():
    signals = fetch_hn_signals("acme", "run_001", fetch=_fake_fetch)
    ids = [s.id for s in signals]
    assert len(ids) == len(set(ids))
