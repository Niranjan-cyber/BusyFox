# Graph Report - BusyFox  (2026-09-17)

## Corpus Check
- 73 files · ~149,026 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 166 nodes · 223 edges · 19 communities (11 shown, 8 thin omitted)
- Extraction: 94% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 12 edges (avg confidence: 0.86)
- Token cost: 0 input · 181,473 output

## Community Hubs (Navigation)
- Quality Gate & Provenance
- Agent Architecture & Sources
- Eligibility & Event Rules
- Day 3: Action & Execution
- Evidence Labeling & Fallback Ladder
- Core Docs & Lane Ownership
- Verification Philosophy & AWS Story
- Day 1: Foundations
- Day 4: Submission
- Day 2: Pipeline & Ranking
- Scope Discipline (P0/P1/P2)
- Product Naming
- idea-refine Script
- Amplify Hosting
- CREDITS.md Requirement
- DynamoDB + S3 Storage
- LEARNING.md Journal
- opp_ ID Convention
- Submission Artifacts

## God Nodes (most connected - your core abstractions)
1. `Opportunity Entity` - 14 edges
2. `Day 2 Plan` - 9 edges
3. `Market Agent` - 9 edges
4. `Agent Runtime Contract (Section 10.1a)` - 9 edges
5. `Implementation Plan: Opportunity Engine (tasks/plan.md)` - 9 edges
6. `Day 3 Plan` - 8 edges
7. `First Commit Event` - 8 edges
8. `Synthesis Agent` - 8 edges
9. `Task 1: Core Entity Schema` - 8 edges
10. `Day 1 Plan` - 7 edges

## Surprising Connections (you probably didn't know these)
- `Phase 1 Checklist` --shares_data_with--> `Day 1 Plan`  [INFERRED]
  tasks/todo.md → BUILD_PLAN.md
- `Phase 2: Day 2 Milestones` --shares_data_with--> `Day 2 Plan`  [INFERRED]
  tasks/plan.md → BUILD_PLAN.md
- `Phase 3: Day 3 Milestones` --shares_data_with--> `Day 3 Plan`  [INFERRED]
  tasks/plan.md → BUILD_PLAN.md
- `P0 Scope` --shares_data_with--> `MVP Scope (Section 20)`  [INFERRED]
  BUILD_PLAN.md → opportunity_engine_prd_v8.md
- `P1 Scope` --shares_data_with--> `MVP Scope (Section 20)`  [INFERRED]
  BUILD_PLAN.md → opportunity_engine_prd_v8.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Core Loop: Discover to Track** — opportunity_engine_prd_v8_orchestrator, opportunity_engine_prd_v8_market_agent, opportunity_engine_prd_v8_synthesis_agent, opportunity_engine_prd_v8_evidence_check, opportunity_engine_prd_v8_quality_gate_ranker, opportunity_engine_prd_v8_action_agent [EXTRACTED 1.00]
- **Provenance Chain Entities** — opportunity_engine_prd_v8_sourcedocument, opportunity_engine_prd_v8_evidence, opportunity_engine_prd_v8_claim, opportunity_engine_prd_v8_opportunity [EXTRACTED 1.00]
- **Hard Event Constraints (Disqualification Risk)** — agents_eligibility_gate, agents_repo_history_rule, agents_submission_artifacts [EXTRACTED 1.00]

## Communities (19 total, 8 thin omitted)

### Community 0 - "Quality Gate & Provenance"
Cohesion: 0.11
Nodes (27): No Composite Opportunity Score, Provenance Chain: SourceDocument to Opportunity, Synthesis Agent Build, Business Entity, Claim Entity, Evidence Entity, Evidence Diversity Check, Mandatory Fields Gate (+19 more)

### Community 1 - "Agent Architecture & Sources"
Cohesion: 0.13
Nodes (22): GitHub REST API Source, Hacker News (Algolia) Source, Five-Field Agent Runtime Contract, signals[] Schema Limit for Research Agents, Step Functions Orchestrator, Strands Agents SDK, Synthesis Agent, Tavily Web Search (+14 more)

### Community 2 - "Eligibility & Event Rules"
Cohesion: 0.12
Nodes (16): Eligibility Gate (India student, 18+), Eligibility Gate Step (Day 1 Step 1), Amazon Fast-Track Interview Program, AWS Builder Center, Bharat Builds Tour, Code of Conduct, First Commit Hackathon Requirements, Eligibility Requirements (+8 more)

### Community 3 - "Day 3: Action & Execution"
Cohesion: 0.17
Nodes (15): Action Agent + ExecutionPack Build, Anveshan Precision Clip, Day 3 Plan, Evaluation Run Against Gold Set, Five P0 Screens Build, Value Model (saas_arr) Wiring, Action Agent, Anveshan Precision (P1 Business) (+7 more)

