import type { ExecutionPack } from '../types/entities'

/**
 * Fixture ExecutionPack for screen 5 (§16.1). Its outreach draft cites `sig_311`, the same
 * strength `opp_07`'s `strengths_it_builds_on` already names (`./opportunities.ts`) — so the
 * "clickable back to its source signal" acceptance criterion has a real cross-reference to
 * point at rather than an invented id.
 */
const EXECUTION_PACKS: ExecutionPack[] = [
  {
    id: 'pack_opp_07',
    opportunity_id: 'opp_07',
    offer: 'A 14-day PulseStack trial pre-configured with low-noise alerting defaults.',
    proposal:
      'Migrate your alert rules from your current tool in under a day; keep the on-call paging you already rely on.',
    outreach_drafts: [
      {
        channel: 'email',
        draft:
          'Teams your size often tell us alert noise is the #1 reason they look elsewhere. PulseStack was built for exactly that.',
        proof_point_signal_id: 'sig_311',
        outreach_policy_checked: true,
      },
    ],
    status: 'draft',
  },
]

/** One pack per opportunity; falls back to the first when the id is unknown — same fallback
    convention as `fetchOpportunity` (`api/client.ts`). */
export function executionPackFor(opportunityId: string): ExecutionPack {
  return EXECUTION_PACKS.find((pack) => pack.opportunity_id === opportunityId) ?? EXECUTION_PACKS[0]
}
