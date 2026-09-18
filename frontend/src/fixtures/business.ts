import type { Business, Signal } from '../types/entities'
import { summariseFeedback } from '../lib/viewModels'

/**
 * PulseStack — the simulated business from PRD §8.1 / §14.1.
 *
 * PulseStack itself is simulated (`is_simulated: true`, surfaced in the UI). Its named
 * competitors are real companies, so nothing here invents a claim about one of them (§3.3);
 * competitor material lives in evidence quotes with their sources attached.
 */
export const business: Business = {
  id: 'biz_pulsestack',
  name: 'PulseStack',
  is_simulated: true,
  scenario_id: 'pulsestack_v1',
  industry: 'developer_tools_observability',
  playbook_id: 'b2b_saas_it',
  icp: ['seed_to_series_a_startup', '3_15_engineer_team'],
  pricing: { starter_usd_month: 29, team_usd_month: 99 },
  current_mrr_usd: 8200,
  goal: { metric: 'mrr', change_usd: 15000, horizon_days: 90 },
  capabilities: [
    { key: 'slack_integration', confirmed: true },
    { key: 'on_call_paging', confirmed: true },
    { key: 'custom_dashboards', confirmed: false },
    { key: 'sso', confirmed: false },
  ],
  named_competitors: ['Sentry', 'Datadog', 'New Relic', 'Better Stack'],
  data_assets: ['asset_tickets_01', 'asset_survey_01'],
  created_at: '2026-09-17T10:00:00+05:30',
}

/**
 * Feedback signals over PulseStack's own tickets and survey responses (§9.2).
 *
 * `/businesses/{id}/feedback-summary` returns `Signal[]` (docs/contract.md:61) — there is no
 * separate "theme" entity, so each theme below is expanded into one Signal per mention and
 * grouped back into themes client-side by `summariseFeedback` (lib/viewModels.ts). Total/
 * positive/negative counts are therefore always exactly what the signals below sum to, not a
 * separately-asserted number.
 */
interface FeedbackThemeSeed {
  aspect: string
  polarity: Signal['polarity']
  claim_text: string
  evidence_id: string
  mention_count: number
}

const FEEDBACK_THEME_SEEDS: FeedbackThemeSeed[] = [
  {
    aspect: 'alert_noise',
    polarity: 'positive',
    claim_text:
      'Three weeks in and every page we got was a real incident. Our previous tool trained us to ignore it.',
    evidence_id: 'evd_101',
    mention_count: 41,
  },
  {
    aspect: 'onboarding',
    polarity: 'positive',
    claim_text: 'Had our API under monitoring before lunch. No agent install, no YAML archaeology.',
    evidence_id: 'evd_102',
    mention_count: 33,
  },
  {
    aspect: 'slack_integration',
    polarity: 'positive',
    claim_text:
      'The per-incident Slack thread is the feature. Everyone sees the same timeline without anyone narrating it.',
    evidence_id: 'evd_103',
    mention_count: 24,
  },
  {
    aspect: 'multi_service_onboarding',
    polarity: 'negative',
    claim_text: 'Service four took as long as service one. There is no way to clone a config or bulk-import.',
    evidence_id: 'evd_104',
    mention_count: 29,
  },
  {
    aspect: 'custom_dashboards',
    polarity: 'negative',
    claim_text: 'I export to CSV every Monday to build the view my CTO actually wants to see.',
    evidence_id: 'evd_105',
    mention_count: 22,
  },
  {
    aspect: 'sso',
    polarity: 'negative',
    claim_text: 'Security review stopped at SSO. We are stuck on two seats until that ships.',
    evidence_id: 'evd_106',
    mention_count: 14,
  },
  {
    aspect: 'mobile_app',
    polarity: 'negative',
    claim_text: 'Acknowledging a page from my phone means loading the full web app on a 4G connection.',
    evidence_id: 'evd_107',
    mention_count: 7,
  },
]

export const feedbackSignals: Signal[] = FEEDBACK_THEME_SEEDS.flatMap((seed, seedIndex) =>
  Array.from({ length: seed.mention_count }, (_, i) => ({
    id: `sig_feedback_${seedIndex}_${i}`,
    run_id: 'run_fixture_01',
    source_kind: 'owner_upload',
    aspect: seed.aspect,
    polarity: seed.polarity,
    claim_text: seed.claim_text,
    evidence_ids: [seed.evidence_id],
    produced_by: 'feedback_pipeline_agent',
  })),
)

export const feedbackSummary = summariseFeedback(feedbackSignals)
