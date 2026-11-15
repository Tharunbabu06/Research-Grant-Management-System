> Submission inventory note (15 November 2026): this is the supplied Chapter 13 Markdown conversion. Its original DOCX and three referenced media assets were not present in the repository. The converter claims below describe the original conversion, not a verified inventory of this checkout. See the root submission checklist.

# Agentic AI Worklets — 14-Lab Build Book


> **Source:** `Agentic_AI_15_Worklets_14Lab_Build_Book.docx`

> **Conversion:** DOCX → Markdown with document-order text, tables, and extracted images preserved.

> **Completeness:** All document-body paragraphs and tables were processed; all embedded media files were extracted.


CHAPTER 13

Research Grant Management System

From funding-call discovery to a compliant, Dean-R&D-approved submission package.

Human authority: the PI / research office.   Primary output: grant proposal and compliance package.

The 14-Lab Method (Recap)

Every worklet in this book is built the same way: as a coordinator-plus-workers agentic system that is grown, one capability at a time, through 14 hands-on labs. This chapter is self-contained — it restates the method, the node-graph legend and the pseudocode conventions before applying them to this worklet — so it can be handed to a team on its own.

The guiding design principle is constant across all worklets: agents draft and flag; a named human approves. No worklet takes a consequential action autonomously — the human authority named in this chapter signs off before anything is published or sent.

The four phases

| Phase | What it establishes |
| --- | --- |
| Phase A — Foundations (Labs 1–6) | Turn a single agent loop into a tool-using, skill-driven, memory-backed agent that reaches all data through one connector and runs inside a governed runtime with an audit log. |
| Phase B — Orchestration (Labs 7–8) | Wire the specialist agents into an explicit node graph, then parallelise the per-unit work and merge the best results. |
| Phase C — Applied reliability (Labs 9–11) | Ground every output in evidence, make the pipeline self-healing on validation failure, and treat the spec as a tested build. |
| Phase D — Governance & capstone (Labs 12–14) | Add safety, approval, evaluation and rollback; plug in domain specialists; integrate everything into a deployed, team-owned system. |

Reading the node graph

- Navy — the apniLeap AURA Coordinator: owns the run-state, plan, budgets and audit log.

- Light blue — specialist agents, each with one responsibility and a typed message contract.

- Amber — the human review gate: a hard stop; the named human is the final authority.

- Green — governed publish/act: versioned, auditable, reversible.

- Dashed grey — coordinator oversight of every agent; a red back-edge is validation → regenerate.

Pseudocode conventions

- Pseudocode is language-neutral: Coordinator orchestrates; Agent.step(ctx) is one specialist doing its job on the shared run-context; a human gate returns approve / edit / override.

- The blueprint/plan is locked before work begins; validation is a hard gate; the human approves before publish.

13.1  Worklet Overview

Faculty miss relevant funding calls scattered across agency websites and mailing lists; literature and novelty framing take days; and proposal drafts, budgets, and compliance checklists are prepared in silos with no shared source of truth.

This worklet proposes a Research Grant Management System, owned by the Dean R&D office, that discovers matched calls, compiles a literature/novelty summary, drafts the proposal, prepares an agency-compliant budget, runs a compliance check, and packages the submission — turning a scattered, deadline-driven process into one auditable, agency-compliant pipeline.

Stakeholders: Faculty, HoD, Dean R&D, Research Office

Problems heard

- Faculty miss relevant funding calls because listings are scattered across agency websites and mailing lists.

- Literature review and novelty framing take days of manual searching.

- Proposal drafts, budgets, and compliance checklists are prepared in silos with no shared source of truth.

- Dean R&D has no consolidated view of which proposals are in progress, their deadlines, or compliance status.

- Compliance issues surface late, close to the submission deadline.

13.2  Target Final Solution (Definition of Done)

The capstone (Lab 14) is complete when, for a real case, the worklet turns a request into a validated, evidence-grounded grant proposal and compliance package that passes every check, is reviewed and approved by the PI / research office, and is published with a full audit trail — with light human edits, not a rewrite.

Capabilities

| Capability | What it means |
| --- | --- |
| Faculty | Faculty specifies their research area, target funding types, and consent to use their profile/publication history for matching. |
| The | The Funding Discovery Agent surfaces matched calls while the Literature Review Agent compiles a related-work and novelty summary, in parallel. |
| The | The Proposal Drafting Agent drafts the narrative using the matched call's requirements and the literature summary. |
| The | The Budget Planning Agent prepares an agency-compliant budget while the Compliance Checking Agent runs an eligibility/format check, in parallel. |
| The | The Submission Agent packages the proposal, budget, and compliance checklist into the agency's required format. |
| Dean | Dean R&D/HoD/Research Office reviews the package, approves or requests corrections, and authorizes final submission. |

Success metrics (KPIs)

- 100% of validation checks pass before the PI / research office review (e.g. budget totals reconcile).

- Every grant proposal and compliance package is grounded in the funder's guidelines and institutional policy, with an evidence record.

- Zero consequential actions without the PI / research office's approval; a complete audit trail and one-click rollback.

13.3  System at a Glance — the Node Graph

A coordinator-plus-workers system: the apniLeap AURA Coordinator holds the plan, run-state and audit log and drives the pipeline; validation is a hard gate; the human review is a hard stop before publish.

Figure 13 — the Research Grant Management System agent graph. Amber = human gate; green = governed publish; dashed = coordinator oversight.

End-to-end flow

- Faculty specifies their research area, target funding types, and consent to use their profile/publication history for matching.

- The Funding Discovery Agent surfaces matched calls while the Literature Review Agent compiles a related-work and novelty summary, in parallel.

- The Proposal Drafting Agent drafts the narrative using the matched call's requirements and the literature summary.

- The Budget Planning Agent prepares an agency-compliant budget while the Compliance Checking Agent runs an eligibility/format check, in parallel.

- The Submission Agent packages the proposal, budget, and compliance checklist into the agency's required format.

- Dean R&D/HoD/Research Office reviews the package, approves or requests corrections, and authorizes final submission.

13.4  Agent Roster — Roles, Communication & Guardrails

| # | Agent | Role & communication | Guardrails |
| --- | --- | --- | --- |
| 0 | apniLeap AURA Coordinator | Receives the faculty/Dean R&D prompt command, checks permissions, creates the run plan, initializes agents, monitors state. | Never bypass human approval; enforce data scope, audit logging, source citation, and exception routing. |
| 1 | Funding Discovery Agent | Surfaces funding calls (DST, SERB, AICTE, industry CSR) matched to area, eligibility, and deadline, in parallel with B. | Surface only verified agencies; never present an expired call as active; cite source and deadline. |
| 2 | Literature Review Agent | Compiles related work and a novelty/gap summary from approved databases, in parallel with A. | Cite every claim to a verifiable source; never fabricate a reference; flag thin literature rather than overstating novelty. |
| 3 | Proposal Drafting Agent | Drafts objectives, methodology, and timeline using the call requirements and literature summary. | Draft within provided scope; mark AI text as a draft; never present preliminary findings as established. |
| 4 | Budget Planning Agent | Prepares an itemized budget per agency norms and ceilings, in parallel with E. | Use approved templates/ceilings; flag line items exceeding norms; never adjust figures without showing the basis. |
| 5 | Compliance Checking Agent | Checks eligibility, formatting, and documentation against the agency's guidelines, in parallel with D. | Check against the specific call's guidelines; never mark compliant without evidence; flag ambiguous requirements. |
| 6 | Submission Agent | Packages the proposal, budget, and checklist into the agency's required format. | Do not submit without Dean R&D/HoD/Research Office sign-off; keep a version-controlled package; re-trigger review on any post-sign-off change. |
| 7 | Dean R&D / HoD / Research Office Review | Reviews the package, approves or requests corrections, and authorizes final submission. | Dean R&D/HoD/Research Office decision is the final authority for authorizing submission. |

13.5  Agent Interconnections (Message Map)

