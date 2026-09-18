"""Task 20 — DynamoDB single-table writes/reads for the nine core entities."""

from __future__ import annotations

from backend.db.dynamo import get_entity, put_entity, query_children, to_item
from backend.fixtures.fixtures import BUSINESS, OPPORTUNITY, RUN, SOURCE_DOCUMENT_HN
from backend.schemas.entities import Business, DynamoKeyPrefix


def _matches(condition, item: dict) -> bool:
    """Evaluate a boto3 dynamodb.conditions object (Key().eq()/.begins_with(),
    composed with &) against a plain dict — enough to fake a Query without AWS
    or moto, by walking the same `_values` tuples boto3 builds internally."""
    lhs, rhs = condition._values
    if type(condition).__name__ == "And":
        return _matches(lhs, item) and _matches(rhs, item)
    attribute = item.get(lhs.name, "")
    if type(condition).__name__ == "Equals":
        return attribute == rhs
    if type(condition).__name__ == "BeginsWith":
        return attribute.startswith(rhs)
    raise NotImplementedError(f"unsupported condition: {condition}")


class _FakeTable:
    """In-memory stand-in for a boto3 DynamoDB Table — enough surface to
    exercise the DAO's key-building and query logic without AWS or moto."""

    def __init__(self) -> None:
        self._items: dict[tuple[str, str], dict] = {}

    def put_item(self, Item: dict) -> None:
        self._items[(Item["PK"], Item["SK"])] = Item

    def get_item(self, Key: dict) -> dict:
        item = self._items.get((Key["PK"], Key["SK"]))
        return {} if item is None else {"Item": item}

    def query(self, IndexName: str, KeyConditionExpression) -> dict:
        assert IndexName == "GSI1"
        items = [item for item in self._items.values() if _matches(KeyConditionExpression, item)]
        return {"Items": items}


def test_to_item_builds_pk_sk_from_entity_prefix() -> None:
    item = to_item(BUSINESS)
    assert item["PK"] == f"BIZ#{BUSINESS.id}"
    assert item["SK"] == "METADATA"
    assert "GSI1PK" not in item


def test_to_item_sets_ttl_from_source_document_expiry() -> None:
    item = to_item(SOURCE_DOCUMENT_HN)
    assert item["ttl"] == int(SOURCE_DOCUMENT_HN.expires_at.timestamp())


def test_put_and_get_entity_round_trips() -> None:
    table = _FakeTable()
    put_entity(table, BUSINESS)
    result = get_entity(table, DynamoKeyPrefix.BUSINESS, BUSINESS.id, Business)
    assert result == BUSINESS


def test_get_entity_returns_none_when_missing() -> None:
    table = _FakeTable()
    assert get_entity(table, DynamoKeyPrefix.BUSINESS, "biz_nope", Business) is None


def test_query_children_finds_items_by_parent_key() -> None:
    table = _FakeTable()
    parent_key = f"RUN#{RUN.id}"
    put_entity(table, OPPORTUNITY, parent_key=parent_key)
    put_entity(table, BUSINESS)  # unrelated item — must not match

    children = query_children(table, parent_key, DynamoKeyPrefix.OPPORTUNITY)

    assert children == [to_item(OPPORTUNITY, parent_key=parent_key)]
