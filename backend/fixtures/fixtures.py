"""Fixture data for the Task 2 stub Lambdas.

Built directly from the Task 1 Pydantic models (backend/schemas/entities.py)
so a fixture can never silently drift from the schema — an invalid fixture
fails to import rather than failing a curl at demo time. Based on the
PulseStack/Sentry worked examples in PRD §12/§14.
"""

from __future__ import annotations

import hashlib

from backend.schemas.entities import (
    AccountFitInference,
    AgentInvocation,
    Business,
    Capability,
    Claim,
    ClaimSupport,
    Competitor,
    DerivedSignal,
    Evidence,
    EvidenceDiversity,
    ExecutionPack,
    Freshness,
    Goal,
    MonthlyRange,
    ObservedFact,
    Opportunity,
    OpportunityMechanism,
    OutreachDraft,
    PainToFix,
    Pricing,
    RejectedCandidate,
    Run,
    Signal,
    SignalReason,
    SourceDocument,
    SuggestedContact,
    Target,
    ValueAssumption,
    ValueModel,
    CompetitiveContextItem,
)


def _quote_hash(quote: str) -> str:
    return f"sha256:{hashlib.sha256(quote.encode()).hexdigest()}"


BUSINESS = Business(
    id="biz_pulsestack",
    name="PulseStack",
    is_simulated=True,
    scenario_id="pulsestack_v1",
    industry="developer_tools_observability",
    playbook_id="b2b_saas_it",
    icp=["seed_to_series_a_startup", "3_15_engineer_team"],
    pricing=Pricing(starter_usd_month=29, team_usd_month=99),
    current_mrr_usd=8200,
    goal=Goal(metric="mrr", change_usd=15000, horizon_days=90),
    capabilities=[
        Capability(key="slack_integration", confirmed=True),
        Capability(key="on_call_paging", confirmed=True),
        Capability(key="custom_dashboards", confirmed=False),
        Capability(key="sso", confirmed=False),
    ],
    named_competitors=["Sentry", "Datadog", "New Relic", "Better Stack"],
    data_assets=["asset_tickets_01", "asset_survey_01"],
    created_at="2026-09-17T10:00:00+05:30",
)

RUN = Run(
    id="run_001",
    business_id=BUSINESS.id,
    started_at="2026-09-18T09:00:00+05:30",
    finished_at="2026-09-18T09:02:10+05:30",
    status="succeeded",
    agent_invocations=[
        AgentInvocation(component="market_agent", iterations=2, tool_calls=4, runtime_seconds=38, truncated=False),
        AgentInvocation(component="feedback_pipeline", iterations=1, tool_calls=2, runtime_seconds=12, truncated=False),
        AgentInvocation(component="competitor_agent", iterations=3, tool_calls=6, runtime_seconds=54, truncated=True),
    ],
    opportunities_produced=6,
    opportunities_rejected=3,
    estimated_cost_usd=0.41,
)

SOURCE_DOCUMENT_HN = SourceDocument(
    id="src_001",
    run_id=RUN.id,
    source_kind="hn",
    retrieval_mode="live",
    url="https://news.ycombinator.com/item?id=41000001",
    fetched_at="2026-09-18T09:01:12+05:30",
    raw_text_s3_key="s3://busyfox-runs/run_001/src_001.txt",
    expires_at="2026-10-18T09:01:12+05:30",
)

_QUOTE_ALERT_NOISE = "our team has been reconsidering monitoring costs because alert noise from Sentry is out of hand"
_QUOTE_PRICING = "Sentry's pricing change pushed us to look at alternatives this quarter"

EVIDENCE_ALERT_NOISE = Evidence(
    id="evd_001",
    source_document_id=SOURCE_DOCUMENT_HN.id,
    source_kind="hn",
    retrieval_mode="live",
    url=SOURCE_DOCUMENT_HN.url,
    retrieved_at="2026-09-18T09:12:00+05:30",
    author="hn_user_412",
    published_at="2026-08-30T00:00:00Z",
    quote=_QUOTE_ALERT_NOISE,
    quote_hash=_quote_hash(_QUOTE_ALERT_NOISE),
    claim_support=ClaimSupport(status="supports", confidence=0.93, reason="Directly states alert-noise-driven cost reconsideration."),
    freshness=Freshness(status="fresh", age_days=23, limit_days=180),
)

