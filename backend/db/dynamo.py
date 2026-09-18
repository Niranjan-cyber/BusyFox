"""DynamoDB single-table design for all nine core entities (Task 20, PRD §14/§17.2).

One table, keyed on the Task 1 prefixes already defined in
backend/schemas/entities.py (`DynamoKeyPrefix`): PK = "<PREFIX><id>",
SK = "METADATA" gives O(1) get-by-id for every entity type on one table.

GSI1 (GSI1PK/GSI1SK) covers the provenance-chain list access patterns the
API surface needs (docs/contract.md) — e.g. "opportunities for this
business", "claims for this opportunity" — by writing the parent's key into
GSI1PK and the item's own key into GSI1SK at write time.

`ttl` (native DynamoDB Time To Live) enforces the §18.8 "raw collected text
expires after 30 days" rule for SourceDocument without a cleanup job.
"""

from __future__ import annotations

import os
from typing import TypeVar

import boto3
from boto3.dynamodb.conditions import Key
from pydantic import BaseModel

from backend.schemas.entities import (
    Business,
    Claim,
    Competitor,
    DynamoKeyPrefix,
    Evidence,
    ExecutionPack,
    Opportunity,
    Run,
    Signal,
    SourceDocument,
    Target,
)

TABLE_NAME = os.environ.get("DYNAMO_TABLE_NAME", "opportunity-engine")

_PREFIX_BY_MODEL: dict[type[BaseModel], DynamoKeyPrefix] = {
    Business: DynamoKeyPrefix.BUSINESS,
    Run: DynamoKeyPrefix.RUN,
    SourceDocument: DynamoKeyPrefix.SOURCE_DOCUMENT,
    Evidence: DynamoKeyPrefix.EVIDENCE,
    Claim: DynamoKeyPrefix.CLAIM,
    Signal: DynamoKeyPrefix.SIGNAL,
    Opportunity: DynamoKeyPrefix.OPPORTUNITY,
    Target: DynamoKeyPrefix.TARGET,
    ExecutionPack: DynamoKeyPrefix.EXECUTION_PACK,
    Competitor: DynamoKeyPrefix.COMPETITOR,
}

ModelT = TypeVar("ModelT", bound=BaseModel)


def get_table(table_name: str = TABLE_NAME):
    return boto3.resource("dynamodb").Table(table_name)


def prefix_for(model: BaseModel) -> DynamoKeyPrefix:
    prefix = _PREFIX_BY_MODEL.get(type(model))
    if prefix is None:
        raise ValueError(f"no DynamoDB key prefix registered for {type(model).__name__}")
    return prefix


def to_item(model: BaseModel, *, parent_key: str | None = None) -> dict:
    """Build the raw DynamoDB item for any of the nine core entities.

    `parent_key` (e.g. "BIZ#biz_pulsestack") populates GSI1PK so the item is
    listable by its containing entity; omitted for entities with no useful
    parent-list access pattern.
    """
    prefix = prefix_for(model)
    own_key = f"{prefix.value}{model.id}"
    item: dict = {"PK": own_key, "SK": "METADATA", **model.model_dump(mode="json")}
    if parent_key is not None:
        item["GSI1PK"] = parent_key
        item["GSI1SK"] = own_key
    if isinstance(model, SourceDocument):
        item["ttl"] = int(model.expires_at.timestamp())
    return item


def put_entity(table, model: BaseModel, *, parent_key: str | None = None) -> dict:
    item = to_item(model, parent_key=parent_key)
    table.put_item(Item=item)
    return item


def get_entity(table, prefix: DynamoKeyPrefix, entity_id: str, model_cls: type[ModelT]) -> ModelT | None:
    response = table.get_item(Key={"PK": f"{prefix.value}{entity_id}", "SK": "METADATA"})
    item = response.get("Item")
    return None if item is None else model_cls.model_validate(item)


def query_children(table, parent_key: str, child_prefix: DynamoKeyPrefix) -> list[dict]:
    """Raw items whose GSI1PK is `parent_key` and GSI1SK starts with `child_prefix`."""
    response = table.query(
        IndexName="GSI1",
        KeyConditionExpression=Key("GSI1PK").eq(parent_key) & Key("GSI1SK").begins_with(child_prefix.value),
    )
    return response.get("Items", [])
