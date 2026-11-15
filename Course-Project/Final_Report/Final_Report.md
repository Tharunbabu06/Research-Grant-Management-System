> Preserved report source: results below describe the historical Linux packaging run of 15 November 2026. See [current verification](../docs/Verification.md) for the Windows reorganization checks. The accompanying PDF is preserved unchanged and may contain the former folder names.

# Research Grant Management System
Final Course Project Report
Team 13 | Agentic AI (26ECAC401)
KLE Technological University, Hubballi

## Project overview

### Abstract

The Research Grant Management System supports the institutional journey from a faculty request to a reviewed grant proposal and compliance package. A coordinator orchestrates funding discovery, literature retrieval, narrative drafting, budget calculation and compliance checks. The college application combines LangGraph orchestration, a FastAPI backend, local Qwen through Ollama, OpenAlex discovery, Crossref DOI metadata and institutional research records. Outputs are assembled for human authorization, versioned internal release and manual submission through the agency channel.

### Problem statement

Funding opportunities are scattered across agency websites and office communications. Faculty must relate their research to a suitable call, review prior work, draft a narrative and prepare documents against changing requirements. Separate files make it difficult for the Dean R&D office to monitor deadlines and discover compliance gaps early. Chapter 13 frames the worklet as a shared, governed process with a named human authority.

### Objectives

Provide an editable grant plan; centralize source access; retrieve relevant literature with provenance; generate an explicitly proposed narrative; calculate an itemized budget; check the selected call and institutional requirements; preserve review decisions and versions; and provide a dashboard showing the case and its next action.

### Stakeholders and scope

Faculty or PI supplies the request, research intent, consent and supporting material. HoD participates within department permissions. Research Office or Dean records authoritative rules and authorizes institutional release. The submission includes standalone assignments and the integrated GrantOffice application as related implementations with separate contracts and tests.

## Architecture and workflow

### System components

The browser interface calls authenticated FastAPI endpoints. The application coordinator creates the locked plan and starts a LangGraph StateGraph. Specialist nodes invoke a governed Connector for institutional data, call rules and evidence. SQLite stores local accounts, runs, approvals, audit events and release versions; a separate SQLite checkpointer supports graph recovery. Model generation uses the local Ollama endpoint and a typed response contract.

### Execution order

Intake and editable planning precede execution. Funding discovery and literature review fan out concurrently and join before drafting. Budget calculation and preliminary compliance fan out from the draft and join at validation. A passing result is assembled, hashed and paused at a human review interrupt. Approval resumes the saved thread and produces an internal release after authority and deadline checks.

### Dependencies and failure paths

Calls are ranked against research area, funding type, duration and source status. Literature supports drafting, while the budget and call constraints feed validation. An inconsistent budget total can be recomputed within a bounded retry limit. Missing evidence, an excessive budget or unresolved mandatory rule blocks progression. Review requests can create a revised draft and invalidate earlier approval.

### Book-to-code interpretation

The build book describes parallel discovery/literature and budget/compliance stages, alongside simplified sequential pseudocode. GrantOffice implements the explicit parallel stages. Its current graph validates before assembling the package. Checking the exact rendered agency files is a further acceptance requirement for an agency-specific pilot. The connector supplies an MCP-style governed interface; the supplied application does not implement MCP wire-protocol interoperability.

## Data, retrieval and model integration

### College catalog

The merged catalog contains 527 publication records, 19 detailed historical awards, two applications with unknown outcomes and 60 searchable legacy records. Publication import preserves workbook or CSV row references and reconciles duplicate identifiers and DOI-only rows. Historical award totals use the detailed modern register. Legacy references and applied amounts are excluded from that aggregate.

### Evidence and source boundaries

A source record identifies its document or URL, locator and relevant text. The application records guideline and policy versions and manual office attestation. A current call must have a valid deadline and current verification before selection. College records establish institutional context. Official call rules and human assessments are still required for a real proposal. Source authenticity is not established merely by the presence of a citation.

