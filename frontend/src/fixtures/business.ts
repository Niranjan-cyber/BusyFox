import type { Business, FeedbackSummary } from '../types/entities'

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

/** Theme aggregation over PulseStack's own tickets and survey responses (§9.2). */
export const feedbackSummary: FeedbackSummary = {
  business_id: 'biz_pulsestack',
  run_id: 'run_fixture_01',
  total_items: 184,
  positive_count: 112,
  negative_count: 72,
  themes: [
    {
      id: 'thm_alert_precision',
      aspect: 'alert_noise',
      summary: 'Alerts fire on real incidents, not on noise',
      polarity: 'positive',
      mention_count: 41,
      representative_quote:
        'Three weeks in and every page we got was a real incident. Our previous tool trained us to ignore it.',
      representative_evidence_id: 'evd_101',
      retrieval_mode: 'demo_fixture',
    },
    {
      id: 'thm_setup_speed',
      aspect: 'onboarding',
      summary: 'First service is monitored within an afternoon',
      polarity: 'positive',
      mention_count: 33,
      representative_quote:
        'Had our API under monitoring before lunch. No agent install, no YAML archaeology.',
      representative_evidence_id: 'evd_102',
      retrieval_mode: 'demo_fixture',
    },
    {
      id: 'thm_slack_flow',
      aspect: 'slack_integration',
      summary: 'Slack thread per incident keeps the whole team in context',
      polarity: 'positive',
      mention_count: 24,
      representative_quote:
        'The per-incident Slack thread is the feature. Everyone sees the same timeline without anyone narrating it.',
      representative_evidence_id: 'evd_103',
      retrieval_mode: 'demo_fixture',
    },
    {
      id: 'thm_multi_service',
      aspect: 'multi_service_onboarding',
      summary: 'Adding services beyond the first is slow and manual',
      polarity: 'negative',
      mention_count: 29,
      representative_quote:
        'Service four took as long as service one. There is no way to clone a config or bulk-import.',
      representative_evidence_id: 'evd_104',
      retrieval_mode: 'demo_fixture',
    },
    {
      id: 'thm_dashboards',
      aspect: 'custom_dashboards',
      summary: 'No custom dashboards, so reporting happens in a spreadsheet',
      polarity: 'negative',
      mention_count: 22,
      representative_quote:
        'I export to CSV every Monday to build the view my CTO actually wants to see.',
      representative_evidence_id: 'evd_105',
      retrieval_mode: 'demo_fixture',
    },
    {
      id: 'thm_sso',
      aspect: 'sso',
      summary: 'No SSO blocks rollout past a certain team size',
      polarity: 'negative',
      mention_count: 14,
      representative_quote:
        'Security review stopped at SSO. We are stuck on two seats until that ships.',
      representative_evidence_id: 'evd_106',
      retrieval_mode: 'demo_fixture',
    },
    {
      id: 'thm_mobile',
      aspect: 'mobile_app',
      summary: 'On-call handoff is awkward away from a laptop',
      polarity: 'negative',
      mention_count: 7,
      representative_quote:
        'Acknowledging a page from my phone means loading the full web app on a 4G connection.',
      representative_evidence_id: 'evd_107',
      retrieval_mode: 'demo_fixture',
    },
  ],
}
