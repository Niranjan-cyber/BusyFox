import { describe, expect, it } from 'vitest'
import { feedbackSummary } from './business'
import { claims, opportunities } from './opportunities'
import { derivePriority } from '../screens/Inbox/grouping'
import type { ResearchAgentOutput } from '../types/entities'

/**
 * The four guardrails in AGENTS.md, as tests.
 *
 * These are the rules that "end the project outright if violated", so they get a test rather
 * than a convention. They check the data the UI actually renders, which is where a violation
 * would reach a judge.
 */

describe('no composite opportunity score (§13.1)', () => {
  const forbidden = ['score', 'opportunity_score', 'score_breakdown', 'composite', 'weighted']

  it.each(opportunities)('$id carries no score-shaped field', (opportunity) => {
    const keys = Object.keys(opportunity).map((key) => key.toLowerCase())
    for (const term of forbidden) {
      expect(keys.some((key) => key.includes(term))).toBe(false)
    }
  })

  it('keeps evidence confidence, priority and value as three separate fields', () => {
    for (const opportunity of opportunities) {
      expect(opportunity.evidence_confidence).toBeDefined()
      expect(opportunity.priority).toBeDefined()
      expect(opportunity.value.monthly_usd).toBeDefined()
    }
  })

  it('derives every fixture priority from the rule table, not from a computation', () => {
    for (const opportunity of opportunities) {
      expect(opportunity.priority).toBe(
        derivePriority(opportunity.evidence_confidence, opportunity.fix_first_flag),
      )
    }
  })
})

describe('value estimates survive being checked by hand (§13.2)', () => {
  it.each(opportunities)('$id monthly range matches its own assumptions', (opportunity) => {
    const { assumptions, monthly_usd } = opportunity.value
    const low =
      assumptions.estimated_qualified_accounts.low *
      assumptions.expected_conversion *
      assumptions.arpa_usd
    const high =
      assumptions.estimated_qualified_accounts.high *
      assumptions.expected_conversion *
      assumptions.arpa_usd
    // The card prints these inputs beside the range, so a reader can redo the arithmetic.
    // It has to come out to the number shown.
    expect(monthly_usd.low).toBe(Math.round(low))
    expect(monthly_usd.high).toBe(Math.round(high))
  })

  it('never shows a bare point value', () => {
    for (const opportunity of opportunities) {
      expect(opportunity.value.monthly_usd.high).toBeGreaterThan(opportunity.value.monthly_usd.low)
    }
  })
})

describe('every claim reaching the UI is labelled (§13.3)', () => {
  it.each(claims)('$id is Observed, Inferred or Assumed', (claim) => {
    expect(['OBSERVED', 'INFERRED', 'ASSUMED']).toContain(claim.label)
  })

  it('gives every opportunity all four claim types (§14.8)', () => {
    for (const opportunity of opportunities) {
      const types = claims
        .filter((claim) => claim.opportunity_id === opportunity.id)
        .map((claim) => claim.type)
        .sort()
      expect(types).toEqual(['mechanism', 'why_now', 'why_this', 'why_you'])
    }
  })

  it('resolves every claim_id on an opportunity to a real claim', () => {
    const byId = new Set(claims.map((claim) => claim.id))
    for (const opportunity of opportunities) {
      for (const claimId of opportunity.claim_ids) {
        expect(byId.has(claimId)).toBe(true)
      }
    }
  })
})

describe('every source is labelled with its retrieval level (§7.2)', () => {
  it.each(feedbackSummary.themes)('$id states how it was retrieved', (theme) => {
    expect(['live', 'cached', 'demo_fixture']).toContain(theme.retrieval_mode)
  })
})

describe('research agents emit signals only (§10.1a)', () => {
  it('rejects an opportunities field structurally, not by convention', () => {
    const output: ResearchAgentOutput = { signals: [], truncated: false }
    expect(output.signals).toEqual([])

    // @ts-expect-error — research-agent output must be structurally incapable of carrying
    // opportunities. If this line ever stops erroring, the guarantee has been lost.
    const violation: ResearchAgentOutput = { signals: [], truncated: false, opportunities: [] }
    expect(violation).toBeDefined()
  })
})

describe('every opportunity states its mechanism (§9.5)', () => {
  it.each(opportunities)('$id has a non-empty mechanism statement', (opportunity) => {
    expect(opportunity.opportunity_mechanism.statement.length).toBeGreaterThan(0)
    expect(opportunity.opportunity_mechanism.shared_segment.length).toBeGreaterThan(0)
    expect(opportunity.opportunity_mechanism.actionable_because.length).toBeGreaterThan(0)
  })
})
