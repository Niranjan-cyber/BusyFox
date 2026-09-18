"""Shared API Gateway proxy response helpers, plus (Task 21) a DynamoDB
lookup wrapper the handlers use to serve real persisted rows once a pipeline
run exists, falling back to the Task 2 fixtures otherwise — so a handler
never 500s just because the table is empty, unreachable, or (in local
dev/test, with no AWS credentials) doesn't exist at all.
"""

from __future__ import annotations

import json
import os
from typing import Any, Optional, TypeVar

from pydantic import BaseModel

from backend.db.dynamo import get_entity, query_children
from backend.schemas.entities import DynamoKeyPrefix

_HEADERS = {"Content-Type": "application/json"}
ModelT = TypeVar("ModelT", bound=BaseModel)


def _running_in_lambda() -> bool:
    """AWS sets this automatically inside a real Lambda execution
    environment. Gating on it (rather than just trying the DynamoDB call
    and catching whatever error comes back) matters because boto3's
    credential-resolution fallback chain takes several real seconds to time
    out with no credentials configured — exactly local dev/test's normal
    state — turning every handler call into a multi-second hang instead of
    an instant fixture fallback."""

    return bool(os.environ.get("AWS_LAMBDA_FUNCTION_NAME"))


def _to_jsonable(payload: Any) -> Any:
    if isinstance(payload, BaseModel):
        return json.loads(payload.model_dump_json())
    if isinstance(payload, list):
        return [_to_jsonable(item) for item in payload]
    return payload


def ok(payload: Any) -> dict:
    return {"statusCode": 200, "headers": _HEADERS, "body": json.dumps(_to_jsonable(payload))}


def not_found(message: str) -> dict:
    return {"statusCode": 404, "headers": _HEADERS, "body": json.dumps({"error": message})}


def path_param(event: dict, name: str) -> str | None:
    return (event.get("pathParameters") or {}).get(name)


def dynamo_get(prefix: DynamoKeyPrefix, entity_id: str, model_cls: type[ModelT]) -> Optional[ModelT]:
    """`get_entity`, skipped outside a real Lambda and swallowing any
    connection/credentials error as "not in Dynamo" rather than a 500 — the
    caller falls back to the Task 2 fixture in either case."""

    if not _running_in_lambda():
        return None
    try:
        from backend.db.dynamo import get_table

        return get_entity(get_table(), prefix, entity_id, model_cls)
    except Exception:
        return None


def dynamo_children(parent_key: str, child_prefix: DynamoKeyPrefix, model_cls: type[ModelT]) -> Optional[list[ModelT]]:
    """`query_children`, same skip-outside-Lambda/fallback-on-error
    treatment as `dynamo_get`. Returns None (not []) on failure, so callers
    can tell "table unreachable" apart from "table reachable, genuinely no
    rows yet"."""

    if not _running_in_lambda():
        return None
    try:
        from backend.db.dynamo import get_table

        items = query_children(get_table(), parent_key, child_prefix)
        return [model_cls.model_validate(item) for item in items]
    except Exception:
        return None
