# GrantOffice - Research Grant Management System

Final Course Project Report

KLE Technological University, Hubballi

Agentic AI (26ECAC401) | Chapter / Worklet 13 | 18 November 2026

Team 13 (team-supplied; independent filled-document confirmation pending)

| Member | USN |
| --- | --- |
| Soujanya Tikare | 01FE23BCI064 |
| K. Tharun Babu | 01FE23BCI078 |
| NT Basavaraj | 01FE23BCI113 |
| K. Rohith | 01FE23BCI031 |

Division: to be completed by the team. Names/USNs follow the team's corrected details. Available review sheet/canvas are blank. No reviewer marks, faculty signatures or institutional approvals are asserted.

## Abstract

GrantOffice is a course-project research-grant workspace that coordinates intake, source retrieval, drafting, financial checks and authorized internal review. The main implementation is React/Vite with an Express/Node stage engine; an independent Python/FastAPI/LangGraph edition remains separately runnable. Institutional publications and grant history retain source-row provenance, while practice calls and policy fixtures remain explicitly synthetic. Current correctness work preserves entered whole-INR amounts, separates scholarly/publication/proposal/award concepts, surfaces provider and storage failures, binds review to saved content and supports genuine saved-version DOCX/PDF exports. Verification combines backend regressions, frontend lint/build, isolated Python tests, fourteen lab trace checks and document inspection. These checks demonstrate software behavior within their stated scope; they do not establish live agency compliance, scientific novelty, a funding award or institutional deployment approval.

## 1. Introduction, motivation and scope

Faculty grant preparation involves fragmented call notices, literature metadata, narratives, spreadsheets and approvals. Inconsistent copies can obscure evidence, change costs or leave a reviewer assessing stale content. The course worklet proposes a coordinator-and-workers system in which agents draft and flag, while named people decide consequential actions.

GrantOffice implements this direction as a locally hosted classroom application. The objective is traceable coordination rather than automatic submission. Faculty/PIs own inputs and revisions; HoDs, Dean R&D and Research Office roles review within their configured permissions. The original problem statement requires a real-case compliant package with human sign-off. This release verifies a practice workflow and authentic source browsing, not a genuine-current-call institutional acceptance study.

The current working implementation is authoritative. Older reference README files, reports and screenshots supply course structure and historical evidence only. Existing Course-Project/backend/frontend paths were retained; the Python edition is independent and no second copy of the main application was introduced. The detailed requirement mapping identifies what remains before the original real-case definition of done can be claimed.

## 2. Objectives and requirements

The implementation aims to capture explicit consent and a locked plan; preserve submitted inputs; retrieve and label source evidence; produce editable sections; calculate reconciled budgets without changing faculty costs; stop on failed compliance; preserve role/ownership boundaries; require package-specific human review; and retain an audit trail, immutable versions and reusable exports.

The system must also tell the truth about failure: an absent database is local storage, failed metadata retrieval is not provider success, a source-ID match is not scientific validation, and an internal release is not external submission. Regressions exercise these distinctions rather than manufacturing a target publication or award count.


## 3. Requirement-to-implementation mapping

[Original problem statement](../Problem_Statement/Research_Grant_Management_System.docx), [extracted original](../Problem_Statement/Problem_Statement.md) and [build book](../docs/originals/Agentic_AI_15_Worklets_14Lab_Build_Book.docx) remain unchanged. This mapping separately describes current scope.

| Original direction | Implemented behavior | Evidence | Remaining gap |
| --- | --- | --- | --- |
| Clarify request/lock plan | Consent, contracts, input snapshot | [Engine](../backend/src/engine.js) | Genuine user study |
| Discover authentic calls | Ranked guarded practice discovery | [Agents](../backend/src/agents.js) | Office-approved live ingestion |
| Evidence/novelty framing | Archive/public metadata/source coverage | [Sources](../backend/src/research-sources.js) | Expert entailment/novelty assessment |
| Draft objectives/methods/timeline | Structured provider contracts/fallback | [Drafting](../backend/src/llm-drafting.js) | Live quality and authentic forms |
| Agency-compliant budget | Exact INR/categories/caps/alternatives | [Rules](../backend/src/budget-rules.js) | Authentic policy verification |
| Validate before review | Blocking checks and bounded repair | [Tests](../backend/tests/pipeline.test.js) | Ambiguous ethics evidence needs humans |
| Dean/office approval | Permission/checksum-bound review/audit | [API](../backend/src/api.js) | Campus identity/security approval |
| Package/rollback | Genuine formats/confirmed Restore | [Exports](../backend/src/exports.js) | Word rendering/legacy context gaps |
| Human-controlled actions | No external transmission | [Governance](../backend/src/api.js) | Agency submission not implemented |
| Real-case capstone | Practice integration/preserved labs | [Verification](../docs/VERIFICATION.md) | Genuine-current-call human acceptance |

