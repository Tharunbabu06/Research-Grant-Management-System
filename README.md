# Research Grant Management System

**Course project and fourteen laboratory assignments**<br>
**Course:** Agentic AI (26ECAC401)<br>
**Institution:** KLE Technological University, Hubballi<br>
**Department:** Computer Science & Engineering (AI)<br>
**Team:** 13<br>
**Repository:** Research-Grant-Management-System

## Team details

| Name | USN | Division |
| --- | --- | --- |
| Soujanya Tikare | 01FE23BCI064 | Confirmation required |
| K. Tharun Babu | 01FE23BCI078 | Confirmation required |
| NT Basavaraj | 01FE23BCI031 | Confirmation required |
| K Rohith | 01FE23BCI113 | Confirmation required |

Names and USNs preserve the supplied submission details. The division and original team evaluation sheet require confirmation.

## Submission artifacts

[Fourteen assignments](Assignments/) | [Application code](Course-Project/code/GrantOffice/) | [Shared laboratory implementation](Course-Project/code/Lab_Support/) | [Problem statement](Course-Project/Problem_Statement/Problem_Statement.md) | [Supplied Chapter 13 build book](Course-Project/Problem_Statement/Build_Book.md) | [Final report PDF](Course-Project/Final_Report/Final_Report.pdf) | [Editable report](Course-Project/Final_Report/Final_Report.md) | [Supporting documentation](Course-Project/docs/) | [Current verification](Course-Project/docs/Verification.md) | [Execution evidence](Course-Project/docs/evidence/)

## Repository structure

```text
Research-Grant-Management-System/       # Git repository root; checkout directory may differ
├── README.md
├── .gitignore
├── requirements.txt                   # application + lab dependency entry point
├── Assignments/
│   ├── lab01.py ... lab08.py
│   └── lab09.py ... lab14.py           # fourteen Python entry files
└── Course-Project/
    ├── Problem_Statement/
    │   ├── Build_Book.md               # supplied Chapter 13 conversion
    │   └── Problem_Statement.md
    ├── Final_Report/
    │   ├── Final_Report.pdf            # preserved original PDF
    │   └── Final_Report.md             # editable source; current-path annotation
    ├── code/
    │   ├── GrantOffice/                # FastAPI application
    │   │   ├── app/, static/, scripts/, tests/, notebooks/
    │   │   ├── data/                   # college originals, reconciled catalog, mocks
    │   │   ├── requirements.txt, requirements-lock.txt
    │   │   └── *.bat, start.sh, Dockerfile, compose.yaml
    │   └── Lab_Support/
    │       ├── agents/, connector/, graph/, memory/
    │       ├── runtime/, skills/, swarm/, tools/
    │       ├── data/, tests/
    │       └── requirements.txt
    └── docs/
        ├── README.md, ARCHITECTURE.md, Verification.md
        ├── WINDOWS_SETUP.md, USAGE_GUIDE.md, OPERATIONS.md
        ├── OLLAMA.md, UPGRADE.md, DATA_AUDIT.md, LAB_MAPPING.md
        └── evidence/                  # dated historical and current execution records
```

Local `.venv/`, application `runtime/` and generated lab `outputs/` are ignored. Existing local accounts and databases were retained during the move. There is no redundant inner repository folder.

## Assignment overview

All fourteen entries were inspected and imported independently on Windows with Python 3.13.7. Logic and fixtures remain in Lab_Support; its location is added to each entry's import path. The supplied lab suite has 70 passing tests, principally for Labs 9–14 and their graph integration. This does not mean every interactive or connector scenario was executed.