### Literature services

OpenAlex is requested only when the plan contains explicit public literature keywords and the server has OPENALEX_API_KEY. The gateway requests up to six works, reconstructs available abstracts and merges discovered DOI matches with local records. Crossref enriches up to two newly discovered DOIs. Status values distinguish no request, missing key, no results and unavailable sources. Local retrieval remains available independently.

### Local generation and retrieval limits

Qwen defaults to qwen2.5:3b through Ollama on the local loopback endpoint. Structured JSON outputs are validated against Pydantic schemas and their evidence IDs are checked against the provided context. Invalid output receives bounded retries, followed by a labelled template fallback. Local ranking uses lexical feature hashing. This can rank papers with common wording above more relevant domain papers, so relevance and scientific claims require review.

## Assignment implementation

### Submission organization

Assignments contains fourteen Python entry files. Labs 1-8 and 14 reuse the supplied standalone entries with a small import-path preamble. The submitted archive implements Labs 9-13 under graph/ and tests/; the new assignment entries run these supplied acceptance scenarios. Shared implementations and fixtures are under Course-Project/code/Lab_Support so the Assignments folder contains only the requested Python files.

### Labs 1-4

Lab 1 demonstrates clarify, plan and revise. Lab 2 reads funding and budget data and calculates a total through tools. Lab 3 packages planning and formatting as reusable skills. Lab 4 separates session state from reference and history retrieval. The early exercises use local example data and gradually establish the contracts needed by later stages.

### Labs 5-8

Lab 5 exposes source data through an authenticated local connector. Lab 6 adds execution control, audit records and checkpoints. Lab 7 compiles the grant node graph. Lab 8 dispatches parallel work and merges results against the plan. The standalone connector uses port 8000, so the web application must be stopped while running connector-backed lab demos. Parallelism does not imply a measured latency improvement for every workload.

### Labs 9-14

Lab 9 validates evidence and relevance. Lab 10 diagnoses faults and repairs supported constraints. Lab 11 applies an acceptance suite to the locked specification. Lab 12 tests identity contracts, authorization, publication and rollback. Lab 13 applies government, industry and international funder profiles. Lab 14 integrates a graph run with a static dashboard. A blocked capstone result is expected when genuine sources or approval are absent.

### Assignment count

The team identifies the fourteen build-book labs as its course assignments. All fourteen are included. The instructor notice refers to twelve assignments; the team should confirm the numbering arrangement rather than omit two lab deliverables.

## Governance and user interface

### Authentication and scope

GrantOffice has faculty, HoD, Research Office and Dean roles. Run access uses ownership and department scope. Raw grant spreadsheet rows are restricted to Research Office or Dean. Passwords are hashed and sessions expire. The standalone assignment authorization contract is a teaching demonstration and remains separate from deployed user identity.

### Review and release

Institutional drafts need the proposal owner confirmation and per-rule eligibility assessment from the office. A passing rule must reference eligibility evidence. Reviews are tied to a digest of the plan, narrative, call, literature and evidence. A changed fingerprint requires fresh review. Institutional release requires Research Office or Dean authority; the selected call and validation are checked again at release.

### Versioning and audit

The release operation stores the package and hash with a version and reviewer record. Revision resets active approval and retains prior release history. Rollback restores an approved internal version. Audit events form a hash chain and preserve input/output references and decisions. The export includes the proposal, budget, compliance, literature, evidence and audit material.

### Dashboard and usability

The supplied interface provides overview metrics, a pipeline, call registry, research archive, evidence entry, proposal tabs, review/version views and administrative settings. The UI exposes source status and template fallback. Screenshots from later development show requested improvements, but this report uses the uploaded GrantOffice code as the deliverable baseline. A college pilot should verify mode labels, practice filtering, status wording, provider status, responsive layout and accessible review actions.

