# Graph Report - BusyFox  (2026-09-19)

## Corpus Check
- 112 files · ~77,104 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 19 file(s) not represented in the graph (top: .css 14, (none) 3, .example 1)

## Summary
- 1237 nodes · 3304 edges · 87 communities (56 shown, 31 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 402 edges (avg confidence: 0.93)
- Token cost: 0 input · 151,616 output

## Community Hubs (Navigation)
- DynamoDB DAO & Fixtures
- DynamoDB Entity Access Helpers
- Feedback Labelling Pipeline
- Synthesis Agent
- Deploy Config & Lane Docs
- App Store & GitHub Collectors
- Frontend Entity Types
- Card UI Component
- Market Agent
- Frontend API Client
- Orchestrator & PulseStack Simulator
- Evidence Check
- Guardrails & PRD Core Concepts
- Competitor Agent
- Orchestrator Pipeline Wiring
- Collector APIs & Runtime Contract
- Market Agent Live Collection
- CLAUDE.md Guardrails
- Frontend TS Config (App)
- Bedrock Session Override
- Inbox Grouping Logic
- Deploy Wizard Script
- HN Collector
- Frontend Package Dependencies
- Design Token Contrast Check
- Retrieval Mode & Labels UI
- Frontend TS Config (Node)
- Frontend App Shell
- Competitor Agent Live Collection
- GitHub Collector
- Day 3 Plan & Claim Labels
- Day 4 Plan & Repo Rules
- Orchestrator Tests
- Day 1 Plan & Eligibility
- Competitor Agent Hooks
- Product Hunt Collector
- Rejected Ideas View Model
- Day 2 Plan & Quality Gate
- App Store Collector
- Hackathon Rules Doc
- Synthesis Agent Hooks
- Feature Freeze & Scope Phases
- Frontend Dev Dependencies
- API Client Fetch Hooks
- PulseStack & Attribution Safety
- Market Agent Hooks
- Demo Video & Track Rules
- Design Plan Critique
- Evidence Check & Action Agent Concepts
- Competitor Agent Signal Emission
- Live Pipeline Runner Script
- Orchestrator Stub Lambda
- Lambda Requirements & CodeUri
- Frontend Lint Config
- Frontend NPM Scripts
- Doc Cadence Notes
- Issue Tracker Conventions
- Frontend Root TS Config
- Contract Source of Truth
- Ponytail Plugin Note
- Domain ADR Convention
- Contract Business/Run Types
- Phase 3 & Feature Freeze
- Amplify Hosting
- CREDITS.md
- DynamoDB + S3 State
- LEARNING.md
- Opportunity Engine (root concept)
- Stable ID Prefixes
- Submission Artifacts
- Definition of Done
- Triage Labels Table
- Contract Competitor Type
- Day 1 Log
- Day 2 Log
- Plan Phase 1
- Plan Phase 2
- Plan Phase 4

## God Nodes (most connected - your core abstractions)
1. `SourceKind` - 77 edges
2. `Signal` - 72 edges
3. `Polarity` - 56 edges
4. `AgentRuntimeContract` - 47 edges
5. `RuntimeBudget` - 39 edges
6. `run_quality_gate()` - 38 edges
7. `Evidence` - 36 edges
8. `Opportunity` - 36 edges
9. `_opportunity()` - 31 edges
10. `build_opportunity()` - 30 edges

## Surprising Connections (you probably didn't know these)
- `Favicon: zigzag mark, seafoam mint on dark petrol slate` --shares_data_with--> `Seven color tokens (bg/surface/ink/slate/muted/accent/on-slate-muted)`  [INFERRED]
  frontend/public/favicon.svg → docs/design-plan.md
- `P0 Scope` --shares_data_with--> `MVP Scope (Section 20)`  [INFERRED]
  BUILD_PLAN.md → opportunity_engine_prd_v8.md
- `P1 Scope` --shares_data_with--> `MVP Scope (Section 20)`  [INFERRED]
  BUILD_PLAN.md → opportunity_engine_prd_v8.md
- `P2 Scope` --shares_data_with--> `MVP Scope (Section 20)`  [INFERRED]
  BUILD_PLAN.md → opportunity_engine_prd_v8.md
- `Live Tavily Round-Trip + Level-3 Fixture` --references--> `Data Acquisition Risk: Live to Cached to Demo Fixture Ladder`  [EXTRACTED]
  BUILD_PLAN.md → opportunity_engine_prd_v8.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Hard Event Constraints (Disqualification Risk)** — agents_eligibility_gate, agents_repo_history_rule, agents_submission_artifacts [EXTRACTED 1.00]
- **Core Loop: Discover to Track** — opportunity_engine_prd_v8_orchestrator, opportunity_engine_prd_v8_market_agent, opportunity_engine_prd_v8_synthesis_agent, opportunity_engine_prd_v8_evidence_check, opportunity_engine_prd_v8_quality_gate_ranker, opportunity_engine_prd_v8_action_agent [EXTRACTED 1.00]
- **Provenance Chain Entities** — opportunity_engine_prd_v8_sourcedocument, opportunity_engine_prd_v8_evidence, opportunity_engine_prd_v8_claim, opportunity_engine_prd_v8_opportunity [EXTRACTED 1.00]
- **OpportunityEngineTable stores all nine core entities via one single-table design** — infra_api_gateway_table, docs_contract_business, docs_contract_run, docs_contract_sourcedocument, docs_contract_evidence, docs_contract_claim, docs_contract_signal, docs_contract_opportunity, docs_contract_target, docs_contract_executionpack [EXTRACTED 1.00]
- **No-composite-score guardrail enforced identically in guardrail doc, contract entity, design system and frontend rendering rules** — claude_no_composite_score, docs_contract_opportunity, docs_design_plan_three_numbers_three_shapes, frontend_readme_rendering_rules [INFERRED 0.90]
- **Live -> Cached -> Demo Fixture retrieval ladder implemented end to end via header, CORS expose, and frontend blocker tracking** — claude_retrieval_ladder, docs_contract_retrieval_mode_header, infra_api_gateway_api, frontend_readme_known_blockers [INFERRED 0.90]

## Communities (87 total, 31 thin omitted)

### Community 0 - "DynamoDB DAO & Fixtures"
Cohesion: 0.06
Nodes (119): DynamoDB single-table design for all nine core entities (Task 20, PRD…, Fixture data for the Task 2 stub Lambdas. Built directly from the Task 1…, check_account_evidence_integrity(), check_actionable(), check_attribution_safety(), check_capability(), check_claim_evidence_support(), check_mandatory_fields() (+111 more)

### Community 1 - "DynamoDB Entity Access Helpers"
Cohesion: 0.06
Nodes (87): Any, get_entity(), get_table(), prefix_for(), put_entity(), BaseModel, ModelT, query_children() (+79 more)

### Community 2 - "Feedback Labelling Pipeline"
Cohesion: 0.08
Nodes (65): aggregate_and_balance(), _aspect_groups(), _AspectItem, bedrock_labeller(), labeller(), _dominant_polarity(), _evidence_for(), _fake_labeller() (+57 more)

### Community 3 - "Synthesis Agent"
Cohesion: 0.09
Nodes (52): assemble_synthesis_output(), emit_candidate_opportunity(), build_opportunity(), _competitor_name(), _fake_collect(), mechanism_is_concrete(), passes_self_critique(), _provisional_priority() (+44 more)

### Community 4 - "Deploy Config & Lane Docs"
Cohesion: 0.07
Nodes (53): Amplify Hosting buildspec (lint -> typecheck -> build), backend/requirements.txt (pydantic, pytest, boto3, strands-agents), Lane A - Backend/Agents, Lane B - Frontend/UX, Lane C - Floating, DynamoDB single-table design (Task 20), No route for gate-rejected candidates (gap 2), Known blockers table (Tasks 22-23) (+45 more)

### Community 5 - "App Store & GitHub Collectors"
Cohesion: 0.09
Nodes (24): App Store customer-reviews RSS collector (Task 11, PRD §7 S4) — P1 enrichment:…, GitHub REST collector (Task 3) — release/issue activity for a named competitor,…, HN Algolia collector (Task 4) — public story discussion of a competitor or…, Product Hunt GraphQL v2 collector (Task 11, PRD §7 S5) — P1 enrichment: launch…, FailureMode, probe(), Tavily search+extract probe (Task 5) — one live round-trip against the PRD's…, One search call, then one extract call on the top result. Returns a report:… (+16 more)

### Community 6 - "Frontend Entity Types"
Cohesion: 0.05
Nodes (36): AccountFitInference, AgentInvocation, AgentRuntimeContract, Capability, ClaimStatus, ClaimSupport, ClaimSupportStatus, CompetitiveContextItem (+28 more)

### Community 7 - "Card UI Component"
Cohesion: 0.12
Nodes (29): Card(), CardBody(), CardFooter(), CardHeader(), Section(), ClaimLabel(), CONFIDENCE_STEPS, ConfidenceMeter() (+21 more)

### Community 8 - "Market Agent"
Cohesion: 0.14
Nodes (29): assemble_research_output(), emit_market_signal(), build_signal(), _fake_collect(), is_valid_market_claim(), NamedTuple, Market Agent (Task 15) — Strands agent (Haiku) over web/HN/GitHub producing…, §9.4 validation + §10.1a truncation labelling, all in one place — the boundary… (+21 more)

### Community 9 - "Frontend API Client"
Cohesion: 0.14
Nodes (24): baseUrl(), declaredMode(), fetchClaims(), Fetched, fetchFeedbackSignals(), fetchInbox(), fetchOpportunities(), get() (+16 more)

### Community 10 - "Orchestrator & PulseStack Simulator"
Cohesion: 0.11
Nodes (27): PulseStack's own feedback, for the simulated demo business (§18.1: always…, run_feedback_stage(), generate_pulsestack_feedback(), add_effects(), add_item(), load_scenario(), _polarity_for(), PulseStackFeedback (+19 more)

### Community 11 - "Evidence Check"
Cohesion: 0.14
Nodes (27): EvidenceCandidate, EvidenceCheckResult, freshness_limit_days(), NamedTuple, quote_exists(), Entry point Task 21's orchestrator calls between Synthesis and Quality Gate.…, §12.1 citation verification — reuses Task 14's verbatim-or-fuzzy span check…, One quote Evidence Check must verify, for one Claim. The orchestrator (Task 21)… (+19 more)

### Community 12 - "Guardrails & PRD Core Concepts"
Cohesion: 0.12
Nodes (23): No Composite Opportunity Score, Provenance Chain: SourceDocument to Opportunity, Synthesis Agent Build, Business Entity, Claim Entity, Competitor Entity, Evidence Entity, Evidence Diversity Check (+15 more)

### Community 13 - "Competitor Agent"
Cohesion: 0.19
Nodes (22): assemble_research_output(), build_signal(), is_valid_competitor_claim(), §9.4/§18.4 validation + §10.1a truncation labelling, all in one place — the…, §9.4: a signal missing a concrete count, date window, or source reference fails…, validate_claims(), Competitor Agent (Task 16) — §9.4 claim validation + §18.4 named- competitor…, §10.1a — structurally enforced, not just unused by convention. (+14 more)

### Community 14 - "Orchestrator Pipeline Wiring"
Cohesion: 0.17
Nodes (22): _candidates_for_claim(), _fake_market_collect(), _matched_signal_ids(), PipelineResult, _Provenance, _published_at(), datetime, NamedTuple (+14 more)

### Community 15 - "Collector APIs & Runtime Contract"
Cohesion: 0.13
Nodes (21): GitHub REST API Source, Hacker News (Algolia) Source, Five-Field Agent Runtime Contract, signals[] Schema Limit for Research Agents, Step Functions Orchestrator, Strands Agents SDK, Synthesis Agent, Tavily Web Search (+13 more)

### Community 16 - "Market Agent Live Collection"
Cohesion: 0.15
Nodes (15): live_collect(), collect(), RawSignalCollector, Call before each model turn. False means the contract is already exhausted —…, Call before each tool invocation. False means stop; the caller must not run the…, Entry point Task 21's orchestrator calls. `collect` does the actual tool-…, Returns a `collect` callable that runs a real Strands agent — pass this as…, run_market_agent() (+7 more)

### Community 17 - "CLAUDE.md Guardrails"
Cohesion: 0.11
Nodes (21): Guardrail: no composite opportunity score, Guardrail: Live -> Cached -> Demo Fixture labelling, Guardrail: research agents emit signals[] only, Claim entity, Evidence entity, ExecutionPack entity, Opportunity entity, Quality Gate + Ranker component (+13 more)

### Community 18 - "Frontend TS Config (App)"
Cohesion: 0.10
Nodes (19): compilerOptions, allowArbitraryExtensions, allowImportingTsExtensions, erasableSyntaxOnly, jsx, lib, module, moduleDetection (+11 more)

### Community 19 - "Bedrock Session Override"
Cohesion: 0.20
Nodes (18): bedrock_session(), BEDROCK_AWS_PROFILE routes every Bedrock call (this agent, Competitor,…, _fake_semantic_check(), bedrock_semantic_support_checker(), check(), build_evidence(), check_freshness(), _fake_semantic_check() (+10 more)

### Community 20 - "Inbox Grouping Logic"
Cohesion: 0.16
Nodes (14): derivePriority(), groupOpportunities(), InboxSection, SECTION_ORDER, sectionFor(), SectionKey, valueMidpoint(), LIVE_BUSINESS (+6 more)

### Community 21 - "Deploy Wizard Script"
Cohesion: 0.25
Nodes (18): ask(), ask_secret(), banner(), _clear(), confirm(), _existing(), finish(), note() (+10 more)

### Community 22 - "HN Collector"
Cohesion: 0.23
Nodes (17): fetch_hn_signals(), Fetch, Recent HN stories matching query, mapped to Signals., _fake_synthesis_collect(), contradiction_exists(), §11.1 check 4 — counter-evidence exists: some other signal from this run makes…, Polarity, Signal (+9 more)

### Community 23 - "Frontend Package Dependencies"
Cohesion: 0.12
Nodes (16): dependencies, react, react-dom, name, private, type, version, oxlint (+8 more)

### Community 24 - "Design Token Contrast Check"
Cohesion: 0.19
Nodes (14): channel(), contrastLevel, contrastRatio(), luminance(), readTokenColors(), theme, toRgb(), ALL_TOKENS (+6 more)

### Community 25 - "Retrieval Mode & Labels UI"
Cohesion: 0.19
Nodes (13): Served, weakestMode(), CLAIM_DESCRIPTION, SOURCE_TEXT, SourceLabel(), BannerSource, EmptyState(), ErrorState() (+5 more)

### Community 26 - "Frontend TS Config (Node)"
Cohesion: 0.12
Nodes (16): compilerOptions, allowImportingTsExtensions, erasableSyntaxOnly, lib, module, moduleDetection, noEmit, noFallthroughCasesInSwitch (+8 more)

### Community 27 - "Frontend App Shell"
Cohesion: 0.21
Nodes (10): App(), AppShell(), ScreenRoute, SCREENS, frontend_src_index, currentRoute(), useHashRoute(), frontend_src_styles_theme (+2 more)

### Community 28 - "Competitor Agent Live Collection"
Cohesion: 0.21
Nodes (12): live_collect(), collect(), NamedTuple, RawSignalCollector, Competitor Agent (Task 16) — Strands agent (Haiku) over web/HN/GitHub (P0) plus…, Entry point Task 21's orchestrator calls. `collect` does the actual tool-…, Returns a `collect` callable that runs a real Strands agent — pass this as…, A claim the schema dropped before Synthesis ever saw it. Not part of any entity… (+4 more)

### Community 29 - "GitHub Collector"
Cohesion: 0.28
Nodes (10): fetch_github_signals(), Fetch, Recent releases and open issues for owner/repo, mapped to Signals., _fake_fetch(), GitHub REST collector (Task 3) — releases/issues for a named competitor, mapped…, test_open_issue_becomes_a_negative_signal(), test_pull_requests_are_not_treated_as_issues(), test_release_becomes_a_positive_signal() (+2 more)

### Community 30 - "Day 3 Plan & Claim Labels"
Cohesion: 0.18
Nodes (12): Observed / Inferred / Assumed Labeling, Action Agent + ExecutionPack Build, Day 3 Plan, Evaluation Run Against Gold Set, Evidence Drawer 3-Level Fallback Wiring, Five P0 Screens Build, Value Model (saas_arr) Wiring, Account Evidence Integrity Check (+4 more)

### Community 31 - "Day 4 Plan & Repo Rules"
Cohesion: 0.17
Nodes (12): Repo History Must Match Event Window, Day 4 Plan, Demo Video Recording, Create Public Repo as First Commit, Submission Checklist, Writeup Deliverable, Disqualification Criteria, Judging Criteria (+4 more)

### Community 32 - "Orchestrator Tests"
Cohesion: 0.29
Nodes (11): _fake_competitor_collect(), _fake_market_collect(), _fake_semantic_check(), _fake_synthesis_collect_no_signals(), Orchestrator (Task 21) — wiring Market/Feedback/Competitor -> Synthesis ->…, The gap this module exists to close: Signal drops the raw source_url/…, _run(), test_full_run_produces_a_gate_passed_opportunity() (+3 more)

### Community 33 - "Day 1 Plan & Eligibility"
Cohesion: 0.18
Nodes (11): Eligibility Gate (India student, 18+), Bedrock Model Access Confirmation, Day 1 Plan, Eligibility Gate Step (Day 1 Step 1), GitHub REST + HN Algolia Integration, Skeleton AWS Deploy (Day 1), Live Tavily Round-Trip + Level-3 Fixture, AWS Builder Center (+3 more)

### Community 34 - "Competitor Agent Hooks"
Cohesion: 0.18
Nodes (9): _build_live_agent(), search_app_store(), search_github(), search_hn(), search_producthunt(), search_web(), _producthunt_token(), Wires a real strands.Agent with the web/HN/GitHub/App Store/Product Hunt tools… (+1 more)

### Community 35 - "Product Hunt Collector"
Cohesion: 0.31
Nodes (9): fetch_producthunt_signals(), Fetch, Most recent launch comments for a product slug, mapped to Signals., _fake_fetch(), Product Hunt GraphQL collector (Task 11) — launch comments for a named…, test_comment_body_lands_in_claim_text(), test_missing_post_returns_no_signals(), test_returns_task1_shaped_signals() (+1 more)

### Community 36 - "Rejected Ideas View Model"
Cohesion: 0.22
Nodes (9): RejectedIdeas(), CLAIM_TYPE_LABEL, FeedbackSummary, FeedbackTheme, fixFirstFlag(), RejectedIdea, ClaimType, Polarity (+1 more)

### Community 37 - "Day 2 Plan & Quality Gate"
Cohesion: 0.20
Nodes (10): Quality Gate (code), Day 2 Plan, DynamoDB Writes for Core Entities, Evidence Check Build, Feedback/Competitor-Signal Pipeline Build, Gold Set Labelling (80+20), Quality Gate + Ranker Build, Fix-First Rule (Section 9.3) (+2 more)

### Community 38 - "App Store Collector"
Cohesion: 0.38
Nodes (9): fetch_app_store_signals(), Fetch, Most recent customer reviews for app_id, mapped to Signals., _fake_fetch(), App Store RSS collector (Task 11) — reviews for a named competitor's mobile…, test_high_rating_becomes_a_positive_signal(), test_low_rating_becomes_a_negative_signal(), test_mid_rating_and_missing_rating_are_dropped() (+1 more)

### Community 39 - "Hackathon Rules Doc"
Cohesion: 0.20
Nodes (10): Amazon Fast-Track Interview Program, Bharat Builds Tour, Code of Conduct, First Commit Hackathon Requirements, First Commit Event, In-Person Bangalore Event, Prizes, Scholarships Program (+2 more)

### Community 40 - "Synthesis Agent Hooks"
Cohesion: 0.22
Nodes (7): _build_live_agent(), live_collect(), collect(), RawCandidateCollector, Wires a real strands.Agent with a single `emit_candidate_opportunity` tool and…, Returns a `collect` callable that runs a real Strands agent — pass this as…, _signals_prompt()

### Community 41 - "Feature Freeze & Scope Phases"
Cohesion: 0.22
Nodes (9): Feature Freeze (Day 3, 8pm), P0 Scope, P1 Scope, P2 Scope, PulseStack Simulator Build, P0-Before-P1/P2 Guardrail, Business Simulator (S1), MVP Scope (Section 20) (+1 more)

### Community 42 - "Frontend Dev Dependencies"
Cohesion: 0.22
Nodes (9): devDependencies, oxlint, @types/node, @types/react, @types/react-dom, typescript, vite, @vitejs/plugin-react (+1 more)

### Community 43 - "API Client Fetch Hooks"
Cohesion: 0.36
Nodes (7): fetchBusiness(), fetchRejectedIdeas(), LOADING, State, useServed(), goalCoverage(), InboxScreen()

### Community 44 - "PulseStack & Attribution Safety"
Cohesion: 0.25
Nodes (8): PulseStack (Simulated Business), Attribution Safety Check, b2b_saas_it Playbook, Koa Studio (P2 Business), PulseStack (Flagship Business, P0), Quality Gate: Quality/Safety Group, Sample-Business Policy (Section 3.3), Vertical-Agnostic Reasoning Engine Principle (Section 3.1)

### Community 45 - "Market Agent Hooks"
Cohesion: 0.25
Nodes (6): _build_live_agent(), search_github(), search_hn(), search_web(), Wires a real strands.Agent with the web/HN/GitHub tools and the §10.1a hooks.…, _tavily_api_key()

### Community 46 - "Demo Video & Track Rules"
Cohesion: 0.25
Nodes (8): Anveshan Precision Clip, Build It Track, Project Rules, Ship It Track, Anveshan Precision (P1 Business), AWS Architecture (Section 17), Demo Video Script (Section 21), Evaluation Metrics (Section 19)

### Community 47 - "Design Plan Critique"
Cohesion: 0.25
Nodes (8): Seven color tokens (bg/surface/ink/slate/muted/accent/on-slate-muted), Measured WCAG 2.1 AA contrast table, Pass 2 critique against the brief (shape not colour, no eyebrow caps, stratified radii), Outfit typeface, Google Fonts, system-ui fallback, SPA root entry (#root, main.tsx, Outfit font), Favicon: zigzag mark, seafoam mint on dark petrol slate, Hash routing (#/business, #/inbox, #/tokens), Contrast must be checked per surface, not once

### Community 48 - "Evidence Check & Action Agent Concepts"
Cohesion: 0.38
Nodes (7): Evidence Check (code), Action Agent, Agents Discover, Code Verifies, Humans Decide, Evidence Check, ExecutionPack Entity, Outreach Policy (Section 18.1), Screen 5: Execution Pack

### Community 49 - "Competitor Agent Signal Emission"
Cohesion: 0.43
Nodes (7): emit_competitor_signal(), _fake_collect(), One candidate claim exactly as the model's `emit_competitor_signal` tool call…, RawCompetitorSignal, _fake_competitor_collect(), §12 — evidence/source provenance kind., SourceKind

### Community 50 - "Live Pipeline Runner Script"
Cohesion: 0.40
Nodes (5): backend_agents, _business_context(), main(), Runs the real pipeline (Task 21's run_pipeline) against the live Bedrock…, uuid

### Community 51 - "Orchestrator Stub Lambda"
Cohesion: 0.47
Nodes (4): Orchestrator stub Lambda (Task 6) — the single Task state Step Functions…, run_stub(), Orchestrator stub Lambda (Task 6) — sanity check for the Step Functions Task…, test_returns_status_and_echoes_input()

### Community 52 - "Lambda Requirements & CodeUri"
Cohesion: 0.33
Nodes (6): backend/requirements-lambda.txt (pydantic, boto3), Globals.Function.CodeUri: ../ packaging config, Root requirements.txt points at requirements-lambda.txt, .samignore was always inert, Symlinked CodeUri reverted (git core.symlinks=false), Root requirements.txt (-r backend/requirements-lambda.txt)

### Community 53 - "Frontend Lint Config"
Cohesion: 0.33
Nodes (5): plugins, rules, react/only-export-components, react/rules-of-hooks, $schema

### Community 54 - "Frontend NPM Scripts"
Cohesion: 0.33
Nodes (6): scripts, build, dev, lint, preview, test

### Community 56 - "Issue Tracker Conventions"
Cohesion: 0.67
Nodes (4): Guardrail: repo history 17-20 Sept 2026, Issue tracker conventions (plan.md + todo.md), tasks/plan.md - full task detail, tasks/todo.md - checkbox tracker

## Ambiguous Edges - Review These
- `Guardrail: repo history 17-20 Sept 2026` → `tasks/plan.md - full task detail`  [AMBIGUOUS]
  CLAUDE.md · relation: references

## Knowledge Gaps
- **191 isolated node(s):** `$schema`, `plugins`, `react/rules-of-hooks`, `react/only-export-components`, `name` (+186 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 429 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **31 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Guardrail: repo history 17-20 Sept 2026` and `tasks/plan.md - full task detail`?**
  _Edge tagged AMBIGUOUS (relation: references) - confidence is low._
- **Why does `SourceKind` connect `Competitor Agent Signal Emission` to `DynamoDB DAO & Fixtures`, `Orchestrator Tests`, `Competitor Agent Hooks`, `Synthesis Agent`, `Product Hunt Collector`, `App Store & GitHub Collectors`, `App Store Collector`, `Feedback Labelling Pipeline`, `Market Agent`, `Orchestrator & PulseStack Simulator`, `Evidence Check`, `Market Agent Hooks`, `Orchestrator Pipeline Wiring`, `Competitor Agent`, `Bedrock Session Override`, `HN Collector`, `Competitor Agent Live Collection`, `GitHub Collector`?**
  _High betweenness centrality (0.054) - this node is a cross-community bridge._
- **Why does `Signal` connect `HN Collector` to `DynamoDB DAO & Fixtures`, `DynamoDB Entity Access Helpers`, `Feedback Labelling Pipeline`, `Synthesis Agent`, `Product Hunt Collector`, `App Store & GitHub Collectors`, `App Store Collector`, `Orchestrator Tests`, `Market Agent`, `Synthesis Agent Hooks`, `Orchestrator & PulseStack Simulator`, `Evidence Check`, `Competitor Agent`, `Orchestrator Pipeline Wiring`, `Bedrock Session Override`, `Competitor Agent Live Collection`, `GitHub Collector`?**
  _High betweenness centrality (0.032) - this node is a cross-community bridge._
- **Why does `Polarity` connect `HN Collector` to `DynamoDB DAO & Fixtures`, `Orchestrator Tests`, `Feedback Labelling Pipeline`, `Synthesis Agent`, `Product Hunt Collector`, `App Store & GitHub Collectors`, `App Store Collector`, `Market Agent`, `Orchestrator & PulseStack Simulator`, `Evidence Check`, `Competitor Agent`, `Orchestrator Pipeline Wiring`, `Bedrock Session Override`, `Competitor Agent Live Collection`, `GitHub Collector`?**
  _High betweenness centrality (0.021) - this node is a cross-community bridge._
- **Are the 44 inferred relationships involving `SourceKind` (e.g. with `_fake_collect()` and `RawCompetitorSignal`) actually correct?**
  _`SourceKind` has 44 INFERRED edges - model-reasoned connections that need verification._
- **Are the 29 inferred relationships involving `Signal` (e.g. with `assemble_synthesis_output()` and `build_opportunity()`) actually correct?**
  _`Signal` has 29 INFERRED edges - model-reasoned connections that need verification._
- **Are the 30 inferred relationships involving `Polarity` (e.g. with `build_signal()` and `build_signal()`) actually correct?**
  _`Polarity` has 30 INFERRED edges - model-reasoned connections that need verification._