A green synthetic suite does not prove the real-case definition of done. No external approval form or reviewer assessment was completed.

## 4. Data, provenance and distinct counts

### Source inventory

[Catalog](../langgraph_edition/data/catalog.json) has 527 established scholarly records, 19 detailed historical awards, two applications and retained legacy sources. [Historical register](../backend/src/projects.js) has 30 rows. Sources overlap; counts/amounts cannot simply be added.

[Original inputs](../langgraph_edition/data/originals/) and [CSV supplements](../langgraph_edition/data/supplement/) contain annual college publication workbooks 2022–26, External_Funded_Project_List.xlsx, Applied_Sanctioned_Grants_2025-26-Format.xlsx and the legacy sanctioned-project document/CSV. Filenames, sheets and rows remain inspectable. These materials were already supplied with the repository; no new open-data license or broader redistribution permission is implied.

[Importer](../langgraph_edition/scripts/import_data.py), [supplement merger](../langgraph_edition/scripts/merge_supplement.py) and [audit](../tools/audit_data.py) normalize whitespace, authors, DOI identities and financial fields. The catalog-bound [sidecar](../langgraph_edition/data/reconciliation.json) retains provenance/conflict candidates without silently promoting them. Its SHA-256 must match the catalog. Originals remain unchanged. Null amounts mean unknown; sanctioned, received and requested amounts differ. Legacy summaries, applications and mocks are excluded from detailed sanctioned-award financial totals.

### Identity and overlapping awards

[Directory](../backend/src/researcher-directory.js) derives researchers separately from accounts; [explicit aliases](../backend/src/faculty.js) support known variants. Authors, home_authors, PI/co-PI evidence and original rows are considered. A first-name match is insufficient; homonyms stay ambiguous.

Saroja Siddamal / Dr. Saroja V Siddamal resolve together on supported evidence. Saroja S Bhusare remains separate, without invented papers. Two source-specific reviewed overlaps connect e-Krushi and MATOMAC register/catalog rows after title, investigator and source-year checks. Both records remain; e-Krushi's INR 600 discrepancy is visible. Other fuzzy candidates remain unresolved. Scholarly attribution does not establish verified campus authentication.

### Counter definitions

| Counter | Basis |
| --- | --- |
| Research publications | Resolved scholarly record IDs, never proposal status |
| Proposals created | Unique visible proposal IDs linked by owner/explicit stable faculty IDs |
| Awaiting review | Visible records currently awaiting_review |
| Internally approved proposals | Current approval and matching artifact/context hashes; exact historical Restore keeps historical provenance |
| Funded awards | Supported sanctioned source groups, excluding applications/internal approvals |
| Versions | Saved entries; several versions remain one proposal |

[Activity](../backend/src/proposal-activity.js) filters by viewer permissions before returning details/counts. Edits invalidate current approval but retain history. [Tests](../backend/tests/correctness.test.js) derive 1 approved proposal / 0 papers / 0 awards and unique counts across versions.

### Search and practice fixtures

[Archive search](../backend/src/research-sources.js) is offline, searches supported normalized fields and returns total/page/displayed/totalPages. Default page size 20; maximum 100. OpenAlex topic search and Crossref enrichment have separate labels/outcomes; college fallback is never OpenAlex success.

[Seed corpus](../backend/src/seed.js), [Python mocks](../langgraph_edition/data/mock/) and lab seeds contain practice calls, policies, costs, quotations and literature. These are not official agency rules. Authentic metadata does not prove scientific entailment or novelty. Private workflow/account databases are excluded from Git.

## 5. Architecture and data flow

### Main application

[React entry](../frontend/src/App.jsx) calls authenticated [API helpers](../frontend/src/lib/api.js). Vite proxies `/api` to port 3000 in development. [Express startup](../backend/index.js) serves the built console on loopback and only reports readiness after successful binding.

