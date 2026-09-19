"""Level 2 of the §7.2 resilience ladder: S3 cache of evidence that was
successfully re-fetched live, re-served when a later live re-fetch fails.

One JSON object per evidence item. Written only on a live success, so
everything in here was really fetched — never seeded from a fixture.
"""

from __future__ import annotations

import os
from typing import Optional

import boto3
from botocore.exceptions import ClientError

from backend.schemas.entities import Evidence


def _bucket() -> str:
    return os.environ["EVIDENCE_CACHE_BUCKET"]


def _key(competitor_id: str, evidence_id: str) -> str:
    return f"evidence-cache/{competitor_id}/{evidence_id}.json"


def get_cached(competitor_id: str, evidence_id: str, *, client=None) -> Optional[Evidence]:
    """None on a miss. Any other S3 failure propagates — the caller decides
    whether "cache unreachable" should also fall through."""

    client = client or boto3.client("s3")
    try:
        body = client.get_object(Bucket=_bucket(), Key=_key(competitor_id, evidence_id))["Body"].read()
    except ClientError as exc:
        if exc.response["Error"]["Code"] == "NoSuchKey":
            return None
        raise
    return Evidence.model_validate_json(body)


def put_cached(competitor_id: str, evidence: Evidence, *, client=None) -> None:
    client = client or boto3.client("s3")
    client.put_object(
        Bucket=_bucket(),
        Key=_key(competitor_id, evidence.id),
        Body=evidence.model_dump_json().encode(),
        ContentType="application/json",
    )