EVIDENCE_PRICING = Evidence(
    id="evd_002",
    source_document_id=SOURCE_DOCUMENT_HN.id,
    source_kind="hn",
    retrieval_mode="live",
    url=SOURCE_DOCUMENT_HN.url,
    retrieved_at="2026-09-18T09:13:00+05:30",
    author="hn_user_889",
    published_at="2026-09-02T00:00:00Z",
    quote=_QUOTE_PRICING,
    quote_hash=_quote_hash(_QUOTE_PRICING),
    claim_support=ClaimSupport(status="supports", confidence=0.88, reason="States a pricing-driven evaluation of alternatives."),
    freshness=Freshness(status="fresh", age_days=16, limit_days=180),
)

# Unlike evd_001/evd_002 (Task 2 placeholders — their URL is a real HN item, but the
# quote is not on it), this one is a real, verbatim HN comment: Tavily's extract of the
# URL contains the quote, so the evidence drawer's live re-fetch can genuinely pass on it
# (Task 28 rehearsal). Collected 2026-09-19 via HN Algolia. 4+ years old, hence stale.
SOURCE_DOCUMENT_HN_SENTRY_NOISE = SourceDocument(
    id="src_002",
    run_id=RUN.id,
    source_kind="hn",
    retrieval_mode="live",
    url="https://news.ycombinator.com/item?id=31781473",
    fetched_at="2026-09-19T20:10:00+05:30",
    raw_text_s3_key="s3://busyfox-runs/run_001/src_002.txt",
    expires_at="2026-10-19T20:10:00+05:30",
)

_QUOTE_SENTRY_NOISE = "We've had scenarios like the one I mentioned (and worse) go undetected because of the noise Sentry generates."

EVIDENCE_SENTRY_NOISE_HN = Evidence(
    id="evd_hn_31781473",
    source_document_id=SOURCE_DOCUMENT_HN_SENTRY_NOISE.id,
    source_kind="hn",
    retrieval_mode="live",
    url=SOURCE_DOCUMENT_HN_SENTRY_NOISE.url,
    retrieved_at="2026-09-19T20:10:00+05:30",
    author="treis",
    published_at="2022-06-17T00:00:00Z",
    quote=_QUOTE_SENTRY_NOISE,
    quote_hash=_quote_hash(_QUOTE_SENTRY_NOISE),
    claim_support=ClaimSupport(status="supports", confidence=0.85, reason="Directly attributes missed incidents to the noise Sentry generates."),
    freshness=Freshness(status="stale", age_days=1555, limit_days=180),
)

EVIDENCE_BY_ID = {e.id: e for e in (EVIDENCE_ALERT_NOISE, EVIDENCE_PRICING, EVIDENCE_SENTRY_NOISE_HN)}

CLAIMS = [
    Claim(
        id="claim_001",
        opportunity_id="opp_001",
        type="why_this",
        text="8 public discussions mention alert fatigue as a reason teams reconsider their monitoring vendor.",
        status="verified",
        evidence_ids=["evd_001"],
    ),
    Claim(
        id="claim_002",
        opportunity_id="opp_001",
        type="why_you",
        text="PulseStack already serves teams of this exact size and profile with a confirmed low-noise capability.",
        status="verified",
        evidence_ids=["evd_001"],
    ),
    Claim(
        id="claim_003",
        opportunity_id="opp_001",
        type="why_now",
        text="A named competitor's recent pricing change is visible in 8 public discussions in the last 45 days.",
        status="verified",
        evidence_ids=["evd_002"],
    ),
    Claim(
        id="claim_004",
        opportunity_id="opp_001",
        type="mechanism",
        text="Small engineering teams frustrated by alert noise can be targeted with PulseStack's low-noise positioning.",
        status="verified",
        evidence_ids=["evd_001", "evd_002"],
    ),
]

SIGNALS = [
    Signal(
        id="sig_001",
        run_id=RUN.id,
        source_kind="hn",
        aspect="alert_noise",
        polarity="negative",
        claim_text="7 public discussions in the last 60 days mention teams reconsidering monitoring costs.",
        evidence_ids=["evd_001"],
        produced_by="market_agent",
    ),
    Signal(
        id="sig_002",
        run_id=RUN.id,
        source_kind="simulated",
        aspect="onboarding",
        polarity="positive",
        claim_text="PulseStack users repeatedly praise a 10-minute setup versus a full day for their previous tool.",
        evidence_ids=[],
        produced_by="feedback_pipeline",
    ),
    Signal(
        id="sig_003",
        run_id=RUN.id,
        source_kind="simulated",
        aspect="custom_dashboards",
        polarity="negative",
        claim_text="Several PulseStack users ask for custom dashboards, currently unconfirmed as a capability.",
        evidence_ids=[],
        produced_by="feedback_pipeline",
    ),
]

