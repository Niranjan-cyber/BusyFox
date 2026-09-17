"""GitHub REST collector (Task 3) — release/issue activity for a named
competitor, mapped to the Task-1 Signal shape (§14.7).

Collector-level output only: list[Signal], not a ResearchAgentOutput — the
Competitor agent that wraps this into a full ResearchAgentOutput is Day 2
work, and so is the Live -> Cached -> Demo Fixture fallback ladder every
external source needs (CLAUDE.md). Today this is a bare Live call: a fetch
failure raises out to the caller instead of silently substituting anything.
"""

from __future__ import annotations

import json
import urllib.request
from typing import Callable

from backend.schemas.entities import Polarity, Signal, SourceKind

_API_ROOT = "https://api.github.com"
_HEADERS = {"Accept": "application/vnd.github+json", "User-Agent": "opportunity-engine"}

Fetch = Callable[[str], list[dict]]


def _http_get_json(url: str) -> list[dict]:
    request = urllib.request.Request(url, headers=_HEADERS)
    with urllib.request.urlopen(request, timeout=10) as response:
        return json.loads(response.read())


def fetch_github_signals(owner: str, repo: str, run_id: str, *, fetch: Fetch = _http_get_json) -> list[Signal]:
    """Recent releases and open issues for owner/repo, mapped to Signals."""

    def signal(id_suffix: str, aspect: str, polarity: Polarity, claim_text: str) -> Signal:
        return Signal(
            id=f"sig_gh_{owner}_{repo}_{id_suffix}",
            run_id=run_id,
            source_kind=SourceKind.GITHUB,
            aspect=aspect,
            polarity=polarity,
            claim_text=claim_text,
            evidence_ids=[],
            produced_by="github_collector",
        )

    signals = []

    for release in fetch(f"{_API_ROOT}/repos/{owner}/{repo}/releases?per_page=5"):
        signals.append(
            signal(
                f"release_{release['id']}",
                "release_velocity",
                Polarity.POSITIVE,
                f"{owner}/{repo} shipped release {release['tag_name']!r}.",
            )
        )

    for issue in fetch(f"{_API_ROOT}/repos/{owner}/{repo}/issues?state=open&per_page=5"):
        if "pull_request" in issue:
            continue
        signals.append(
            signal(
                f"issue_{issue['number']}",
                "reported_pain",
                Polarity.NEGATIVE,
                f"Open issue on {owner}/{repo}: {issue['title']!r}.",
            )
        )

    return signals
