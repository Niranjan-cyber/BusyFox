"""Opportunity Inbox, detail and execution-pack endpoints (screens 3, 4, 5).

Task 21: reads DynamoDB first, falling back to the Task 2 fixture for the
demo business/opportunity — same treatment as `businesses_stub.py`.
"""

from __future__ import annotations

from backend.fixtures.fixtures import BUSINESS, EXECUTION_PACK, OPPORTUNITY, REJECTED_IDEAS
from backend.handlers._common import dynamo_children, dynamo_get, not_found, ok, path_param
from backend.schemas.entities import (
    Business,
    DynamoKeyPrefix,
    ExecutionPack,
    Opportunity,
    RejectedCandidate,
    RetrievalMode,
)


def list_opportunities(event: dict, context: object) -> dict:
    """GET /businesses/{id}/opportunities"""
    business_id = path_param(event, "id")
    business = dynamo_get(DynamoKeyPrefix.BUSINESS, business_id, Business)
    if business is None and business_id != BUSINESS.id:
        return not_found(f"no business with id {business_id!r}")

    opportunities = dynamo_children(
        f"{DynamoKeyPrefix.BUSINESS.value}{business_id}", DynamoKeyPrefix.OPPORTUNITY, Opportunity
    )
    if opportunities:
        return ok(opportunities, retrieval_mode=RetrievalMode.LIVE)
    if business_id != BUSINESS.id:
        return ok([], retrieval_mode=RetrievalMode.LIVE)
    return ok([OPPORTUNITY], retrieval_mode=RetrievalMode.DEMO_FIXTURE)


def list_rejected_ideas(event: dict, context: object) -> dict:
    """GET /businesses/{id}/rejected-ideas — docs/contract.md gap 2, closed by
    Task 19's `RejectedCandidate` (backend/pipeline/quality_gate.py)."""
    business_id = path_param(event, "id")
    business = dynamo_get(DynamoKeyPrefix.BUSINESS, business_id, Business)
    if business is None and business_id != BUSINESS.id:
        return not_found(f"no business with id {business_id!r}")

    rejected = dynamo_children(
        f"{DynamoKeyPrefix.BUSINESS.value}{business_id}", DynamoKeyPrefix.REJECTED_CANDIDATE, RejectedCandidate
    )
    if rejected is not None:
        return ok(rejected, retrieval_mode=RetrievalMode.LIVE)
    if business_id != BUSINESS.id:
        return ok([], retrieval_mode=RetrievalMode.LIVE)
    return ok(REJECTED_IDEAS, retrieval_mode=RetrievalMode.DEMO_FIXTURE)


def get_opportunity(event: dict, context: object) -> dict:
    """GET /opportunities/{id}"""
    opportunity_id = path_param(event, "id")
    opportunity = dynamo_get(DynamoKeyPrefix.OPPORTUNITY, opportunity_id, Opportunity)
    if opportunity is not None:
        return ok(opportunity, retrieval_mode=RetrievalMode.LIVE)
    if opportunity_id != OPPORTUNITY.id:
        return not_found(f"no opportunity with id {opportunity_id!r}")
    return ok(OPPORTUNITY, retrieval_mode=RetrievalMode.DEMO_FIXTURE)


def get_execution_pack(event: dict, context: object) -> dict:
    """GET /opportunities/{id}/execution-pack

    Task 26: reads DynamoDB first (Action Agent persists one pack per
    gate-passed opportunity, parented to it), falling back to the Task 2
    fixture for the demo opportunity — same treatment as the other handlers.
    """
    opportunity_id = path_param(event, "id")
    packs = dynamo_children(
        f"{DynamoKeyPrefix.OPPORTUNITY.value}{opportunity_id}", DynamoKeyPrefix.EXECUTION_PACK, ExecutionPack
    )
    if packs:
        return ok(packs[0], retrieval_mode=RetrievalMode.LIVE)
    if opportunity_id != OPPORTUNITY.id:
        return not_found(f"no opportunity with id {opportunity_id!r}")
    return ok(EXECUTION_PACK, retrieval_mode=RetrievalMode.DEMO_FIXTURE)