OPPORTUNITY = Opportunity(
    id="opp_001",
    type="competitive_gap",
    claim_ids=[c.id for c in CLAIMS],
    opportunity_mechanism=OpportunityMechanism(
        statement="Small engineering teams frustrated by alert noise can be targeted with PulseStack's low-noise positioning because PulseStack already serves teams of this exact size and profile.",
        shared_segment="3-15 engineer teams",
        actionable_because="confirmed capability (low false-positive rate) + existing ICP overlap",
    ),
    strengths_it_builds_on=[SignalReason(signal_id="sig_002", reason="Low-noise onboarding experience already resonates with this ICP.")],
    pains_to_fix_first=[PainToFix(signal_id="sig_001", reason="Alert fatigue is the named reason teams reconsider their vendor.", severity=3)],
    competitive_context=[CompetitiveContextItem(signal_id="sig_001", competitor="Sentry", pattern="competitor_pain_business_strength")],
    evidence_diversity=EvidenceDiversity(source_kind_count=1, domain_count=1, author_count=2, underlying_event_risk="unknown"),
    evidence_confidence="HIGH",
    priority="Blocked",
    value=ValueModel(
        model="saas_arr",
        assumptions=[
            ValueAssumption(key="signal_count", label="OBSERVED", description="24 observed 'evaluating alternatives' mentions"),
            ValueAssumption(key="estimated_qualified_accounts", label="ASSUMED", description="1,200-3,600 — playbook multiplier applied to signal_count"),
            ValueAssumption(key="expected_conversion", label="ASSUMED", description="5% conversion assumption"),
            ValueAssumption(key="ARPA", label="OBSERVED", description="$99/month team plan, from the business's own pricing"),
        ],
        monthly_usd=MonthlyRange(low=5940, high=17820),
    ),
)

# docs/contract.md gap 2 / frontend/src/fixtures/opportunities.ts:397 — same two
# worked examples, kept in sync by hand since the frontend fixture predates this one.
REJECTED_IDEAS = [
    RejectedCandidate(
        id="opp_018",
        opportunity_type="unmet_need",
        title="Sell an enterprise compliance bundle",
        rejected_because=(
            "The only supporting quote came from a single thread and could not be matched to a "
            "source document on re-check, so the claim failed quote-exists."
        ),
        failed_gate="Evidence Check — quote not found in source",
    ),
    RejectedCandidate(
        id="opp_019",
        opportunity_type="competitive_gap",
        title="Position against a competitor recent outage",
        rejected_because=(
            "All four supporting evidence items trace to one news event and one domain, so "
            "evidence diversity did not clear the bar and the claim would rest on a single "
            "underlying event."
        ),
        failed_gate="Quality Gate — evidence diversity (§11.2)",
    ),
]

COMPETITOR_SENTRY = Competitor(
    id="cmp_001",
    run_id=RUN.id,
    name="Sentry",
    sources_checked=["web_public", "hn", "github"],
    enrichment_sources_checked=["app_store"],
    summary_id="sent_001",
    public_url="https://sentry.io",
)

TARGET = Target(
    id="tgt_001",
    opportunity_id=OPPORTUNITY.id,
    organisation="A named public company or ICP-matching account found via research",
    observed_facts=[
        ObservedFact(
            claim="Public HN comment from a self-identified employee discussing monitoring alternatives",
            evidence_ids=["evd_001"],
            source_kind="hn",
        )
    ],
    derived_signals=[
        DerivedSignal(
            signal="Team size, from public job postings, falls in the 3-15 engineer range",
            signal_id="sig_001",
            confidence="medium",
            last_verified_at="2026-09-18T09:05:00+05:30",
            evidence_ids=["evd_001"],
        )
    ],
    account_fit_inference=AccountFitInference(
        statement="Company appears to fit PulseStack's ICP based on observed facts and derived signals above",
        confidence="medium",
    ),
    suggested_contact=SuggestedContact(
        role="CTO",
        reason="At this team size, tooling decisions are typically owned at this level.",
    ),
)

EXECUTION_PACK = ExecutionPack(
    id="pack_001",
    opportunity_id=OPPORTUNITY.id,
    offer="A 14-day PulseStack trial pre-configured with low-noise alerting defaults.",
    proposal="Migrate your alert rules from Sentry in under a day; keep the on-call paging you already rely on.",
    outreach_drafts=[
        OutreachDraft(
            channel="email",
            draft="Teams your size often tell us alert noise is the #1 reason they look elsewhere. PulseStack was built for exactly that.",
            proof_point_signal_id="sig_001",
            outreach_policy_checked=True,
        )
    ],
    status="draft",
)
