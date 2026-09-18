import { renderToStaticMarkup } from 'react-dom/server'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { fetchBusiness, fetchFeedbackSignals, fetchInbox } from '../api/client'
import { OpportunityCard } from '../components/inbox/OpportunityCard'
import { PolaritySplitBar } from '../components/polarity/PolaritySplitBar'
import { ServedBanner } from '../components/common/ScreenState'
import { summariseFeedback } from '../lib/viewModels'
import { goalCoverage, groupOpportunities } from './Inbox/grouping'
import type { Business, Claim, Opportunity, Signal } from '../types/entities'

/**
 * Screens 1 and 3 against a real API payload.
 *
 * The bodies below are recorded verbatim from the deployed stage (README.md,
 * `https://vx59qs2osl.execute-api.eu-north-1.amazonaws.com`, recorded 2026-09-18) — including
 * `current_mrr_usd: 8200.0` and `starter_usd_month: 29.0`, which arrive as JSON floats rather
 * than the integers the fixtures use, and `evidence_ids: []` on the feedback signals. They are
 * here, inline and only in this test, so that nothing can mistake them for UI fixture data.
 *
 * The point of the test is the thing render tests against `src/fixtures/` cannot prove: that
 * the screens read a payload shaped by the Pydantic models rather than one shaped by whatever
 * the UI happened to want. The unit tests either side of it cover the client and the
 * components; this covers the seam.
 */