### Data handling

Original college data is included in the project archive. Institution-approved sharing scope and repository visibility must be confirmed before GitHub publication. Runtime accounts, API keys, local databases and model weights are excluded from the submission package. Practice fixtures retain their testing labels and do not represent verified funding opportunities.

## Evaluation and results

### Verification method

The supplied standalone lab and web suites were executed on 15 November 2026 using Python 3.12.14 in an isolated Linux environment. Tests use controlled records, temporary state and mocked model or network responses where supplied. Both suites were rerun from their reorganized repository locations. The assignment entries for Labs 9-13 were also executed individually and returned successful exit codes.

### Measured outcomes

Standalone lab implementation: 70 tests passed. GrantOffice web application: 53 tests passed. All fourteen assignment entry files parsed successfully. The suites are separate and their counts are reported separately. One environment warning concerns a pytest plugin API scheduled for removal. Native Windows and the exact locked dependency set were not independently reproduced in this packaging run.

### What the tests establish

The lab suite exercises evidence rejection, relevance screening, diagnosis, budget repair, acceptance checks, authorization, specialist contracts and capstone summaries. The web suite covers authenticated endpoints, budget validation, checkpoint recovery, hash-bound decisions, revision invalidation, raw-row restrictions, structured LLM handling and mocked OpenAlex/Crossref behavior.

### Unmeasured acceptance

This run did not perform live Ollama inference, live OpenAlex or Crossref requests, interactive Labs 1 and 6, a browser walkthrough or a genuine institutional funding-call review. Test outcomes therefore support software behavior under the tested inputs. Real proposal quality, source accuracy, eligibility and light-edit acceptance require faculty and research-office evaluation.

### Limitations and next validation

The supplied app archive has no fourteen-folder integrated lab tree. Assignments are provided from the separate lab source. The web pipeline produces a generic export and requires selected agency templates for final submission. Improve topic relevance and inspect exact rendered package requirements before a real pilot. Choose one current official call, record its policy and required evidence, test a passing case and a blocked case, and verify the authorized export with the designated reviewer.

## Deployment and references

### Local deployment

Open Course-Project/code/GrantOffice on Windows and execute start.bat. First launch installs the local environment and initializes missing accounts. The app listens on 127.0.0.1:8000. Read the generated FIRST_LOGIN file locally, configure the installed Qwen model and set OPENALEX_API_KEY in the same server environment. The key is needed for external discovery; it is not part of the repository.

### Lab execution

Install Course-Project/code/Lab_Support/requirements.txt in a separate lab environment and run the corresponding Assignments/labNN.py entry. Lab 1 and Lab 6 require interactive input. Labs 5-8 and 14 use the standalone connector; launch connector/grant_connector.py from Lab_Support after stopping the web app. Run pytest within each implementation folder to reproduce its independent verification suite.

### Conclusion

The submission demonstrates incremental construction of a governed research-grant workflow through fourteen labs and an integrated web application. The recorded tests support the implemented failure handling, evidence structure and authorization paths. Institutional deployment proceeds through a scoped pilot with current official rules, faculty review and an authorized package release.

### References

1. Course-supplied Agentic AI Worklets - 14-Lab Build Book, Chapter 13, Research Grant Management System, sections 13.1-13.12. Included as [Build_Book.md](../Problem_Statement/Build_Book.md).
2. Submitted Grant_Agent_Project (3).zip, standalone lab implementation and acceptance tests.
3. Submitted GrantOffice_Updated(1).zip, integrated application, catalog and tests.
4. LangGraph documentation: https://docs.langchain.com/oss/python/langgraph/overview
5. Ollama structured output documentation: https://docs.ollama.com/capabilities/structured-outputs
6. OpenAlex API documentation: https://help.openalex.org/api/authentication/
7. Crossref REST API documentation: https://www.crossref.org/documentation/retrieve-metadata/rest-api/
