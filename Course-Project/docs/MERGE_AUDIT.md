> Historical reference/merge document. Use [current documentation](README.md) and [fresh verification](VERIFICATION.md).

# Source comparison and merge audit

Prepared 15 November 2026. Main source: the complete `Reasearch-grant-management-system-main (1).zip` (149 files). See source_inputs.json and primary_archive_inventory.json for exact identities. Earlier incomplete archives were not used as the implementation baseline.

## Folder inspection

| Source folder | What was inspected / retained |
|---|---|
| Assignments | 14 standalone lab scripts, 14 notebooks, notebook builder and supplied trace acceptance cells |
| Course-Project/backend | Express routes, coordinator, agent stages, tools, source fixtures, model drafting, persistence, projects, users, governance, tests, dependency lock |
| Course-Project/frontend | React routing, login, faculty/Dean dashboards, intake, runs, tabs, people, projects, audit and platform controls; dependency lock and build |
| Course-Project/Problem_Statement | Original DOCX; extracted text confirms Chapter 13 grant-discovery → evidence → proposal/budget/compliance → human authority |
| Course-Project/docs | Original build book, lab guide, review sheet, canvas and historical screenshots retained. Build-book text extracted to check scope |
| Course-Project/evidence | Supplied lab evidence retained; fresh test results kept separately |
| Course-Project/Final_Report | Upstream contained a placeholder README, not a finished report. Added a technical report for the merge |

## Technology comparison

| Concern | Main complete reference | Earlier GrantOffice | Merged delivery |
|---|---|---|---|
| Frontend | React / Vite | Static web assets | React with GrantOffice navy/teal styling |
| API / workflow | Express / JavaScript coordinator | FastAPI / Python LangGraph | Express main; original LangGraph app in langgraph_edition |
| Model | Optional Groq | Ollama / Qwen | Ollama/Qwen default; explicit optional Groq |
| Literature | Seeded practice corpus | College catalog and public providers | Separate college/public literature search; public terms in intake; source-labelled results |
| Public metadata | No live OpenAlex/Crossref integration | Provider integrations | Server OpenAlex search plus Crossref DOI enrichment |
| Storage | Optional MongoDB; file fallback for runs | SQLite and LangGraph checkpoints | Original modes preserved; local budget edits now persist too |
| Assignments | 14 scripts/notebooks | 14 capability mapping | Exact complete-reference assignment files retained |

These are two distinct applications. The main Node workflow has not been converted to LangGraph. No OpenClaw runtime or MCP wire-protocol server was added. Course runtime/connector capabilities are implemented by the supplied JavaScript and Python code.

## Fixes and additions

- Opaque expiring server sessions replace fabricated identity tokens. Passwordless login and x-actor-id impersonation are rejected. Session logout is effective. Classroom demo credentials remain explicit.
- Faculty run reads, edits, download routes and lists enforce ownership. Dean / office permissions govern review. UI role selection no longer changes a logged-in identity.
- Project budget updates validate positive integer INR and ownership, compute totals and persist to the local file store when MongoDB is absent.
- Removed startup cleanup that deleted existing runs/accounts based on names or fixture labels. Removed silent 50-run truncation and collision-prone count-based run IDs.
- Draft revisions validate the whole request before mutation. Unreviewed manual prose cannot inherit generated citation coverage as certification. A dedicated source-review editor remains future work.
- Reviews carry the checksum of the opened package. Server approval rechecks current validation and the content fingerprint, rather than trusting cached pass counts. Inline edits during approval are rejected.
- Authenticated proposal download works through a bearer-authenticated fetch.
- Ollama adapter uses the local loopback service and a configurable Qwen model, timeouts and structured output. Errors produce recorded template fallbacks. Provider status does not assert a model response occurred.
- College catalog records include spreadsheet provenance. OpenAlex abstracts and metadata carry their evidence level; normalized DOI duplicates are consolidated. Crossref enriches up to four returned DOI records and reports partial failures.
- Optional public literature keywords and faculty methodology are saved with the intake. Empty public terms deliberately make no external request. The public literature view is separately searchable.
- The bench-loop fallback composer preserves the pump/sensor/digital-model scope and avoids unsupported aorta software or clinical-cohort claims. Other reference domain templates retain their practice-only status.
- Corrected source coverage so nonexistent sources and missing evidence cannot count as grounded. The test still checks resolution, not scientific truth.
- Root setup/start/verify scripts and current documentation replace obsolete application paths. Historical upstream README files are preserved with REFERENCE prefixes.

## Remaining limits

The reference source is a classroom demonstration, not a verified funding-call feed. Its `verified` call field means accepted within the fixture register; it is not independent verification of a real agency call. Therefore the main workspace remains visibly marked Practice workflow. Seeded fixture costs and citations cannot be relabelled as official evidence. Real calls require source documents, current eligibility checks and Research Office review; the preserved Python edition has its own institutional workflow.

The default corpus and templates are strongly oriented to the supplied demonstration topics. The new bench scope is supported, but arbitrary topics need further retrieval-quality and source-entailment work. If fewer than four abstract sources are available, the main proposal composer can use its seeded practice corpus; source status and source records remain visible. Public-search success does not prove novelty.

The 527-record college catalog is not forcibly merged with the reference project's separate historical project register: they represent different registers and totals must not be added as distinct awards without a reconciliation rule. The directory and passwords are for local demo use, not campus authentication. Sessions are process-local. MongoDB/cloud credentials and live external services were not tested.

Current validation is structural and rule based. Passing it is not approval of methodology, clinical safety, eligibility, novelty, budget quotations or research findings. No external submission is sent by the workflow.
