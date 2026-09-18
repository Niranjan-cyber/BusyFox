/**
 * Core entity types — mirrors PRD §14 (the nine core entities plus Competitor).
 *
 * STATUS: this file is Lane B's transcription of §14, written so screens 1 and 3 could be
 * built before Phase 0 Task 1 landed. `backend/schemas/entities.py` is the source of truth
 * once it exists; reconcile this file against it at the next stand-up and correct here, not
 * there. Field names and shapes below are taken verbatim from the PRD so the diff stays small.
 *
 * Provenance chain (§14.0): SourceDocument -> Evidence -> Claim -> Signal -> Opportunity
 * -> Target -> ExecutionPack. Business and Run are the containing entities.
 */

/** §13.3 — applied everywhere a claim reaches the UI. */
export type ClaimLabel = 'OBSERVED' | 'INFERRED' | 'ASSUMED'

/** §7.2 — the three-level resilience ladder. Never substituted silently. */
export type RetrievalMode = 'live' | 'cached' | 'demo_fixture'

/** §12 — evidence confidence, kept separate from priority and value (§13.1). */
export type EvidenceConfidence = 'HIGH' | 'MEDIUM' | 'LOW'

/** §13.1 — a rule table, not arithmetic. "Blocked" is shown separately, not ranked. */
export type Priority = 'High' | 'Medium' | 'Low' | 'Blocked'

/** §5.1 — mutually exclusive, one per opportunity. */
export type OpportunityType =
  | 'competitive_gap'
  | 'segment_expansion'
  | 'positioning_shift'
  | 'packaging_pricing'
  | 'retention_fix'
  | 'partnership'

export type Polarity = 'positive' | 'negative'

export type SourceKind =
  | 'simulator'
  | 'web_public'
  | 'hn'
  | 'github'
  | 'app_store'
  | 'product_hunt'

/** §14.1 */
export interface Business {
  id: string
  name: string
  is_simulated: boolean
  scenario_id: string
  industry: string
  playbook_id: string
  icp: string[]
  pricing: Record<string, number>
  current_mrr_usd: number
  goal: { metric: string; change_usd: number; horizon_days: number }
  capabilities: { key: string; confirmed: boolean }[]
  named_competitors: string[]
  data_assets: string[]
  created_at: string
}

/** §14.2 — a thin supporting entity, not a tenth core one. */
export interface Competitor {
  id: string
  run_id: string
  name: string
  sources_checked: SourceKind[]
  enrichment_sources_checked: SourceKind[]
  summary_id: string
  public_url: string
}

/** §10.1a — the five-field runtime contract, as stored on a Run. */
export interface AgentInvocation {
  component: string
  iterations: number
  tool_calls: number
  runtime_seconds: number
  truncated: boolean
}

/** §14.3 */
export interface Run {
  id: string
  business_id: string
  started_at: string
  finished_at: string | null
  status: 'running' | 'succeeded' | 'failed'
  agent_invocations: AgentInvocation[]
  opportunities_produced: number
  opportunities_rejected: number
  estimated_cost_usd: number
}

/** §14.4 */
export interface SourceDocument {
  id: string
  run_id: string
  source_kind: SourceKind
  retrieval_mode: RetrievalMode
  url: string
  fetched_at: string
  raw_text_s3_key: string
  expires_at: string
}

/** §12, §14.5 */
export interface Evidence {
  id: string
  source_document_id: string
  quote: string
  quote_hash: string
  author: string | null
  published_at: string | null
  polarity: Polarity
  claim_support: 'supports' | 'contradicts' | 'unrelated'
  freshness_days: number
  retrieval_mode: RetrievalMode
}

/** §14.6 — the entity v7 was missing. */
export interface Claim {
  id: string
  opportunity_id: string
  type: 'why_this' | 'why_you' | 'why_now' | 'mechanism'
  text: string
  status: 'verified' | 'unsupported' | 'hypothesis'
  label: ClaimLabel
  evidence_ids: string[]
}

