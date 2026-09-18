import type { Claim, Opportunity, RejectedIdea } from '../types/entities'

/**
 * Fixture inbox for PulseStack (PRD §1.3, §1.4, §14.8).
 *
 * Covers every section screen 3 has to render: two High, one Blocked (HIGH evidence plus a
 * fix-first flag, per the §13.1 rule table), one Medium, one Low, and two rejected ideas.
 * `opp_07` reproduces the worked value example from §13.2 exactly — 1,200-3,600 accounts at
 * 5% conversion on a $99 plan gives $5,940-$17,820/mo — so the arithmetic on screen can be
 * checked by hand against the PRD.
 *
 * Note there is no score field on any of these, by design (§13.1).
 */
export const opportunities: Opportunity[] = [
  {
    id: 'opp_07',
    type: 'competitive_gap',
    title: 'Capture teams migrating away from heavyweight monitoring platforms',
    claim_ids: ['claim_0701', 'claim_0702', 'claim_0703', 'claim_0704'],
    opportunity_mechanism: {
      statement:
        'Small engineering teams frustrated by alert noise can be targeted with PulseStack low-noise positioning because PulseStack already serves teams of this exact size and profile.',
      shared_segment: '3-15 engineer teams',
      actionable_because: 'confirmed capability (low false-positive rate) + existing ICP overlap',
    },
    strengths_it_builds_on: [
      { signal_id: 'sig_311', reason: 'Alert precision is the most-praised theme in own feedback' },
    ],
    pains_to_fix_first: [],
    competitive_context: [
      {
        signal_id: 'sig_204',
        competitor: 'Datadog',
        pattern: 'competitor_pain_business_strength',
      },
    ],
    evidence_diversity: {
      source_kind_count: 3,
      domain_count: 4,
      author_count: 6,
      underlying_event_risk: 'unknown',
    },
    evidence_confidence: 'HIGH',
    fix_first_flag: false,
    priority: 'High',
    value: {
      model: 'saas_arr',
      assumptions: {
        signal_count: 24,
        estimated_qualified_accounts: { low: 1200, high: 3600 },
        expected_conversion: 0.05,
        arpa_usd: 99,
      },
      monthly_usd: { low: 5940, high: 17820 },
    },
    what_to_do: 'Target engineering teams publicly evaluating alternatives.',
    fit: [
      { key: 'slack_integration', label: 'Slack integration' },
      { key: 'on_call_paging', label: 'On-call paging' },
      { key: 'starter_plan', label: '$29 starter plan' },
      { key: 'icp_match', label: '3-15 engineer ICP' },
    ],
  },
  {
    id: 'opp_11',
    type: 'segment_expansion',
    title: 'Target seed-stage startups setting up monitoring for the first time',
    claim_ids: ['claim_1101', 'claim_1102', 'claim_1103', 'claim_1104'],
    opportunity_mechanism: {
      statement:
        'Teams standing up their first monitoring stack can be reached with a same-afternoon setup promise because onboarding speed is PulseStack most-corroborated strength.',
      shared_segment: 'seed-stage teams with no incumbent tool',
      actionable_because: 'observed setup-time praise + no migration cost for the buyer',
    },
    strengths_it_builds_on: [
      { signal_id: 'sig_312', reason: 'Setup speed praised across 33 feedback items' },
    ],
    pains_to_fix_first: [],
    competitive_context: [
      { signal_id: 'sig_212', competitor: 'New Relic', pattern: 'competitor_setup_friction' },
    ],
    evidence_diversity: {
      source_kind_count: 3,
      domain_count: 3,
      author_count: 5,
      underlying_event_risk: 'low',
    },
    evidence_confidence: 'HIGH',
    fix_first_flag: false,
    priority: 'High',
    value: {
      model: 'saas_arr',
      assumptions: {
        signal_count: 17,
        estimated_qualified_accounts: { low: 850, high: 1190 },
        expected_conversion: 0.05,
        arpa_usd: 99,
      },
      monthly_usd: { low: 4208, high: 5891 },
    },
    what_to_do: 'Run a first-monitoring-stack onboarding offer for teams under 10 engineers.',
    fit: [
      { key: 'onboarding', label: 'Same-day setup' },
      { key: 'starter_plan', label: '$29 starter plan' },
      { key: 'icp_match', label: 'Seed to Series A ICP' },
    ],
  },
  {
    id: 'opp_04',
    type: 'retention_fix',
    title: 'Convert single-service trials into multi-service accounts',
    claim_ids: ['claim_0401', 'claim_0402', 'claim_0403', 'claim_0404'],
    opportunity_mechanism: {
      statement:
        'Accounts that monitor one service can be expanded to their whole stack because the same team already trusts the product, but the manual per-service setup stops them.',
      shared_segment: 'existing accounts with exactly one monitored service',
      actionable_because: 'observed expansion intent + a blocking product gap in the same path',
    },
    strengths_it_builds_on: [
      { signal_id: 'sig_311', reason: 'Existing accounts already trust alert quality' },
    ],
    pains_to_fix_first: [
      {
        signal_id: 'sig_321',
        reason: 'Adding services beyond the first is manual; 29 feedback items name it',
        severity: 3,
      },
    ],
    competitive_context: [],
    evidence_diversity: {
      source_kind_count: 2,
      domain_count: 2,
      author_count: 11,
      underlying_event_risk: 'low',
    },
    evidence_confidence: 'HIGH',
    fix_first_flag: true,
    priority: 'Blocked',
    value: {
      model: 'saas_arr',
      assumptions: {
        signal_count: 29,
        estimated_qualified_accounts: { low: 210, high: 340 },
        expected_conversion: 0.18,
        arpa_usd: 99,
      },
      monthly_usd: { low: 3742, high: 6059 },
    },
    what_to_do:
      'Ship bulk service import first. Until then this expansion play sells against a known blocker.',
    fit: [
      { key: 'slack_integration', label: 'Slack integration' },
      { key: 'on_call_paging', label: 'On-call paging' },
    ],
  },
  {
    id: 'opp_15',
    type: 'packaging_pricing',
    title: 'Introduce a per-service tier between Starter and Team',
    claim_ids: ['claim_1501', 'claim_1502', 'claim_1503', 'claim_1504'],
    opportunity_mechanism: {
      statement:
        'Accounts that outgrow Starter but balk at Team pricing can be held with an intermediate tier because the jump, not the product, is what they object to.',
      shared_segment: 'accounts at the Starter seat ceiling',
      actionable_because: 'observed pricing objections at one specific threshold',
    },
    strengths_it_builds_on: [
      { signal_id: 'sig_313', reason: 'Starter plan is repeatedly called good value' },
    ],
    pains_to_fix_first: [],
    competitive_context: [
      { signal_id: 'sig_221', competitor: 'Better Stack', pattern: 'competitor_tier_structure' },
    ],
    evidence_diversity: {
      source_kind_count: 2,
      domain_count: 2,
      author_count: 4,
      underlying_event_risk: 'medium',
    },
    evidence_confidence: 'MEDIUM',
    fix_first_flag: false,
    priority: 'Medium',
    value: {
      model: 'saas_arr',
      assumptions: {
        signal_count: 9,
        estimated_qualified_accounts: { low: 320, high: 640 },
        expected_conversion: 0.07,
        arpa_usd: 59,
      },
      monthly_usd: { low: 1322, high: 2643 },
    },
    what_to_do: 'Test a $59 tier with the accounts currently at the Starter seat limit.',
    fit: [{ key: 'pricing', label: 'Existing two-tier pricing' }],
  },
  {
    id: 'opp_21',
    type: 'positioning_shift',
    title: 'Lead with on-call quality of life rather than uptime',
    claim_ids: ['claim_2101', 'claim_2102', 'claim_2103', 'claim_2104'],
    opportunity_mechanism: {
      statement:
        'Engineers who choose their own tools can be reached through on-call experience because that is what the praise in the feedback set is actually about.',
      shared_segment: 'engineers with tool-choice influence',
      actionable_because: 'consistent praise theme, but thin external corroboration so far',
    },
    strengths_it_builds_on: [
      { signal_id: 'sig_311', reason: 'Alert precision praise maps to on-call quality of life' },
    ],
    pains_to_fix_first: [],
    competitive_context: [],
    evidence_diversity: {
      source_kind_count: 1,
      domain_count: 1,
      author_count: 3,
      underlying_event_risk: 'high',
    },
    evidence_confidence: 'LOW',
    fix_first_flag: false,
    priority: 'Low',
    value: {
      model: 'saas_arr',
      assumptions: {
        signal_count: 5,
        estimated_qualified_accounts: { low: 150, high: 400 },
        expected_conversion: 0.05,
        arpa_usd: 99,
      },
      monthly_usd: { low: 743, high: 1980 },
    },
    what_to_do: 'Rewrite the landing headline around on-call experience and measure signup rate.',
    fit: [{ key: 'on_call_paging', label: 'On-call paging' }],
  },
]

