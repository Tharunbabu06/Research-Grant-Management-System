> Historical reference/merge document. Use [current documentation](README.md) and [fresh verification](VERIFICATION.md).

# Research Grant Management System (apniLeap AURA)

**Agentic AI (26ECAC401) · Worklet 13 · KLE Technological University**

From funding-call discovery to a compliant, Dean-R&D-approved submission package: an
eight-agent pipeline that turns a faculty brief into a validated, evidence-grounded, costed and
compliance-checked grant proposal package. **Agents draft and flag; the Dean R&D / Research Office approves.**

![Dashboard](./Course-Project/docs/screenshots/dashboard.png)

---

## 1. Team

| Team name / number | _to be filled_ |
|---|---|
| Division | _to be filled_ |

| # | Name | USN | Division |
|---|------|-----|----------|
| 1 | _Name_ | _USN_ | _Div_ |
| 2 | _Name_ | _USN_ | _Div_ |
| 3 | _Name_ | _USN_ | _Div_ |
| 4 | _Name_ | _USN_ | _Div_ |

---

## 2. Quick links

| What | Where |
|---|---|
| Assignments (all lab notebooks) | [`Assignments/`](./Assignments) |
| Course project code | [`Course-Project/backend`](./Course-Project/backend) · [`Course-Project/frontend`](./Course-Project/frontend) |
| Course project technical README | [`Course-Project/README.md`](./Course-Project/README.md) |
| Problem statement | [`Course-Project/Problem_Statement/`](./Course-Project/Problem_Statement) |
| Project documentation (screenshots, course templates) | [`Course-Project/docs/`](./Course-Project/docs) |
| Final course project report | [`Course-Project/Final_Report/`](./Course-Project/Final_Report) |
| Evidence (console trace + check report per lab) | [`Course-Project/evidence/`](./Course-Project/evidence) |

---

## 3. Repository structure

```
Research-Grant-Management-System/
├── README.md
├── requirements.txt
├── .gitignore
├── Assignments/                 # Lab 1 – Lab 14 notebooks (executed, with outputs)
│   └── scripts/                 # the same labs as plain .py files + shared seed data + notebook builder
└── Course-Project/
    ├── README.md                # full technical documentation of the system
    ├── Problem_Statement/       # worklet problem statement
    ├── Final_Report/            # final course project report
    ├── backend/                 # Node + Express API, the eight agents, engine, tests
    ├── frontend/                # React + Vite console (dashboards, intake, runs, governance, audit)
    ├── evidence/                # exported artifacts per lab
    └── docs/                    # screenshots, course-issued originals
```

---

## 4. Overview of the assignments

Each assignment is a Jupyter notebook that runs standalone (Colab or local) and ends with
acceptance checks asserted on the trace of its own run. No lab needs an API key, a network
connection or any package outside the Python standard library.