### Community 4 - "Evidence Labeling & Fallback Ladder"
Cohesion: 0.14
Nodes (14): Observed / Inferred / Assumed Labeling, PulseStack (Simulated Business), Evidence Drawer 3-Level Fallback Wiring, Account Evidence Integrity Check, Attribution Safety Check, Competitor Entity, Data Acquisition Risk: Live to Cached to Demo Fixture Ladder, Observed/Inferred/Assumed Labeling (Section 13.3) (+6 more)

### Community 5 - "Core Docs & Lane Ownership"
Cohesion: 0.15
Nodes (11): Part B Two-Person Working Cadence, Opportunity Engine PRD v8, Implementation Plan: Opportunity Engine (tasks/plan.md), Lane B: Frontend/UX, Lane C: Floating, Phase 2: Day 2 Milestones, Phase 3: Day 3 Milestones, Task 10: PulseStack Simulator (+3 more)

### Community 6 - "Verification Philosophy & AWS Story"
Cohesion: 0.18
Nodes (11): Evidence Check (code), Quality Gate (code), Build It Track, Project Rules, Ship It Track, Agents Discover, Code Verifies, Humans Decide, AWS Architecture (Section 17), Demo Video Script (Section 21) (+3 more)

### Community 7 - "Day 1: Foundations"
Cohesion: 0.18
Nodes (11): Repo History Must Match Event Window, Bedrock Model Access Confirmation, Day 1 Plan, GitHub REST + HN Algolia Integration, Create Public Repo as First Commit, Skeleton AWS Deploy (Day 1), Live Tavily Round-Trip + Level-3 Fixture, Disqualification Criteria (+3 more)

### Community 8 - "Day 4: Submission"
Cohesion: 0.22
Nodes (9): Day 4 Plan, Demo Video Recording, Submission Checklist, Writeup Deliverable, Submission Requirements, AWS Use Must Be Visible in Video, Submission: Three Artifacts, Phase 4: Day 4 Milestones (+1 more)

### Community 9 - "Day 2: Pipeline & Ranking"
Cohesion: 0.25
Nodes (8): Day 2 Plan, DynamoDB Writes for Core Entities, Evidence Check Build, Feedback/Competitor-Signal Pipeline Build, Gold Set Labelling (80+20), Quality Gate + Ranker Build, Fix-First Rule (Section 9.3), Priority Rule Table (Section 13.1)

### Community 10 - "Scope Discipline (P0/P1/P2)"
Cohesion: 0.25
Nodes (8): Feature Freeze (Day 3, 8pm), P0 Scope, P1 Scope, P2 Scope, PulseStack Simulator Build, P0-Before-P1/P2 Guardrail, MVP Scope (Section 20), PulseStack Simulator (Section 8)

## Ambiguous Edges - Review These
- `BusyFox (Repo/Placeholder Name)` → `Opportunity Engine (Product, Placeholder Name)`  [AMBIGUOUS]
  README.md · relation: conceptually_related_to

## Knowledge Gaps
- **49 isolated node(s):** `idea-refine.sh script`, `idea-refine.sh script`, `CREDITS.md Requirement`, `LEARNING.md (Learning Journal)`, `Three Submission Artifacts` (+44 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 60 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `BusyFox (Repo/Placeholder Name)` and `Opportunity Engine (Product, Placeholder Name)`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **Why does `Opportunity Entity` connect `Quality Gate & Provenance` to `Day 3: Action & Execution`, `Evidence Labeling & Fallback Ladder`, `Verification Philosophy & AWS Story`?**
  _High betweenness centrality (0.155) - this node is a cross-community bridge._
- **Why does `Implementation Plan: Opportunity Engine (tasks/plan.md)` connect `Core Docs & Lane Ownership` to `Quality Gate & Provenance`, `Day 4: Submission`, `Evidence Labeling & Fallback Ladder`?**
  _High betweenness centrality (0.134) - this node is a cross-community bridge._
- **Why does `First Commit Event` connect `Eligibility & Event Rules` to `Day 4: Submission`, `Verification Philosophy & AWS Story`?**
  _High betweenness centrality (0.133) - this node is a cross-community bridge._
- **What connects `idea-refine.sh script`, `idea-refine.sh script`, `CREDITS.md Requirement` to the rest of the system?**
  _49 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Quality Gate & Provenance` be split into smaller, more focused modules?**
  _Cohesion score 0.11396011396011396 - nodes in this community are weakly interconnected._
- **Should `Agent Architecture & Sources` be split into smaller, more focused modules?**
  _Cohesion score 0.12554112554112554 - nodes in this community are weakly interconnected._