"""Runs the real Action Agent (Task 26) against an already-persisted,
gate-passed Opportunity and writes its ExecutionPack to the deployed
DynamoDB table — same treatment as scripts/run_live_pipeline.py, one stage
later in the pipeline.

Needs OPENCODE_GO_API_KEY (repo .env) and an AWS profile with the deployed
table's access, e.g.:

    set -a; source .env; set +a
    AWS_PROFILE=<profile> DYNAMO_TABLE_NAME=<table> python scripts/run_action_agent_live.py <opportunity_id>
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# See run_live_pipeline.py's identical note — strands' callback_handler
# print()s raw model reasoning text, which breaks on Windows' cp1252 console
# default the moment the model emits a non-ASCII char.
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from backend.agents import action_agent
from backend.db.dynamo import get_entity, get_table
from backend.orchestrator import persist_execution_pack
from backend.schemas.entities import AgentRuntimeContract, DynamoKeyPrefix, Opportunity

_DEFAULT_OPPORTUNITY_ID = "opp_run_7f023794a99d_0"


def main() -> None:
    opportunity_id = sys.argv[1] if len(sys.argv) > 1 else _DEFAULT_OPPORTUNITY_ID
    table = get_table()
    opportunity = get_entity(table, DynamoKeyPrefix.OPPORTUNITY, opportunity_id, Opportunity)
    if opportunity is None:
        raise SystemExit(f"no persisted opportunity with id {opportunity_id!r} in {os.environ.get('DYNAMO_TABLE_NAME')}")

    print(f"Opportunity {opportunity.id} — priority={opportunity.priority} confidence={opportunity.evidence_confidence}")

    pack, invocation, rejected = action_agent.run_action_agent(
        opportunity,
        contract=AgentRuntimeContract(max_tokens=4096),
        collect=action_agent.live_collect(),
    )

    print(f"offer: {pack.offer}")
    print(f"proposal: {pack.proposal}")
    print(f"outreach_drafts kept: {len(pack.outreach_drafts)}, rejected: {len(rejected)}")
    for r in rejected:
        print(f"  rejected  reason={r.reason}  draft={r.raw.draft[:80]!r}")
    print(f"invocation: iterations={invocation.iterations} tool_calls={invocation.tool_calls} truncated={invocation.truncated}")

    persist_execution_pack(table, pack)
    print(f"persisted {pack.id} to {os.environ.get('DYNAMO_TABLE_NAME', '<default table name>')}")


if __name__ == "__main__":
    main()