| Lab | Topic | Notebook | What it demonstrates | Checks |
|---|---|---|---|---|
| 1 | Agent vs Chatbot | [`LAB_1`](./Assignments/LAB_1_Worklet13_Agent_vs_Chatbot.ipynb) | Clarify → plan → revise loop; feedback mutates the same plan object; budget/ceiling conflict caught before plan lock | 10/10 |
| 2 | Tool-Using Agent | [`LAB_2`](./Assignments/LAB_2_Worklet13_Tool_Using_Agent.ipynb) | Typed tools behind one choke point; budget arithmetic only in tools; graceful tool failure; draft-only notification | 10/10 |
| 3 | Skill Creation | [`LAB_3`](./Assignments/LAB_3_Worklet13_Skill_Creation.ipynb) | Reusable schema-typed `plan` and `format` skills, checksum-locked, shared by government and industry/CSR domains | 11/11 |
| 4 | Memory & Retrieval | [`LAB_4`](./Assignments/LAB_4_Worklet13_Memory_and_Retrieval.ipynb) | Session state vs stored knowledge; topic-scoped and TF-IDF retrieval; staleness policy; permission-gated writes | 8/8 |
| 5 | MCP-Style Connector | [`LAB_5`](./Assignments/LAB_5_Worklet13_MCP_Connector.ipynb) | One governed server over all sources; capability discovery; agent token and caller permissions; audit log | 10/10 |
| 6 | OpenCLA / OpenClaw Runtime | [`LAB_6`](./Assignments/LAB_6_Worklet13_Runtime.ipynb) | Step/tool budgets, per-user memory, checkpoints, rate limiting, escalation to a human after repeated failure | 10/10 |
| 7 | Agentic Node Graph | [`LAB_7`](./Assignments/LAB_7_Worklet13_Node_Graph.ipynb) | Full pipeline as an explicit graph with parallel branches, a bounded retry back-edge and the Dean gate | 10/10 |
| 8 | Parallel Swarm | [`LAB_8`](./Assignments/LAB_8_Worklet13_Parallel_Swarm.ipynb) | `ThreadPoolExecutor` fan-out of section specialists, plan-aligned merge, cross-agent conflict critique | 10/10 |
| 9 | Deep Research / Grounding | [`LAB_9`](./Assignments/LAB_9_Worklet13_Deep_Research_Grounding.ipynb) | Claim-level evidence table; out-of-scope sources rejected; contradictions and source quality surfaced | 10/10 |
| 10 | Ops Resilience | [`LAB_10`](./Assignments/LAB_10_Worklet13_Ops_Resilience.ipynb) | Fault injection, diagnosis and targeted repair inside a 3-attempt budget; high-risk fixes gated | 11/11 |
| 11 | Agentic SDLC Factory | [`LAB_11`](./Assignments/LAB_11_Worklet13_SDLC_Factory.ipynb) | Acceptance suite derived from the spec as a hard gate; a deliberate bug is caught by independent tests | 9/9 |
| 12 | Safety & Governance | [`LAB_12`](./Assignments/LAB_12_Worklet13_Safety_and_Governance.ipynb) | Evaluation gate, role-checked Dean approval, versioning, one-click rollback, finance clearance threshold | 11/11 |
| 13 | Domain Specialists | [`LAB_13`](./Assignments/LAB_13_Worklet13_Domain_Specialists.ipynb) | Government, industry/CSR and international funder specialists with checkable contracts | 8/8 |
| 14 | Capstone | [`LAB_14`](./Assignments/LAB_14_Worklet13_Capstone.ipynb) | All capabilities integrated: brief → validated package → Dean approval → published version | 12/12 |

**Total: 140 / 140 acceptance checks passing across 14 notebooks, 0 execution errors.**
Every notebook is committed with its outputs, and each lab also runs both of its graded assignments.

---

## 5. Course project — Research Grant Management System

### 5.1 Problem statement
Faculty miss relevant funding calls because listings are scattered across agency websites and
mailing lists. Literature review and novelty framing take days of manual searching. Proposal
drafts, budgets and compliance checklists are prepared in silos with no shared source of truth,
the Dean R&D has no consolidated view of proposals in progress, and compliance issues surface
late, close to the submission deadline.

Stakeholders: Faculty (PI), HoD, Dean R&D, Research Office.
Full statement: [`Course-Project/Problem_Statement/`](./Course-Project/Problem_Statement).

### 5.2 Objectives
1. Discover verified, open funding calls matched to the faculty brief, and compile a cited literature / novelty summary, **in parallel**.
2. Draft the proposal narrative within the faculty's scope, with every claim linked to in-scope evidence.
3. Prepare an agency-compliant budget and run the matched call's compliance checklist, **in parallel**.
4. Package the proposal, budget and checklist with a manifest and SHA-256 checksum, behind a hard acceptance gate.
5. Keep a human in charge: nothing is submitted without Dean R&D / Research Office approval.
6. Make everything auditable: source citations, audit log, immutable versions, one-click rollback.

### 5.3 Approach
A coordinator runs a hybrid workflow: sequential gates where quality or approval matter, and
parallel execution where agents are independent.

| Stage | Mode | Agent |
|---|---|---|
| Intake (consent + permissions, clarifying questions) | Sequential | apniLeap AURA Coordinator |
| Discovery | **Parallel** | Funding Discovery · Literature Review agents |
| Plan reconciled to the matched call | Sequential | Coordinator |
| Proposal drafting | Sequential (parallel section swarm inside) | Proposal Drafting Agent |
| Budget and compliance | **Parallel** | Budget Planning · Compliance Checking agents |
| Validate → diagnose → targeted repair (max 3 attempts) | Sequential, with a back-edge | Coordinator |
| Packaging + acceptance suite (hard gate) | Sequential | Submission Agent |
| Approval | Sequential | Dean R&D / HoD / Research Office (human) |
| Publish version + dashboard | After approval | Coordinator |

Guardrails: never surface an expired or unverified call, never state a claim without a resolvable
source, never present preliminary findings as results, never let the model create or change a
budget amount, never pass a compliance item without evidence, never submit without sign-off.

