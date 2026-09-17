"""Invokes every Task 2 stub Lambda directly and validates its response body
against the matching Task 1 Pydantic model.

This is the curl-equivalent verification named in tasks/plan.md's Task 2
acceptance criteria, adapted for a repo with no live AWS deployment yet
(deployment is Task 6) — invoking handler(event, context) locally is
equivalent to hitting the route once it's behind API Gateway, since the
handler is the entire implementation on either side of that boundary.
"""

from __future__ import annotations

import json

import pytest

from backend.fixtures.fixtures import COMPETITOR_SENTRY, EVIDENCE_ALERT_NOISE
from backend.handlers import businesses_stub, claims_stub, competitors_stub, opportunities_stub
from backend.schemas.entities import Business, Claim, Competitor, Evidence, ExecutionPack, Opportunity, Signal


def _event(**path_params: str) -> dict:
    return {"pathParameters": path_params}


def _body(response: dict):
    assert response["statusCode"] == 200
    return json.loads(response["body"])


def test_get_business_returns_task1_shaped_payload():
    response = businesses_stub.get_business(_event(id="biz_pulsestack"), None)
    Business.model_validate(_body(response))


def test_get_business_feedback_summary_returns_signals():
    response = businesses_stub.get_feedback_summary(_event(id="biz_pulsestack"), None)
    body = _body(response)
    assert len(body) > 0
    for item in body:
        Signal.model_validate(item)


def test_list_opportunities_returns_task1_shaped_payload():
    response = opportunities_stub.list_opportunities(_event(id="biz_pulsestack"), None)
    body = _body(response)
    assert len(body) > 0
    for item in body:
        Opportunity.model_validate(item)


def test_get_opportunity_returns_task1_shaped_payload():
    response = opportunities_stub.get_opportunity(_event(id="opp_001"), None)
    opp = Opportunity.model_validate(_body(response))
    assert not hasattr(opp, "score") and not hasattr(opp, "opportunity_score")


def test_get_execution_pack_returns_task1_shaped_payload():
    response = opportunities_stub.get_execution_pack(_event(id="opp_001"), None)
    ExecutionPack.model_validate(_body(response))


def test_list_claims_returns_task1_shaped_payload():
    response = claims_stub.list_claims(_event(id="opp_001"), None)
    body = _body(response)
    assert len(body) == 4
    for item in body:
        Claim.model_validate(item)


def test_get_claim_evidence_resolves_the_chain():
    response = claims_stub.get_claim_evidence(_event(id="claim_001"), None)
    body = _body(response)
    assert len(body) > 0
    for item in body:
        Evidence.model_validate(item)


def test_list_competitors_returns_task1_shaped_payload():
    response = competitors_stub.list_competitors(_event(), None)
    body = _body(response)
    assert len(body) > 0
    for item in body:
        Competitor.model_validate(item)


def test_get_competitor_evidence_live_returns_task1_shaped_payload():
    response = competitors_stub.get_competitor_evidence_live(
        _event(id=COMPETITOR_SENTRY.id, evidenceId=EVIDENCE_ALERT_NOISE.id), None
    )
    Evidence.model_validate(_body(response))


@pytest.mark.parametrize(
    "handler, event",
    [
        (businesses_stub.get_business, _event(id="biz_nonexistent")),
        (opportunities_stub.get_opportunity, _event(id="opp_nonexistent")),
        (claims_stub.get_claim_evidence, _event(id="claim_nonexistent")),
        (competitors_stub.get_competitor_evidence_live, _event(id="cmp_nonexistent", evidenceId="evd_001")),
    ],
)
def test_unknown_ids_return_404_not_a_500(handler, event):
    response = handler(event, None)
    assert response["statusCode"] == 404