[API routes](../backend/src/api.js) enforce opaque expiring bearer sessions, role permissions and ownership. Sessions are memory-only. Seed identities support classroom login, not verified campus identity. Researcher profiles do not confer authentication permissions.

[Engine](../backend/src/engine.js), [agents](../backend/src/agents.js) and [runtime](../backend/src/core.js) implement a JavaScript stage graph. Eight visible roles comprise coordinator, funding discovery, literature, drafting, budget, compliance, packaging and human review. The last role is a person.

1. Capture request, consent and immutable input snapshot; construct/lock the plan.
2. Discover eligible practice calls and retrieve literature, retaining provider/source labels.
3. Draft sections; enforce structured model/source contracts or record template fallback.
4. Compute categorized budget/compliance; validate totals, evidence, scope and required fields.
5. Apply bounded targeted repair. Financial alternatives require explicit acceptance; impossible cases block.
6. Prepare a checksum-bound package, wait for authorized review and save an internal version.
7. Export the selected saved package or confirm a scope-aware historical Restore. No external submission occurs.

### Storage and integrations

Primary workflow state is local JSON (`AURA_DATA_DIR`, default Course-Project/backend/data). [Atomic writer](../backend/src/atomic-store.js) flushes unique same-directory temporary files and retries transient Windows locks. Persistent failure is surfaced; corrupt JSON refuses startup. Audit and project-budget edits persist locally. One backend writer per directory is assumed.

[MongoDB](../backend/src/database.js) optionally supports account/project administration and asynchronous workflow mirroring. [Persistence diagnostics](../backend/src/persistence.js) distinguish absent configuration and safe connection failure categories. A connected mirror does not replace an acknowledged JSON write. Runtime-created fallback accounts are not durable.

[College adapter](../backend/src/college-data.js) reads the Python edition's catalog in place; operational stores are separate. [Research sources](../backend/src/research-sources.js) separate offline archive browsing from OpenAlex public-topic search and Crossref DOI metadata. [HTTP policy](../backend/src/provider-http.js) implements bounded transient retries and Retry-After.

[Model gateway](../backend/src/model.js) selects local Ollama/Qwen or explicit Groq. Structured/source-ID checks do not prove truth, entailment or novelty. Public search terms and optional cloud drafting context have different disclosure boundaries.

### Independent edition and labs

[Python app](../langgraph_edition/app/) uses FastAPI, real LangGraph stages and SQLite state/checkpoints under `GRANT_DATA_DIR`. It serves its own static UI on port 8000, not the React UI. No operational synchronization is implemented.

[Supplied labs](../../Assignments/scripts/) are standard-library demonstrations. [Earlier lab support](../code/Lab_Support/) supports retained earlier assignment programs. Neither establishes MCP wire compatibility or an installed OpenClaw runtime. Their checks have separate scope.

## 6. Correctness and governance evidence

Public summary of current code and reproducible tests. Detailed operational audits remain locally retained and excluded from publication.

| Concern | Implemented behavior | Source evidence |
| --- | --- | --- |
| Budget preservation | Immutable inputs, categories; no silent scaling/minimum inflation | [Engine](../backend/src/engine.js), [agents](../backend/src/agents.js) |
| Monetary arithmetic | Whole INR, rational percentages/half-up rounding, explicit charge permissions and bases | [Budget rules](../backend/src/budget-rules.js) |
| Financial alternatives | Separate proposals; confirmed acceptance; stale fingerprint rejection; approval invalidation | [API](../backend/src/api.js) |
| Identity/counts | Stable IDs, retained duplicate sources/conflicts; distinct activity | [Directory](../backend/src/researcher-directory.js), [activity](../backend/src/proposal-activity.js) |
| Persistence | Unique atomic writes, bounded Windows retries, surfaced failure | [Writer](../backend/src/atomic-store.js), [core](../backend/src/core.js) |
| Providers | Safe missing/rejected/rate/timeout/network/malformed diagnostics and Retry-After | [HTTP adapter](../backend/src/provider-http.js), [sources](../backend/src/research-sources.js) |
| Exports | Genuine saved-version DOCX/PDF, auth, MIME and immutable hashes | [Renderer](../backend/src/exports.js) |
| Restore | Authorized confirmed deep-copy snapshot; missing context stays unavailable | [Engine](../backend/src/engine.js), [UI](../frontend/src/pages/aura-rundetail.jsx) |

### Budget fixture and policy boundaries

