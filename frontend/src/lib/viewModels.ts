import type {
  Claim,
  ClaimType,
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
