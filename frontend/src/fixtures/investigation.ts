import type { Signal } from '../types/entities'
import { feedbackSignals } from './business'

/**
 * Market and Competitive lane signals for screen 2 (PRD §16.1).
 *
 * `business.ts`'s `feedbackSignals` already covers the Feedback lane (real fixture data, used
 * by screen 1 too); these two are new because no fixture previously needed `market_agent` or
 * `competitor_agent` output on its own. IDs are unreferenced elsewhere — `strengths_it_builds_on`
 * / `competitive_context` signal_ids on the inbox fixtures (`opportunities.ts`) are display text,
 * never resolved against a Signal list (see `OpportunityCard.tsx`).
 */
const marketSignals: Signal[] = [
  {
    id: 'sig_market_01',
    run_id: 'run_fixture_01',
    source_kind: 'hn',
    aspect: 'alert_noise',
    polarity: 'negative',
    claim_text: '7 public discussions in the last 60 days mention teams reconsidering monitoring costs.',
    evidence_ids: ['evd_001'],
    produced_by: 'market_agent',
  },
  {
    id: 'sig_market_02',
    run_id: 'run_fixture_01',
    source_kind: 'github',
    aspect: 'sso',
    polarity: 'negative',
    claim_text: 'Open issues across several observability tools ask for SSO before their security review will pass.',
    evidence_ids: ['evd_004'],
    produced_by: 'market_agent',
  },
  {
    id: 'sig_market_03',
    run_id: 'run_fixture_01',
    source_kind: 'web_public',
    aspect: 'pricing_pain',
    polarity: 'negative',
    claim_text: 'A recent competitor pricing change is visible in 8 public discussions in the last 45 days.',
    evidence_ids: ['evd_002', 'evd_003'],
    produced_by: 'market_agent',
  },
]

const competitiveSignals: Signal[] = [
  {
    id: 'sig_competitive_01',
    run_id: 'run_fixture_01',
    source_kind: 'web_public',
    aspect: 'alert_noise',
    polarity: 'negative',
    claim_text: 'Alert fatigue appears repeatedly in public discussions among users of several monitoring tools.',
    evidence_ids: ['evd_001'],
    produced_by: 'competitor_agent',
  },
  {
    id: 'sig_competitive_02',
    run_id: 'run_fixture_01',
    source_kind: 'app_store',
    aspect: 'setup_friction',
    polarity: 'negative',
    claim_text: 'Setup friction on two competing tools is discussed in 6 threads from the last 60 days.',
    evidence_ids: ['evd_012', 'evd_013'],
    produced_by: 'competitor_agent',
  },
]

/**
 * `feedbackSignals` expands each theme into one entry per mention (170 items) for §1's polarity
 * counting — correct there, but rendering 170 near-identical cards on screen 2's per-signal
 * list would be noise, not signal. One representative per theme keeps this lane's scale
 * consistent with the Market/Competitive lanes above.
 */
function representativeFeedbackSignals(): Signal[] {
  const seen = new Set<string>()
  return feedbackSignals.filter((signal) => {
    const key = `${signal.aspect}::${signal.polarity}`
    if (seen.has(key)) return false
    seen.add(key)
    return true
  })
}

export const investigationSignals: Signal[] = [
  ...marketSignals,
  ...representativeFeedbackSignals(),
  ...competitiveSignals,
]
