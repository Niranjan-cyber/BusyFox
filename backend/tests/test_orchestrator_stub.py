"""Orchestrator stub Lambda (Task 6) — sanity check for the Step Functions
Task state's handler, invoked directly with a fake event."""

from __future__ import annotations

from backend.handlers.orchestrator_stub import run_stub


def test_returns_status_and_echoes_input():
    result = run_stub({"business_id": "biz_001"}, None)
    assert result["status"] == "orchestrator_reached"
    assert result["input"] == {"business_id": "biz_001"}
