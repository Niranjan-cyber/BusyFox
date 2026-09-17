"""Tavily probe (Task 5) — failure-mode handling. Network is stubbed via
an injected `post` function; no live HTTP call is made in tests. The live
round-trip itself needs a real TAVILY_API_KEY and is run manually via
`python -m backend.collectors.tavily "<query>"`.
"""

from __future__ import annotations

import urllib.error

from backend.collectors.tavily import FailureMode, probe

_SEARCH_URL = "https://api.tavily.com/search"
_EXTRACT_URL = "https://api.tavily.com/extract"


def test_clean_round_trip_has_no_failure_modes():
    def post(url, payload):
        if url == _SEARCH_URL:
            return {"results": [{"url": "https://example.com/a"}]}
        if url == _EXTRACT_URL:
            return {"results": [{"url": "https://example.com/a", "raw_content": "some extracted text"}]}
        raise AssertionError(f"unexpected url: {url}")

    report = probe("query", "key", post=post)
    assert report["failure_modes"] == []
    assert report["result_count"] == 1
    assert report["extracted_chars"] == len("some extracted text")


def test_empty_search_results_is_a_labelled_failure_mode():
    report = probe("query", "key", post=lambda url, payload: {"results": []})
    assert report["failure_modes"] == [FailureMode.EMPTY_RESULTS]


def test_malformed_extract_is_a_labelled_failure_mode():
    def post(url, payload):
        if url == _SEARCH_URL:
            return {"results": [{"url": "https://example.com/a"}]}
        return {"results": [{"url": "https://example.com/a"}]}  # no raw_content

    report = probe("query", "key", post=post)
    assert report["failure_modes"] == [FailureMode.MALFORMED_EXTRACT]


def test_http_error_is_labelled_with_stage_and_code():
    def post(url, payload):
        raise urllib.error.HTTPError(url, 429, "Too Many Requests", hdrs=None, fp=None)

    report = probe("query", "key", post=post)
    assert report["failure_modes"] == [f"{FailureMode.HTTP_ERROR}:search:429"]


def test_timeout_during_extract_is_labelled_with_stage():
    def post(url, payload):
        if url == _SEARCH_URL:
            return {"results": [{"url": "https://example.com/a"}]}
        raise TimeoutError("timed out")

    report = probe("query", "key", post=post)
    assert report["failure_modes"] == [f"{FailureMode.TIMEOUT}:extract:timed out"]
