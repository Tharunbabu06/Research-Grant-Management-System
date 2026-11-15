# Grant Office — College Edition 2.0

Research grant management for KLE Technological University: institutional research evidence, proposal development, governed LangGraph agents, local LLM assistance and named-human approval.

## Start or upgrade

**New installation:** extract the full ZIP, install Python 3.12, and double-click **start.bat**. Initial account passwords are created in `runtime/FIRST_LOGIN.txt`. The browser opens at http://127.0.0.1:8000 after the server is ready.

**Already using version 1:** stop the old server and extract this release into a separate folder. Before the first launch, run **import_previous_data.bat** and select the old GrantOffice folder. It copies your accounts, proposals, evidence and checkpoints while keeping the old folder unchanged. Do not overwrite or delete your old runtime. See `docs/UPGRADE.md`.

**Faculty sign-in problem:** stop the server and run **reset_faculty_password.bat**. Enter a new password twice, then run start.bat and sign in as `faculty`. It changes only the password and sessions; your proposals remain intact. Office/Dean can also reset accounts in **Office settings → Recover an account**. The old password printed in FIRST_LOGIN.txt is no longer valid after a reset.

## Changes in this release

- Professional institution-facing names and branding, with **Institutional** as the default workspace.
- Case-insensitive usernames with surrounding whitespace removed; show/hide password and clear recovery guidance.
- Faculty/local password recovery and authenticated office account resets, preserving existing records.
- Repeat setup preserves existing passwords and saved initial credentials. Old account display-name prefixes are migrated without changing account IDs.
- Local Ollama integration in **both proposal drafting and the research assistant**, with retrieved source context, structured response validation, bounded repair and evidence-ID checking.
- A visible model connection/configuration panel and a live **Test model response** action.
- A fourteen-lab verification screen, test report and `verify_14_labs.bat`.
- Existing approval, audit, checkpoint recovery, source isolation, versioning and rollback behavior retained and regression-tested.

## Enable the LLM

1. Install Ollama from https://ollama.com/download/windows and start it.
2. Run **setup_llm.bat** to download `qwen2.5:3b` locally. This requires internet and several GB of disk space once; model weights are not inside this ZIP.
3. Open **Office settings**. Choose the model and **Use local LLM when available**.
4. Click **Check connection**, then **Test model response**.
5. Create a proposal or ask the Research assistant a question.

The application calls only the fixed local Ollama endpoint. Proxy environment variables are deliberately ignored for these local requests. No cloud LLM is configured. If a model is unavailable or returns invalid output, the interface explicitly reports template/retrieval mode; it never pretends that a model ran.

The implementation is included and its success, retry, timeout and unsupported-citation paths are tested with controlled HTTP fixtures. Live inference using your installed model must be verified on your computer. Models can still make factual errors even when citation IDs are valid; faculty review remains mandatory.

## Institutional and practice data

The ordinary workflow uses the **Institutional** workspace. Funding calls, policy rules, salary norms and eligibility evidence must come from actual office-approved sources. The uploaded files contain institutional history, not a verified live funding-call database.

For testing the full approval cycle, **New proposal → Load sample proposal** creates a clearly separated **Practice — synthetic data only** case. Sample sources and exported practice packages remain identified as **SAMPLE DATA — NOT FOR SUBMISSION**. Removing branding does not change invented records into genuine college policies or agency announcements.

The original uploads remain unchanged, including their source filenames and audit warnings. Historical saved documents may retain their original wording; signed package contents are never silently rewritten merely to change presentation.

## Included data and capabilities

- 527 reconciled publication records from the master workbooks and supplemental CSVs, with source locations.
- 19 detailed historical awards and two applications, with distinct financial semantics.
- 60 searchable legacy grant entries with CSV provenance, excluded from aggregate funding totals.
- Dashboard, funding registry, research archive, evidence room and grounded assistant.
- Real LangGraph parallel stages, validated typed planning/package skills, bounded repair, persistent checkpoints, human interrupt and versioned internal releases.
- Budget ceilings, consent, required evidence, deadline/timezone, source freshness and ethics checks.
- Role and department scope, hashed passwords, expiring sessions, audit trail, evidence attachments and internal rollback.
- Downloadable proposal HTML/Markdown, budget CSV, compliance/evidence/literature JSON and audit package.

## How to verify

Run **verify_14_labs.bat**, then open **Worklet verification** in the sidebar. The report maps executable checks to all fourteen labs and shows which claims still depend on external institutional acceptance.

At delivery, **50 automated tests passed**. The suite uses isolated temporary databases and does not erase office records. Browser verification covers faculty sign-in, sample proposal creation, HoD approval, package download, evidence/policy entry, office password recovery, model controls, the fourteen-lab view and a phone-width layout. See `docs/TEST_REPORT.md`.

A green software check is not a certification that actual funder requirements, research novelty, live-model quality or campus production deployment have been approved. The worklet's real-case capstone needs the college's actual official documents and named review.

## Quick practice workflow

Sign in as faculty → New proposal → Load sample proposal → read/check consent → Preview editable plan → Lock plan & run agents → inspect Budget & checks → sign out → sign in as hod → Review & versions → approve with a review note → download the internally released practice package.

To exercise the institutional workflow, first register genuine policy and call records using the office account, then include the required eligibility, CV, narrative-review and ethics evidence.

## Main files

| Path | Purpose |
|---|---|
| app/ | API, authentication, local LLM gateway, connector, schemas and LangGraph |
| static/ | Responsive interface; no npm build or third-party CDN needed |
| data/originals/ | Your exact uploaded source files |
| data/catalog.json | Source-traceable normalized records |
| data/mock/ | Original synthetic fixtures, separate from official registry |
| docs/ | Upgrade, setup, LLM, usage, data audit, architecture and lab reports |
| tests/ | Isolated acceptance and regression suite |
| notebooks/ | Lab 1 clarify/plan/revise example |
| runtime/ | Created locally; accounts, evidence and workflow history; excluded from ZIP |

Default launch uses a single local process at 127.0.0.1. Wider deployment requires institutional HTTPS/identity, operations and access-control review. No email or funding-agency submission is performed automatically.
