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

from backend.db.dynamo import put_entity
from backend.fixtures.fixtures import BUSINESS, CLAIMS, COMPETITOR_SENTRY, EVIDENCE_ALERT_NOISE, OPPORTUNITY
from backend.handlers import businesses_stub, claims_stub, competitors_stub, opportunities_stub
from backend.schemas.entities import Business, Claim, Competitor, DynamoKeyPrefix, Evidence, ExecutionPack, Opportunity, Signal
from backend.tests.test_dynamo import _FakeTable


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


# ---------------------------------------------------------------------------
# Task 21 — real DynamoDB rows win over the Task 2 fixture once a pipeline
# run has persisted them; outside a real Lambda (no AWS_LAMBDA_FUNCTION_NAME)
# the fixture keeps serving local dev/test exactly as before.
# ---------------------------------------------------------------------------


def _fake_table_with(*entities_and_parents) -> _FakeTable:
    table = _FakeTable()
    for entity, parent_key in entities_and_parents:
        put_entity(table, entity, parent_key=parent_key)
    return table


def test_get_business_prefers_real_dynamo_row_when_running_in_lambda(monkeypatch):
    real_business = BUSINESS.model_copy(update={"name": "Real PulseStack"})
    table = _fake_table_with((real_business, None))
    monkeypatch.setenv("AWS_LAMBDA_FUNCTION_NAME", "test")
    monkeypatch.setattr("backend.db.dynamo.get_table", lambda: table)

    body = _body(businesses_stub.get_business(_event(id="biz_pulsestack"), None))
    assert body["name"] == "Real PulseStack"


def test_list_opportunities_prefers_real_dynamo_rows_when_running_in_lambda(monkeypatch):
    biz_key = f"{DynamoKeyPrefix.BUSINESS.value}{BUSINESS.id}"
    table = _fake_table_with((BUSINESS, None), (OPPORTUNITY, biz_key))
    monkeypatch.setenv("AWS_LAMBDA_FUNCTION_NAME", "test")
    monkeypatch.setattr("backend.db.dynamo.get_table", lambda: table)

    body = _body(opportunities_stub.list_opportunities(_event(id="biz_pulsestack"), None))
    assert [Opportunity.model_validate(item).id for item in body] == [OPPORTUNITY.id]


def test_list_claims_prefers_real_dynamo_rows_when_running_in_lambda(monkeypatch):
    opp_key = f"{DynamoKeyPrefix.OPPORTUNITY.value}{OPPORTUNITY.id}"
    table = _fake_table_with((OPPORTUNITY, None), *((c, opp_key) for c in CLAIMS))
    monkeypatch.setenv("AWS_LAMBDA_FUNCTION_NAME", "test")
    monkeypatch.setattr("backend.db.dynamo.get_table", lambda: table)

    body = _body(claims_stub.list_claims(_event(id="opp_001"), None))
    assert len(body) == len(CLAIMS)


def test_unknown_id_still_404s_when_running_in_lambda_with_empty_table(monkeypatch):
    monkeypatch.setenv("AWS_LAMBDA_FUNCTION_NAME", "test")
    monkeypatch.setattr("backend.db.dynamo.get_table", lambda: _FakeTable())

    response = businesses_stub.get_business(_event(id="biz_nonexistent"), None)
    assert response["statusCode"] == 404


# ---------------------------------------------------------------------------
# X-Retrieval-Mode header — frontend/README.md blocker 1. Business/Signal/
# Opportunity/Claim have no retrieval_mode field of their own, so the §7.2
# ladder for the whole response travels as a header instead.
# ---------------------------------------------------------------------------


def test_fixture_served_responses_are_labelled_demo_fixture():
    assert businesses_stub.get_business(_event(id="biz_pulsestack"), None)["headers"]["X-Retrieval-Mode"] == "demo_fixture"
    assert opportunities_stub.get_opportunity(_event(id="opp_001"), None)["headers"]["X-Retrieval-Mode"] == "demo_fixture"
    assert claims_stub.list_claims(_event(id="opp_001"), None)["headers"]["X-Retrieval-Mode"] == "demo_fixture"
    assert competitors_stub.list_competitors(_event(), None)["headers"]["X-Retrieval-Mode"] == "demo_fixture"


def test_dynamo_served_responses_are_labelled_live(monkeypatch):
    real_business = BUSINESS.model_copy(update={"name": "Real PulseStack"})
    table = _fake_table_with((real_business, None))
    monkeypatch.setenv("AWS_LAMBDA_FUNCTION_NAME", "test")
    monkeypatch.setattr("backend.db.dynamo.get_table", lambda: table)

    response = businesses_stub.get_business(_event(id="biz_pulsestack"), None)
    assert response["headers"]["X-Retrieval-Mode"] == "live"
