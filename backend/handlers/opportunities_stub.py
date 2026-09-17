"""Stub Lambdas for the Opportunity Inbox, detail and execution-pack endpoints (screens 3, 4, 5)."""

from __future__ import annotations

from backend.fixtures.fixtures import BUSINESS, EXECUTION_PACK, OPPORTUNITY
from backend.handlers._common import not_found, ok, path_param


def list_opportunities(event: dict, context: object) -> dict:
    """GET /businesses/{id}/opportunities"""
    business_id = path_param(event, "id")
    if business_id != BUSINESS.id:
        return not_found(f"no business with id {business_id!r}")
    return ok([OPPORTUNITY])


def get_opportunity(event: dict, context: object) -> dict:
    """GET /opportunities/{id}"""
    opportunity_id = path_param(event, "id")
    if opportunity_id != OPPORTUNITY.id:
        return not_found(f"no opportunity with id {opportunity_id!r}")
    return ok(OPPORTUNITY)


def get_execution_pack(event: dict, context: object) -> dict:
    """GET /opportunities/{id}/execution-pack"""
    opportunity_id = path_param(event, "id")
    if opportunity_id != OPPORTUNITY.id:
        return not_found(f"no opportunity with id {opportunity_id!r}")
    return ok(EXECUTION_PACK)
