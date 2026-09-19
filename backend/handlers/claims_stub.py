"""Claim listing and evidence-chain resolution (§15, screen 4).

Task 21: reads DynamoDB first, falling back to the Task 2 fixture for the
demo opportunity/claim — same treatment as `businesses_stub.py`.
"""

from __future__ import annotations

from backend.fixtures.fixtures import CLAIMS, EVIDENCE_BY_ID, OPPORTUNITY
from backend.handlers._common import dynamo_children, dynamo_get, not_found, ok, path_param
from backend.schemas.entities import Claim, DynamoKeyPrefix, Evidence, Opportunity, RetrievalMode

_CLAIMS_BY_ID = {c.id: c for c in CLAIMS}


def list_claims(event: dict, context: object) -> dict:
    """GET /opportunities/{id}/claims"""
    opportunity_id = path_param(event, "id")
    opportunity = dynamo_get(DynamoKeyPrefix.OPPORTUNITY, opportunity_id, Opportunity)
    if opportunity is None and opportunity_id != OPPORTUNITY.id:
        return not_found(f"no opportunity with id {opportunity_id!r}")

    claims = dynamo_children(f"{DynamoKeyPrefix.OPPORTUNITY.value}{opportunity_id}", DynamoKeyPrefix.CLAIM, Claim)
    if claims:
        return ok(claims, retrieval_mode=RetrievalMode.LIVE)
    if opportunity_id != OPPORTUNITY.id:
        return ok([], retrieval_mode=RetrievalMode.LIVE)
    return ok(CLAIMS, retrieval_mode=RetrievalMode.DEMO_FIXTURE)


def get_claim_evidence(event: dict, context: object) -> dict:
    """GET /claims/{id}/evidence — resolves a Claim's full evidence chain."""
    claim_id = path_param(event, "id")
    claim = dynamo_get(DynamoKeyPrefix.CLAIM, claim_id, Claim)
    if claim is not None:
        evidence = dynamo_children(f"{DynamoKeyPrefix.CLAIM.value}{claim_id}", DynamoKeyPrefix.EVIDENCE, Evidence)
        return ok(evidence or [], retrieval_mode=RetrievalMode.LIVE)

    fixture_claim = _CLAIMS_BY_ID.get(claim_id)
    if fixture_claim is None:
        return not_found(f"no claim with id {claim_id!r}")
    evidence = [EVIDENCE_BY_ID[eid] for eid in fixture_claim.evidence_ids if eid in EVIDENCE_BY_ID]
    return ok(evidence, retrieval_mode=RetrievalMode.DEMO_FIXTURE)
