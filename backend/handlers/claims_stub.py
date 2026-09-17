"""Stub Lambdas for Claim listing and evidence-chain resolution (§15, screen 4)."""

from __future__ import annotations

from backend.fixtures.fixtures import CLAIMS, EVIDENCE_BY_ID, OPPORTUNITY
from backend.handlers._common import not_found, ok, path_param

_CLAIMS_BY_ID = {c.id: c for c in CLAIMS}


def list_claims(event: dict, context: object) -> dict:
    """GET /opportunities/{id}/claims"""
    opportunity_id = path_param(event, "id")
    if opportunity_id != OPPORTUNITY.id:
        return not_found(f"no opportunity with id {opportunity_id!r}")
    return ok(CLAIMS)


def get_claim_evidence(event: dict, context: object) -> dict:
    """GET /claims/{id}/evidence — resolves a Claim's full evidence chain."""
    claim_id = path_param(event, "id")
    claim = _CLAIMS_BY_ID.get(claim_id)
    if claim is None:
        return not_found(f"no claim with id {claim_id!r}")
    evidence = [EVIDENCE_BY_ID[eid] for eid in claim.evidence_ids if eid in EVIDENCE_BY_ID]
    return ok(evidence)
