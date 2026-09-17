"""Shared API Gateway proxy response helpers for the Task 2 stub Lambdas."""

from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel

_HEADERS = {"Content-Type": "application/json"}


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