How the agents are wired — the payloads that flow between them and when. The last rows show the human gate and governed publish.

| From | To | Message / payload | When |
| --- | --- | --- | --- |
| Coordinator | Funding Discovery Agent | run-context + task | run start |
| Funding Discovery Agent | Literature Review Agent | state / partial result | in pipeline |
| Literature Review Agent | Proposal Drafting Agent | state / partial result | in pipeline |
| Proposal Drafting Agent | Budget Planning Agent | state / partial result | in pipeline |
| Budget Planning Agent | Compliance Checking Agent | state / partial result | in pipeline |
| Compliance Checking Agent | Submission Agent | state / partial result | in pipeline |
| Submission Agent | Dean R&D / HoD / Research Office Review | state / partial result | in pipeline |
| Dean R&D / HoD / Research Office Review | The Pi / Research Office gate | draft grant proposal and compliance package + evidence | for review |
| The Pi / Research Office gate | Coordinator | approve \| edit \| override | human decision |
| Coordinator | Governance / Publish | final grant proposal and compliance package (versioned) | on approval |

13.6  Data Model

| Entity | Key fields |
| --- | --- |
| Faculty research profile | Research area, eligibility, and publication history for matching. |
| Funding call | Verified agency calls with deadlines and requirements. |
| Literature & novelty | Related-work and gap summary with citations. |
| Proposal & budget | Draft narrative and an agency-compliant itemized budget. |
| Compliance & submission | Compliance checklist and the packaged submission, pending authorization. |

13.7  Solution Paradigm — Pseudocode

Orchestrator (the whole run)

| function run_research_grant_management_system(request):<br>ctx = Coordinator.new_run(request)        # isolated, checkpointed<br>plan = Coordinator.build_plan(request)     # locked before work begins<br>ctx = FundingDiscoveryAgent.step(ctx, plan)<br>ctx = LiteratureReviewAgent.step(ctx, plan)<br>ctx = ProposalDraftingAgent.step(ctx, plan)<br>ctx = BudgetPlanningAgent.step(ctx, plan)<br>ctx = ComplianceCheckingAgent.step(ctx, plan)<br>ctx = SubmissionAgent.step(ctx, plan)<br>ctx = DeanRDHoDResearchOfficeReview.step(ctx, plan)<br>report = ValidationAgent.validate(ctx, plan)   # hard gate<br>while not report.passed and attempts < MAX:    # self-healing (Lab 10)<br>Coordinator.regenerate(report.failing); report = validate(ctx, plan)<br>draft = assemble(ctx)                          # the grant proposal and compliance package<br>decision = TheGate.review(draft)  # HUMAN — final authority<br>if decision.approved:<br>final = apply(decision.edits, draft)<br>Governance.publish(final, version=next()); Audit.log_all()<br>return final |
| --- |

Validation (the acceptance gate)

| function ValidationAgent.validate(ctx, plan):<br>checks = [<br>('budget totals reconcile', test_0(ctx, plan)),<br>('eligibility and compliance are met', test_1(ctx, plan)),<br>('no submission happens without PI approval', test_2(ctx, plan)),<br>('every deadline is tracked', test_3(ctx, plan)),<br>]<br>failing = [n for n,ok in checks if not ok]<br>return Report(passed = not failing, failing = failing,<br>diagnosis = explain(failing)) |
| --- |

Connector (one governed surface for all sources)

| connector.expose:<br>read('funding calls & guidelines')<br>read('budget & personnel data')<br>read('compliance rules')<br>agents.use(connector)   # no agent touches a source directly |
| --- |

Worked example — one proposal / grant, end to end

How a single proposal / grant travels through the pipeline, from plan to a validated, approved and published grant proposal and compliance package. This is the level of traceability every proposal / grant should have.

| Stage | What happens |
| --- | --- |
| Plan / slot | The coordinator locks the plan and picks one proposal / grant to work — its constraints fixed before any content is chosen. |
| Source candidate | A retrieval agent proposes a candidate for this proposal / grant from funding calls & guidelines, with provenance. |
| Grounded candidate | A generation agent produces a fresh candidate grounded in the funder's guidelines and institutional policy, attaching an evidence record (source, scope, tags). |
| Screen & select | Candidates are calibrated and screened; the best-aligned one that satisfies the plan is selected, the rest logged. |
| Validation | The result is checked (budget totals reconcile; no submission happens without PI approval); on failure only this proposal / grant is regenerated. |
| Human review | The Pi / Research Office sees the draft grant proposal and compliance package with its evidence and validation report, and approves, edits or overrides. |
| Publish & audit | On approval the governed publish versions the grant proposal and compliance package, records the audit trail, and updates history for future runs. |

13.8  Hybrid Execution Methodology

How the coordinator runs each stage — what is human-gated, what runs in parallel, what is sequential.

| Stage | Execution mode & coordinator behavior |
| --- | --- |
| Gate 1: profile intake | Sequential — start only after research area, funding type, and consent are provided. |
| Parallel discovery & review | Parallel — Funding Discovery surfaces calls while Literature Review compiles the novelty summary. |
| Drafting | Sequential — drafting runs after both the call match and literature summary are available. |
| Parallel budget & compliance | Parallel — Budget Planning and Compliance Checking both run against the drafted proposal. |
| Packaging | Sequential — the Submission Agent assembles the package after budget and compliance are available. |
| Stakeholder approval | Sequential — Dean R&D/HoD/Research Office approves and authorizes; corrections route back. |
| Dashboard update | Parallel after approval — grants dashboard (pipeline, deadlines, compliance) publishes once approved. |

13.9  Dashboard Template

What the PI / research office sees to review, approve and monitor.

| Panel | Shows |
| --- | --- |
| Funding pipeline | Matched calls, deadlines, and proposal status. |
| Proposal & literature | Draft narrative and novelty summary with citations. |
| Budget & compliance | Itemized budget against ceilings and the compliance checklist. |
| Submission package | Version-controlled package with authorization status. |

13.10  The 14-Lab Evolution

Each lab is a working increment that adds one capability to this worklet and activates specific nodes. Ship the deliverable and pass acceptance before advancing — by Lab 14 they compose into the deployed grant proposal and compliance package system.

Lab 1 — Agent vs Chatbot — the grant proposal and compliance package planner loop

Phase: A · Foundations     Goal: Establish the agent loop (clarify → plan → revise) instead of a one-shot chatbot answer.

What it adds to this worklet.  A minimal planner that clarifies the request, proposes a plan for producing the grant proposal and compliance package, and revises on feedback — the seed this worklet grows from.

| Inputs | Outputs | Agents / nodes | Deliverable & acceptance |
| --- | --- | --- | --- |
| Free-text request; core parameters. | A clarified request + an editable outline plan for the grant proposal and compliance package. | Coordinator (loop only). | A notebook agent that clarifies, plans and revises a grant proposal and compliance package outline.  Accept: Given a vague request it asks at least two clarifying questions and yields a coherent, editable plan. |

Nodes activated.  Coordinator loop (no specialist nodes yet).

Pitfall to avoid.  Don't answer in one shot — without clarify/revise it's a chatbot, not an agent.

Lab 1 — plan & revise

| req  = clarify(user_request)         # ask until inputs complete<br>plan = propose_plan(req)             # outline for the grant proposal and compliance package<br>while user.wants_changes(plan): plan = revise(plan, user.feedback)<br>return plan                          # not final — a structured plan |
| --- |

Lab 2 — Tool-Using Agent — call data & compute

Phase: A · Foundations     Goal: Give the agent tools it must call to act, rather than answering from memory.

What it adds to this worklet.  Readers for funding calls & guidelines and budget & personnel data, plus a domain calculator/checker, so the planner acts on real data.

| Inputs | Outputs | Agents / nodes | Deliverable & acceptance |
| --- | --- | --- | --- |
| funding calls & guidelines; budget & personnel data; parameters. | Verified computed values and parsed inputs. | Coordinator + tool layer. | An agent that reads funding calls & guidelines and computes/validates through typed tools.  Accept: Key numbers and lookups always go through tools, never hand-done in the prompt. |

