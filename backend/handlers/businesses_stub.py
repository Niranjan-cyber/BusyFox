"""Business profile and feedback-summary endpoints (screen 1).

Task 21: reads DynamoDB first (real rows once a pipeline run has persisted
them), falling back to the Task 2 fixture for the demo business — so this
keeps working identically in local dev/test (no AWS credentials) and starts
serving real data the moment a run exists, with no separate cutover.
"""

from __future__ import annotations

from backend.fixtures.fixtures import BUSINESS, SIGNALS
from backend.handlers._common import dynamo_children, dynamo_get, not_found, ok, path_param
from backend.schemas.entities import Business, DynamoKeyPrefix, Signal

_FEEDBACK_PRODUCERS = {"feedback_pipeline_labeller", "pulsestack_simulator"}


def get_business(event: dict, context: object) -> dict:
    """GET /businesses/{id}"""
    business_id = path_param(event, "id")
    business = dynamo_get(DynamoKeyPrefix.BUSINESS, business_id, Business)
    if business is not None:
        return ok(business)
    if business_id != BUSINESS.id:
        return not_found(f"no business with id {business_id!r}")
    return ok(BUSINESS)


def get_feedback_summary(event: dict, context: object) -> dict:
    """GET /businesses/{id}/feedback-summary — signals from the business's own feedback, by polarity."""
    business_id = path_param(event, "id")
    business = dynamo_get(DynamoKeyPrefix.BUSINESS, business_id, Business)
    if business is None and business_id != BUSINESS.id:
        return not_found(f"no business with id {business_id!r}")

    signals = dynamo_children(f"{DynamoKeyPrefix.BUSINESS.value}{business_id}", DynamoKeyPrefix.SIGNAL, Signal)
    own_feedback = [s for s in signals if s.produced_by in _FEEDBACK_PRODUCERS] if signals else []
    if own_feedback:
        return ok(own_feedback)
    if business_id != BUSINESS.id:
        return ok([])
    return ok([s for s in SIGNALS if s.produced_by == "feedback_pipeline"])
