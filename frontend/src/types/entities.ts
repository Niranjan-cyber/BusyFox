/**
 * Core entity schema — PRD §14 (opportunity_engine_prd_v8.md).
 *
 * Mirrors backend/schemas/entities.py field-for-field. Human-readable
 * mirror: docs/contract.md. If this file and the Python schema ever
 * disagree, the Python schema is source of truth (CLAUDE.md).
 *
 * Provenance chain (§14.0):
 * SourceDocument -> Evidence -> Claim -> Signal -> Opportunity -> Target -> ExecutionPack
 * Business and Run are the containing entities.
 */

// ---------------------------------------------------------------------------
// Shared enums
// ---------------------------------------------------------------------------

/** §13.3 — the one label system applied everywhere a claim reaches the UI. */
export type ObservedInferredAssumed = "OBSERVED" | "INFERRED" | "ASSUMED";

/** §12 — evidence/source provenance kind. */
export type SourceKind =
  | "simulated"
  | "owner_upload"
  | "web_public"
  | "app_store"
  | "product_hunt"
  | "github"
  | "hn"
  | "model_inference";

/** §7.2/§12.2 — the three-tier resilience ladder. Never substituted silently. */
export type RetrievalMode = "cached" | "live" | "demo_fixture";

/** §14.6 — an opportunity's four required claim types. */
export type ClaimType = "why_this" | "why_you" | "why_now" | "mechanism";

export type ClaimStatus = "verified" | "unsupported" | "hypothesis";

/** §12.1 — semantic support check outcome. */
export type ClaimSupportStatus = "supports" | "partial" | "unsupported";

export type FreshnessStatus = "fresh" | "stale";

/** §13.1 — kept structurally separate from priority and potential value. */
export type EvidenceConfidence = "HIGH" | "MEDIUM" | "LOW";

/** §13.1 — rule-table output, never a computed composite score. */
export type Priority = "High" | "Medium" | "Low" | "Blocked";

export type RunStatus = "running" | "succeeded" | "failed";

export type Polarity = "positive" | "negative";

/**
 * PRD names competitive_gap explicitly (§14.8); other playbook-specific
 * types are expected but not yet enumerated — extend as they appear.
 *
 * segment_expansion/retention_fix/packaging_pricing/positioning_shift added
 * 2026-09-18 once Lane B's PulseStack fixtures needed them for real.
 */
export type OpportunityType =
  | "competitive_gap"
  | "unmet_need"
  | "expansion"
  | "segment_expansion"
  | "retention_fix"
  | "packaging_pricing"
  | "positioning_shift";

export type ExecutionPackStatus = "draft" | "sent";

export type OutreachChannel = "email";

// ---------------------------------------------------------------------------
// Id / DynamoDB key prefixes (AGENTS.md: "Stable prefixes: opp_ and DynamoDB
// keys like OPP#")
// ---------------------------------------------------------------------------

export const EntityIdPrefix = {
  BUSINESS: "biz_",
  RUN: "run_",
  SOURCE_DOCUMENT: "src_",
  EVIDENCE: "evd_",
  CLAIM: "claim_",
  SIGNAL: "sig_",
  OPPORTUNITY: "opp_",
  TARGET: "tgt_",
  EXECUTION_PACK: "pack_",
  COMPETITOR: "cmp_",
} as const;

export const DynamoKeyPrefix = {
  BUSINESS: "BIZ#",
  RUN: "RUN#",
  SOURCE_DOCUMENT: "SRC#",
  EVIDENCE: "EVD#",
  CLAIM: "CLAIM#",
  SIGNAL: "SIG#",
  OPPORTUNITY: "OPP#",
  TARGET: "TGT#",
  EXECUTION_PACK: "PACK#",
  COMPETITOR: "CMP#",
} as const;

// ---------------------------------------------------------------------------
// §14.1 Business
// ---------------------------------------------------------------------------

export interface Goal {
  metric: string;
  change_usd: number;
  horizon_days: number;
}

export interface Pricing {
  starter_usd_month?: number;
  team_usd_month?: number;
}

export interface Capability {
  key: string;
  confirmed: boolean;
}

export interface Business {
  id: string;
  name: string;
  is_simulated: boolean;
  scenario_id?: string;
  industry: string;
  playbook_id: string;
  icp: string[];
  pricing: Pricing;
  current_mrr_usd: number;
  goal: Goal;
  capabilities: Capability[];
  named_competitors: string[];
  data_assets: string[];
  created_at: string; // ISO 8601
}

// ---------------------------------------------------------------------------
// §14.2 Competitor — thin supporting entity, not one of the nine core ones
// ---------------------------------------------------------------------------

export interface Competitor {
  id: string;
  run_id: string;
  name: string;
  sources_checked: SourceKind[];
  enrichment_sources_checked: SourceKind[];
  summary_id: string;
  public_url: string;
}

// ---------------------------------------------------------------------------
// §14.3 Run
// ---------------------------------------------------------------------------

/**
 * One row per agent invocation inside a Run — where the §10.1a runtime
 * contract's actual usage (not its limits) is recorded.
 */
export interface AgentInvocation {
  component: string;
  iterations: number;
  tool_calls: number;
  runtime_seconds: number;
  truncated: boolean;
}

export interface Run {
  id: string;
  business_id: string;
  started_at: string;
  finished_at?: string;
  status: RunStatus;
  agent_invocations: AgentInvocation[];
  opportunities_produced: number;
  opportunities_rejected: number;
  estimated_cost_usd: number;
}

/**
 * §10.1a — the five-field ceiling enforced around every Strands agent loop.
 * Bounds one invocation; actuals are recorded as an AgentInvocation.
 */