TEST input: personnel INR 250000 + equipment INR 150000 + consumables INR 50000 = INR 450000 direct. Explicit TEST rates of 15% overhead and 5% contingency on direct yield INR 67500 and INR 22500, total INR 540000. A higher minimum fails without changing costs. These rates are not agency policy.

Categories: personnel, equipment, consumables, travel, other. Legacy unclassified input cannot truthfully pass category caps. Charges round half up once to whole INR using rational intermediates; up to six fractional percentage digits are supported. Missing rates are zero; charge-disallowed flags take precedence. Charge bases: direct or direct excluding equipment. Category denominators: direct or total.

The standalone old core.tools.capReport signature retains a compatibility assumption when its denominator settings are absent; output is marked requiresPolicyReview, not official policy. Runtime typed tools use explicit rules. Historical approved figures are not rewritten. A recalled original amount cannot be reconstructed from available evidence; no missing input is invented. Working corrections retain before/after costs and invalidate current validation/package/approval. Old snapshots missing call context cannot borrow current rules.

### Approval, exports and Restore

Backend identifiers stay compatible; labels say internally approved proposals. Artifact/context hashes bind review to opened content. Exports use selected saved package/narrative/budget, without model generation or current-field substitution. Existing Markdown/CSV remain authenticated. `?version=1` selects history; stale current exports return 409.

Restore requires version:rollback authority, rejects active execution, and explains selected version, scope and missing fields before confirmation. Deep copies protect original versions. Exact historical approval provenance is retained as history, never a new review. Subsequent edits clear current approval.

[Correctness regressions](../backend/tests/correctness.test.js) cover all these paths as part of the fresh 50-test suite, including private-profile visibility, restart and persistent-write HTTP failure. Prior live OpenAlex checks returned 401/503; MongoDB is locally absent. No successful live provider, institutional acceptance or scientific truth claim follows from mocks. See [verification](../docs/VERIFICATION.md).

## 7. Setup and configuration

### Main Node/React app

Use Node 24. The supplied scripts require Node 22.13+; fresh checks used Node 24.11.1/npm 11.6.2 on Windows. From root:

```sh
npm --prefix Course-Project/backend ci
npm --prefix Course-Project/frontend ci
npm --prefix Course-Project/frontend run build
```

Copy [the safe example](../backend/.env.example) to Course-Project/backend/.env, preserving existing configuration. Start from backend so dotenv reads that file:

```sh
cd Course-Project/backend
npm start
```

Open http://localhost:3000. Windows Course-Project/setup.bat and Course-Project/start.bat provide the install/build/start path. Dependency installation needs network; offline workflow/tests need no keys, MongoDB Atlas or Ollama. A fresh clone ships no operational proposals.

Development: run `npm --prefix Course-Project/backend run dev` and `npm --prefix Course-Project/frontend run dev` in separate terminals; Vite uses http://localhost:5173 and proxies API port 3000. Rebuild before using the single-process console.

| Variable | Behavior |
| --- | --- |
| `PORT` | Backend port, default 3000; adjust Vite proxy if changed |
| `AURA_DATA_DIR` | Primary workflow directory; default Course-Project/backend/data |
| `AURA_LLM=off` | Deterministic offline template drafting |
| `GRANT_LLM` | ollama default; template disables model; groq explicitly selects cloud |
| `OLLAMA_MODEL` | Default qwen2.5:3b |
| `AURA_LLM_CONCURRENCY` | Default 1 |
| `AURA_LLM_SECTIONS` | Optional comma-separated model-drafted sections |
| `OPENALEX_API_KEY` | Optional server-side public metadata credential |
| `GROQ_API_KEY`, `GROQ_MODEL` | Explicit Groq cloud drafting |
| `MONGODB_URI` / `MONGO_URI` | Optional MongoDB; absent means JSON, not live MongoDB |
| `MONGODB_DB` | Default research_grant |
| `GRANTOFFICE_EXPORT_FONT` | Optional installed Unicode TTF for PDF |
| `AURA_STEP_DELAY`, `AURA_RETRY_BUDGET` | Pacing and bounded repair controls |

Install Ollama separately and run `ollama pull qwen2.5:3b` for local drafting. Weights are not bundled. Inspect model/template diagnostics; configuration does not guarantee successful generation. Explicit Groq sends drafting context off-device. Public search should contain only public keywords.

