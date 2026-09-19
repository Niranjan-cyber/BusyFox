"""Task 28: evidence-drawer Live -> Cached (S3) -> Demo Fixture ladder (§7.2/§12.2)."""

from __future__ import annotations

import json

import pytest
from botocore.exceptions import ClientError

from backend.db import evidence_cache
from backend.fixtures.fixtures import COMPETITOR_SENTRY, EVIDENCE_ALERT_NOISE
from backend.handlers import competitors_stub
from backend.schemas.entities import RetrievalMode

_EVENT = {"pathParameters": {"id": COMPETITOR_SENTRY.id, "evidenceId": EVIDENCE_ALERT_NOISE.id}}


class _FakeS3:
    """Enough of boto3's S3 client for get_object/put_object."""

    def __init__(self):
        self.objects: dict[str, bytes] = {}

    def put_object(self, *, Bucket, Key, Body, ContentType):
        self.objects[Key] = Body

    def get_object(self, *, Bucket, Key):
        if Key not in self.objects:
            raise ClientError({"Error": {"Code": "NoSuchKey"}}, "GetObject")
        body = self.objects[Key]
        return {"Body": type("B", (), {"read": lambda self: body})()}


@pytest.fixture
def in_lambda(monkeypatch):
    monkeypatch.setattr(competitors_stub, "_running_in_lambda", lambda: True)
    monkeypatch.setenv("EVIDENCE_CACHE_BUCKET", "test-bucket")
    monkeypatch.setenv("TAVILY_API_KEY", "tvly-test")
    s3 = _FakeS3()
    monkeypatch.setattr(competitors_stub, "get_cached", lambda c, e: evidence_cache.get_cached(c, e, client=s3))
    monkeypatch.setattr(competitors_stub, "put_cached", lambda c, ev: evidence_cache.put_cached(c, ev, client=s3))
    return s3


def _live_page(monkeypatch, text: str):
    monkeypatch.setattr(competitors_stub, "extract_text", lambda url, key: text)


def _live_fails(monkeypatch):
    def boom(url, key):
        raise TimeoutError("tavily down")

    monkeypatch.setattr(competitors_stub, "extract_text", boom)


def _serve() -> tuple[str, dict]:
    response = competitors_stub.get_competitor_evidence_live(_EVENT, None)
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    # body and header must name the same rung
    assert body["retrieval_mode"] == response["headers"]["X-Retrieval-Mode"]
    return body["retrieval_mode"], body


def test_live_success_is_live_and_writes_the_cache(monkeypatch, in_lambda):
    _live_page(monkeypatch, f"...  {EVIDENCE_ALERT_NOISE.quote.upper()}  ...")  # whitespace/case-insensitive
    mode, _ = _serve()
    assert mode == RetrievalMode.LIVE.value
    assert len(in_lambda.objects) == 1


def test_live_success_skips_the_cache_read(monkeypatch, in_lambda):
    _live_page(monkeypatch, EVIDENCE_ALERT_NOISE.quote)

    def no_read(c, e):
        raise AssertionError("cache read on a live success")

    monkeypatch.setattr(competitors_stub, "get_cached", no_read)
    assert _serve()[0] == RetrievalMode.LIVE.value


def test_live_failure_with_cache_hit_serves_cached(monkeypatch, in_lambda):
    _live_page(monkeypatch, EVIDENCE_ALERT_NOISE.quote)
    _, first = _serve()  # populates the cache
    _live_fails(monkeypatch)
    mode, body = _serve()
    assert mode == RetrievalMode.CACHED.value
    assert body["retrieved_at"] == first["retrieved_at"]  # the original fetch time, not now
    assert body["quote"] == EVIDENCE_ALERT_NOISE.quote


def test_live_failure_with_cache_miss_falls_to_fixture(monkeypatch, in_lambda):
    _live_fails(monkeypatch)
    mode, body = _serve()
    assert mode == RetrievalMode.DEMO_FIXTURE.value
    assert body["quote"] == EVIDENCE_ALERT_NOISE.quote


def test_quote_gone_from_source_is_a_live_failure(monkeypatch, in_lambda):
    _live_page(monkeypatch, "an unrelated page")
    assert _serve()[0] == RetrievalMode.DEMO_FIXTURE.value


def test_missing_tavily_key_falls_through(monkeypatch, in_lambda):
    monkeypatch.delenv("TAVILY_API_KEY")
    assert _serve()[0] == RetrievalMode.DEMO_FIXTURE.value


def test_unreachable_cache_falls_to_fixture_not_a_500(monkeypatch, in_lambda):
    _live_fails(monkeypatch)

    def unreachable(c, e):
        raise OSError("s3 down")

    monkeypatch.setattr(competitors_stub, "get_cached", unreachable)
    assert _serve()[0] == RetrievalMode.DEMO_FIXTURE.value


def test_failed_cache_write_does_not_break_a_live_success(monkeypatch, in_lambda):
    _live_page(monkeypatch, EVIDENCE_ALERT_NOISE.quote)

    def unwritable(c, ev):
        raise OSError("s3 down")

    monkeypatch.setattr(competitors_stub, "put_cached", unwritable)
    assert _serve()[0] == RetrievalMode.LIVE.value


def test_outside_lambda_never_touches_s3(monkeypatch):
    _live_fails(monkeypatch)
    monkeypatch.setenv("TAVILY_API_KEY", "tvly-test")

    def s3_touched(*a):
        raise AssertionError("S3 touched outside Lambda")

    monkeypatch.setattr(competitors_stub, "get_cached", s3_touched)
    assert _serve()[0] == RetrievalMode.DEMO_FIXTURE.value
