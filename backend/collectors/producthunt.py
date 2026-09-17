"""Product Hunt GraphQL v2 collector (Task 11, PRD §7 S5) — P1 enrichment:
launch comments for a named competitor's product, mapped to the Task-1
Signal shape.

Collector-level output only, same scope note as github.py/hn.py/app_store.py:
no ResearchAgentOutput wrapper, no Live -> Cached -> Demo Fixture fallback
ladder yet. A fetch failure (including a missing/invalid token) raises out
to the caller — per PRD §7.4/§8.2 this source must skip cleanly rather than
block a run, so callers should catch and drop it, not retry.

Polarity: same call as hn.py — a launch comment appearing at all is treated
as POSITIVE (engagement on the query); the API gives no sentiment signal
and comment bodies aren't parsed for it here.
# ponytail: no pain/praise split; add a title/body classifier (or LLM pass)
# if Synthesis later needs PH signals split by sentiment.
"""

from __future__ import annotations

import json
import urllib.request
from typing import Callable

from backend.schemas.entities import Polarity, Signal, SourceKind

_API_ROOT = "https://api.producthunt.com/v2/api/graphql"

Fetch = Callable[[str, str], dict]


def _http_post_graphql(query: str, token: str) -> dict:
    request = urllib.request.Request(
        _API_ROOT,
        data=json.dumps({"query": query}).encode(),
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=10) as response:
        body = json.loads(response.read())
    if "errors" in body:
        raise RuntimeError(body["errors"])
    return body["data"]


def fetch_producthunt_signals(
    slug: str,
    product_name: str,
    run_id: str,
    token: str,
    *,
    fetch: Fetch = _http_post_graphql,
) -> list[Signal]:
    """Most recent launch comments for a product slug, mapped to Signals."""

    query = f'query {{ post(slug: "{slug}") {{ comments(first: 20) {{ edges {{ node {{ id body }} }} }} }} }}'
    post = fetch(query, token).get("post")
    edges = post["comments"]["edges"] if post else []

    signals = []
    for edge in edges:
        node = edge["node"]
        signals.append(
            Signal(
                id=f"sig_ph_{slug}_{node['id']}",
                run_id=run_id,
                source_kind=SourceKind.PRODUCT_HUNT,
                aspect="launch_comment",
                polarity=Polarity.POSITIVE,
                claim_text=f"{product_name} Product Hunt launch comment: {node['body'][:200]!r}.",
                evidence_ids=[],
                produced_by="producthunt_collector",
            )
        )

    return signals


if __name__ == "__main__":
    import os
    import sys
    from pathlib import Path

    env_file = Path(__file__).resolve().parents[2] / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, _, v = line.partition("=")
                os.environ.setdefault(k.strip(), v.strip())

    ph_token = os.environ.get("PRODUCT_HUNT_TOKEN")
    if not ph_token:
        raise SystemExit("Set PRODUCT_HUNT_TOKEN first.")
    slug = sys.argv[1] if len(sys.argv) > 1 else "sentry"
    name = sys.argv[2] if len(sys.argv) > 2 else "Sentry"
    signals = fetch_producthunt_signals(slug, name, "run_live_probe", ph_token)
    print(json.dumps([s.model_dump() for s in signals], indent=2))
