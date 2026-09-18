"""Runs the real pipeline (Task 21's run_pipeline) against the live Bedrock
agents/collectors and persists to the deployed DynamoDB table — the Day 2
checkpoint's "a full run produces at least one gate-passed opportunity",
made real rather than the fake-collector version backend/tests exercise.

Needs TAVILY_API_KEY/PRODUCT_HUNT_TOKEN (repo .env) and an AWS profile with
Bedrock + the deployed table's access, e.g.:

    set -a; source .env; set +a
    AWS_PROFILE=<profile> DYNAMO_TABLE_NAME=<table> python scripts/run_live_pipeline.py
"""

from __future__ import annotations

import os
import sys
import uuid
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.agents import competitor_agent, market_agent, synthesis_agent
from backend.db.dynamo import get_table
from backend.fixtures.fixtures import BUSINESS
from backend.orchestrator import persist, run_pipeline
from backend.pipeline.evidence_check import bedrock_semantic_support_checker


def _business_context(business) -> str:
    return (
        f"{business.name} is a {business.industry} product on the "
        f"{business.playbook_id} playbook, targeting {', '.join(business.icp)}. "
        f"Current MRR is ${business.current_mrr_usd:,.0f}, goal is +${business.goal.change_usd:,.0f} "
        f"{business.goal.metric} over {business.goal.horizon_days} days. "
        f"Named competitors: {', '.join(business.named_competitors)}."
    )


def main() -> None:
    business = BUSINESS
    run_id = f"run_{uuid.uuid4().hex[:12]}"
    now = datetime.now(timezone.utc)
    context = _business_context(business)

    print(f"Run {run_id} — {business.name} — {now.isoformat()}")

    result = run_pipeline(
        business,
        run_id=run_id,
        now=now,
        market_collect=market_agent.live_collect(context),
        competitor_collect=competitor_agent.live_collect(context, business.named_competitors),
        synthesis_collect=synthesis_agent.live_collect(),
        semantic_check=bedrock_semantic_support_checker(),
    )

    print(f"signals: {len(result.signals)}")
    print(f"ranked (gate-passed): {len(result.ranked)}")
    print(f"blocked: {len(result.blocked)}")
    print(f"rejected: {len(result.rejected)}")
    for opp in result.ranked:
        print(f"  ranked  {opp.id}  {opp.priority}  {opp.evidence_confidence}")
    for opp in result.blocked:
        print(f"  blocked {opp.id}  {opp.priority}  {opp.evidence_confidence}")

    persist(get_table(), result)
    print(f"persisted to {os.environ.get('DYNAMO_TABLE_NAME', '<default table name>')}")


if __name__ == "__main__":
    main()
