# Research Grant Management System

Team 13 | Agentic AI (26ECAC401)  
Computer Science & Engineering (AI), KLE Technological University, Hubballi

## Team members

| Name | USN | Division |
| --- | --- | --- |
| Soujanya Tikare | 01FE23BCI064 | To confirm |
| K. Tharun Babu | 01FE23BCI078 | To confirm |
| NT Basavaraj | 01FE23BCI031 | To confirm |
| K Rohith | 01FE23BCI113 | To confirm |

Confirm division before submission. Names and USNs follow the supplied team evaluation sheet.

## Project overview

Faculty need a common workflow to find funding opportunities, review literature, draft proposals, prepare budgets and resolve compliance requirements. The Dean R&D office needs visibility into status, deadlines and review decisions. The project creates an evidence-grounded proposal and compliance package through a coordinator and specialist agents, with validation and human authorization before release.

[Problem statement](Course_Project/Documentation/Problem_Statement.md) | [Supplied Chapter 13 build book](Course_Project/Documentation/Build_Book.md) | [Final report PDF](Course_Project/Documentation/Final_Report.pdf) | [Editable report](Course_Project/Documentation/Final_Report.md) | [Verification](Course_Project/Documentation/Verification.md)

## Assignments overview

The team identifies the build-book labs as its assignment work. All fourteen labs are retained here. Confirm the numbering with the instructor because the general notice mentions twelve assignments.

| Lab | Capability | File |
| --- | --- | --- |
| 1 | Agent vs Chatbot | [lab01.py](Assignments/lab01.py) |
| 2 | Tool-Using Agent | [lab02.py](Assignments/lab02.py) |
| 3 | Reusable Skills | [lab03.py](Assignments/lab03.py) |
| 4 | Memory and Retrieval | [lab04.py](Assignments/lab04.py) |
| 5 | MCP-Style Connector | [lab05.py](Assignments/lab05.py) |
| 6 | Governed Runtime | [lab06.py](Assignments/lab06.py) |
| 7 | Agentic Node Graph | [lab07.py](Assignments/lab07.py) |
| 8 | Parallel Swarm | [lab08.py](Assignments/lab08.py) |
| 9 | Evidence Grounding | [lab09.py](Assignments/lab09.py) |
| 10 | Targeted Repair | [lab10.py](Assignments/lab10.py) |
| 11 | Acceptance Factory | [lab11.py](Assignments/lab11.py) |
| 12 | Safety and Governance | [lab12.py](Assignments/lab12.py) |
| 13 | Domain Specialists | [lab13.py](Assignments/lab13.py) |
| 14 | Capstone | [lab14.py](Assignments/lab14.py) |

[Assignments](Assignments/) contains only fourteen Python files. Imported implementations, fixtures and acceptance tests are under [Lab_Support](Course_Project/Lab_Support/). Labs 1-8 and 14 preserve the supplied entry code with an import-path preamble. Labs 9-13 run their supplied acceptance scenarios through newly added entry files, since their implementations arrived as modules and tests.

## Approach and implementation

[GrantOffice](Course_Project/GrantOffice/) is the integrated application. It uses FastAPI for authenticated endpoints, LangGraph for state and routing, Qwen through local Ollama for structured drafting, OpenAlex for paper discovery, Crossref for DOI metadata and the college catalog for institutional research context. SQLite persists runs, review records, checkpoints and releases. HTML, CSS and JavaScript provide the dashboard.

Funding discovery and literature review run in parallel. Drafting follows their join. Budget and compliance run in parallel, followed by validation, assembly, human review and authorized internal release. Failed checks block or trigger bounded targeted repair. PI confirmation and office eligibility review bind to the draft fingerprint. Revision requires fresh reviews. The office exports the authorized package for manual agency submission.

The standalone assignment implementation and GrantOffice have separate source trees and test suites. Lab exercises progressively demonstrate the book's capabilities. The web application integrates corresponding capabilities through its own production-facing contracts.

## Results

The supplied catalog contains 527 reconciled publications, 19 historical awards, two applications and 60 searchable legacy records. On 15 November 2026, 70 standalone lab tests and 53 web-application tests passed in Python 3.12. These are separate suites and use controlled inputs. Live Ollama quality, live external requests, browser behavior and acceptance on a genuine call require checks on the college deployment.

## Run GrantOffice on Windows

Open a terminal in Course_Project/GrantOffice and run:

```powershell
.\start.bat
```

The launcher installs dependencies and opens http://127.0.0.1:8000. Local initial passwords are generated under runtime/FIRST_LOGIN.txt. Configure the installed Qwen model in Office settings. Set OPENALEX_API_KEY in the server environment for public literature search. [Windows instructions](Course_Project/GrantOffice/docs/WINDOWS_SETUP.md).

## Run the assignments

From the repository root:

```powershell
py -3.12 -m venv .lab-venv
.\.lab-venv\Scripts\python.exe -m pip install -r Course_Project/Lab_Support/requirements.txt
.\.lab-venv\Scripts\python.exe Assignments/lab01.py
.\.lab-venv\Scripts\python.exe Assignments/lab09.py
```

Lab 1 and Lab 6 request interactive input. For Labs 5-8 and 14, stop GrantOffice and start the lab connector in a separate terminal:

```powershell
cd Course_Project/Lab_Support
..\..\.lab-venv\Scripts\python.exe connector/grant_connector.py
```

The lab connector and GrantOffice both use port 8000. Run the selected assignment in another terminal at the repository root. Connector-backed literature exercises can access external scholarly sources. Labs 9-13 run local acceptance scenarios without live services.

Run all supplied lab tests:

```powershell
.\.lab-venv\Scripts\python.exe -m pytest Course_Project/Lab_Support/tests -q
```

Run the web suite from GrantOffice using its installed environment:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

## Repository submission

Use one repository named Research-Grant-Management-System. Confirm the institution's permission and repository visibility before publishing the college source data. The ignore file excludes credentials, runtime databases, virtual environments, generated outputs and caches. Keep the supplied fixtures identifiable as practice data.

Fill the team divisions, review the report, verify links, push the repository and transfer it to the instructor's designated organization. Submit the resulting organization repository URL in the course approval form.
