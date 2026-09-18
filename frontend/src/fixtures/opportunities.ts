import type { Claim, Opportunity } from '../types/entities'
import type { RejectedIdea } from '../lib/viewModels'

/**
 * Fixture inbox for PulseStack (PRD §1.3, §1.4, §14.8).
 *
 * Covers every section screen 3 has to render: two High, one Blocked (HIGH evidence plus a
 * fix-first pain, per the §13.1 rule table), one Medium, one Low, and two rejected ideas.
 * `opp_07`'s value assumptions reproduce the worked example from §13.2 in prose — 1,200-3,600
 * accounts at 5% conversion on a $99 plan gives $5,940-$17,820/mo — so the arithmetic can still
 * be checked by hand against the PRD, just as a description rather than separate numeric
 * fields (canonical `ValueAssumption` only has `key`/`label`/`description`, §13.2).
 *
 * Note there is no score field on any of these, by design (§13.1). There is also no `title`,
 * `fit` or `what_to_do` field — those aren't in the canonical `Opportunity` contract and
 * aren't derivable from it (see LEARNING.md); the card uses `opportunity_mechanism.statement`
 * as its headline instead (lib/viewModels.ts).
 */
export const opportunities: Opportunity[] = [
  {
    id: 'opp_07',
    type: 'competitive_gap',
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
    priority: 'High',
    value: {
      model: 'saas_arr',
      assumptions: [
        {
          key: 'qualified_accounts',
          label: 'ASSUMED',
          description: '24 observed signals imply 1,200-3,600 estimated qualified accounts',
        },
        { key: 'conversion', label: 'ASSUMED', description: '5% expected conversion' },
        { key: 'arpa', label: 'OBSERVED', description: '$99 per account per month' },
      ],
      monthly_usd: { low: 5940, high: 17820 },
    },
  },
  {
    id: 'opp_11',
    type: 'segment_expansion',
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
    priority: 'High',
    value: {
      model: 'saas_arr',
      assumptions: [
        {
          key: 'qualified_accounts',
          label: 'ASSUMED',
          description: '17 observed signals imply 850-1,190 estimated qualified accounts',
        },
        { key: 'conversion', label: 'ASSUMED', description: '5% expected conversion' },
        { key: 'arpa', label: 'OBSERVED', description: '$99 per account per month' },
      ],
      monthly_usd: { low: 4208, high: 5891 },
    },
  },
  {
    id: 'opp_04',
    type: 'retention_fix',
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
    priority: 'Blocked',
    value: {
      model: 'saas_arr',
      assumptions: [
        {
          key: 'qualified_accounts',
          label: 'ASSUMED',
          description: '29 observed signals imply 210-340 estimated qualified accounts',
        },
        { key: 'conversion', label: 'ASSUMED', description: '18% expected conversion' },
        { key: 'arpa', label: 'OBSERVED', description: '$99 per account per month' },
      ],
      monthly_usd: { low: 3742, high: 6059 },
    },
  },
  {
    id: 'opp_15',
    type: 'packaging_pricing',
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
    priority: 'Medium',
    value: {
      model: 'saas_arr',
      assumptions: [
        {
          key: 'qualified_accounts',
          label: 'ASSUMED',
          description: '9 observed signals imply 320-640 estimated qualified accounts',
        },
        { key: 'conversion', label: 'ASSUMED', description: '7% expected conversion' },
        { key: 'arpa', label: 'OBSERVED', description: '$59 per account per month' },
      ],
      monthly_usd: { low: 1322, high: 2643 },
    },
  },
  {
    id: 'opp_21',
    type: 'positioning_shift',
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
    priority: 'Low',
    value: {
      model: 'saas_arr',
      assumptions: [
        {
          key: 'qualified_accounts',
          label: 'ASSUMED',
          description: '5 observed signals imply 150-400 estimated qualified accounts',
        },
        { key: 'conversion', label: 'ASSUMED', description: '5% expected conversion' },
        { key: 'arpa', label: 'OBSERVED', description: '$99 per account per month' },
      ],
      monthly_usd: { low: 743, high: 1980 },
    },
  },
]

/**
 * Four claims per opportunity (§14.8 requires all four types, each verified). No `label` field
 * — OBSERVED/INFERRED is a rendering convention derived from `type` (why_this/why_you/why_now
 * -> OBSERVED, mechanism -> INFERRED; docs/contract.md), not a stored property.
 */
