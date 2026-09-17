"""Stub Lambdas for the Business profile and feedback-summary endpoints (screen 1)."""

from __future__ import annotations

from backend.fixtures.fixtures import BUSINESS, SIGNALS
from backend.handlers._common import not_found, ok, path_param


def get_business(event: dict, context: object) -> dict:
    """GET /businesses/{id}"""
    business_id = path_param(event, "id")
    if business_id != BUSINESS.id:
        return not_found(f"no business with id {business_id!r}")
    return ok(BUSINESS)


def get_feedback_summary(event: dict, context: object) -> dict:
    """GET /businesses/{id}/feedback-summary — signals from the business's own feedback, by polarity."""
    business_id = path_param(event, "id")
    if business_id != BUSINESS.id:
        return not_found(f"no business with id {business_id!r}")
    own_feedback_signals = [s for s in SIGNALS if s.produced_by == "feedback_pipeline"]
    return ok(own_feedback_signals)
