"""GitHub REST collector (Task 3) — releases/issues for a named competitor,
mapped to Task-1 Signal shape. Network is stubbed via an injected fetch
function; no live HTTP call is made in tests.
"""

from __future__ import annotations

from backend.collectors.github import fetch_github_signals
from backend.schemas.entities import Polarity, Signal, SourceKind

_RELEASES_URL = "https://api.github.com/repos/acme/widget/releases?per_page=5"
_ISSUES_URL = "https://api.github.com/repos/acme/widget/issues?state=open&per_page=5"

_RELEASES = [{"id": 501, "tag_name": "v2.4.0"}]
_ISSUES = [
    {"number": 12, "title": "Export button silently fails on large datasets"},
    {"number": 13, "title": "Docs link 404s", "pull_request": {"url": "https://api.github.com/..."}},
]


def _fake_fetch(url: str):
    if url == _RELEASES_URL:
        return _RELEASES
    if url == _ISSUES_URL:
        return _ISSUES
    raise AssertionError(f"unexpected URL: {url}")


def test_returns_task1_shaped_signals():
    signals = fetch_github_signals("acme", "widget", "run_001", fetch=_fake_fetch)
    assert len(signals) > 0
    for signal in signals:
        Signal.model_validate(signal.model_dump())
        assert signal.source_kind == SourceKind.GITHUB
        assert signal.run_id == "run_001"
        assert signal.evidence_ids == []


def test_release_becomes_a_positive_signal():
    signals = fetch_github_signals("acme", "widget", "run_001", fetch=_fake_fetch)
    release_signals = [s for s in signals if s.aspect == "release_velocity"]
    assert len(release_signals) == 1
    assert release_signals[0].polarity == Polarity.POSITIVE
    assert "v2.4.0" in release_signals[0].claim_text


def test_open_issue_becomes_a_negative_signal():
    signals = fetch_github_signals("acme", "widget", "run_001", fetch=_fake_fetch)
    issue_signals = [s for s in signals if s.aspect == "reported_pain"]
    assert len(issue_signals) == 1
    assert issue_signals[0].polarity == Polarity.NEGATIVE
    assert "Export button silently fails" in issue_signals[0].claim_text


def test_pull_requests_are_not_treated_as_issues():
    signals = fetch_github_signals("acme", "widget", "run_001", fetch=_fake_fetch)
    assert all("Docs link 404s" not in s.claim_text for s in signals)


def test_signal_ids_are_unique_across_competitors():
    other_issues_url = "https://api.github.com/repos/other/thing/issues?state=open&per_page=5"
    other_releases_url = "https://api.github.com/repos/other/thing/releases?per_page=5"

    def other_fetch(url: str):
        if url == other_releases_url:
            return []
        if url == other_issues_url:
            return [{"number": 12, "title": "Same issue number, different repo"}]
        raise AssertionError(f"unexpected URL: {url}")

    acme_signals = fetch_github_signals("acme", "widget", "run_001", fetch=_fake_fetch)
    other_signals = fetch_github_signals("other", "thing", "run_001", fetch=other_fetch)

    acme_ids = {s.id for s in acme_signals}
    other_ids = {s.id for s in other_signals}
    assert acme_ids.isdisjoint(other_ids)
