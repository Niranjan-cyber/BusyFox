"""App Store customer-reviews RSS collector (Task 11, PRD §7 S4) — P1
enrichment: real reviews for a named competitor's companion mobile app,
mapped to the Task-1 Signal shape.

Collector-level output only, same scope note as github.py/hn.py: no
ResearchAgentOutput wrapper, no Live -> Cached -> Demo Fixture fallback
ladder yet. A fetch failure raises out to the caller — per PRD §7.4/§8.2
this source must skip cleanly rather than block a run, so callers should
catch and drop it, not retry.

Polarity: rating >=4 -> POSITIVE, <=2 -> NEGATIVE, ==3 dropped (no clear
signal). Aspect is always "review_sentiment" — the feed gives no other
axis to split by.
"""

from __future__ import annotations

import json
import urllib.request
from typing import Callable

from backend.schemas.entities import Polarity, Signal, SourceKind

_API_ROOT = "https://itunes.apple.com"

Fetch = Callable[[str], dict]


def _http_get_json(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=10) as response:
        return json.loads(response.read())


def fetch_app_store_signals(
    app_id: str,
    app_name: str,
    run_id: str,
    *,
    country: str = "us",
    fetch: Fetch = _http_get_json,
) -> list[Signal]:
    """Most recent customer reviews for app_id, mapped to Signals."""

    url = f"{_API_ROOT}/{country}/rss/customerreviews/id={app_id}/sortBy=mostRecent/json"
    entries = fetch(url).get("feed", {}).get("entry", [])

    signals = []
    for entry in entries:
        rating_label = entry.get("im:rating", {}).get("label")
        if rating_label is None:
            continue
        rating = int(rating_label)
        if rating >= 4:
            polarity = Polarity.POSITIVE
        elif rating <= 2:
            polarity = Polarity.NEGATIVE
        else:
            continue

        review_id = entry["id"]["label"]
        title = entry["title"]["label"]
        signals.append(
            Signal(
                id=f"sig_appstore_{app_id}_{review_id}",
                run_id=run_id,
                source_kind=SourceKind.APP_STORE,
                aspect="review_sentiment",
                polarity=polarity,
                claim_text=f"{app_name} App Store review ({rating}★): {title!r}.",
                evidence_ids=[],
                produced_by="app_store_collector",
            )
        )

    return signals


if __name__ == "__main__":
    import sys

    app_id = sys.argv[1] if len(sys.argv) > 1 else "1391380318"
    app_name = sys.argv[2] if len(sys.argv) > 2 else "Datadog"
    print(json.dumps([s.model_dump() for s in fetch_app_store_signals(app_id, app_name, "run_live_probe")], indent=2))
