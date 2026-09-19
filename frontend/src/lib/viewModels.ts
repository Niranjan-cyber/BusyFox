import type {
  Claim,
  ClaimType,
  Evidence,
  ObservedInferredAssumed,
  Opportunity,
  Polarity,
  RetrievalMode,
  Signal,
} from '../types/entities'

/**
 * Frontend-only view models and adapters.
 *
 * Nothing here is a canonical entity — `backend/schemas/entities.py`,
 * `frontend/src/types/entities.ts` and `docs/contract.md` stay the source of truth, and this
 * file only derives display shapes from data those files already define. Where a UI need has
 * no legitimate source in the canonical contract, it does not appear here (see LEARNING.md).
 */

/**
 * What the client can honestly say about where a payload came from.
 *
 * `RetrievalMode` is the canonical §7.2 ladder and stays exactly three rungs. `undeclared` is
 * not a fourth rung — it is the state of a response that did not say which rung it is on, and
 * it exists so the UI can report that instead of picking a rung on the response's behalf. It
 * is a rendering concern, so it lives here rather than in the canonical entity contract.
 */
export type ServedMode = RetrievalMode | 'undeclared'

/** §13.3 rendering convention (docs/contract.md): why_this/why_you/why_now claims are
    OBSERVED, mechanism claims are INFERRED. Not a stored field on Claim. */
const CLAIM_TYPE_LABEL: Record<ClaimType, ObservedInferredAssumed> = {
  why_this: 'OBSERVED',
  why_you: 'OBSERVED',
  why_now: 'OBSERVED',
  mechanism: 'INFERRED',
}

export function claimLabel(claim: Pick<Claim, 'type'>): ObservedInferredAssumed {
  return CLAIM_TYPE_LABEL[claim.type]
}

/** §14.6 display heading and card/screen order for the four claim types. Shared by the inbox
    card and the opportunity detail screen so the two never drift. */
export const CLAIM_HEADING: Record<ClaimType, string> = {
  why_this: 'Why this',
  why_you: 'Why you',
  why_now: 'Why now',
  mechanism: 'Mechanism',
}

export const CLAIM_ORDER: ClaimType[] = ['why_this', 'why_you', 'why_now', 'mechanism']

/** §13.1's Blocked tier: a real, gate-passed opportunity with a product fix in the way.
    Derived from whether a pain-to-fix-first is on record, not a separate stored flag. */
export function fixFirstFlag(opportunity: Pick<Opportunity, 'pains_to_fix_first'>): boolean {
  return opportunity.pains_to_fix_first.length > 0
}

/** No canonical `title` field. Every opportunity must state a mechanism (§9.5), so that
    one sentence doubles as the card headline rather than inventing separate copy. */
export function opportunityTitle(opportunity: Pick<Opportunity, 'opportunity_mechanism'>): string {
  return opportunity.opportunity_mechanism.statement
}

/**
 * A candidate that failed Evidence Check / Quality Gate before ever becoming a stored
 * `Opportunity`. Distinct from `priority: "Blocked"`, which is a real, gate-passed opportunity
 * with a product-fix blocker. Not in the canonical contract: no entity, no endpoint in
 * `docs/contract.md`'s API table — this is unbuilt Quality Gate work (Lane A, Day 2), so the
 * type lives here rather than in `types/entities.ts` until that work ships a real shape.
 */
export interface RejectedIdea {
  id: string
  title: string
  rejected_because: string
  failed_gate: string
}

/** `backend/pipeline/quality_gate.py`'s gate-category slugs, screen-3-facing. */
const REJECTION_GATE_LABEL: Record<string, string> = {
  truth: 'Evidence Check',
  relevance: 'Relevance Check',
  commerciality: 'Commerciality Check',
  quality_safety: 'Quality & Safety Check',
}

/** `backend/pipeline/quality_gate.py`'s per-check failure slugs, screen-3-facing. */
const REJECTION_REASON_LABEL: Record<string, string> = {
  no_verified_evidence: 'No claim in this idea has verified evidence backing it.',
  citation_exists_but_unsupported: "A cited source exists but doesn't support the claim.",
  why_now_rests_solely_on_stale_evidence: 'The "why now" claim rests only on stale evidence.',
  mechanism_missing: 'No mechanism statement, segment, or reason it is actionable.',
  incomplete_opportunity: 'Missing one of the four required claim types.',
  not_actionable: 'No concrete next step, or a narrative claim failed to verify.',
  invented_competitor_claim: 'Cites a signal that was never actually collected.',
  simulated_claim_attributed_to_competitor: "Attributes PulseStack's own simulated data to a competitor.",
  account_fit_inference_without_observed_facts: 'Account fit was inferred without observed facts.',
}

function humanizeSlug(slug: string): string {
  return slug.charAt(0).toUpperCase() + slug.slice(1).replace(/_/g, ' ')
}

/** Screen 3's rejected-gate label. Falls back to a humanized slug for anything not yet mapped,
    so an unmapped or future gate category still renders as prose, not a blank. */
