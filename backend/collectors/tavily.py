"""Tavily search+extract probe (Task 5) — one live round-trip against the
PRD's top-named technical risk (§7.2, "web search/extraction is the single
most fragile P0 dependency").

Unlike the GitHub/HN collectors this doesn't emit Signal-shaped output: the
deliverable here is a report of latency and observed failure modes, not
competitor signals. `probe()` never raises — swallowing and labelling the
failure *is* the point, since today's goal is characterizing how Tavily
fails, not just proving one success.
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from typing import Callable

_SEARCH_URL = "https://api.tavily.com/search"
_EXTRACT_URL = "https://api.tavily.com/extract"

Post = Callable[[str, dict], dict]


class FailureMode:
    HTTP_ERROR = "http_error"
    TIMEOUT = "timeout"
    EMPTY_RESULTS = "empty_results"
    MALFORMED_EXTRACT = "malformed_extract"


def _post_json(url: str, payload: dict) -> dict:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=10) as response:
        return json.loads(response.read())


def extract_text(url: str, api_key: str, *, post: Post = _post_json) -> str:
    """Raw text of one page. Unlike `probe`, this raises on any failure —
    the caller (evidence-drawer re-fetch, §12.2) treats *any* failure as
    "fall to the next level", so there's nothing to characterize here."""

    results = post(_EXTRACT_URL, {"api_key": api_key, "urls": [url]}).get("results") or []
    if not results or not results[0].get("raw_content"):
        raise ValueError(f"empty extract for {url}")
    return results[0]["raw_content"]


def probe(query: str, api_key: str, *, post: Post = _post_json) -> dict:
    """One search call, then one extract call on the top result.

    Returns a report: `failure_modes` (empty on a clean round-trip),
    `search_latency_s`, `extract_latency_s`, and whatever else was observed
    before a failure stopped the chain.
    """

    report: dict = {"query": query, "failure_modes": []}

    start = time.monotonic()
    try:
        search = post(_SEARCH_URL, {"api_key": api_key, "query": query, "search_depth": "basic", "max_results": 5})
    except urllib.error.HTTPError as exc:
        report["failure_modes"].append(f"{FailureMode.HTTP_ERROR}:search:{exc.code}")
        return report
    except (urllib.error.URLError, TimeoutError, ValueError) as exc:
        report["failure_modes"].append(f"{FailureMode.TIMEOUT}:search:{exc}")
        return report
    report["search_latency_s"] = round(time.monotonic() - start, 2)

    results = search.get("results") or []
    report["result_count"] = len(results)
    if not results:
        report["failure_modes"].append(FailureMode.EMPTY_RESULTS)
        return report

    top_url = results[0].get("url")
    start = time.monotonic()
    try:
        extract = post(_EXTRACT_URL, {"api_key": api_key, "urls": [top_url]})
    except urllib.error.HTTPError as exc:
        report["failure_modes"].append(f"{FailureMode.HTTP_ERROR}:extract:{exc.code}")
        return report
    except (urllib.error.URLError, TimeoutError, ValueError) as exc:
        report["failure_modes"].append(f"{FailureMode.TIMEOUT}:extract:{exc}")
        return report
    report["extract_latency_s"] = round(time.monotonic() - start, 2)

    extracted = extract.get("results") or []
    if not extracted or not extracted[0].get("raw_content"):
        report["failure_modes"].append(FailureMode.MALFORMED_EXTRACT)
        return report

    report["extracted_chars"] = len(extracted[0]["raw_content"])
    return report


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

    key = os.environ.get("TAVILY_API_KEY")
    if not key:
        raise SystemExit("Set TAVILY_API_KEY first.")
    query = sys.argv[1] if len(sys.argv) > 1 else "customer feedback analysis SaaS tools"
    print(json.dumps(probe(query, key), indent=2))