export const claims: Claim[] = [
  {
    id: 'claim_0701',
    opportunity_id: 'opp_07',
    type: 'why_this',
    text: 'Public discussions show teams evaluating alternatives following pricing and complexity concerns.',
    status: 'verified',
    evidence_ids: ['evd_001', 'evd_004'],
  },
  {
    id: 'claim_0702',
    opportunity_id: 'opp_07',
    type: 'why_you',
    text: 'PulseStack customers repeatedly praise low false-positive alerts, the thing those same threads complain about.',
    status: 'verified',
    evidence_ids: ['evd_101'],
  },
  {
    id: 'claim_0703',
    opportunity_id: 'opp_07',
    type: 'why_now',
    text: 'A named competitor recent pricing change is visible in 8 public discussions in the last 45 days.',
    status: 'verified',
    evidence_ids: ['evd_002', 'evd_003'],
  },
  {
    id: 'claim_0704',
    opportunity_id: 'opp_07',
    type: 'mechanism',
    text: 'PulseStack already serves teams in the 3-15 engineer range that generate this exact complaint pattern, so the fit is existing rather than hypothetical.',
    status: 'verified',
    evidence_ids: ['evd_101', 'evd_004'],
  },

  {
    id: 'claim_1101',
    opportunity_id: 'opp_11',
    type: 'why_this',
    text: 'Public threads from seed-stage teams describe choosing a first monitoring tool without an incumbent to migrate from.',
    status: 'verified',
    evidence_ids: ['evd_011'],
  },
  {
    id: 'claim_1102',
    opportunity_id: 'opp_11',
    type: 'why_you',
    text: '33 feedback items describe getting a first service monitored within an afternoon.',
    status: 'verified',
    evidence_ids: ['evd_102'],
  },
  {
    id: 'claim_1103',
    opportunity_id: 'opp_11',
    type: 'why_now',
    text: 'Setup friction on two competing tools is discussed in 6 threads from the last 60 days.',
    status: 'verified',
    evidence_ids: ['evd_012', 'evd_013'],
  },
  {
    id: 'claim_1104',
    opportunity_id: 'opp_11',
    type: 'mechanism',
    text: 'Teams with no incumbent have no migration cost, so the setup-speed strength converts directly into a reason to choose.',
    status: 'verified',
    evidence_ids: ['evd_011', 'evd_102'],
  },

  {
    id: 'claim_0401',
    opportunity_id: 'opp_04',
    type: 'why_this',
    text: 'Accounts monitoring one service describe wanting their whole stack covered.',
    status: 'verified',
    evidence_ids: ['evd_104'],
  },
  {
    id: 'claim_0402',
    opportunity_id: 'opp_04',
    type: 'why_you',
    text: 'These are existing paying accounts that already rate alert quality highly.',
    status: 'verified',
    evidence_ids: ['evd_101'],
  },
  {
    id: 'claim_0403',
    opportunity_id: 'opp_04',
    type: 'why_now',
    text: '29 feedback items name per-service setup as manual, 11 of them from the last 30 days.',
    status: 'verified',
    evidence_ids: ['evd_104'],
  },
  {
    id: 'claim_0404',
    opportunity_id: 'opp_04',
    type: 'mechanism',
    text: 'Expansion revenue sits behind one specific product gap, so fixing bulk import unblocks an audience that has already bought once.',
    status: 'verified',
    evidence_ids: ['evd_104'],
  },

  {
    id: 'claim_1501',
    opportunity_id: 'opp_15',
    type: 'why_this',
    text: 'Pricing objections cluster at the Starter seat ceiling rather than across the plan range.',
    status: 'verified',
    evidence_ids: ['evd_021'],
  },
  {
    id: 'claim_1502',
    opportunity_id: 'opp_15',
    type: 'why_you',
    text: 'The Starter plan is described as good value in 12 feedback items.',
    status: 'verified',
    evidence_ids: ['evd_022'],
  },
  {
    id: 'claim_1503',
    opportunity_id: 'opp_15',
    type: 'why_now',
    text: 'A competitor introduced an intermediate tier, discussed in 3 public threads.',
    status: 'hypothesis',
    evidence_ids: ['evd_023'],
  },
  {
    id: 'claim_1504',
    opportunity_id: 'opp_15',
    type: 'mechanism',
    text: 'Accounts at the seat ceiling are already converted buyers, so the objection is to the size of the jump rather than to the product.',
    status: 'verified',
    evidence_ids: ['evd_021'],
  },

  {
    id: 'claim_2101',
    opportunity_id: 'opp_21',
    type: 'why_this',
    text: 'On-call burden appears as a recurring theme in engineer-authored discussions.',
    status: 'hypothesis',
    evidence_ids: ['evd_031'],
  },
  {
    id: 'claim_2102',
    opportunity_id: 'opp_21',
    type: 'why_you',
    text: 'Alert precision is PulseStack single most-praised attribute.',
    status: 'verified',
    evidence_ids: ['evd_101'],
  },
  {
    id: 'claim_2103',
    opportunity_id: 'opp_21',
    type: 'why_now',
    text: 'Only 3 distinct authors across 1 source kind discuss this, so timing is not established.',
    status: 'hypothesis',
    evidence_ids: ['evd_031'],
  },
  {
    id: 'claim_2104',
    opportunity_id: 'opp_21',
    type: 'mechanism',
    text: 'Engineers who choose their own tools respond to daily experience, which is where the praise concentrates.',
    status: 'hypothesis',
    evidence_ids: ['evd_031', 'evd_101'],
  },
]

/** §1.3 — the rejected trail, with the reason, is a feature of the screen. Frontend-only type
    (lib/viewModels.ts) — no canonical entity or endpoint backs this yet (Quality Gate, Day 2). */
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