DOCX needs no Office installation. PDF detects Segoe UI on Windows or DejaVu Sans on Linux; otherwise configure an installed Unicode TTF. Missing fonts return a service error.

### Main verification

```sh
npm --prefix Course-Project/backend test
npm --prefix Course-Project/frontend run lint -- --max-warnings 0
npm --prefix Course-Project/frontend run build
python Course-Project/tools/verify_labs.py
python Course-Project/tools/check_docs.py
```

Labs need Python 3.10+ standard library. Set `PYTHONUTF8=1` and `PYTHONIOENCODING=utf-8` on Windows. verify.bat runs the checks above; it does not install/run the independent Python environment. Notebook rebuilding is optional; supplied outputs were not overwritten.

### Independent Python edition

Use a separate Python 3.12 environment; preserved setup accepts 3.11–3.13. From langgraph_edition:

```sh
python -m venv .venv
# Activate the virtual environment for your operating system.
python -m pip install -r requirements-lock.txt
python scripts/setup_users.py
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

PowerShell activation: `.venv/Scripts/Activate.ps1`; Linux/macOS: `source .venv/bin/activate`. Explicitly select Python 3.12 when multiple interpreters are installed. Windows setup.bat uses py -3 if present; verify that launcher selects a supported interpreter. Its initial passwords are in ignored runtime/FIRST_LOGIN.txt and differ from the Node demo password.

Storage uses `GRANT_DATA_DIR` or runtime/ SQLite/checkpoints. `AURA_DATA_DIR` does not configure this edition. In its environment run `python -m pytest -q`. Its lab mapping reuses those tests; do not count them twice. Earlier support tests run from Course-Project/code/Lab_Support with its requirements installed. [Verification](../docs/VERIFICATION.md) records executed environments.

## 8. Agent roles and implementation details

| Role | Inputs and responsibility | Governance boundary |
| --- | --- | --- |
| Coordinator | Request, consent, plan and scoped task packets | Cannot bypass review or change ownership |
| Funding discovery | Practice-call source, deadlines and eligibility | No verified live-call feed is claimed |
| Literature | College/public metadata and related work | Sources remain labeled; novelty requires review |
| Drafting | Locked plan, evidence and methods | Structured output checked; invalid output falls back visibly |
| Budget | Categorized expenses and selected rules | Original costs remain immutable; alternatives need acceptance |
| Compliance | Evidence, budget and selected constraints | Blocking/ambiguous checks stop or escalate |
| Packaging | Validated narrative, budget and checklist | Hashes bind saved content to review/export |
| Human reviewer | Opened package, permissions and decision | Internal approval only; no automatic agency submission |

The visible eight-role model includes a human gate. Actual parallelism occurs in selected discovery/drafting branches; validation and approval are gates. The JavaScript graph is implemented in its own engine, not LangGraph. The independent Python edition uses a real LangGraph graph and SQLite checkpoints. Scoped connectors centralize typed access but are not certified MCP protocol implementations. Runtime demonstrations do not prove an installed OpenClaw runtime.

The React interface includes intake, project register, research archive, faculty profiles, proposal stages, budget editing, review/version controls and platform diagnostics. Stable IDs join activity without assigning authentication privileges. Authenticated download helpers support both current and selected historical packages. Confirmed working-budget changes and revisions invalidate validation, package and current approval; this prevents new content inheriting an old decision.

## 9. Verification methodology and results

Verification is organized by scope: Node tests exercise the main API/engine; lint/build checks frontend source; Python tests exercise the independent edition; the earlier support suite covers separate lab code; supplied notebook terminal assertions check captured script traces. Counts from overlapping/repeated suites are never added. Real records are not replaced by fixtures to obtain a passing result.

Fresh results on 18 November 2026: main backend 50 passed; frontend lint zero errors/warnings; production build passed; supplied labs 140/140 trace assertions; independent Python application 66 passed; earlier lab support 70 passed. The original installed Python 3.10 run required UTF-8 mode; the first default-encoding run produced one decoding failure (65 passed/1 failed), then passed 66 with UTF-8. The installed dependency environment emitted one pytest deprecation warning. A separate clean Python 3.12 lock installation and verification is recorded in the verification document; reruns are not additional unique tests.

The new correctness regressions cover explicit categories and cap bases, immutable input snapshots, no silent minimum inflation or ceiling scaling, homonym separation, retained project conflicts, unique permission-filtered activity, stale approval/package rejection, deep-copy Restore, authenticated current/historical binary exports, atomic transient/persistent Windows failures, corrupt state, HTTP save failure, process restart, provider classifications, independent Crossref behavior and startup port failure.

The current browser check captures only public login branding and records zero page runtime errors. Earlier same-day isolated browser checks covered routes/tabs at desktop/tablet/phone widths and financial/review behavior; these remain prior evidence, not a fresh full browser rerun. Recent provider probes returned OpenAlex 401/503 and do not establish a valid key or successful retrieval. No fresh live provider, MongoDB or model-quality acceptance is claimed here.

Document validation checks genuine OOXML ZIP/XML/table structure and PDF parsing/rendering. Native Microsoft Word COM rendering was previously blocked by the Windows logon-session restriction; no Word-rendered layout is claimed. Final actual document results and reproducible commands are maintained in the verification record.

## 10. Genuine current screenshot

![Current public login branding, captured in Microsoft Edge on 18 November 2026](../docs/screenshots/current/login-brand-2026-11-18.png)

The crop intentionally excludes account details and proposal text. It documents the present KLE/GrantOffice branding. Supplied older screenshots are labeled historical and are not represented as current evidence.

## 11. Limitations and future work


| Status | Finding |
| --- | --- |
| Implemented/tested | Main workflow, ownership, budgets, counts, exports and Restore have offline regressions, not institutional certification. |
| Implemented/live unverified | MongoDB auth/network/recovery/mirror need infrastructure; current local mode is JSON. |
| Implemented/quality unverified | Ollama/Qwen and explicit Groq have controlled response/outage tests; no fresh live quality result. |
| Provider failure | Prior OpenAlex checks returned 401/503. No fresh live Crossref success is claimed. |
| Persistence boundary | JSON assumes one writer; fallback-created accounts/sessions are memory-only; no distributed JSON/Mongo transaction. |
| Historical gap | Recalled input cannot be reconstructed; missing old context stays unavailable. |
| Policy boundary | Practice calls/rates/quotations are synthetic. Legacy cap-helper compatibility is marked for policy review. |
| Rendering boundary | Native Word COM rendering was blocked; DOCX structure and PDF rendering are separately checked. |
| Dependency warning | Installed anyio pytest plugin emits PytestRemovedIn10Warning; assertions remain enabled. |
| Course completion | Division and independent confirmation of team details need a filled document. Marks/signatures remain blank. |
| Attribution | No new license or broader source-data redistribution permission. |

Future work: approved live-call ingestion; authentic agency/ethics policy/quotations; expert entailment/novelty review; campus SSO and production sessions/passwords; institutional security review, HTTPS, backups/recovery; agreed production engine/storage; pending identity/financial conflict review; live integration and genuine-call college acceptance. No measured speed improvement, external submission or production deployment is claimed.

## 12. References and reproducibility

1. [Original course problem statement](../Problem_Statement/Research_Grant_Management_System.docx), supplied project document, preserved unchanged.
2. [Agentic AI 15 Worklets / 14-Lab Build Book](../docs/originals/Agentic_AI_15_Worklets_14Lab_Build_Book.docx) and [lab guide](../docs/originals/Agentic_AI_Lab_Guide.docx), supplied course originals.
3. [Current backend source](../backend/src/) and [backend tests](../backend/tests/), implementation evidence, inspected 18 November 2026.
4. [College catalog](../langgraph_edition/data/catalog.json), [provenance reconciliation](../langgraph_edition/data/reconciliation.json) and retained original workbooks/CSVs, supplied institutional records.
5. [OpenAlex authentication documentation](https://help.openalex.org/api/authentication/) and [error documentation](https://help.openalex.org/api/errors/), consulted during the earlier correctness diagnostic; no successful live retrieval inferred.
6. [docx Packer](https://docx.js.org/api/classes/index.Packer.html) and [PDFKit tables](https://pdfkit.org/docs/table.html), library references for genuine binary exports.
7. [Fresh verification record](../docs/VERIFICATION.md), [assignment index](../../Assignments/README.md) and [repository audit](../docs/REPOSITORY_UPDATE_REPORT.md).

No literature performance comparison, measured productivity improvement, completed faculty review or production deployment is invented. To regenerate report binaries after editing this Markdown, install backend dependencies and run `node Course-Project/tools/render_report.js` from repository root. The report renderer is separate from the application's saved-proposal export path.
