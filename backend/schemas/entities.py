"""Core entity schema — PRD §14 (opportunity_engine_prd_v8.md).

Nine core entities plus the Competitor supporting entity, mirrored field-for-field
in frontend/src/types/entities.ts. Human-readable mirror: docs/contract.md.

Provenance chain (§14.0): SourceDocument -> Evidence -> Claim -> Signal -> Opportunity -> Target -> ExecutionPack,
with Business and Run as the containing entities.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Shared enums
# ---------------------------------------------------------------------------


class ObservedInferredAssumed(str, Enum):
    """§13.3 — the one label system applied everywhere a claim reaches the UI."""

    OBSERVED = "OBSERVED"
    INFERRED = "INFERRED"
    ASSUMED = "ASSUMED"


class SourceKind(str, Enum):
    """§12 — evidence/source provenance kind."""

    SIMULATED = "simulated"
    OWNER_UPLOAD = "owner_upload"
    WEB_PUBLIC = "web_public"
    APP_STORE = "app_store"
    PRODUCT_HUNT = "product_hunt"
    GITHUB = "github"
    HN = "hn"
    MODEL_INFERENCE = "model_inference"


class RetrievalMode(str, Enum):
    """§7.2/§12.2 — the three-tier resilience ladder. Never substituted silently."""

    CACHED = "cached"
    LIVE = "live"
    DEMO_FIXTURE = "demo_fixture"


class ClaimType(str, Enum):
    """§14.6 — an opportunity's four required claim types."""

    WHY_THIS = "why_this"
    WHY_YOU = "why_you"
    WHY_NOW = "why_now"
    MECHANISM = "mechanism"


class ClaimStatus(str, Enum):
    VERIFIED = "verified"
    UNSUPPORTED = "unsupported"
    HYPOTHESIS = "hypothesis"


class ClaimSupportStatus(str, Enum):
    """§12.1 — semantic support check outcome."""

    SUPPORTS = "supports"
    PARTIAL = "partial"
    UNSUPPORTED = "unsupported"


class FreshnessStatus(str, Enum):
    FRESH = "fresh"
    STALE = "stale"


class EvidenceConfidence(str, Enum):
    """§13.1 — kept structurally separate from priority and potential value."""

    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class Priority(str, Enum):
    """§13.1 — rule-table output, never a computed composite score."""

    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    BLOCKED = "Blocked"