Nodes activated.  Tool layer feeding the early data agents.

Pitfall to avoid.  Never assert a fact in the prompt that a tool should verify.

Lab 2 — typed tools

| a = tool.read('funding calls & guidelines')<br>b = tool.read('budget & personnel data')<br>v = tool.compute(a, b)<br>assert v.valid |
| --- |

Lab 3 — Skill Creation — reusable plan & format skills

Phase: A · Foundations     Goal: Package repeatable capability as reusable, schema-typed skills.

What it adds to this worklet.  A plan/blueprint skill and a formatting skill that renders the grant proposal and compliance package — both reusable across cases.

| Inputs | Outputs | Agents / nodes | Deliverable & acceptance |
| --- | --- | --- | --- |
| Parsed inputs; template spec. | A locked plan object; a formatted grant proposal and compliance package shell. | Planning and assembly emerge as skills. | Two callable skills with schemas, invoked by the agent.  Accept: The same skill works for two different cases without code changes. |

Nodes activated.  Plan node + Assembly node (as skills).

Pitfall to avoid.  Keep skills case-agnostic and typed; hard-coding one case breaks reuse.

Lab 3 — skill interface

| skill plan(inputs) -> Plan:  return expand(inputs).lock()<br>skill format_grant(result, template) -> Document |
| --- |

Lab 4 — Memory & Retrieval — state vs stored

Phase: A · Foundations     Goal: Separate short-term run state from long-term stored knowledge.

What it adds to this worklet.  Session state (the current draft) vs stored reference — funding calls & guidelines and the history of past proposal / grants — retrieved by tags and by similarity.

| Inputs | Outputs | Agents / nodes | Deliverable & acceptance |
| --- | --- | --- | --- |
| funding calls & guidelines; history of prior proposal / grants; current draft. | Tag- and similarity-based retrieval. | Retrieval agent; foundations of later screening. | Retrieval over the store + history with tag filters and embedding similarity.  Accept: For a given task, retrieval returns correctly-tagged candidates and similar prior items. |

Nodes activated.  Retrieval node; seeds validation/no-repeat.

Pitfall to avoid.  Don't conflate run state with the archive — mixing them corrupts the baseline.

Lab 4 — memory split

| state.draft = candidate                       # short-term<br>hits  = retrieve(store, tags)                 # long-term<br>prior = retrieve(history, embed(candidate), k=5)  # similarity |
| --- |

Lab 5 — MCP-Style Connector — one server for all sources

Phase: A · Foundations     Goal: Expose every data source through one typed connector.

What it adds to this worklet.  A single connector fronting funding calls & guidelines, budget & personnel data and compliance rules so every agent reaches data the same governed way.

| Inputs | Outputs | Agents / nodes | Deliverable & acceptance |
| --- | --- | --- | --- |
| The worklet's data sources. | A uniform, typed tool surface. | Connector used by all data-facing agents. | A connector server with typed endpoints and auth; agents call only through it.  Accept: All data access goes through the connector; swapping a source needs no agent change. |

Nodes activated.  Connector under the data agents.

Pitfall to avoid.  No agent should touch a source directly; a bypass defeats governance later.

Lab 5 — connector

| connector.expose:<br>read('funding calls & guidelines')<br>read('budget & personnel data')<br>read('compliance rules')<br>agents.use(connector)   # no agent touches a source directly |
| --- |

Lab 6 — Runtime — skills, tools, memory, audit

Phase: A · Foundations     Goal: Run the agent inside a controlled runtime with a full audit log.

What it adds to this worklet.  A runtime binding skills + tools + memory behind the loop, enforcing budgets and approval gates and logging every step — the backbone later labs plug into.

| Inputs | Outputs | Agents / nodes | Deliverable & acceptance |
| --- | --- | --- | --- |
| Skills (Lab 3), connector (Lab 5), memory (Lab 4). | A governed run with audit + checkpoints. | Coordinator hardened into the runtime controller. | Runtime wrapping the agent: budgets, gates, checkpoint/resume, audit log.  Accept: Every action is logged with inputs/outputs; a crashed run resumes from its last checkpoint. |

Nodes activated.  Coordinator runtime around all nodes.

Pitfall to avoid.  Log inputs and outputs, not just messages; checkpoint before risky steps or resume loses state.

Lab 6 — controlled loop

| run = Runtime(budget=B, gates=[publish])<br>for step in agent.loop():<br>audit.log(step.intent, step.action, step.result)<br>if step.risky: wait_for_approval(step)<br>checkpoint(run.state) |
| --- |

Lab 7 — Agentic Node Graph — the full pipeline

Phase: B · Orchestration     Goal: Wire the specialist agents into one explicit graph with state and branching.

What it adds to this worklet.  The complete pipeline as a node graph: Funding Discovery Agent, Literature Review Agent, Proposal Drafting Agent → … → the PI / research office gate → publish, with a validation → regenerate back-edge.