| Lab | Implementation and purpose | Entry file | Current verification |
| --- | --- | --- | --- |
| 1 | Clarify a request, create a plan and accept revisions | [lab01.py](Assignments/lab01.py) | Syntax/import pass; scripted input run passed (no revision requested) |
| 2 | Read funding and budget fixtures; calculate and validate costs through tools | [lab02.py](Assignments/lab02.py) | Syntax/import and fixture demonstration passed |
| 3 | Reuse planning and formatting skills for two research topics | [lab03.py](Assignments/lab03.py) | Syntax/import and both demonstration cases passed |
| 4 | Separate session memory from reference and proposal-history retrieval | [lab04.py](Assignments/lab04.py) | Syntax/import and fixture demonstration passed |
| 5 | Access data through the authenticated local connector | [lab05.py](Assignments/lab05.py) | Syntax/import passed; connector demonstration not run |
| 6 | Bound runtime actions; audit, checkpoint, resume and gate publication | [lab06.py](Assignments/lab06.py) | Syntax/import passed; interactive connector demonstration not run |
| 7 | Execute the LangGraph grant workflow with validation and review routing | [lab07.py](Assignments/lab07.py) | Syntax/import and suite integration checks passed; connector demonstration not run |
| 8 | Fan out three work items and merge the highest plan-alignment result | [lab08.py](Assignments/lab08.py) | Syntax/import and all four built-in acceptance checks passed |
| 9 | Validate evidence locators, source scope and literature relevance | [lab09.py](Assignments/lab09.py) | Acceptance entry passed: 13 tests |
| 10 | Diagnose failures and apply bounded targeted repairs | [lab10.py](Assignments/lab10.py) | Acceptance entry passed: 9 tests |
| 11 | Enforce locked-plan acceptance checks before advancing | [lab11.py](Assignments/lab11.py) | Acceptance entry passed: 12 tests |
| 12 | Enforce identity, approval, versioning and rollback contracts | [lab12.py](Assignments/lab12.py) | Acceptance entry passed: 14 tests |
| 13 | Apply government, industry and international funder specialists | [lab13.py](Assignments/lab13.py) | Acceptance entry passed: 15 tests |
| 14 | Integrate the grant graph and generate a capstone dashboard | [lab14.py](Assignments/lab14.py) | Syntax/import and 7 capstone suite tests passed; connector demonstration not run |

Labs 9–13 are acceptance-scenario entry files: they discover the original `test_lab9_*`, `test_lab10_resilience`, `test_lab11_acceptance`, `test_lab12_governance` and `test_lab13_specialists` modules. The archive supplied their implementations as modules and tests rather than numbered entry scripts. Lab 8 also executes its own acceptance checks. Lab 14 calls `run_capstone`; missing authentic evidence or human authorization must produce a blocked result. The application has its own separate 53-test acceptance suite and capability mapping.

## Project explanation

### Problem statement and objectives

Faculty find funding opportunities across agency websites and office communications, then prepare literature reviews, narratives, budgets and compliance material in separate files. Late eligibility checks and fragmented records make deadlines and review status difficult for the Dean R&D office to monitor. Chapter 13 specifies a coordinator with specialist workers and a named human authority.

The objectives are to centralize the request and locked plan, match suitable calls, retrieve literature with provenance, draft an editable proposal, calculate a justified budget, validate call-specific requirements, and assemble a versioned proposal and compliance package. Faculty, HoD, Research Office and Dean participate according to their roles. Institutional release remains subject to human approval; agency submission occurs manually.

### Approach and agent workflow

The coordinator clarifies intake, records consent and locks the plan. Funding discovery and literature review run in parallel and join before proposal drafting. Budget planning and preliminary compliance then run in parallel. Validation checks plan consistency, evidence, deadlines, required documents and integer-INR budget calculations. A reconcilable total can be repaired within a bounded retry limit; unresolved failures block progression.

Passing validation permits package assembly and hashing, followed by a human review interrupt. Faculty confirmation and office eligibility assessments bind to the draft fingerprint. Changes require renewed review. Authorized Research Office or Dean release creates a version and audit record; exports support manual agency submission and rollback retains version history. See [architecture and contracts](Course-Project/docs/ARCHITECTURE.md).

### Implementation and component roles