export interface AgentRuntimeContract {
  max_iterations: number; // default 3
  max_tool_calls: number; // default 6
  max_runtime_seconds: number; // default 60
  max_results: number; // default 10
  max_tokens: number; // model- and role-appropriate, set per component
}

// ---------------------------------------------------------------------------
// §14.4 SourceDocument
// ---------------------------------------------------------------------------

export interface SourceDocument {
  id: string;
  run_id: string;
  source_kind: SourceKind;
  retrieval_mode: RetrievalMode;
  url: string;
  fetched_at: string;
  raw_text_s3_key: string;
  expires_at: string;
}

// ---------------------------------------------------------------------------
// §14.5 / §12 Evidence
// ---------------------------------------------------------------------------

export interface ClaimSupport {
  status: ClaimSupportStatus;
  confidence: number;
  reason: string;
}

export interface Freshness {
  status: FreshnessStatus;
  age_days: number;
  limit_days: number;
}

export interface Evidence {
  id: string;
  source_document_id: string;
  source_kind: SourceKind;
  retrieval_mode: RetrievalMode;
  url: string;
  retrieved_at: string;
  author?: string;
  published_at?: string;
  quote: string;
  quote_hash: string;
  claim_support: ClaimSupport;
  freshness: Freshness;
}

// ---------------------------------------------------------------------------
// §14.6 Claim
// ---------------------------------------------------------------------------

export interface Claim {
  id: string;
  opportunity_id: string;
  type: ClaimType;
  text: string;
  status: ClaimStatus;
  evidence_ids: string[];
}

// ---------------------------------------------------------------------------
// §14.7 Signal — the only shape a research agent is allowed to emit
// ---------------------------------------------------------------------------

export interface Signal {
  id: string;
  run_id: string;
  source_kind: SourceKind;
  aspect: string;
  polarity: Polarity;
  claim_text: string;
  evidence_ids: string[];
  produced_by: string;
}

// ---------------------------------------------------------------------------
// §14.8 Opportunity
// ---------------------------------------------------------------------------

/**
 * Non-negotiable per BUILD_PLAN.md Day 2 step 3 — every candidate must
 * state one of these, not just carry evidence.
 */
export interface OpportunityMechanism {
  statement: string;
  shared_segment: string;
  actionable_because: string;
}

export interface SignalReason {
  signal_id: string;
  reason: string;
}

export interface PainToFix {
  signal_id: string;
  reason: string;
  severity: number;
}

export interface CompetitiveContextItem {
  signal_id: string;
  competitor: string;
  pattern: string;
}

export interface EvidenceDiversity {
  source_kind_count: number;
  domain_count: number;
  author_count: number;
  underlying_event_risk: string;
}

export interface MonthlyRange {
  low: number;
  high: number;
}

/** §13.2 — each value-model variable carries its own OBSERVED/ASSUMED label. */
export interface ValueAssumption {
  key: string;
  label: ObservedInferredAssumed;
  description: string;
}

export interface ValueModel {
  model: "saas_arr";
  assumptions: ValueAssumption[];
  monthly_usd: MonthlyRange;
}

/**
 * §14.8. No `opportunities_score` / `score_breakdown` field (§13.1) —
 * evidence_confidence, value and priority stay three separate fields.
 */
export interface Opportunity {
  id: string;
  type: OpportunityType;
  claim_ids: string[];
  opportunity_mechanism: OpportunityMechanism;
  strengths_it_builds_on: SignalReason[];
  pains_to_fix_first: PainToFix[];
  competitive_context: CompetitiveContextItem[];
  evidence_diversity: EvidenceDiversity;
  evidence_confidence: EvidenceConfidence;
  priority: Priority;
  value: ValueModel;
}

// ---------------------------------------------------------------------------
// §14.9 Target / Account
// ---------------------------------------------------------------------------

export interface ObservedFact {
  claim: string;
  evidence_ids: string[];
  source_kind: SourceKind;
}

export interface DerivedSignal {
  signal: string;
  signal_id: string;
  confidence: string;
  last_verified_at: string;
  evidence_ids: string[];
}

export interface AccountFitInference {
  statement: string;
  source_kind: "model_inference";
  confidence: string;
}

export interface SuggestedContact {
  role: string;
  reason: string;
  basis: "model_inference";
}

export interface Target {
  id: string;
  opportunity_id: string;
  organisation: string;
  observed_facts: ObservedFact[];
  derived_signals: DerivedSignal[];
  account_fit_inference: AccountFitInference;
  suggested_contact: SuggestedContact;
}

// ---------------------------------------------------------------------------
// §14.10 ExecutionPack
// ---------------------------------------------------------------------------

export interface OutreachDraft {
  channel: OutreachChannel;
  draft: string;
  proof_point_signal_id: string;
  outreach_policy_checked: boolean;
}

export interface ExecutionPack {
  id: string;
  opportunity_id: string;
  offer: string;
  proposal: string;
  outreach_drafts: OutreachDraft[];
  status: ExecutionPackStatus;
  sent_by?: string | null;
  sent_at?: string | null;
}

// ---------------------------------------------------------------------------
// §10.1a — research-agent vs. synthesis-agent output shapes.
// The absence of an `opportunities`/`candidate_opportunities` field on
// ResearchAgentOutput is the structural enforcement §10.1a requires: there
// is no field for a research agent to fill in even if it tried.
// ---------------------------------------------------------------------------

/** Market / Feedback Pipeline / Competitor agent output (§10.1a). */
export interface ResearchAgentOutput {
  run_id: string;
  produced_by: string;
  signals: Signal[];
  truncated: boolean;
}

/**
 * Synthesis Agent output — the only component allowed to emit candidate
 * opportunities, and only from already-collected signals (§10.1a, §10.3).
 */
export interface SynthesisAgentOutput {
  run_id: string;
  candidate_opportunities: Opportunity[];
}