const LIVE_BUSINESS: Business = {
  id: 'biz_pulsestack',
  name: 'PulseStack',
  is_simulated: true,
  scenario_id: 'pulsestack_v1',
  industry: 'developer_tools_observability',
  playbook_id: 'b2b_saas_it',
  icp: ['seed_to_series_a_startup', '3_15_engineer_team'],
  pricing: { starter_usd_month: 29.0, team_usd_month: 99.0 },
  current_mrr_usd: 8200.0,
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

const LIVE_SIGNALS: Signal[] = [
  {
    id: 'sig_002',
    run_id: 'run_001',
    source_kind: 'simulated',
    aspect: 'onboarding',
    polarity: 'positive',
    claim_text:
      'PulseStack users repeatedly praise a 10-minute setup versus a full day for their previous tool.',
    evidence_ids: [],
    produced_by: 'feedback_pipeline',
  },
  {
    id: 'sig_003',
    run_id: 'run_001',
    source_kind: 'simulated',
    aspect: 'custom_dashboards',
    polarity: 'negative',
    claim_text:
      'Several PulseStack users ask for custom dashboards, currently unconfirmed as a capability.',
    evidence_ids: [],
    produced_by: 'feedback_pipeline',
  },
]

const LIVE_OPPORTUNITY: Opportunity = {
  id: 'opp_001',
  type: 'competitive_gap',
  claim_ids: ['claim_001', 'claim_002', 'claim_003', 'claim_004'],
  opportunity_mechanism: {
    statement:
      "Small engineering teams frustrated by alert noise can be targeted with PulseStack's low-noise positioning because PulseStack already serves teams of this exact size and profile.",
    shared_segment: '3-15 engineer teams',
    actionable_because: 'confirmed capability (low false-positive rate) + existing ICP overlap',
  },
  strengths_it_builds_on: [
    { signal_id: 'sig_002', reason: 'Low-noise onboarding experience already resonates with this ICP.' },
  ],
  pains_to_fix_first: [
    {
      signal_id: 'sig_001',
      reason: 'Alert fatigue is the named reason teams reconsider their vendor.',
      severity: 3,
    },
  ],
  competitive_context: [
    { signal_id: 'sig_001', competitor: 'Sentry', pattern: 'competitor_pain_business_strength' },
  ],
  evidence_diversity: {
    source_kind_count: 1,
    domain_count: 1,
    author_count: 2,
    underlying_event_risk: 'unknown',
  },
  evidence_confidence: 'HIGH',
  priority: 'High',
  value: {
    model: 'saas_arr',
    assumptions: [
      { key: 'signal_count', label: 'OBSERVED', description: "24 observed 'evaluating alternatives' mentions" },
      {
        key: 'estimated_qualified_accounts',
        label: 'ASSUMED',
        description: '1,200-3,600 — playbook multiplier applied to signal_count',
      },
      { key: 'expected_conversion', label: 'ASSUMED', description: '5% conversion assumption' },
      { key: 'ARPA', label: 'OBSERVED', description: "$99/month team plan, from the business's own pricing" },
    ],
    monthly_usd: { low: 5940.0, high: 17820.0 },
  },
}

const LIVE_CLAIMS: Claim[] = [
  {
    id: 'claim_001',
    opportunity_id: 'opp_001',
    type: 'why_this',
    text: '8 public discussions mention alert fatigue as a reason teams reconsider their monitoring vendor.',
    status: 'verified',
    evidence_ids: ['evd_001'],
  },
  {
    id: 'claim_002',
    opportunity_id: 'opp_001',
    type: 'why_you',
    text: 'PulseStack already serves teams of this exact size and profile with a confirmed low-noise capability.',
    status: 'verified',
    evidence_ids: ['evd_001'],
  },
  {
    id: 'claim_003',
    opportunity_id: 'opp_001',
    type: 'why_now',
    text: "A named competitor's recent pricing change is visible in 8 public discussions in the last 45 days.",
    status: 'verified',
    evidence_ids: ['evd_002'],
  },
  {
    id: 'claim_004',
    opportunity_id: 'opp_001',
    type: 'mechanism',
    text: "Small engineering teams frustrated by alert noise can be targeted with PulseStack's low-noise positioning.",
    status: 'verified',
    evidence_ids: ['evd_001', 'evd_002'],
  },
]

const BASE = 'https://vx59qs2osl.execute-api.eu-north-1.amazonaws.com'

/** Answers the four contract routes with the recorded bodies. `mode` is the header the API is
    expected to send once a handler sets it; `undefined` is what it sends today. */
function stubDeployedApi(mode?: string) {
  vi.stubEnv('VITE_API_BASE_URL', BASE)
  vi.stubGlobal('fetch', async (url: string) => {
    const body = url.endsWith('/feedback-summary')
      ? LIVE_SIGNALS
      : url.endsWith('/opportunities')
        ? [LIVE_OPPORTUNITY]
        : url.endsWith('/claims')
          ? LIVE_CLAIMS
          : LIVE_BUSINESS
    return new Response(JSON.stringify(body), {
      status: 200,
      headers: mode === undefined ? {} : { 'X-Retrieval-Mode': mode },
    })
  })
}

afterEach(() => {
  vi.unstubAllGlobals()
  vi.unstubAllEnvs()
})

describe('screen 1 on a live payload', () => {
  it('renders the business profile the API actually returns', async () => {
    stubDeployedApi('live')

    const profile = await fetchBusiness('biz_pulsestack')

    expect(profile.retrieval_mode).toBe('live')
    expect(profile.data.name).toBe('PulseStack')
    // Floats from Pydantic, not the integers the fixtures happen to use.
    expect(profile.data.current_mrr_usd).toBe(8200)
    expect(profile.data.capabilities.filter((c) => c.confirmed)).toHaveLength(2)
  })

  it('splits live feedback signals by polarity and states both counts', async () => {
    stubDeployedApi('live')

    const feedback = await fetchFeedbackSignals('biz_pulsestack')
    const summary = summariseFeedback(feedback.data)

    expect(summary.total_items).toBe(2)
    expect(summary.positive_count).toBe(1)
    expect(summary.negative_count).toBe(1)
    expect(summary.themes.map((theme) => theme.aspect)).toEqual(['onboarding', 'custom_dashboards'])

    const html = renderToStaticMarkup(
      <PolaritySplitBar positive={summary.positive_count} negative={summary.negative_count} />,
    )
    expect(html).toContain('1 of 2 labelled feedback items are positive, 1 are negative')
    expect(html).toContain('2 labelled items')
  })

  it('labels a live payload live and a fallback demo fixture, never the other way round', async () => {
    stubDeployedApi('live')
    const live = await fetchBusiness('biz_pulsestack')

    vi.stubGlobal('fetch', async () => new Response('{}', { status: 503 }))
    const fellBack = await fetchFeedbackSignals('biz_pulsestack')

    const html = renderToStaticMarkup(
      <ServedBanner
        sources={[
          { label: 'Business profile', served: live },
          { label: 'Customer feedback', served: fellBack },
        ]}
      />,
    )
    expect(html).toContain('LIVE RESEARCH')
    expect(html).toContain('DEMO FIXTURE')
    expect(html).toContain('503')
    expect(fellBack.retrieval_mode).toBe('demo_fixture')
  })
})

describe('screen 3 on a live payload', () => {
  it('pairs each live opportunity with the claims the contract route returns for it', async () => {
    stubDeployedApi('live')

    const inbox = await fetchInbox('biz_pulsestack')

    expect(inbox.retrieval_mode).toBe('live')
    expect(inbox.data.opportunities.map((o) => o.id)).toEqual(['opp_001'])
    expect(inbox.data.claims.map((c) => c.type)).toEqual([
      'why_this',
      'why_you',
      'why_now',
      'mechanism',
    ])
  })

  it('groups and ranks by the priority the Quality Gate assigned, without recomputing it', async () => {
    stubDeployedApi('live')

    const inbox = await fetchInbox('biz_pulsestack')
    const sections = groupOpportunities(inbox.data.opportunities)
    const placed = sections.filter((section) => section.opportunities.length > 0)

    // §13.1: priority is the gate's output, not something the inbox derives. Whatever the API
    // says, the card lands in that tier — the frontend must not quietly re-rank the backend.
    expect(placed).toHaveLength(1)
    expect(placed[0].key).toBe('high_confidence')
    expect(placed[0].opportunities[0].priority).toBe('High')
  })

  it('counts the live value range against the live goal', async () => {
    stubDeployedApi('live')

    const inbox = await fetchInbox('biz_pulsestack')
    const profile = await fetchBusiness('biz_pulsestack')
    const coverage = goalCoverage(inbox.data.opportunities, profile.data.goal.change_usd)

    expect(coverage.low).toBe(5940)
    expect(coverage.high).toBe(17820)
    expect(coverage.lowShare).toBeCloseTo(0.396, 3)
  })

  it('renders a live opportunity card with its claims, three separate readings and no score', async () => {
    stubDeployedApi('live')

    const inbox = await fetchInbox('biz_pulsestack')
    const html = renderToStaticMarkup(
      <OpportunityCard
        opportunity={inbox.data.opportunities[0]}
        claims={inbox.data.claims}
      />,
    )

    for (const heading of ['Why this', 'Why you', 'Why now', 'Mechanism']) {
      expect(html).toContain(heading)
    }
    expect(html).toContain('OBSERVED')
    expect(html).toContain('INFERRED')
    expect(html).toContain('High priority')
    expect(html).toContain('Evidence confidence')
    expect(html).toContain('Potential value')
    expect(html).toContain('ASSUMED')
    expect(html).toContain('alert fatigue')
    expect(html.toLowerCase()).not.toMatch(/score[:\s]/)
  })

  it('falls back to the whole fixture inbox when the live list is unreachable', async () => {
    vi.stubEnv('VITE_API_BASE_URL', BASE)
    vi.stubGlobal('fetch', async () => {
      throw new TypeError('Failed to fetch')
    })

    const inbox = await fetchInbox('biz_pulsestack')

    expect(inbox.retrieval_mode).toBe('demo_fixture')
    expect(inbox.data.opportunities.length).toBeGreaterThan(0)
    // Fixture opportunities keep their fixture claims: every card still has all four.
    for (const opportunity of inbox.data.opportunities) {
      const types = inbox.data.claims
        .filter((claim) => claim.opportunity_id === opportunity.id)
        .map((claim) => claim.type)
      expect(types).toHaveLength(4)
    }
  })
})

describe('the provenance header the deployed API does not send yet', () => {
  it('reports every payload undeclared, and the banner claims no level for them', async () => {
    stubDeployedApi(undefined)

    const profile = await fetchBusiness('biz_pulsestack')
    const inbox = await fetchInbox('biz_pulsestack')

    expect(profile.retrieval_mode).toBe('undeclared')
    expect(inbox.retrieval_mode).toBe('undeclared')

    const html = renderToStaticMarkup(
      <ServedBanner
        sources={[
          { label: 'Business profile', served: profile },
          { label: 'Opportunities and claims', served: inbox },
        ]}
      />,
    )
    expect(html).toContain('PROVENANCE NOT STATED')
    expect(html).not.toContain('LIVE RESEARCH')
    expect(html).not.toContain('CACHED VERIFIED SOURCE')
    expect(html).not.toContain('DEMO FIXTURE')
  })
})