### 5.4 Implementation

| Layer | Location | Labs | Supplies |
|---|---|---|---|
| Core | `backend/src/core.js` | 2–6, 8, 13 | connector, typed tools, memory, skills, runtime, specialists, swarm |
| Agents | `backend/src/agents.js` | 7, 14 | Groups A–F (discovery, literature, drafting, budget, compliance, submission) and repair helpers |
| Engine | `backend/src/engine.js` | 1, 7, 9–12, 14 | graph, evidence table, validation/repair, acceptance suite, governance, metrics |
| Drafting model | `backend/src/groq.js`, `llm-drafting.js` | 9 | contract-checked LLM drafting with source and numeric guardrails (optional) |
| Data | `backend/src/seed.js`, `projects.js`, `models/` | 4–5 | calls, literature, policies, people, 30 sanctioned projects, MongoDB schemas |
| API | `backend/src/api.js` | 14 | REST surface for runs, review, rollback, connector, audit |
| Console | `frontend/src/` | 14 | React console: projects, new proposal, run detail, agents, governance, audit |

Stack: Node 22+, Express 5, React 19, Vite 8, MongoDB Atlas via Mongoose (optional, with a local
JSON fallback) and Groq for four drafted sections (optional, deterministic fallback). The lab
notebooks are plain Python.

**Run the course project**
```bash
cd Course-Project/frontend && npm install && npm run build
cd ../backend && npm install
cp .env.example .env        # optional: Groq key and MongoDB URI; runs offline without them
npm start                   # opens http://localhost:3000
npm test                    # 9 acceptance / integration tests
```
Sign in with any profile on the login screen (demo password `password123`).

**Run a notebook:** open any file in `Assignments/` in Jupyter or Google Colab and run all cells.
**Run a lab as a script:** `python Assignments/scripts/lab01_agent_vs_chatbot.py`.
**Rebuild and re-execute all notebooks:** `pip install -r requirements.txt` then `python Assignments/scripts/build_notebooks.py`.

### 5.5 Results
- **14 / 14 labs implemented, 140 / 140 notebook acceptance checks passing**; the backend suite passes 9 / 9 tests.
- **A vague brief is not answered, it is clarified:** intake returns clarifying questions and blocks launch until the brief is complete.
- **Budget arithmetic lives in tools:** 4 budget lines give direct ₹45,28,000, 15% overhead and 5% contingency, total ₹54,33,600, computed by `compute_budget`, never by the model.
- **Ungrounded claims are removed, not softened:** in the grounding lab 2 of 3 claims resolve to in-scope sources and the one citing a non-existent source is rejected.
- **The pipeline heals itself:** four injected faults (missing section, budget mismatch, equipment cap breach, ungrounded claim) are diagnosed and repaired within the 3-attempt budget.
- **The acceptance suite is independent:** a deliberately broken overhead figure is caught by test TC-03 and the build is blocked.
- **The system refuses:** bad agent tokens, unpermitted callers, a PI approving their own proposal, proposals without a rollback plan, unscrubbed patient data and expired calls are all blocked, and each refusal is demoable.
- **Nothing ships without a human:** every run stops at `awaiting_dean_review`; approval publishes an immutable, checksummed version that can be rolled back.

### 5.6 Demo guide
| Screen | What to show |
|---|---|
| Projects | 30 sanctioned projects; filter by year and department |
| Project → Budget | Add Requirement + Cost rows, save; the total comes only from the rows |
| New proposal | Enter a brief → clarifying questions → Prepare plan → Launch run |
| Run detail | Discovery, draft with claim-level evidence, budget caps, compliance checklist, package |
| New proposal → Failure injection | Inject a fault and watch diagnosis and targeted repair |
| Review (as Dean R&D) | Approve → version v1 published; as PI the approval is refused |
| Governance → Versions | One-click rollback |
| Audit trail | Every agent step with intent, action and result |

Screenshots of every screen are in [`Course-Project/docs/screenshots/`](./Course-Project/docs/screenshots).

---

## 6. Documentation
- Technical README (agents, pipeline, API, schema): [`Course-Project/README.md`](./Course-Project/README.md)
- Problem statement: [`Course-Project/Problem_Statement/`](./Course-Project/Problem_Statement)
- Screenshots and course-issued templates (canvas, review sheet, lab guide, build book): [`Course-Project/docs/`](./Course-Project/docs)
- Final report: [`Course-Project/Final_Report/`](./Course-Project/Final_Report)
