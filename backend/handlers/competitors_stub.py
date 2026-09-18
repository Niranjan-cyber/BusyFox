"""Stub Lambdas for competitor listing and the evidence-drawer live re-fetch (§15)."""

from __future__ import annotations

from backend.fixtures.fixtures import COMPETITOR_SENTRY, EVIDENCE_BY_ID
from backend.handlers._common import not_found, ok, path_param
from backend.schemas.entities import RetrievalMode


def list_competitors(event: dict, context: object) -> dict:
    """GET /competitors

    Not wired to DynamoDB (the orchestrator never writes a Competitor row) —
    always the Task 2 fixture.
    """
    return ok([COMPETITOR_SENTRY], retrieval_mode=RetrievalMode.DEMO_FIXTURE)


def get_competitor_evidence_live(event: dict, context: object) -> dict:
    """GET /competitors/{id}/evidence/{evidenceId}/live

    Re-fetch/re-verify a competitor quote for the evidence drawer. Real live
    re-fetch + Live -> Cached -> Demo Fixture fallback (§7.2/§12.2) lands
    with the real Tavily/collector wiring (Task 5+); this stub always
    returns the fixture evidence item labelled as the fixture tier.
    """
    competitor_id = path_param(event, "id")
    evidence_id = path_param(event, "evidenceId")
    if competitor_id != COMPETITOR_SENTRY.id:
        return not_found(f"no competitor with id {competitor_id!r}")
    evidence = EVIDENCE_BY_ID.get(evidence_id)
    if evidence is None:
        return not_found(f"no evidence with id {evidence_id!r}")
    return ok(evidence)