| Component | Actual role and limits |
| --- | --- |
| FastAPI and browser interface | Authenticated endpoints and a same-origin HTML/CSS/JavaScript dashboard for intake, cases, evidence, review and export |
| LangGraph | Explicit state graph, parallel branches, joins, bounded repair, persisted checkpoint threads and human interrupt/resume |
| Qwen through Ollama | Local structured narrative generation; default model `qwen2.5:3b`. Pydantic and evidence-ID checks bound outputs; invalid/unavailable generation leads to a labelled template fallback. Model weights are external |
| OpenAlex | Optional public literature discovery when explicit public keywords and `OPENALEX_API_KEY` are configured; source status is surfaced |
| Crossref | DOI metadata enrichment for discovered literature; outages retain local retrieval. Neither service proves scientific novelty |
| SQLite | Local users, sessions, runs, approvals, immutable registry records, release versions and hash-chained audit; separate SQLite graph checkpoints |
| College dataset | Institutional research context and provenance: 527 publications, 19 detailed historical awards, 2 applications and 60 searchable legacy records in the current catalog |
| Governed connector | Central typed/scoped data and tool access. It is an MCP-style interface, without MCP wire-protocol interoperability |
| Validation and human approval | Software gates reject inconsistent or unsupported packages; named reviewers establish factual adequacy, eligibility and institutional authority |

College history is not a verified current funding-call registry. Practice fixtures are synthetic and cannot establish official eligibility. Structural citations do not establish source authenticity. Lexical hashing retrieval needs faculty relevance review, and the generic export still requires the selected agency's exact forms.

### Measured results and evidence boundaries

On **15 November 2026**, the relocated code passed **70 standalone lab tests** and **53 application tests** on **Windows, Python 3.13.7**. All fourteen assignment files passed syntax/import checks; Labs 1–4 and 8–13 ran successfully. The application started through `scripts/serve.py` with disposable accounts/storage; health, home and static assets returned HTTP 200. Browser opening was suppressed. Existing local office runtime hashes remained unchanged during startup checking.

The root dependency installation succeeded offline against already installed packages, and `pip check` passed. This verifies installed dependency compatibility; it is not a clean online installation. An initial application test failure used Windows default decoding for UTF-8 UI files; explicit UTF-8 fixed it before the passing rerun. See [verification details](Course-Project/docs/Verification.md) and [evidence provenance](Course-Project/docs/evidence/README.md).

Tests use fixtures, controlled model/network responses and temporary state. No live Ollama inference, OpenAlex/Crossref requests, current browser walkthrough or genuine institutional acceptance was performed in this correction. Historical Linux test records and the original October browser/timing report are separately labelled. Their counts and catalog baselines must not be combined with current measurements.

## Windows installation and execution

Run commands from the Git repository root unless a `Set-Location` command is shown. Install Python 3.11–3.13; 3.12 is the supplied reference version. These commands select 3.12 explicitly; use `py -3.13` if that is the installed supported interpreter. The default `python` on the checked machine is 3.10 and is unsuitable; the preserved application environment provides 3.13.7.

### Install the shared dependencies

```powershell
py -3.12 -m venv Course-Project/code/GrantOffice/.venv
.\Course-Project\code\GrantOffice\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\Course-Project\code\GrantOffice\.venv\Scripts\python.exe -m pip check
```

Use the existing environment if present; do not recreate it unnecessarily. The root entry point includes both original requirement files and constrains them with the supplied application lock. Ollama and Qwen are separate installations. For live local generation, start Ollama and run `ollama pull qwen2.5:3b`, then configure/test the model in Office settings. Set `$env:OPENALEX_API_KEY` privately in the server terminal for public search; never commit it.

### Start the application

```powershell
Set-Location Course-Project/code/GrantOffice
.\start.bat
```

The launcher resolves its own directory, initializes missing users and opens http://127.0.0.1:8000. Read initial passwords locally from `runtime/FIRST_LOGIN.txt`; existing accounts remain intact. Stop with Ctrl+C. To start without opening a browser, from the same directory:

```powershell
.\.venv\Scripts\python.exe scripts/setup_users.py
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 1
```

See [Windows setup](Course-Project/docs/WINDOWS_SETUP.md), [usage](Course-Project/docs/USAGE_GUIDE.md), [local models](Course-Project/docs/OLLAMA.md) and [account-preserving upgrades](Course-Project/docs/UPGRADE.md).

