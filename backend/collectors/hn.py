"""HN Algolia collector (Task 4) — public story discussion of a competitor
or topic, mapped to the Task-1 Signal shape (§14.7).

Collector-level output only: list[Signal], same scope note as the GitHub
collector (backend/collectors/github.py) — no ResearchAgentOutput wrapper,
no Live -> Cached -> Demo Fixture fallback yet. A fetch failure raises out
to the caller.

Polarity: a story surfacing at all is treated as POSITIVE (market
attention on the query) — the API gives no sentiment signal, and titles
aren't parsed for it here.
# ponytail: no pain/praise split; add a title classifier (or LLM pass) if
# Synthesis later needs HN signals split by sentiment.
"""

from __future__ import annotations

import json
import urllib.parse
import urllib.request
from typing import Callable

from backend.schemas.entities import Polarity, Signal, SourceKind

_API_ROOT = "https://hn.algolia.com/api/v1"

Fetch = Callable[[str], list[dict]]


def _http_get_json(url: str) -> list[dict]:
    with urllib.request.urlopen(url, timeout=10) as response:
        return json.loads(response.read())["hits"]


def fetch_hn_signals(query: str, run_id: str, *, fetch: Fetch = _http_get_json) -> list[Signal]:
    """Recent HN stories matching query, mapped to Signals."""

    url = f"{_API_ROOT}/search?query={urllib.parse.quote(query)}&tags=story"

    signals = []
    for hit in fetch(url):
        signals.append(
            Signal(
                id=f"sig_hn_{hit['objectID']}",
                run_id=run_id,
                source_kind=SourceKind.HN,
                aspect="market_mention",
                polarity=Polarity.POSITIVE,
                claim_text=f"HN discussion: {hit['title']!r} ({hit['points']} points, {hit['num_comments']} comments).",
                evidence_ids=[],
                produced_by="hn_collector",
            )
        )

    return signals
