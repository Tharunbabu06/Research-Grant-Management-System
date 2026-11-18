# GrantOffice: Research Grant Management System

Technical implementation report · Chapter 13 · Agentic AI (26ECAC401) · 15 November 2026

## Problem statement

Faculty grant development combines fragmented call discovery, literature search, proposal writing, budgeting and compliance. Separate files make deadlines, evidence and review status difficult to track. The course worklet calls for a coordinator-plus-workers application that drafts and flags while a named human authorizes consequential actions.

## Objectives

Provide a single faculty intake and proposal workflow; retrieve candidate evidence; match eligible demonstration calls; draft structured sections; calculate and check budgets; record source resolution and audit events; require human review; preserve versions and downloadable artifacts. Maintain a usable college-facing interface and clearly distinguish actual source records, proposed work and classroom fixtures.

## Sources and implementation approach

The main implementation comes from the complete supplied Course-Project repository. Its Express backend and React frontend form the primary runnable edition. GrantOffice contributes its navy/teal design language, preserved Python implementation and college publication catalog. A server-side provider adapter adds local Ollama/Qwen and optional explicitly selected Groq. OpenAlex performs public keyword search; Crossref completes DOI metadata. API keys remain server-side.

The original Python/FastAPI/LangGraph application is included independently under langgraph_edition. Its SQLite checkpoint workflow is not the engine used by the main React application. This distinction is deliberate and visible in the documentation; a full conversion or unification was not performed.

## Architecture and workflow

The React console calls the Express API using an opaque bearer session. The API enforces role and run ownership before accessing workflow state. The coordinator invokes call discovery, literature retrieval, section drafting, budget preparation, compliance, validation, bounded repair and review stages. Independent sections can execute concurrently; validation and approval remain sequential gates. The service binds to loopback for local use.

MongoDB is optional. Without its connection string, the main service retains runs in its local JSON state store and budget overrides in a separate local JSON file. The original Python edition uses its own SQLite databases. These stores are not synchronized. The source catalog is read-only for main public-literature retrieval.

Intake preserves public search terms separately from the faculty plan. Empty public terms make no external request. Candidate records carry provider, abstract/metadata level and available provenance. DOI normalization consolidates duplicates. A source timeout is distinguishable from a successful empty result. The proposed engineering methodology remains part of the run parameters and drafting context.

The model returns structured paragraphs with source IDs. The application rejects malformed or unsupported-contract output and records a template fallback. The bench-loop template maintains the proposed pump, tubing, sensor and calibration scope. It does not assert completed results or invent a particular CFD package. Model connectivity and accepted output are separate facts.

## Governance and quality controls

Session identity comes from the server rather than editable actor headers. Faculty may access their own runs. Office roles can review according to the supplied role permissions. Draft edits are validated before mutation. Manual text cannot inherit generated-source certification. Reviews bind to the opened package checksum and revalidate the current content fingerprint. A changed package requires revalidation. Internal publication creates a version; it sends nothing to a funding agency.

Citation checks confirm source-ID resolution and quote presence. They do not establish that a source entails a claim or that a method is novel. Practice-call flags and generated estimates remain demonstration information. Real agency eligibility, institutional approval, ethics and quotations require original evidence and authorized review.

## Verification and results

The final backend suite passes 18 tests, including all 9 supplied reference tests. The added regressions cover authentication, ownership, persisted budgets, public-source normalization and failures, local model behavior, intake persistence, checksum-bound review, authenticated download, atomic edits and bench-scope drafting. The React production build passes.

All 14 supplied lab scripts run successfully against their notebook terminal acceptance cells, giving 140 of 140 trace assertions. The separately preserved Python application passes 53 pytest tests with one dependency deprecation warning. These are distinct verification scopes and must not be combined into a claim that every feature has independent end-to-end coverage.

A browser smoke test could not start Chromium because the execution environment prohibited its local socket. Native Windows launch, live Ollama responses, live provider keys and MongoDB Atlas were not tested. The supplied local demo checklist covers those remaining checks. No measured latency improvement, scientific result or live funding match is claimed.

## Limitations and future work

The main application is a practice workflow with seeded calls, policies, costs and literature. Its source-coverage score is a structural retrieval indicator. Several reference domain templates remain tailored to demonstration topics. Sparse public results can leave the composer using the labelled practice corpus. Further work should add a real funding-call ingestion and office verification process, stronger semantic relevance and entailment assessment, a citation-aware manual revision interface, campus SSO, durable session management and one agreed production workflow engine.

The separate historical project and college award registers need a reviewed reconciliation policy before totals can be combined. Before a college pilot, validate permissions against actual institutional roles, replace fixture policy and rates with approved documents, test on native Windows and inspect the interface and downloads in a live browser.

## Reproducibility and references

See ../docs/VERIFICATION.md for commands and test scopes, ../docs/MERGE_AUDIT.md for the source comparison, and ../docs/source_inputs.json for input archive identities. The original problem statement, course build book, lab guide and review sheet are retained in this package. Upstream evidence and screenshots remain historical materials.