/** Four claims per opportunity (§14.8 requires all four types, each verified). */
export const claims: Claim[] = [
  {
    id: 'claim_0701',
    opportunity_id: 'opp_07',
    type: 'why_this',
    text: 'Public discussions show teams evaluating alternatives following pricing and complexity concerns.',
    status: 'verified',
    label: 'OBSERVED',
    evidence_ids: ['evd_001', 'evd_004'],
  },
  {
    id: 'claim_0702',
    opportunity_id: 'opp_07',
    type: 'why_you',
    text: 'PulseStack customers repeatedly praise low false-positive alerts, the thing those same threads complain about.',
    status: 'verified',
    label: 'OBSERVED',
    evidence_ids: ['evd_101'],
  },
  {
    id: 'claim_0703',
    opportunity_id: 'opp_07',
    type: 'why_now',
    text: 'A named competitor recent pricing change is visible in 8 public discussions in the last 45 days.',
    status: 'verified',
    label: 'OBSERVED',
    evidence_ids: ['evd_002', 'evd_003'],
  },
  {
    id: 'claim_0704',
    opportunity_id: 'opp_07',
    type: 'mechanism',
    text: 'PulseStack already serves teams in the 3-15 engineer range that generate this exact complaint pattern, so the fit is existing rather than hypothetical.',
    status: 'verified',
    label: 'INFERRED',
    evidence_ids: ['evd_101', 'evd_004'],
  },

  {
    id: 'claim_1101',
    opportunity_id: 'opp_11',
    type: 'why_this',
    text: 'Public threads from seed-stage teams describe choosing a first monitoring tool without an incumbent to migrate from.',
    status: 'verified',
    label: 'OBSERVED',
    evidence_ids: ['evd_011'],
  },
  {
    id: 'claim_1102',
    opportunity_id: 'opp_11',
    type: 'why_you',
    text: '33 feedback items describe getting a first service monitored within an afternoon.',
    status: 'verified',
    label: 'OBSERVED',
    evidence_ids: ['evd_102'],
  },
  {
    id: 'claim_1103',
    opportunity_id: 'opp_11',
    type: 'why_now',
    text: 'Setup friction on two competing tools is discussed in 6 threads from the last 60 days.',
    status: 'verified',
    label: 'OBSERVED',
    evidence_ids: ['evd_012', 'evd_013'],
  },
  {
    id: 'claim_1104',
    opportunity_id: 'opp_11',
    type: 'mechanism',
    text: 'Teams with no incumbent have no migration cost, so the setup-speed strength converts directly into a reason to choose.',
    status: 'verified',
    label: 'INFERRED',
    evidence_ids: ['evd_011', 'evd_102'],
  },

  {
    id: 'claim_0401',
    opportunity_id: 'opp_04',
    type: 'why_this',
    text: 'Accounts monitoring one service describe wanting their whole stack covered.',
    status: 'verified',
    label: 'OBSERVED',
    evidence_ids: ['evd_104'],
  },
  {
    id: 'claim_0402',
    opportunity_id: 'opp_04',
    type: 'why_you',
    text: 'These are existing paying accounts that already rate alert quality highly.',
    status: 'verified',
    label: 'OBSERVED',
    evidence_ids: ['evd_101'],
  },
  {
    id: 'claim_0403',
    opportunity_id: 'opp_04',
    type: 'why_now',
    text: '29 feedback items name per-service setup as manual, 11 of them from the last 30 days.',
    status: 'verified',
    label: 'OBSERVED',
    evidence_ids: ['evd_104'],
  },
  {
    id: 'claim_0404',
    opportunity_id: 'opp_04',
    type: 'mechanism',
    text: 'Expansion revenue sits behind one specific product gap, so fixing bulk import unblocks an audience that has already bought once.',
    status: 'verified',
    label: 'INFERRED',
    evidence_ids: ['evd_104'],
  },

  {
    id: 'claim_1501',
    opportunity_id: 'opp_15',
    type: 'why_this',
    text: 'Pricing objections cluster at the Starter seat ceiling rather than across the plan range.',
    status: 'verified',
    label: 'OBSERVED',
    evidence_ids: ['evd_021'],
  },
  {
    id: 'claim_1502',
    opportunity_id: 'opp_15',
    type: 'why_you',
    text: 'The Starter plan is described as good value in 12 feedback items.',
    status: 'verified',
    label: 'OBSERVED',
    evidence_ids: ['evd_022'],
  },
  {
    id: 'claim_1503',
    opportunity_id: 'opp_15',
    type: 'why_now',
    text: 'A competitor introduced an intermediate tier, discussed in 3 public threads.',
    status: 'hypothesis',
    label: 'OBSERVED',
    evidence_ids: ['evd_023'],
  },
  {
    id: 'claim_1504',
    opportunity_id: 'opp_15',
    type: 'mechanism',
    text: 'Accounts at the seat ceiling are already converted buyers, so the objection is to the size of the jump rather than to the product.',
    status: 'verified',
    label: 'INFERRED',
    evidence_ids: ['evd_021'],
  },

  {
    id: 'claim_2101',
    opportunity_id: 'opp_21',
    type: 'why_this',
    text: 'On-call burden appears as a recurring theme in engineer-authored discussions.',
    status: 'hypothesis',
    label: 'OBSERVED',
    evidence_ids: ['evd_031'],
  },
  {
    id: 'claim_2102',
    opportunity_id: 'opp_21',
    type: 'why_you',
    text: 'Alert precision is PulseStack single most-praised attribute.',
    status: 'verified',
    label: 'OBSERVED',
    evidence_ids: ['evd_101'],
  },
  {
    id: 'claim_2103',
    opportunity_id: 'opp_21',
    type: 'why_now',
    text: 'Only 3 distinct authors across 1 source kind discuss this, so timing is not established.',
    status: 'hypothesis',
    label: 'OBSERVED',
    evidence_ids: ['evd_031'],
  },
  {
    id: 'claim_2104',
    opportunity_id: 'opp_21',
    type: 'mechanism',
    text: 'Engineers who choose their own tools respond to daily experience, which is where the praise concentrates.',
    status: 'hypothesis',
    label: 'INFERRED',
    evidence_ids: ['evd_031', 'evd_101'],
  },
]

/** §1.3 — the rejected trail, with the reason, is a feature of the screen. */
export const rejectedIdeas: RejectedIdea[] = [
  {
    id: 'opp_18',
    title: 'Sell an enterprise compliance bundle',
    rejected_because:
      'The only supporting quote came from a single thread and could not be matched to a source document on re-check, so the claim failed quote-exists.',
    failed_gate: 'Evidence Check — quote not found in source',
  },
  {
    id: 'opp_19',
    title: 'Position against a competitor recent outage',
    rejected_because:
      'All four supporting evidence items trace to one news event and one domain, so evidence diversity did not clear the bar and the claim would rest on a single underlying event.',
    failed_gate: 'Quality Gate — evidence diversity (§11.2)',
  },
]