export function rejectionGateLabel(gate: string): string {
  return REJECTION_GATE_LABEL[gate] ?? humanizeSlug(gate)
}

/** Screen 3's rejected-reason label. `duplicate_merged_into:<id>` carries a dynamic id, so it's
    handled separately rather than as a static lookup entry. */
export function rejectionReasonLabel(reason: string): string {
  const [prefix, id] = reason.split(':')
  if (prefix === 'duplicate_merged_into' && id) {
    return `Merged into a stronger duplicate opportunity (${id}).`
  }
  return REJECTION_REASON_LABEL[reason] ?? humanizeSlug(reason)
}

/**
 * `docs/contract.md:61` — `/businesses/{id}/feedback-summary` returns `Signal[]`, not a
 * bespoke summary type. Grouping those signals by aspect into themes for screen 1 is a
 * presentational aggregation, so the grouped shape lives here, not in the entity contract.
 */
export interface FeedbackTheme {
  id: string
  aspect: string
  summary: string
  polarity: Polarity
  mention_count: number
  representative_quote: string
  representative_evidence_id: string
}

export interface FeedbackSummary {
  total_items: number
  positive_count: number
  negative_count: number
  themes: FeedbackTheme[]
}

/** Groups feedback signals by aspect + polarity. One signal's `claim_text` stands in as both
    the theme summary and the representative quote — nothing here is written that isn't
    already on a Signal. */
/** §16.1 screen 2's three research lanes. */
export type ResearchLane = 'market' | 'feedback' | 'competitive'

export const RESEARCH_LANES: ResearchLane[] = ['market', 'feedback', 'competitive']

export const LANE_LABEL: Record<ResearchLane, string> = {
  market: 'Market',
  feedback: 'Feedback',
  competitive: 'Competitive',
}

const FEEDBACK_PRODUCERS = new Set([
  'feedback_pipeline',
  'feedback_pipeline_agent',
  'feedback_pipeline_labeller',
  'pulsestack_simulator',
])
const COMPETITIVE_PRODUCERS = new Set(['competitor_agent'])

/** A signal's `produced_by` (§14.7) names the agent that emitted it; every research agent
    belongs to exactly one lane. Anything not named above (`market_agent`, and any future
    market-lane producer) defaults to Market rather than getting dropped from the screen. */
export function signalLane(signal: Pick<Signal, 'produced_by'>): ResearchLane {
  if (FEEDBACK_PRODUCERS.has(signal.produced_by)) return 'feedback'
  if (COMPETITIVE_PRODUCERS.has(signal.produced_by)) return 'competitive'
  return 'market'
}

export function summariseFeedback(signals: Signal[]): FeedbackSummary {
  const byTheme = new Map<string, Signal[]>()
  for (const signal of signals) {
    const key = `${signal.aspect}::${signal.polarity}`
    const group = byTheme.get(key)
    if (group) group.push(signal)
    else byTheme.set(key, [signal])
  }

  const themes: FeedbackTheme[] = [...byTheme.entries()].map(([key, group]) => {
    const [aspect] = key.split('::')
    const representative = group[0]
    return {
      id: `thm_${aspect}`,
      aspect,
      summary: representative.claim_text,
      polarity: representative.polarity,
      mention_count: group.length,
      representative_quote: representative.claim_text,
      representative_evidence_id: representative.evidence_ids[0] ?? '',
    }
  })

  return {
    total_items: signals.length,
    positive_count: signals.filter((signal) => signal.polarity === 'positive').length,
    negative_count: signals.filter((signal) => signal.polarity === 'negative').length,
    themes,
  }
}

/**
 * §12.1's three-outcome Evidence Check, read off one Evidence item — screen 4's diagram
 * (§16.1, §21 1:35-1:55). Evidence has no `quote_exists` boolean of its own: quote-exists is a
 * check the backend runs before ever calling the semantic-support model
 * (`backend/pipeline/evidence_check.py::build_evidence`), and when it fails, the exact literal
 * reason `"quote not found in source text"` is what lands in `claim_support.reason` — that
 * string is the only signal the client has that this branch, not semantic support, is why the
 * evidence was rejected.
 */
export type EvidenceCheckStep = 'quote_exists' | 'supports_claim' | 'fresh'
export type EvidenceCheckOutcome = 'accepted' | 'rejected_missing_citation' | 'rejected_unsupported'

const QUOTE_NOT_FOUND_REASON = 'quote not found in source text'

export interface EvidenceCheckResult {
  quoteExists: boolean
  outcome: EvidenceCheckOutcome
}

export function evidenceCheckResult(evidence: Pick<Evidence, 'claim_support'>): EvidenceCheckResult {
  const { status, reason } = evidence.claim_support
  const quoteExists = !(status === 'unsupported' && reason === QUOTE_NOT_FOUND_REASON)
  if (!quoteExists) return { quoteExists, outcome: 'rejected_missing_citation' }
  if (status === 'supports') return { quoteExists, outcome: 'accepted' }
  return { quoteExists, outcome: 'rejected_unsupported' }
}