### Execute assignments

From the repository root, replace the number for the selected lab:

```powershell
$env:PYTHONIOENCODING = 'utf-8'
.\Course-Project\code\GrantOffice\.venv\Scripts\python.exe Assignments/lab01.py
.\Course-Project\code\GrantOffice\.venv\Scripts\python.exe Assignments/lab09.py
```

Lab 1 and Lab 6 request interactive input. Labs 5–7 and 14 use the standalone connector. Stop GrantOffice first because both servers use port 8000. Start the connector in another terminal from the repository root:

```powershell
.\Course-Project\code\GrantOffice\.venv\Scripts\python.exe Course-Project/code/Lab_Support/connector/grant_connector.py
```

Then run the selected assignment in the first terminal. Connector-backed literature exercises may contact external scholarly services. Lab 8 uses local parallel-work fixtures and needs no connector. Labs 9–13 execute local acceptance scenarios without live services. Generated standalone runtime/dashboard files stay in ignored `Lab_Support/outputs/`.

### Run the supplied test suites

From the repository root:

```powershell
$env:PYTHONPATH = (Resolve-Path Course-Project/code/Lab_Support).Path
.\Course-Project\code\GrantOffice\.venv\Scripts\python.exe -m pytest Course-Project/code/Lab_Support/tests -q --junitxml=Course-Project/docs/evidence/windows-labs.xml
Remove-Item Env:PYTHONPATH
Set-Location Course-Project/code/GrantOffice
.\.venv\Scripts\python.exe scripts/verify_labs.py
```

The application script invokes its supplied suite and maps results into `Course-Project/docs/evidence/acceptance-results.xml` and `lab_verification.json`, used by the authenticated Worklet verification view. Application `tests/conftest.py` selects fresh temporary storage and template generation; standalone governance/dashboard tests use temporary directories. Keep the suites separate because their import contracts differ. `test.bat` also runs the application suite from its own directory.

## Demonstration guide

1. Start GrantOffice and sign in using an existing local account or the generated first-login file.
2. Show the institutional catalog and its source provenance. Use the separate practice workspace for a synthetic demonstration.
3. Enter a research request, consent and an editable plan; inspect the two parallel workflow stages.
4. Show evidence IDs, budget calculations, validation failures and bounded repair. Explain any template/model or external-source status.
5. Show the human review gate and role restriction. A real institutional case requires genuine call rules, PI confirmation and office eligibility evidence before authorization.
6. For an authorized fixture case, demonstrate versioned internal release and export; explain that agency submission is manual. Show the two separate automated test reports and remaining live checks.

## Submission checklist

- [x] Required root layout, fourteen assignments, original source/data/report files and Git history retained.
- [x] Updated imports, relative links, documentation locations and Windows launcher references.
- [x] Separate lab/application suites run with disposable test state; current evidence recorded.
- [x] Local account files, databases, secrets, environments, caches and model downloads excluded by ignore rules.
- [ ] Confirm team division and availability of the original evaluation sheet.
- [ ] Confirm with the instructor how fourteen build-book labs correspond to the notice mentioning twelve assignments.
- [ ] **College data sharing:** obtain/confirm the institution's permitted audience and repository visibility. Existing college records are retained under application `data/`; their inclusion does not establish permission for public redistribution. No additional sharing scope is inferred.
- [ ] Supply separate worklet canvas/lab review sheet if required; neither is present. The supplied build book is Markdown; its original DOCX and the three referenced image/media assets (`image1.png`, `image2.png`, `media`) are unavailable.
- [ ] Review the preserved final report PDF: it describes the historical Linux baseline and contains former paths. The editable source has current path annotations; current results are authoritative in Verification.md. A newly rendered PDF was not produced.
- [ ] Verify live Ollama quality, live scholarly services, native browser behavior and a genuine current call with named institutional reviewers.
- [ ] Confirm the final organization/approval-form destination and any required repository transfer. This correction targets the existing `origin/main` repository only.