class RunStatus(str, Enum):
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class Polarity(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"


class OpportunityType(str, Enum):
    """PRD names competitive_gap explicitly (§14.8); other playbook-specific
    types are expected but not yet enumerated — extend as they appear.

    segment_expansion/retention_fix/packaging_pricing/positioning_shift added
    2026-09-18 once Lane B's PulseStack fixtures needed them for real."""

    COMPETITIVE_GAP = "competitive_gap"
    UNMET_NEED = "unmet_need"
    EXPANSION = "expansion"
    SEGMENT_EXPANSION = "segment_expansion"
    RETENTION_FIX = "retention_fix"
    PACKAGING_PRICING = "packaging_pricing"
    POSITIONING_SHIFT = "positioning_shift"


class ExecutionPackStatus(str, Enum):
    DRAFT = "draft"
    SENT = "sent"


class OutreachChannel(str, Enum):
    EMAIL = "email"


# ---------------------------------------------------------------------------
# Id / DynamoDB key prefixes (AGENTS.md: "Stable prefixes: opp_ and DynamoDB
# keys like OPP#")
# ---------------------------------------------------------------------------


class EntityIdPrefix(str, Enum):
    BUSINESS = "biz_"
    RUN = "run_"
    SOURCE_DOCUMENT = "src_"
    EVIDENCE = "evd_"
    CLAIM = "claim_"
    SIGNAL = "sig_"
    OPPORTUNITY = "opp_"
    TARGET = "tgt_"
    EXECUTION_PACK = "pack_"
    COMPETITOR = "cmp_"


class DynamoKeyPrefix(str, Enum):
    BUSINESS = "BIZ#"
    RUN = "RUN#"
    SOURCE_DOCUMENT = "SRC#"
    EVIDENCE = "EVD#"
    CLAIM = "CLAIM#"
    SIGNAL = "SIG#"
    OPPORTUNITY = "OPP#"
    TARGET = "TGT#"
    EXECUTION_PACK = "PACK#"
    COMPETITOR = "CMP#"


# ---------------------------------------------------------------------------
# §14.1 Business
# ---------------------------------------------------------------------------


class Goal(BaseModel):
    metric: str
    change_usd: int
    horizon_days: int


class Pricing(BaseModel):
    starter_usd_month: Optional[float] = None
    team_usd_month: Optional[float] = None


class Capability(BaseModel):
    key: str
    confirmed: bool


class Business(BaseModel):
    id: str
    name: str
    is_simulated: bool
    scenario_id: Optional[str] = None
    industry: str
    playbook_id: str
    icp: list[str]
    pricing: Pricing
    current_mrr_usd: float
    goal: Goal
    capabilities: list[Capability]
    named_competitors: list[str]
    data_assets: list[str]
    created_at: datetime


# ---------------------------------------------------------------------------
# §14.2 Competitor — thin supporting entity, not one of the nine core ones
# ---------------------------------------------------------------------------


class Competitor(BaseModel):
    id: str
    run_id: str
    name: str
    sources_checked: list[SourceKind]
    enrichment_sources_checked: list[SourceKind]
    summary_id: str
    public_url: str


# ---------------------------------------------------------------------------
# §14.3 Run
# ---------------------------------------------------------------------------


class AgentInvocation(BaseModel):
    """One row per agent invocation inside a Run — where the §10.1a runtime
    contract's actual usage (not its limits) is recorded."""

    component: str
    iterations: int
    tool_calls: int
    runtime_seconds: float
    truncated: bool


class Run(BaseModel):
    id: str
    business_id: str
    started_at: datetime
    finished_at: Optional[datetime] = None
    status: RunStatus
    agent_invocations: list[AgentInvocation]
    opportunities_produced: int
    opportunities_rejected: int
    estimated_cost_usd: float


class AgentRuntimeContract(BaseModel):
    """§10.1a — the five-field ceiling enforced around every Strands agent
    loop. Bounds one invocation; actuals are recorded as an AgentInvocation."""

    max_iterations: int = 3
    max_tool_calls: int = 6
    max_runtime_seconds: int = 60
    max_results: int = 10
    max_tokens: int


# ---------------------------------------------------------------------------
# §14.4 SourceDocument
# ---------------------------------------------------------------------------


class SourceDocument(BaseModel):
    id: str
    run_id: str
    source_kind: SourceKind
    retrieval_mode: RetrievalMode
    url: str
    fetched_at: datetime
    raw_text_s3_key: str
    expires_at: datetime


# ---------------------------------------------------------------------------
# §14.5 / §12 Evidence
# ---------------------------------------------------------------------------


class ClaimSupport(BaseModel):
    status: ClaimSupportStatus
    confidence: float
    reason: str


class Freshness(BaseModel):
    status: FreshnessStatus
    age_days: int
    limit_days: int


class Evidence(BaseModel):
    id: str
    source_document_id: str
    source_kind: SourceKind
    retrieval_mode: RetrievalMode
    url: str
    retrieved_at: datetime
    author: Optional[str] = None
    published_at: Optional[datetime] = None
    quote: str
    quote_hash: str
    claim_support: ClaimSupport
    freshness: Freshness


# ---------------------------------------------------------------------------
# §14.6 Claim
# ---------------------------------------------------------------------------


class Claim(BaseModel):
    id: str
    opportunity_id: str
    type: ClaimType
    text: str
    status: ClaimStatus
    evidence_ids: list[str]


# ---------------------------------------------------------------------------
# §14.7 Signal — the only shape a research agent is allowed to emit
# ---------------------------------------------------------------------------


class Signal(BaseModel):
    id: str
    run_id: str
    source_kind: SourceKind
    aspect: str
    polarity: Polarity
    claim_text: str
    evidence_ids: list[str]
    produced_by: str


# ---------------------------------------------------------------------------
# §14.8 Opportunity
# ---------------------------------------------------------------------------


class OpportunityMechanism(BaseModel):
    """Non-negotiable per BUILD_PLAN.md Day 2 step 3 — every candidate must
    state one of these, not just carry evidence."""

    statement: str
    shared_segment: str
    actionable_because: str


class SignalReason(BaseModel):
    signal_id: str
    reason: str


class PainToFix(BaseModel):
    signal_id: str
    reason: str
    severity: int


class CompetitiveContextItem(BaseModel):
    signal_id: str
    competitor: str
    pattern: str


class EvidenceDiversity(BaseModel):
    source_kind_count: int
    domain_count: int
    author_count: int
    underlying_event_risk: str


class MonthlyRange(BaseModel):
    low: float
    high: float


class ValueAssumption(BaseModel):
    """§13.2 — each value-model variable carries its own OBSERVED/ASSUMED label."""

    key: str
    label: ObservedInferredAssumed
    description: str


class ValueModel(BaseModel):
    model: Literal["saas_arr"]
    assumptions: list[ValueAssumption]
    monthly_usd: MonthlyRange


class Opportunity(BaseModel):
    """§14.8. No `opportunities_score` / `score_breakdown` field (§13.1) —
    evidence_confidence, value and priority stay three separate fields."""

    id: str
    type: OpportunityType
    claim_ids: list[str]
    opportunity_mechanism: OpportunityMechanism
    strengths_it_builds_on: list[SignalReason]
    pains_to_fix_first: list[PainToFix]
    competitive_context: list[CompetitiveContextItem]
    evidence_diversity: EvidenceDiversity
    evidence_confidence: EvidenceConfidence
    priority: Priority
    value: ValueModel


# ---------------------------------------------------------------------------
# §14.9 Target / Account
# ---------------------------------------------------------------------------


class ObservedFact(BaseModel):
    claim: str
    evidence_ids: list[str]
    source_kind: SourceKind


class DerivedSignal(BaseModel):
    signal: str
    signal_id: str
    confidence: str
    last_verified_at: datetime
    evidence_ids: list[str]


class AccountFitInference(BaseModel):
    statement: str
    source_kind: SourceKind = SourceKind.MODEL_INFERENCE
    confidence: str


class SuggestedContact(BaseModel):
    role: str
    reason: str
    basis: SourceKind = SourceKind.MODEL_INFERENCE


class Target(BaseModel):
    id: str
    opportunity_id: str
    organisation: str
    observed_facts: list[ObservedFact]
    derived_signals: list[DerivedSignal]
    account_fit_inference: AccountFitInference
    suggested_contact: SuggestedContact


# ---------------------------------------------------------------------------
# §14.10 ExecutionPack
# ---------------------------------------------------------------------------


class OutreachDraft(BaseModel):
    channel: OutreachChannel
    draft: str
    proof_point_signal_id: str
    outreach_policy_checked: bool


class ExecutionPack(BaseModel):
    id: str
    opportunity_id: str
    offer: str
    proposal: str
    outreach_drafts: list[OutreachDraft]
    status: ExecutionPackStatus
    sent_by: Optional[str] = None
    sent_at: Optional[datetime] = None


# ---------------------------------------------------------------------------
# §10.1a — research-agent vs. synthesis-agent output shapes.
# The absence of an `opportunities`/`candidate_opportunities` field on
# ResearchAgentOutput is the structural enforcement §10.1a requires: there is
# no field for a research agent to fill in even if it tried.
# ---------------------------------------------------------------------------


class ResearchAgentOutput(BaseModel):
    """Market / Feedback Pipeline / Competitor agent output (§10.1a)."""

    run_id: str
    produced_by: str
    signals: list[Signal]
    truncated: bool = False


class SynthesisAgentOutput(BaseModel):
    """Synthesis Agent output — the only component allowed to emit candidate
    opportunities, and only from already-collected signals (§10.1a, §10.3).

    `claims` accompanies `candidate_opportunities` because each opportunity's
    `claim_ids` (§14.8) must resolve to real Claim rows (§14.6), and nothing
    upstream of Synthesis creates them — Evidence Check (Task 18) fills in
    each claim's real `status`/`evidence_ids` afterward."""

    run_id: str
    candidate_opportunities: list[Opportunity]
    claims: list[Claim]