/**
 * §14.7 — what a research agent is allowed to emit.
 *
 * Note for anyone extending this: research-agent output must be structurally incapable of
 * carrying opportunities (§10.1a, AGENTS.md). `ResearchAgentOutput` below enforces that —
 * do not add an `opportunities` field to it, and do not widen it to `unknown`.
 */
export interface Signal {
  id: string
  run_id: string
  source_kind: SourceKind
  aspect: string
  polarity: Polarity
  claim_text: string
  evidence_ids: string[]
  produced_by: 'market_agent' | 'feedback_agent' | 'competitor_agent'
}

/** §11.2 */
export interface EvidenceDiversity {
  source_kind_count: number
  domain_count: number
  author_count: number
  underlying_event_risk: 'low' | 'medium' | 'high' | 'unknown'
}

/** §13.2 — always a range, always with its assumptions visible and editable. */
export interface ValueEstimate {
  model: 'saas_arr'
  assumptions: {
    signal_count: number
    estimated_qualified_accounts: { low: number; high: number }
    expected_conversion: number
    arpa_usd: number
  }
  monthly_usd: { low: number; high: number }
}

/** §9.5 — mandatory on every candidate opportunity. */
export interface OpportunityMechanism {
  statement: string
  shared_segment: string
  actionable_because: string
}

/** §14.8 — note there is no composite score field, by design (§13.1). */
export interface Opportunity {
  id: string
  type: OpportunityType
  title: string
  claim_ids: string[]
  opportunity_mechanism: OpportunityMechanism
  strengths_it_builds_on: { signal_id: string; reason: string }[]
  pains_to_fix_first: { signal_id: string; reason: string; severity: number }[]
  competitive_context: { signal_id: string; competitor: string; pattern: string }[]
  evidence_diversity: EvidenceDiversity
  evidence_confidence: EvidenceConfidence
  fix_first_flag: boolean
  priority: Priority
  value: ValueEstimate
  what_to_do: string
  fit: { key: string; label: string }[]
}

/** §1.3 — the rejected trail is part of the product, not an error state. */
export interface RejectedIdea {
  id: string
  title: string
  rejected_because: string
  failed_gate: string
}

/**
 * Theme aggregation over the business's own feedback (§9.2), polarity-split.
 * This is screen 1's "what customers love / complain about" payload. §14.0 leaves
 * FeedbackItem/FeedbackLabel at their v3/v7 shape; this is the aggregated view the
 * screen actually renders, not a new core entity.
 */
export interface FeedbackTheme {
  id: string
  aspect: string
  summary: string
  polarity: Polarity
  mention_count: number
  representative_quote: string
  representative_evidence_id: string
  retrieval_mode: RetrievalMode
}

export interface FeedbackSummary {
  business_id: string
  run_id: string
  total_items: number
  positive_count: number
  negative_count: number
  themes: FeedbackTheme[]
}

/** §14.9 — observed facts stay separate from inference. */
export interface Target {
  id: string
  opportunity_id: string
  name: string
  observed_facts: { fact: string; evidence_id: string }[]
  account_fit_inference: { reason: string; suggested_role: string }
  label: ClaimLabel
}

/** §14.10 */
export interface ExecutionPack {
  id: string
  opportunity_id: string
  offer: string
  proposal: string
  outreach_drafts: { channel: string; body: string; proof_point_evidence_id: string }[]
  outreach_policy_checked: boolean
}

/**
 * §10.1a — research agents emit signals only.
 *
 * `opportunities` is declared as `never` rather than simply omitted so that assigning an
 * object carrying one is a type error, not silently accepted excess-property widening.
 * This is the structural guarantee AGENTS.md requires, not a convention.
 */
export interface ResearchAgentOutput {
  signals: Signal[]
  truncated: boolean
  opportunities?: never
}
