import type { EvidenceConfidence, Opportunity, Priority } from '../../types/entities'

/**
 * The inbox's ranking rules (PRD §13.1, §1.3).
 *
 * §13.1 is emphatic that priority is a decision table and not arithmetic, so it is written
 * here as a table. There is deliberately no formula, no weighting and no composite score for
 * anyone to re-derive.
 */

/** §13.1's rule table, applied exactly as printed in the PRD. */
export function derivePriority(
  confidence: EvidenceConfidence,
  fixFirstFlag: boolean,
): Priority {
  if (fixFirstFlag) return 'Blocked'
  if (confidence === 'HIGH') return 'High'
  if (confidence === 'MEDIUM') return 'Medium'
  return 'Low'
}

export type SectionKey = 'high_confidence' | 'blocked' | 'hypotheses'

export interface InboxSection {
  key: SectionKey
  title: string
  description: string
  opportunities: Opportunity[]
}

/**
 * Which of §1.3's sections a priority belongs to.
 *
 * §13.1 assigns High to the ranked list and LOW to "additional hypotheses", but does not say
 * where MEDIUM goes — §1.3's mock-up only shows four sections. Medium is grouped with Low
 * under "additional hypotheses (lower confidence)", because that header's own words describe
 * it and the alternative would put medium-confidence items under a heading that says
 * "high-confidence". Worth confirming at stand-up; it is a PRD gap, not a preference.
 */
function sectionFor(priority: Priority): SectionKey {
  if (priority === 'Blocked') return 'blocked'
  if (priority === 'High') return 'high_confidence'
  return 'hypotheses'
}

/** Ties within a tier break on the potential-value midpoint, shown but never hidden (§13.1). */
function valueMidpoint(opportunity: Opportunity): number {
  return (opportunity.value.monthly_usd.low + opportunity.value.monthly_usd.high) / 2
}

const SECTION_ORDER: { key: SectionKey; title: string; description: string }[] = [
  {
    key: 'high_confidence',
    title: 'High-confidence opportunities',
    description: 'Evidence cleared the bar and nothing has to be fixed first.',
  },
  {
    key: 'blocked',
    title: 'Blocked by a product issue first',
    description:
      'The evidence holds, but a product gap sits in the path. Shown separately rather than ranked against the clear ones.',
  },
  {
    key: 'hypotheses',
    title: 'Additional hypotheses',
    description: 'Lower evidence confidence. Worth testing, not worth betting the quarter on.',
  },
]

export function groupOpportunities(opportunities: Opportunity[]): InboxSection[] {
  const buckets: Record<SectionKey, Opportunity[]> = {
    high_confidence: [],
    blocked: [],
    hypotheses: [],
  }

  for (const opportunity of opportunities) {
    buckets[sectionFor(opportunity.priority)].push(opportunity)
  }

  for (const key of Object.keys(buckets) as SectionKey[]) {
    buckets[key].sort((a, b) => valueMidpoint(b) - valueMidpoint(a))
  }

  return SECTION_ORDER.map((section) => ({ ...section, opportunities: buckets[section.key] }))
}

/**
 * Goal coverage: the selected opportunities' monthly value range against the goal gap.
 *
 * KNOWN SPEC CONFLICT, flagged rather than silently resolved. §13.2 defines goal coverage as
 * "sum of low/high monthly value × 3 (a 90-day horizon) ÷ goal gap", but §1.3's inbox mock-up
 * compares the monthly sums to the $15k MRR goal directly, with no ×3 ($6.5k + $4.1k against
 * a $15k goal). The two disagree, and ×3 is also dimensionally odd: the goal is stated as a
 * monthly rate (MRR), so multiplying a monthly rate by three months and comparing it to a
 * monthly target overstates coverage threefold.
 *
 * This implements §1.3 — the screen this code renders — and needs a ruling at stand-up.
 *
 * Blocked opportunities are excluded either way: counting revenue that sits behind a known
 * blocker towards the goal is exactly the flattering arithmetic this product exists to avoid.
 */
export function goalCoverage(
  opportunities: Opportunity[],
  goalChangeUsd: number,
): { low: number; high: number; lowShare: number; highShare: number } {
  const counted = opportunities.filter((opportunity) => opportunity.priority !== 'Blocked')
  const low = counted.reduce((sum, o) => sum + o.value.monthly_usd.low, 0)
  const high = counted.reduce((sum, o) => sum + o.value.monthly_usd.high, 0)
  return {
    low,
    high,
    lowShare: goalChangeUsd === 0 ? 0 : low / goalChangeUsd,
    highShare: goalChangeUsd === 0 ? 0 : high / goalChangeUsd,
  }
}
