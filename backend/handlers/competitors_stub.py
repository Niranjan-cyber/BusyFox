"""Competitor listing and the evidence-drawer live re-fetch (§15, §12.2)."""

from __future__ import annotations

import os
from datetime import datetime, timezone

from backend.collectors.tavily import extract_text
from backend.db.evidence_cache import get_cached, put_cached
from backend.fixtures.fixtures import COMPETITOR_SENTRY, EVIDENCE_BY_ID
from backend.handlers._common import _running_in_lambda, not_found, ok, path_param
from backend.schemas.entities import Evidence, RetrievalMode


def list_competitors(event: dict, context: object) -> dict:
    """GET /competitors

    Not wired to DynamoDB (the orchestrator never writes a Competitor row) —
    always the Task 2 fixture.
    """
    return ok([COMPETITOR_SENTRY], retrieval_mode=RetrievalMode.DEMO_FIXTURE)


def _refetch_live(evidence: Evidence) -> Evidence:
    """Re-fetch the evidence's URL and re-verify the quote is still on the
    page. Raises on any failure (no key, HTTP error, timeout, empty
    extract, quote gone) — every one of those means "fall to the next level"."""

    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        raise RuntimeError("TAVILY_API_KEY not set")
    page = " ".join(extract_text(evidence.url, api_key).lower().split())
    if " ".join(evidence.quote.lower().split()) not in page:
        raise ValueError("quote no longer found at source")
    return evidence.model_copy(update={"retrieval_mode": RetrievalMode.LIVE, "retrieved_at": datetime.now(timezone.utc)})


def get_competitor_evidence_live(event: dict, context: object) -> dict:
    """GET /competitors/{id}/evidence/{evidenceId}/live

    Live -> Cached (S3) -> Demo Fixture (§7.2/§12.2). Never errors on a
    failed re-fetch, and the returned `retrieval_mode` (body and
    X-Retrieval-Mode header) always names the level actually served.
    """
    competitor_id = path_param(event, "id")
    evidence_id = path_param(event, "evidenceId")
    if competitor_id != COMPETITOR_SENTRY.id:
        return not_found(f"no competitor with id {competitor_id!r}")
    evidence = EVIDENCE_BY_ID.get(evidence_id)
    if evidence is None:
        return not_found(f"no evidence with id {evidence_id!r}")

    try:
        live = _refetch_live(evidence)
    except Exception:
        live = None
    if live is not None:
        if _running_in_lambda():
            try:
                put_cached(competitor_id, live)
            except Exception:
                pass  # a cache write failing must not turn a live success into an error
        return ok(live, retrieval_mode=RetrievalMode.LIVE)

    # Skipped outside Lambda for the same reason dynamo_get is: no AWS
    # credentials locally means a multi-second boto3 timeout, not a miss.
    cached = None
    if _running_in_lambda():
        try:
            cached = get_cached(competitor_id, evidence_id)
        except Exception:
            cached = None  # cache unreachable == cache empty, fall to the fixture
    if cached is not None:
        return ok(cached.model_copy(update={"retrieval_mode": RetrievalMode.CACHED}), retrieval_mode=RetrievalMode.CACHED)

    # The stored fixture record carries `retrieval_mode="live"` (it was a live
    # fetch when collected); serving it as such now would be the silent
    # substitution §7.2 forbids.
    return ok(
        evidence.model_copy(update={"retrieval_mode": RetrievalMode.DEMO_FIXTURE}),
        retrieval_mode=RetrievalMode.DEMO_FIXTURE,
    )
