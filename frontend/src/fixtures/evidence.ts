import { claims } from './opportunities'
import type { Evidence } from '../types/entities'

/**
 * Fixture Evidence for screen 4's evidence chain and Evidence Check diagram.
 *
 * Covers every `evidence_ids` entry the claims fixture (`./opportunities.ts`) references.
 * Deliberately includes the two reject shapes §21's demo beat (1:35-1:55) names alongside the
 * accept case, so the diagram has real reject data to walk even when no backend is configured:
 * `evd_023` fails quote-exists (the exact "quote not found in source text" string
 * `backend/pipeline/evidence_check.py::build_evidence` emits, so the same status/reason pair a
 * live run would send); `evd_031` passes quote-exists but fails the semantic-support check.
 * Everything else supports its claim, matching the `verified` status those claims already carry.
 */

function evidence(partial: Omit<Evidence, 'quote_hash' | 'retrieval_mode'>): Evidence {
  return { ...partial, retrieval_mode: 'demo_fixture', quote_hash: `sha256:fixture-${partial.id}` }
}

const EVIDENCE_BY_ID: Record<string, Evidence> = Object.fromEntries(
  [
    evidence({
      id: 'evd_001',
      source_document_id: 'src_hn_001',
      source_kind: 'hn',
      url: 'https://news.ycombinator.com/item?id=41000001',
      retrieved_at: '2026-09-18T09:12:00+05:30',
      author: 'hn_user_412',
      published_at: '2026-08-30T00:00:00Z',
      quote: 'we moved our alert rules three times this quarter and still get paged for noise',
      claim_support: { status: 'supports', confidence: 0.91, reason: 'Directly names alert noise as an ongoing, unresolved pain.' },
      freshness: { status: 'fresh', age_days: 23, limit_days: 180 },
    }),
    evidence({
      id: 'evd_002',
      source_document_id: 'src_hn_002',
      source_kind: 'hn',
      url: 'https://news.ycombinator.com/item?id=41000002',
      retrieved_at: '2026-09-18T09:13:00+05:30',
      author: 'hn_user_889',
      published_at: '2026-09-02T00:00:00Z',
      quote: "the pricing change pushed us to look at alternatives this quarter",
      claim_support: { status: 'supports', confidence: 0.88, reason: 'States a pricing-driven evaluation of alternatives.' },
      freshness: { status: 'fresh', age_days: 16, limit_days: 90 },
    }),
    evidence({
      id: 'evd_003',
      source_document_id: 'src_hn_003',
      source_kind: 'hn',
      url: 'https://news.ycombinator.com/item?id=41000003',
      retrieved_at: '2026-09-18T09:14:00+05:30',
      author: 'hn_user_205',
      published_at: '2026-08-20T00:00:00Z',
      quote: 'switched vendors after the tier restructure doubled our bill overnight',
      claim_support: { status: 'supports', confidence: 0.9, reason: 'Names the same pricing change as the reason for switching.' },
      freshness: { status: 'fresh', age_days: 30, limit_days: 90 },
    }),
    evidence({
      id: 'evd_004',
      source_document_id: 'src_web_004',
      source_kind: 'web_public',
      url: 'https://example-forum.dev/t/monitoring-alternatives/42',
      retrieved_at: '2026-09-18T09:15:00+05:30',
      author: 'forum_user_7',
      published_at: '2026-08-25T00:00:00Z',
      quote: 'the team is actively trialling two smaller monitoring vendors this month',
      claim_support: { status: 'supports', confidence: 0.82, reason: 'Confirms an active evaluation of alternatives, matching the claim.' },
      freshness: { status: 'fresh', age_days: 25, limit_days: 180 },
    }),
    evidence({
      id: 'evd_011',
      source_document_id: 'src_hn_011',
      source_kind: 'hn',
      url: 'https://news.ycombinator.com/item?id=41000011',
      retrieved_at: '2026-09-18T09:20:00+05:30',
      author: 'hn_user_120',
      published_at: '2026-08-10T00:00:00Z',
      quote: 'no incumbent tool to migrate off of, so we picked whatever set up fastest',
      claim_support: { status: 'supports', confidence: 0.87, reason: 'Directly describes choosing a first monitoring tool with no migration cost.' },
      freshness: { status: 'fresh', age_days: 40, limit_days: 180 },
    }),
    evidence({
      id: 'evd_012',
      source_document_id: 'src_hn_012',
      source_kind: 'hn',
      url: 'https://news.ycombinator.com/item?id=41000012',
      retrieved_at: '2026-09-18T09:21:00+05:30',
      author: 'hn_user_301',
      published_at: '2026-08-05T00:00:00Z',
      quote: 'took us most of a day just to get the first service reporting anything useful',
      claim_support: { status: 'supports', confidence: 0.85, reason: 'Names setup friction on a competing tool.' },
      freshness: { status: 'fresh', age_days: 45, limit_days: 180 },
    }),
    evidence({
      id: 'evd_013',
      source_document_id: 'src_hn_013',
      source_kind: 'hn',
      url: 'https://news.ycombinator.com/item?id=41000013',
      retrieved_at: '2026-09-18T09:22:00+05:30',
      author: 'hn_user_552',
      published_at: '2026-08-18T00:00:00Z',
      quote: 'the onboarding wizard alone took longer than our actual migration did',
      claim_support: { status: 'supports', confidence: 0.83, reason: 'Names onboarding friction on a competing tool.' },
      freshness: { status: 'fresh', age_days: 32, limit_days: 180 },
    }),
    evidence({
      id: 'evd_021',
      source_document_id: 'src_web_021',
      source_kind: 'web_public',
      url: 'https://example-forum.dev/t/starter-plan-value/9',
      retrieved_at: '2026-09-18T09:25:00+05:30',
      author: 'forum_user_3',
      published_at: '2026-07-15T00:00:00Z',
      quote: 'the Starter plan is genuinely good value, we just wish there was something between it and Team',
      claim_support: { status: 'supports', confidence: 0.86, reason: 'Praises the Starter tier while naming the pricing-ceiling objection.' },
      freshness: { status: 'fresh', age_days: 66, limit_days: 90 },
    }),
    evidence({
      id: 'evd_022',
      source_document_id: 'src_web_022',
      source_kind: 'web_public',
      url: 'https://example-forum.dev/t/starter-plan-value/11',
      retrieved_at: '2026-09-18T09:26:00+05:30',
      author: 'forum_user_18',
      published_at: '2026-06-30T00:00:00Z',
      quote: 'for the price, the Starter plan does everything a five-person team needs',
      claim_support: { status: 'supports', confidence: 0.8, reason: 'Directly calls the Starter plan good value.' },
      freshness: { status: 'stale', age_days: 81, limit_days: 90 },
    }),
    evidence({
      id: 'evd_023',
      source_document_id: 'src_web_023',
      source_kind: 'web_public',
      url: 'https://example-forum.dev/t/competitor-tier-launch/2',
      retrieved_at: '2026-09-18T09:27:00+05:30',
      author: 'forum_user_44',
      published_at: '2026-09-01T00:00:00Z',
      // Deliberately does not appear in this evidence item's own source text (the source page
      // covers something else) — the exact rejection Task 18's quote-exists check produces.
      quote: 'they just launched a mid tier between Starter and Team',
      claim_support: { status: 'unsupported', confidence: 0.0, reason: 'quote not found in source text' },
      freshness: { status: 'fresh', age_days: 18, limit_days: 90 },
    }),
    evidence({
      id: 'evd_031',
      source_document_id: 'src_hn_031',
      source_kind: 'hn',
      url: 'https://news.ycombinator.com/item?id=41000031',
      retrieved_at: '2026-09-18T09:30:00+05:30',
      author: 'hn_user_777',
      published_at: '2021-04-02T00:00:00Z',
      // Quote exists verbatim in the source, but is about on-call load generally rather than
      // the tool-choice claim it is cited for — the semantic-support failure mode, not a
      // missing citation.
      quote: 'on-call is exhausting no matter which vendor you pick',
      claim_support: {
        status: 'unsupported',
        confidence: 0.2,
        reason: 'Quote describes on-call burden in general, not that engineers choosing their own tools respond to it.',
      },
      freshness: { status: 'stale', age_days: 1996, limit_days: 180 },
    }),
    evidence({
      id: 'evd_101',
      source_document_id: 'src_sim_101',
      source_kind: 'simulated',
      url: 'https://pulsestack.internal/feedback/101',
      retrieved_at: '2026-09-18T09:05:00+05:30',
      published_at: '2026-09-10T00:00:00Z',
      quote: 'alert precision here is the best of any tool we have tried',
      claim_support: { status: 'supports', confidence: 0.94, reason: 'Directly praises alert precision, the strength the claim cites.' },
      freshness: { status: 'fresh', age_days: 8, limit_days: 90 },
    }),
    evidence({
      id: 'evd_102',
      source_document_id: 'src_sim_102',
      source_kind: 'simulated',
      url: 'https://pulsestack.internal/feedback/102',
      retrieved_at: '2026-09-18T09:06:00+05:30',
      published_at: '2026-09-05T00:00:00Z',
      quote: 'had our first service monitored within the hour, no complaints',
      claim_support: { status: 'supports', confidence: 0.9, reason: 'Directly praises fast setup, matching the claim.' },
      freshness: { status: 'fresh', age_days: 13, limit_days: 90 },
    }),
    evidence({
      id: 'evd_104',
      source_document_id: 'src_sim_104',
      source_kind: 'simulated',
      url: 'https://pulsestack.internal/feedback/104',
      retrieved_at: '2026-09-18T09:07:00+05:30',
      published_at: '2026-08-28T00:00:00Z',
      quote: 'adding a second service meant redoing the whole setup by hand',
      claim_support: { status: 'supports', confidence: 0.89, reason: 'Directly names manual per-service setup as the blocker the claim describes.' },
      freshness: { status: 'fresh', age_days: 22, limit_days: 90 },
    }),
  ].map((item) => [item.id, item]),
)

/** Evidence for one claim, in the order its `evidence_ids` list them. Unknown ids are dropped
    rather than substituted — an evidence item this fixture set never claimed to describe. */
export function evidenceForClaim(claimId: string): Evidence[] {
  const claim = claims.find((c) => c.id === claimId)
  if (!claim) return []
  return claim.evidence_ids.map((id) => EVIDENCE_BY_ID[id]).filter((item): item is Evidence => item !== undefined)
}