| Inputs | Outputs | Agents / nodes | Deliverable & acceptance |
| --- | --- | --- | --- |
| All Phase-A skills/agents. | An executable graph producing a first end-to-end draft. | All core agents connected (see this chapter's node graph). | A graph runner that produces a full grant proposal and compliance package draft end to end.  Accept: One command yields a validated grant proposal and compliance package draft end to end. |

Nodes activated.  All core nodes + the back-edge.

Pitfall to avoid.  Bound the retry edge — an unbounded regenerate loop can spin forever.

Lab 7 — graph

| graph.chain(ingest -> plan -> workers -> validate)<br>graph.edge(validate --fail--> workers)   # bounded retry<br>graph.edge(validate --pass--> assemble -> gate -> publish) |
| --- |

Lab 8 — Parallel Swarm — many proposal / grants, then merge

Phase: B · Orchestration     Goal: Parallelise the per-unit work and select the best.

What it adds to this worklet.  Several worker agents process proposal / grants in parallel; a merge/selector picks the best per the plan — cutting latency and improving quality.

| Inputs | Outputs | Agents / nodes | Deliverable & acceptance |
| --- | --- | --- | --- |
| Locked plan; per-unit work items. | Best-of-N results merged into one compliant output. | Parallel workers + a Merge selector under the Coordinator. | A fan-out/fan-in that processes all units and merges by alignment to the plan.  Accept: Parallel run matches or beats sequential quality at lower wall-clock time. |

Nodes activated.  Parallel worker fan-out + merge.

Pitfall to avoid.  Merge strictly by plan alignment; picking the 'nicest' output quietly breaks coverage.

Lab 8 — fan-out/in

| results = parallel_map(process_proposal, plan.units)<br>output  = merge(results, key=alignment_to(plan)) |
| --- |

Lab 9 — Deep Research — ground & evidence

Phase: C · Applied reliability     Goal: Ground every output in cited, in-scope evidence.

What it adds to this worklet.  For each proposal / grant the agent builds an evidence record grounded in the funder's guidelines and institutional policy, so validity is auditable and out-of-scope content can't slip through.

| Inputs | Outputs | Agents / nodes | Deliverable & acceptance |
| --- | --- | --- | --- |
| the funder's guidelines and institutional policy; candidate outputs. | An evidence record per unit; a paper-level evidence table. | Generation + grounding step feeding Validation. | Each candidate carries an evidence record; an evidence table is produced.  Accept: Every output maps to an in-scope source; ungrounded candidates are rejected. |

Nodes activated.  Grounding step into the validation check.

Pitfall to avoid.  Require a real source; a plausible-sounding but ungrounded item must be rejected, not kept.

Lab 9 — grounding

| for c in candidates:<br>ev = research(c, source="the funder's guidelines and institutional policy")<br>if not ev.in_scope: reject(c)<br>c.evidence = ev |
| --- |

Lab 10 — Ops Resilience — validate, diagnose, fix

Phase: C · Applied reliability     Goal: Make the pipeline self-healing when validation fails.

What it adds to this worklet.  When a check fails (budget totals reconcile; eligibility and compliance are met), the agent diagnoses the exact failing constraint and regenerates only the offending part.

| Inputs | Outputs | Agents / nodes | Deliverable & acceptance |
| --- | --- | --- | --- |
| Validation report; current output. | A repaired, passing output with a diagnosis log. | Validation agent + Coordinator's regenerate loop. | Failure-injection tests showing automatic diagnosis and targeted repair.  Accept: Injected faults are detected and fixed within the retry budget. |

Nodes activated.  Validation node + self-healing loop.

Pitfall to avoid.  Regenerate only the failing part — rebuilding everything wastes budget and churns good work.

Lab 10 — diagnose & fix

| report = validate(output, plan)<br>while not report.passed and attempts < BUDGET:<br>regenerate(report.failing); report = validate(output, plan)<br>if not report.passed: escalate(report)   # to the human |
| --- |

Lab 11 — SDLC Factory — spec → tested output

Phase: C · Applied reliability     Goal: Treat the plan as a spec and the output as a tested implementation.

What it adds to this worklet.  The worklet becomes a factory: plan in, a grant proposal and compliance package out that provably passes an automated acceptance suite before the PI / research office sees it.

| Inputs | Outputs | Agents / nodes | Deliverable & acceptance |
| --- | --- | --- | --- |
| The locked plan (spec); the acceptance suite. | A result plus a green test report. | Validation as the test harness; Coordinator as the build. | A 'build' command: plan → grant proposal and compliance package + passing acceptance report.  Accept: No grant proposal and compliance package advances to the PI / research office without a fully passing acceptance report. |

Nodes activated.  Validation gates the whole graph.

Pitfall to avoid.  The acceptance suite is the gate; never let a result skip to the human without a green report.

Lab 11 — spec→artifact

| artifact = build(plan)                 # graph run (Lab 7/8/10)<br>report   = acceptance_suite(artifact, plan)<br>require report.all_pass                # gate before human review |
| --- |

Lab 12 — Safety & Governance — approval, eval, rollback

Phase: D · Governance & capstone     Goal: Add confidentiality, approval, evaluation and rollback.

What it adds to this worklet.  Access control and confidentiality, the the PI / research office approval gate as a hard stop, evaluation metrics, versioning and one-click rollback.

| Inputs | Outputs | Agents / nodes | Deliverable & acceptance |
| --- | --- | --- | --- |
| Draft-vs-approved states; role permissions; metrics. | A governed, reversible release. | Governance & Audit agent; the human gate formalised. | Approval workflow + metrics + rollback, with confidentiality controls.  Accept: Only the PI / research office-approved results publish; any release rolls back cleanly. |

Nodes activated.  Human gate + governance node.

Pitfall to avoid.  Confidentiality and rollback are requirements, not extras.

Lab 12 — governed release

| require actor.can_approve and out.status=='draft'<br>final = apply(human.edits, out); final.status='approved'<br>governance.publish(final, version=v+1); metrics.record(...)<br>on rollback(v): restore(version=v) |
| --- |

Lab 13 — Discipline-Specific Agents — domain specialisation

Phase: D · Governance & capstone     Goal: Specialise the worklet to its domain variants.

What it adds to this worklet.  Pluggable specialists — funder profiles (government, industry, international) — so outputs match the specific style and constraints of each case.

| Inputs | Outputs | Agents / nodes | Deliverable & acceptance |
| --- | --- | --- | --- |
| Domain profile; the work item. | Domain-appropriate outputs with correct schemes. | Specialist plugged into the generation node. | A specialist producing domain-correct grant proposal and compliance packages.  Accept: Specialist outputs use valid domain patterns and produce checkable results. |

Nodes activated.  Specialist into the generation node.

Pitfall to avoid.  Every specialist output needs a checkable scheme; clever but vague outputs are unusable.

Lab 13 — specialist plug-in

| specialist = registry.get(domain)<br>out = specialist.generate(item)<br>GenerationAgent.use(specialist) |
| --- |

Lab 14 — Capstone — team-owned system

Phase: D · Governance & capstone     Goal: Integrate everything into a deployed, team-owned system.

What it adds to this worklet.  The full worklet: connector + runtime + node graph + parallel work + grounding + self-healing + governance + specialists, with a the PI / research office dashboard — delivered and demoed end to end.

| Inputs | Outputs | Agents / nodes | Deliverable & acceptance |
| --- | --- | --- | --- |
| All prior lab deliverables. | A deployed worklet: request → approved, published grant proposal and compliance package. | All agents under the Coordinator (this chapter's node graph). | Deployed system + the PI / research office dashboard + audit trail + a demo on a real case.  Accept: The Pi / Research Office produces an approved, validated grant proposal and compliance package in one session. |

Nodes activated.  Every node, deployed.

Pitfall to avoid.  Integrate, don't rewrite — if the labs kept the contracts, the capstone is wiring.

Lab 14 — end-to-end

| system = deploy(connector, runtime, graph, governance)<br>artifact = system.run(request)        # the grant proposal and compliance package<br>dashboard.show(artifact, metrics, audit) |
| --- |

13.11  Reference Architecture, Pilot & MVP

Reference architecture

- Data capture: agency call listings, academic databases, faculty profile, agency budget/format templates.

- Data layer: canonical schema for calls, literature, proposal, budget, compliance, and package.

- AI layer: call matching, literature/novelty synthesis, drafting, budget preparation, compliance checking.

- Workflow layer: Dean R&D review queue, submission authorization, pipeline dashboard.

- Governance layer: source citation, proposal confidentiality, post-sign-off change control, audit log.

Pilot artifacts

- A funding-call discovery and literature-review pipeline for one department pilot.

- A proposal-drafting and budget-planning workflow against one agency's templates.

- A compliance checklist engine.

- A grants dashboard with an exportable submission package.

Suggested MVP roadmap

| Order | Capability | What it delivers | Agents involved |
| --- | --- | --- | --- |
| 1 | Funding discovery + literature | Matched calls and novelty summary. | Coordinator, Funding Discovery & Literature Review Agents. |
| 2 | Proposal drafting | Objectives, methodology, and timeline draft. | Proposal Drafting Agent. |
| 3 | Budget planning | Agency-compliant itemized budget. | Budget Planning Agent. |
| 4 | Compliance checking | Eligibility/format checklist with pass/fail. | Compliance Checking Agent. |
| 5 | Submission packaging | Agency-format package for authorization. | Submission Agent. |
| 6 | Grants dashboard | Pipeline, deadlines, and compliance in one view. | Coordinator. |

Risks & mitigations

| Risk | Why it matters | Mitigation (where handled) |
| --- | --- | --- |
| Plan drift | individual results deviate from the locked plan | Lock the plan (Lab 3/7); validation rejects any deviation before the human sees it. |
| Ungrounded output | content not backed by the funder's guidelines and institutional policy | Grounded generation with an evidence record per unit (Lab 9); ungrounded items are rejected. |
| Failed checks slip through | a result violates a rule (budget totals reconcile) | Validation is a hard gate (Lab 10/11); failing results are diagnosed and regenerated, never advanced. |
| Runaway loops | the regenerate loop never converges | Bound MAX_ATTEMPTS (Lab 7/10); on exhaustion, escalate to the PI / research office with a diagnosis. |
| Over-automation | the system acts without the PI / research office | The human gate is a hard stop; all outputs are drafts; edits and overrides are effortless and logged (Lab 12). |

13.12  Guardrails, Metrics, Milestones & Glossary

Guardrails

- Do not submit a proposal to a funding agency without Dean R&D/HoD/Research Office sign-off.

- Keep one faculty member's draft proposal and budget confidential from other departments.

- Never present AI-drafted narrative or literature claims as final without faculty review.

- Use only approved agency templates and ceilings; flag line items exceeding norms.

- Never alter a figure or claim after compliance sign-off without re-triggering review; keep a version-controlled record.

Delivery milestones

| Week | Labs | Focus | Exit deliverable |
| --- | --- | --- | --- |
| Week 1 | Labs 1–3 | Planner loop, tools, reusable skills | Runnable planner + core skill |
| Week 2 | Labs 4–6 | Memory/retrieval, connector, governed runtime | Data via connector; audited runs |
| Week 3 | Labs 7–8 | Full node graph + parallel processing | End-to-end draft — shared with faculty |
| Week 4 | Labs 9–10 | Grounding + self-healing validation | Grounded output; auto-repair on faults |
| Week 5 | Labs 11–12 | Tested build + safety/governance | Tested artifact; approval, metrics, rollback |
| Week 6 | Labs 13–14 | Domain specialisation + capstone | Deployed system + demo on a real case |
| Checkpoint:  from the 3rd week, worklets are shared with all faculty for feedback — plan the Week-3 end-to-end draft (Labs 7–8) to be demo-ready. | Checkpoint:  from the 3rd week, worklets are shared with all faculty for feedback — plan the Week-3 end-to-end draft (Labs 7–8) to be demo-ready. | Checkpoint:  from the 3rd week, worklets are shared with all faculty for feedback — plan the Week-3 end-to-end draft (Labs 7–8) to be demo-ready. | Checkpoint:  from the 3rd week, worklets are shared with all faculty for feedback — plan the Week-3 end-to-end draft (Labs 7–8) to be demo-ready. |

Glossary

| Term | Meaning |
| --- | --- |
| Coordinator | The orchestrator agent that owns run-state, plan, budgets and the audit log. |
| Node graph | The explicit wiring of agents, gates and back-edges for one worklet. |
| Human gate | The approval step; the named human is the final authority. |
| Grounding | Linking an output to a real in-scope source (evidence). |
| Validation | The automated acceptance gate a result must pass before human review. |
| Blueprint / plan | The locked specification the pipeline obeys. |


---

# Document Headers and Footers


## Section 1 — Footer

Agentic AI Worklets — 14-Lab Build Book     |     Page


---

# Embedded Media Inventory


Total embedded media files extracted: **3**.

- `./images/image1.png` ? referenced by supplied conversion; file unavailable

- `./images/image2.png` ? referenced by supplied conversion; file unavailable

- `./images/media` ? referenced by supplied conversion; file unavailable

---

# Verbatim DOCX Text Audit

> This section preserves text nodes extracted directly from the DOCX XML to ensure no textual content embedded in shapes/text boxes is lost during conversion.

CHAPTER 13Research Grant Management SystemFrom funding-call discovery to a compliant, Dean-R&D-approved submission package.Human authority: the PI / research office.   Primary output: grant proposal and compliance package.The 14-Lab Method (Recap)Every worklet in this book is built the same way: as a coordinator-plus-workers agentic system that is grown, one capability at a time, through 14 hands-on labs. This chapter is self-contained — it restates the method, the node-graph legend and the pseudocode conventions before applying them to this worklet — so it can be handed to a team on its own.The guiding design principle is constant across all worklets: agents draft and flag; a named human approves. No worklet takes a consequential action autonomously — the human authority named in this chapter signs off before anything is published or sent.The four phasesPhaseWhat it establishesPhase A — Foundations (Labs 1–6)Turn a single agent loop into a tool-using, skill-driven, memory-backed agent that reaches all data through one connector and runs inside a governed runtime with an audit log.Phase B — Orchestration (Labs 7–8)Wire the specialist agents into an explicit node graph, then parallelise the per-unit work and merge the best results.Phase C — Applied reliability (Labs 9–11)Ground every output in evidence, make the pipeline self-healing on validation failure, and treat the spec as a tested build.Phase D — Governance & capstone (Labs 12–14)Add safety, approval, evaluation and rollback; plug in domain specialists; integrate everything into a deployed, team-owned system.Reading the node graphNavy — the apniLeap AURA Coordinator: owns the run-state, plan, budgets and audit log.Light blue — specialist agents, each with one responsibility and a typed message contract.Amber — the human review gate: a hard stop; the named human is the final authority.Green — governed publish/act: versioned, auditable, reversible.Dashed grey — coordinator oversight of every agent; a red back-edge is validation → regenerate.Pseudocode conventionsPseudocode is language-neutral: Coordinator orchestrates; Agent.step(ctx) is one specialist doing its job on the shared run-context; a human gate returns approve / edit / override.The blueprint/plan is locked before work begins; validation is a hard gate; the human approves before publish.13.1  Worklet OverviewFaculty miss relevant funding calls scattered across agency websites and mailing lists; literature and novelty framing take days; and proposal drafts, budgets, and compliance checklists are prepared in silos with no shared source of truth.This worklet proposes a Research Grant Management System, owned by the Dean R&D office, that discovers matched calls, compiles a literature/novelty summary, drafts the proposal, prepares an agency-compliant budget, runs a compliance check, and packages the submission — turning a scattered, deadline-driven process into one auditable, agency-compliant pipeline.Stakeholders: Faculty, HoD, Dean R&D, Research OfficeProblems heardFaculty miss relevant funding calls because listings are scattered across agency websites and mailing lists.Literature review and novelty framing take days of manual searching.Proposal drafts, budgets, and compliance checklists are prepared in silos with no shared source of truth.Dean R&D has no consolidated view of which proposals are in progress, their deadlines, or compliance status.Compliance issues surface late, close to the submission deadline.13.2  Target Final Solution (Definition of Done)The capstone (Lab 14) is complete when, for a real case, the worklet turns a request into a validated, evidence-grounded grant proposal and compliance package that passes every check, is reviewed and approved by the PI / research office, and is published with a full audit trail — with light human edits, not a rewrite.CapabilitiesCapabilityWhat it meansFacultyFaculty specifies their research area, target funding types, and consent to use their profile/publication history for matching.TheThe Funding Discovery Agent surfaces matched calls while the Literature Review Agent compiles a related-work and novelty summary, in parallel.TheThe Proposal Drafting Agent drafts the narrative using the matched call's requirements and the literature summary.TheThe Budget Planning Agent prepares an agency-compliant budget while the Compliance Checking Agent runs an eligibility/format check, in parallel.TheThe Submission Agent packages the proposal, budget, and compliance checklist into the agency's required format.DeanDean R&D/HoD/Research Office reviews the package, approves or requests corrections, and authorizes final submission.Success metrics (KPIs)100% of validation checks pass before the PI / research office review (e.g. budget totals reconcile).Every grant proposal and compliance package is grounded in the funder's guidelines and institutional policy, with an evidence record.Zero consequential actions without the PI / research office's approval; a complete audit trail and one-click rollback.13.3  System at a Glance — the Node GraphA coordinator-plus-workers system: the apniLeap AURA Coordinator holds the plan, run-state and audit log and drives the pipeline; validation is a hard gate; the human review is a hard stop before publish.Figure 13 — the Research Grant Management System agent graph. Amber = human gate; green = governed publish; dashed = coordinator oversight.End-to-end flowFaculty specifies their research area, target funding types, and consent to use their profile/publication history for matching.The Funding Discovery Agent surfaces matched calls while the Literature Review Agent compiles a related-work and novelty summary, in parallel.The Proposal Drafting Agent drafts the narrative using the matched call's requirements and the literature summary.The Budget Planning Agent prepares an agency-compliant budget while the Compliance Checking Agent runs an eligibility/format check, in parallel.The Submission Agent packages the proposal, budget, and compliance checklist into the agency's required format.Dean R&D/HoD/Research Office reviews the package, approves or requests corrections, and authorizes final submission.13.4  Agent Roster — Roles, Communication & Guardrails#AgentRole & communicationGuardrails0apniLeap AURA CoordinatorReceives the faculty/Dean R&D prompt command, checks permissions, creates the run plan, initializes agents, monitors state.Never bypass human approval; enforce data scope, audit logging, source citation, and exception routing.1Funding Discovery AgentSurfaces funding calls (DST, SERB, AICTE, industry CSR) matched to area, eligibility, and deadline, in parallel with B.Surface only verified agencies; never present an expired call as active; cite source and deadline.2Literature Review AgentCompiles related work and a novelty/gap summary from approved databases, in parallel with A.Cite every claim to a verifiable source; never fabricate a reference; flag thin literature rather than overstating novelty.3Proposal Drafting AgentDrafts objectives, methodology, and timeline using the call requirements and literature summary.Draft within provided scope; mark AI text as a draft; never present preliminary findings as established.4Budget Planning AgentPrepares an itemized budget per agency norms and ceilings, in parallel with E.Use approved templates/ceilings; flag line items exceeding norms; never adjust figures without showing the basis.5Compliance Checking AgentChecks eligibility, formatting, and documentation against the agency's guidelines, in parallel with D.Check against the specific call's guidelines; never mark compliant without evidence; flag ambiguous requirements.6Submission AgentPackages the proposal, budget, and checklist into the agency's required format.Do not submit without Dean R&D/HoD/Research Office sign-off; keep a version-controlled package; re-trigger review on any post-sign-off change.7Dean R&D / HoD / Research Office ReviewReviews the package, approves or requests corrections, and authorizes final submission.Dean R&D/HoD/Research Office decision is the final authority for authorizing submission.13.5  Agent Interconnections (Message Map)How the agents are wired — the payloads that flow between them and when. The last rows show the human gate and governed publish.FromToMessage / payloadWhenCoordinatorFunding Discovery Agentrun-context + taskrun startFunding Discovery AgentLiterature Review Agentstate / partial resultin pipelineLiterature Review AgentProposal Drafting Agentstate / partial resultin pipelineProposal Drafting AgentBudget Planning Agentstate / partial resultin pipelineBudget Planning AgentCompliance Checking Agentstate / partial resultin pipelineCompliance Checking AgentSubmission Agentstate / partial resultin pipelineSubmission AgentDean R&D / HoD / Research Office Reviewstate / partial resultin pipelineDean R&D / HoD / Research Office ReviewThe Pi / Research Office gatedraft grant proposal and compliance package + evidencefor reviewThe Pi / Research Office gateCoordinatorapprove | edit | overridehuman decisionCoordinatorGovernance / Publishfinal grant proposal and compliance package (versioned)on approval13.6  Data ModelEntityKey fieldsFaculty research profileResearch area, eligibility, and publication history for matching.Funding callVerified agency calls with deadlines and requirements.Literature & noveltyRelated-work and gap summary with citations.Proposal & budgetDraft narrative and an agency-compliant itemized budget.Compliance & submissionCompliance checklist and the packaged submission, pending authorization.13.7  Solution Paradigm — PseudocodeOrchestrator (the whole run)function run_research_grant_management_system(request):    ctx = Coordinator.new_run(request)        # isolated, checkpointed    plan = Coordinator.build_plan(request)     # locked before work begins    ctx = FundingDiscoveryAgent.step(ctx, plan)    ctx = LiteratureReviewAgent.step(ctx, plan)    ctx = ProposalDraftingAgent.step(ctx, plan)    ctx = BudgetPlanningAgent.step(ctx, plan)    ctx = ComplianceCheckingAgent.step(ctx, plan)    ctx = SubmissionAgent.step(ctx, plan)    ctx = DeanRDHoDResearchOfficeReview.step(ctx, plan)    report = ValidationAgent.validate(ctx, plan)   # hard gate    while not report.passed and attempts < MAX:    # self-healing (Lab 10)        Coordinator.regenerate(report.failing); report = validate(ctx, plan)    draft = assemble(ctx)                          # the grant proposal and compliance package    decision = TheGate.review(draft)  # HUMAN — final authority    if decision.approved:        final = apply(decision.edits, draft)        Governance.publish(final, version=next()); Audit.log_all()    return finalValidation (the acceptance gate)function ValidationAgent.validate(ctx, plan):    checks = [      ('budget totals reconcile', test_0(ctx, plan)),      ('eligibility and compliance are met', test_1(ctx, plan)),      ('no submission happens without PI approval', test_2(ctx, plan)),      ('every deadline is tracked', test_3(ctx, plan)),    ]    failing = [n for n,ok in checks if not ok]    return Report(passed = not failing, failing = failing,                  diagnosis = explain(failing))Connector (one governed surface for all sources)connector.expose:    read('funding calls & guidelines')    read('budget & personnel data')    read('compliance rules')agents.use(connector)   # no agent touches a source directlyWorked example — one proposal / grant, end to endHow a single proposal / grant travels through the pipeline, from plan to a validated, approved and published grant proposal and compliance package. This is the level of traceability every proposal / grant should have.StageWhat happensPlan / slotThe coordinator locks the plan and picks one proposal / grant to work — its constraints fixed before any content is chosen.Source candidateA retrieval agent proposes a candidate for this proposal / grant from funding calls & guidelines, with provenance.Grounded candidateA generation agent produces a fresh candidate grounded in the funder's guidelines and institutional policy, attaching an evidence record (source, scope, tags).Screen & selectCandidates are calibrated and screened; the best-aligned one that satisfies the plan is selected, the rest logged.ValidationThe result is checked (budget totals reconcile; no submission happens without PI approval); on failure only this proposal / grant is regenerated.Human reviewThe Pi / Research Office sees the draft grant proposal and compliance package with its evidence and validation report, and approves, edits or overrides.Publish & auditOn approval the governed publish versions the grant proposal and compliance package, records the audit trail, and updates history for future runs.13.8  Hybrid Execution MethodologyHow the coordinator runs each stage — what is human-gated, what runs in parallel, what is sequential.StageExecution mode & coordinator behaviorGate 1: profile intakeSequential — start only after research area, funding type, and consent are provided.Parallel discovery & reviewParallel — Funding Discovery surfaces calls while Literature Review compiles the novelty summary.DraftingSequential — drafting runs after both the call match and literature summary are available.Parallel budget & complianceParallel — Budget Planning and Compliance Checking both run against the drafted proposal.PackagingSequential — the Submission Agent assembles the package after budget and compliance are available.Stakeholder approvalSequential — Dean R&D/HoD/Research Office approves and authorizes; corrections route back.Dashboard updateParallel after approval — grants dashboard (pipeline, deadlines, compliance) publishes once approved.13.9  Dashboard TemplateWhat the PI / research office sees to review, approve and monitor.PanelShowsFunding pipelineMatched calls, deadlines, and proposal status.Proposal & literatureDraft narrative and novelty summary with citations.Budget & complianceItemized budget against ceilings and the compliance checklist.Submission packageVersion-controlled package with authorization status.13.10  The 14-Lab EvolutionEach lab is a working increment that adds one capability to this worklet and activates specific nodes. Ship the deliverable and pass acceptance before advancing — by Lab 14 they compose into the deployed grant proposal and compliance package system.Lab 1 — Agent vs Chatbot — the grant proposal and compliance package planner loopPhase: A · Foundations     Goal: Establish the agent loop (clarify → plan → revise) instead of a one-shot chatbot answer.What it adds to this worklet.  A minimal planner that clarifies the request, proposes a plan for producing the grant proposal and compliance package, and revises on feedback — the seed this worklet grows from.InputsOutputsAgents / nodesDeliverable & acceptanceFree-text request; core parameters.A clarified request + an editable outline plan for the grant proposal and compliance package.Coordinator (loop only).A notebook agent that clarifies, plans and revises a grant proposal and compliance package outline.  Accept: Given a vague request it asks at least two clarifying questions and yields a coherent, editable plan.Nodes activated.  Coordinator loop (no specialist nodes yet).Pitfall to avoid.  Don't answer in one shot — without clarify/revise it's a chatbot, not an agent.Lab 1 — plan & revisereq  = clarify(user_request)         # ask until inputs completeplan = propose_plan(req)             # outline for the grant proposal and compliance packagewhile user.wants_changes(plan): plan = revise(plan, user.feedback)return plan                          # not final — a structured planLab 2 — Tool-Using Agent — call data & computePhase: A · Foundations     Goal: Give the agent tools it must call to act, rather than answering from memory.What it adds to this worklet.  Readers for funding calls & guidelines and budget & personnel data, plus a domain calculator/checker, so the planner acts on real data.InputsOutputsAgents / nodesDeliverable & acceptancefunding calls & guidelines; budget & personnel data; parameters.Verified computed values and parsed inputs.Coordinator + tool layer.An agent that reads funding calls & guidelines and computes/validates through typed tools.  Accept: Key numbers and lookups always go through tools, never hand-done in the prompt.Nodes activated.  Tool layer feeding the early data agents.Pitfall to avoid.  Never assert a fact in the prompt that a tool should verify.Lab 2 — typed toolsa = tool.read('funding calls & guidelines')b = tool.read('budget & personnel data')v = tool.compute(a, b)assert v.validLab 3 — Skill Creation — reusable plan & format skillsPhase: A · Foundations     Goal: Package repeatable capability as reusable, schema-typed skills.What it adds to this worklet.  A plan/blueprint skill and a formatting skill that renders the grant proposal and compliance package — both reusable across cases.InputsOutputsAgents / nodesDeliverable & acceptanceParsed inputs; template spec.A locked plan object; a formatted grant proposal and compliance package shell.Planning and assembly emerge as skills.Two callable skills with schemas, invoked by the agent.  Accept: The same skill works for two different cases without code changes.Nodes activated.  Plan node + Assembly node (as skills).Pitfall to avoid.  Keep skills case-agnostic and typed; hard-coding one case breaks reuse.Lab 3 — skill interfaceskill plan(inputs) -> Plan:  return expand(inputs).lock()skill format_grant(result, template) -> DocumentLab 4 — Memory & Retrieval — state vs storedPhase: A · Foundations     Goal: Separate short-term run state from long-term stored knowledge.What it adds to this worklet.  Session state (the current draft) vs stored reference — funding calls & guidelines and the history of past proposal / grants — retrieved by tags and by similarity.InputsOutputsAgents / nodesDeliverable & acceptancefunding calls & guidelines; history of prior proposal / grants; current draft.Tag- and similarity-based retrieval.Retrieval agent; foundations of later screening.Retrieval over the store + history with tag filters and embedding similarity.  Accept: For a given task, retrieval returns correctly-tagged candidates and similar prior items.Nodes activated.  Retrieval node; seeds validation/no-repeat.Pitfall to avoid.  Don't conflate run state with the archive — mixing them corrupts the baseline.Lab 4 — memory splitstate.draft = candidate                       # short-termhits  = retrieve(store, tags)                 # long-termprior = retrieve(history, embed(candidate), k=5)  # similarityLab 5 — MCP-Style Connector — one server for all sourcesPhase: A · Foundations     Goal: Expose every data source through one typed connector.What it adds to this worklet.  A single connector fronting funding calls & guidelines, budget & personnel data and compliance rules so every agent reaches data the same governed way.InputsOutputsAgents / nodesDeliverable & acceptanceThe worklet's data sources.A uniform, typed tool surface.Connector used by all data-facing agents.A connector server with typed endpoints and auth; agents call only through it.  Accept: All data access goes through the connector; swapping a source needs no agent change.Nodes activated.  Connector under the data agents.Pitfall to avoid.  No agent should touch a source directly; a bypass defeats governance later.Lab 5 — connectorconnector.expose:    read('funding calls & guidelines')    read('budget & personnel data')    read('compliance rules')agents.use(connector)   # no agent touches a source directlyLab 6 — Runtime — skills, tools, memory, auditPhase: A · Foundations     Goal: Run the agent inside a controlled runtime with a full audit log.What it adds to this worklet.  A runtime binding skills + tools + memory behind the loop, enforcing budgets and approval gates and logging every step — the backbone later labs plug into.InputsOutputsAgents / nodesDeliverable & acceptanceSkills (Lab 3), connector (Lab 5), memory (Lab 4).A governed run with audit + checkpoints.Coordinator hardened into the runtime controller.Runtime wrapping the agent: budgets, gates, checkpoint/resume, audit log.  Accept: Every action is logged with inputs/outputs; a crashed run resumes from its last checkpoint.Nodes activated.  Coordinator runtime around all nodes.Pitfall to avoid.  Log inputs and outputs, not just messages; checkpoint before risky steps or resume loses state.Lab 6 — controlled looprun = Runtime(budget=B, gates=[publish])for step in agent.loop():    audit.log(step.intent, step.action, step.result)    if step.risky: wait_for_approval(step)    checkpoint(run.state)Lab 7 — Agentic Node Graph — the full pipelinePhase: B · Orchestration     Goal: Wire the specialist agents into one explicit graph with state and branching.What it adds to this worklet.  The complete pipeline as a node graph: Funding Discovery Agent, Literature Review Agent, Proposal Drafting Agent → … → the PI / research office gate → publish, with a validation → regenerate back-edge.InputsOutputsAgents / nodesDeliverable & acceptanceAll Phase-A skills/agents.An executable graph producing a first end-to-end draft.All core agents connected (see this chapter's node graph).A graph runner that produces a full grant proposal and compliance package draft end to end.  Accept: One command yields a validated grant proposal and compliance package draft end to end.Nodes activated.  All core nodes + the back-edge.Pitfall to avoid.  Bound the retry edge — an unbounded regenerate loop can spin forever.Lab 7 — graphgraph.chain(ingest -> plan -> workers -> validate)graph.edge(validate --fail--> workers)   # bounded retrygraph.edge(validate --pass--> assemble -> gate -> publish)Lab 8 — Parallel Swarm — many proposal / grants, then mergePhase: B · Orchestration     Goal: Parallelise the per-unit work and select the best.What it adds to this worklet.  Several worker agents process proposal / grants in parallel; a merge/selector picks the best per the plan — cutting latency and improving quality.InputsOutputsAgents / nodesDeliverable & acceptanceLocked plan; per-unit work items.Best-of-N results merged into one compliant output.Parallel workers + a Merge selector under the Coordinator.A fan-out/fan-in that processes all units and merges by alignment to the plan.  Accept: Parallel run matches or beats sequential quality at lower wall-clock time.Nodes activated.  Parallel worker fan-out + merge.Pitfall to avoid.  Merge strictly by plan alignment; picking the 'nicest' output quietly breaks coverage.Lab 8 — fan-out/inresults = parallel_map(process_proposal, plan.units)output  = merge(results, key=alignment_to(plan))Lab 9 — Deep Research — ground & evidencePhase: C · Applied reliability     Goal: Ground every output in cited, in-scope evidence.What it adds to this worklet.  For each proposal / grant the agent builds an evidence record grounded in the funder's guidelines and institutional policy, so validity is auditable and out-of-scope content can't slip through.InputsOutputsAgents / nodesDeliverable & acceptancethe funder's guidelines and institutional policy; candidate outputs.An evidence record per unit; a paper-level evidence table.Generation + grounding step feeding Validation.Each candidate carries an evidence record; an evidence table is produced.  Accept: Every output maps to an in-scope source; ungrounded candidates are rejected.Nodes activated.  Grounding step into the validation check.Pitfall to avoid.  Require a real source; a plausible-sounding but ungrounded item must be rejected, not kept.Lab 9 — groundingfor c in candidates:    ev = research(c, source="the funder's guidelines and institutional policy")    if not ev.in_scope: reject(c)    c.evidence = evLab 10 — Ops Resilience — validate, diagnose, fixPhase: C · Applied reliability     Goal: Make the pipeline self-healing when validation fails.What it adds to this worklet.  When a check fails (budget totals reconcile; eligibility and compliance are met), the agent diagnoses the exact failing constraint and regenerates only the offending part.InputsOutputsAgents / nodesDeliverable & acceptanceValidation report; current output.A repaired, passing output with a diagnosis log.Validation agent + Coordinator's regenerate loop.Failure-injection tests showing automatic diagnosis and targeted repair.  Accept: Injected faults are detected and fixed within the retry budget.Nodes activated.  Validation node + self-healing loop.Pitfall to avoid.  Regenerate only the failing part — rebuilding everything wastes budget and churns good work.Lab 10 — diagnose & fixreport = validate(output, plan)while not report.passed and attempts < BUDGET:    regenerate(report.failing); report = validate(output, plan)if not report.passed: escalate(report)   # to the humanLab 11 — SDLC Factory — spec → tested outputPhase: C · Applied reliability     Goal: Treat the plan as a spec and the output as a tested implementation.What it adds to this worklet.  The worklet becomes a factory: plan in, a grant proposal and compliance package out that provably passes an automated acceptance suite before the PI / research office sees it.InputsOutputsAgents / nodesDeliverable & acceptanceThe locked plan (spec); the acceptance suite.A result plus a green test report.Validation as the test harness; Coordinator as the build.A 'build' command: plan → grant proposal and compliance package + passing acceptance report.  Accept: No grant proposal and compliance package advances to the PI / research office without a fully passing acceptance report.Nodes activated.  Validation gates the whole graph.Pitfall to avoid.  The acceptance suite is the gate; never let a result skip to the human without a green report.Lab 11 — spec→artifactartifact = build(plan)                 # graph run (Lab 7/8/10)report   = acceptance_suite(artifact, plan)require report.all_pass                # gate before human reviewLab 12 — Safety & Governance — approval, eval, rollbackPhase: D · Governance & capstone     Goal: Add confidentiality, approval, evaluation and rollback.What it adds to this worklet.  Access control and confidentiality, the the PI / research office approval gate as a hard stop, evaluation metrics, versioning and one-click rollback.InputsOutputsAgents / nodesDeliverable & acceptanceDraft-vs-approved states; role permissions; metrics.A governed, reversible release.Governance & Audit agent; the human gate formalised.Approval workflow + metrics + rollback, with confidentiality controls.  Accept: Only the PI / research office-approved results publish; any release rolls back cleanly.Nodes activated.  Human gate + governance node.Pitfall to avoid.  Confidentiality and rollback are requirements, not extras.Lab 12 — governed releaserequire actor.can_approve and out.status=='draft'final = apply(human.edits, out); final.status='approved'governance.publish(final, version=v+1); metrics.record(...)on rollback(v): restore(version=v)Lab 13 — Discipline-Specific Agents — domain specialisationPhase: D · Governance & capstone     Goal: Specialise the worklet to its domain variants.What it adds to this worklet.  Pluggable specialists — funder profiles (government, industry, international) — so outputs match the specific style and constraints of each case.InputsOutputsAgents / nodesDeliverable & acceptanceDomain profile; the work item.Domain-appropriate outputs with correct schemes.Specialist plugged into the generation node.A specialist producing domain-correct grant proposal and compliance packages.  Accept: Specialist outputs use valid domain patterns and produce checkable results.Nodes activated.  Specialist into the generation node.Pitfall to avoid.  Every specialist output needs a checkable scheme; clever but vague outputs are unusable.Lab 13 — specialist plug-inspecialist = registry.get(domain)out = specialist.generate(item)GenerationAgent.use(specialist)Lab 14 — Capstone — team-owned systemPhase: D · Governance & capstone     Goal: Integrate everything into a deployed, team-owned system.What it adds to this worklet.  The full worklet: connector + runtime + node graph + parallel work + grounding + self-healing + governance + specialists, with a the PI / research office dashboard — delivered and demoed end to end.InputsOutputsAgents / nodesDeliverable & acceptanceAll prior lab deliverables.A deployed worklet: request → approved, published grant proposal and compliance package.All agents under the Coordinator (this chapter's node graph).Deployed system + the PI / research office dashboard + audit trail + a demo on a real case.  Accept: The Pi / Research Office produces an approved, validated grant proposal and compliance package in one session.Nodes activated.  Every node, deployed.Pitfall to avoid.  Integrate, don't rewrite — if the labs kept the contracts, the capstone is wiring.Lab 14 — end-to-endsystem = deploy(connector, runtime, graph, governance)artifact = system.run(request)        # the grant proposal and compliance packagedashboard.show(artifact, metrics, audit)13.11  Reference Architecture, Pilot & MVPReference architectureData capture: agency call listings, academic databases, faculty profile, agency budget/format templates.Data layer: canonical schema for calls, literature, proposal, budget, compliance, and package.AI layer: call matching, literature/novelty synthesis, drafting, budget preparation, compliance checking.Workflow layer: Dean R&D review queue, submission authorization, pipeline dashboard.Governance layer: source citation, proposal confidentiality, post-sign-off change control, audit log.Pilot artifactsA funding-call discovery and literature-review pipeline for one department pilot.A proposal-drafting and budget-planning workflow against one agency's templates.A compliance checklist engine.A grants dashboard with an exportable submission package.Suggested MVP roadmapOrderCapabilityWhat it deliversAgents involved1Funding discovery + literatureMatched calls and novelty summary.Coordinator, Funding Discovery & Literature Review Agents.2Proposal draftingObjectives, methodology, and timeline draft.Proposal Drafting Agent.3Budget planningAgency-compliant itemized budget.Budget Planning Agent.4Compliance checkingEligibility/format checklist with pass/fail.Compliance Checking Agent.5Submission packagingAgency-format package for authorization.Submission Agent.6Grants dashboardPipeline, deadlines, and compliance in one view.Coordinator.Risks & mitigationsRiskWhy it mattersMitigation (where handled)Plan driftindividual results deviate from the locked planLock the plan (Lab 3/7); validation rejects any deviation before the human sees it.Ungrounded outputcontent not backed by the funder's guidelines and institutional policyGrounded generation with an evidence record per unit (Lab 9); ungrounded items are rejected.Failed checks slip througha result violates a rule (budget totals reconcile)Validation is a hard gate (Lab 10/11); failing results are diagnosed and regenerated, never advanced.Runaway loopsthe regenerate loop never convergesBound MAX_ATTEMPTS (Lab 7/10); on exhaustion, escalate to the PI / research office with a diagnosis.Over-automationthe system acts without the PI / research officeThe human gate is a hard stop; all outputs are drafts; edits and overrides are effortless and logged (Lab 12).13.12  Guardrails, Metrics, Milestones & GlossaryGuardrailsDo not submit a proposal to a funding agency without Dean R&D/HoD/Research Office sign-off.Keep one faculty member's draft proposal and budget confidential from other departments.Never present AI-drafted narrative or literature claims as final without faculty review.Use only approved agency templates and ceilings; flag line items exceeding norms.Never alter a figure or claim after compliance sign-off without re-triggering review; keep a version-controlled record.Delivery milestonesWeekLabsFocusExit deliverableWeek 1Labs 1–3Planner loop, tools, reusable skillsRunnable planner + core skillWeek 2Labs 4–6Memory/retrieval, connector, governed runtimeData via connector; audited runsWeek 3Labs 7–8Full node graph + parallel processingEnd-to-end draft — shared with facultyWeek 4Labs 9–10Grounding + self-healing validationGrounded output; auto-repair on faultsWeek 5Labs 11–12Tested build + safety/governanceTested artifact; approval, metrics, rollbackWeek 6Labs 13–14Domain specialisation + capstoneDeployed system + demo on a real caseCheckpoint:  from the 3rd week, worklets are shared with all faculty for feedback — plan the Week-3 end-to-end draft (Labs 7–8) to be demo-ready.GlossaryTermMeaningCoordinatorThe orchestrator agent that owns run-state, plan, budgets and the audit log.Node graphThe explicit wiring of agents, gates and back-edges for one worklet.Human gateThe approval step; the named human is the final authority.GroundingLinking an output to a real in-scope source (evidence).ValidationThe automated acceptance gate a result must pass before human review.Blueprint / planThe locked specification the pipeline obeys.