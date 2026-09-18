import { describe, expect, it } from 'vitest'
import { derivePriority, goalCoverage, groupOpportunities } from './grouping'
import { opportunities } from '../../fixtures/opportunities'
import type { EvidenceConfidence, Opportunity } from '../../types/entities'

/**
 * The ranking rules are the one piece of real branching logic on screen 3, and they encode a
 * guardrail (`AGENTS.md`: no composite score, blocked items are not ranked against clear
 * ones). Tests exist here and not on the markup for that reason.
 */

function stub(id: string, priority: Opportunity['priority'], low: number, high: number) {
  return {
    ...opportunities[0],
    id,
    priority,
    value: { ...opportunities[0].value, monthly_usd: { low, high } },
  }
}

describe('derivePriority — PRD §13.1 rule table', () => {
  const cases: [EvidenceConfidence, boolean, string][] = [
    ['HIGH', false, 'High'],
    ['HIGH', true, 'Blocked'],
    ['MEDIUM', false, 'Medium'],
    ['MEDIUM', true, 'Blocked'],
    ['LOW', true, 'Blocked'],
    ['LOW', false, 'Low'],
  ]

  it.each(cases)('%s confidence, fix-first %s -> %s', (confidence, fixFirst, expected) => {
    expect(derivePriority(confidence, fixFirst)).toBe(expected)
  })

  it('never returns a numeric score', () => {
    for (const [confidence, fixFirst] of cases.map(([c, f]) => [c, f] as const)) {
      expect(typeof derivePriority(confidence, fixFirst)).toBe('string')
    }
  })
})

describe('groupOpportunities', () => {
  it('puts every fixture opportunity in exactly one section', () => {
    const sections = groupOpportunities(opportunities)
    const placed = sections.flatMap((section) => section.opportunities.map((o) => o.id))
    expect(placed).toHaveLength(opportunities.length)
    expect(new Set(placed).size).toBe(opportunities.length)
  })

  it('keeps blocked opportunities out of the ranked section', () => {
    const sections = groupOpportunities(opportunities)
    const ranked = sections.find((s) => s.key === 'high_confidence')!
    expect(ranked.opportunities.every((o) => o.priority === 'High')).toBe(true)

    const blocked = sections.find((s) => s.key === 'blocked')!
    expect(blocked.opportunities.every((o) => o.priority === 'Blocked')).toBe(true)
  })

  it('groups medium and low together under additional hypotheses', () => {
    const sections = groupOpportunities(opportunities)
    const hypotheses = sections.find((s) => s.key === 'hypotheses')!
    expect(hypotheses.opportunities.map((o) => o.priority).sort()).toEqual(['Low', 'Medium'])
  })

  it('breaks ties within a tier on the potential-value midpoint, highest first', () => {
    const sections = groupOpportunities([
      stub('opp_small', 'High', 1000, 2000),
      stub('opp_big', 'High', 8000, 12000),
      stub('opp_mid', 'High', 4000, 6000),
    ])
    const ranked = sections.find((s) => s.key === 'high_confidence')!
    expect(ranked.opportunities.map((o) => o.id)).toEqual(['opp_big', 'opp_mid', 'opp_small'])
  })

  it('returns every section even when one is empty, so the inbox keeps its shape', () => {
    const sections = groupOpportunities([])
    expect(sections.map((s) => s.key)).toEqual(['high_confidence', 'blocked', 'hypotheses'])
    expect(sections.every((s) => s.opportunities.length === 0)).toBe(true)
  })
})

describe('goalCoverage', () => {
  it('excludes blocked opportunities from the total', () => {
    const coverage = goalCoverage(
      [stub('a', 'High', 1000, 2000), stub('b', 'Blocked', 9000, 9000)],
      10_000,
    )
    expect(coverage.low).toBe(1000)
    expect(coverage.high).toBe(2000)
  })

  it('expresses coverage as a share of the goal gap', () => {
    const coverage = goalCoverage([stub('a', 'High', 3000, 15_000)], 15_000)
    expect(coverage.lowShare).toBeCloseTo(0.2)
    expect(coverage.highShare).toBeCloseTo(1)
  })

  it('does not divide by zero when no goal is set', () => {
    const coverage = goalCoverage([stub('a', 'High', 3000, 5000)], 0)
    expect(coverage.lowShare).toBe(0)
    expect(coverage.highShare).toBe(0)
  })
})
