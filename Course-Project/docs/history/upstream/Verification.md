# Verification of the reorganized submission

Date: **15 November 2026**. Environment: **Windows, Python 3.13.7**, existing application `.venv` relocated with the application. The system `python` is 3.10.11; the sandbox user's `py` launcher reports no registered interpreter. Checks therefore used the application's explicit `.venv/Scripts/python.exe`. Application startup has no remaining blocker in that environment. Python 3.12 is still the supplied reference version.

## Current observed checks

| Check actually run | Result | Evidence |
| --- | --- | --- |
| Root requirements installation, `pip install --no-index -r requirements.txt`; `pip check` | Success; all required distributions already installed; no broken requirements | [Installation log](evidence/windows-install.txt) |
| Supplied standalone suite, `pytest Course-Project/code/Lab_Support/tests -q` with support on PYTHONPATH | **70 passed**, 0 skipped, 0 failed; 0.79 s | [JUnit](evidence/windows-labs.xml), [console](evidence/windows-labs.txt) |
| Supplied application suite through relocated `scripts/verify_labs.py` | **53 passed**, 0 skipped, 0 failed; 17.93 s; fourteen application capability groups mapped | [JUnit](evidence/acceptance-results.xml), [console](evidence/windows-application.txt), [mapping](evidence/lab_verification.json) |
| Fourteen assignment files, AST parse and independent runpy import processes | **14/14 passed**, without executing their main blocks | [Import record](evidence/windows-assignment-imports.json) |
| Assignment entry execution | Labs **1–4 and 8–13** exited 0. Lab 1 used scripted clarification/consent/no-revision input. Lab 8 passed all four acceptance checks | `evidence/windows-labNN.txt` for each executed entry |
| Actual `scripts/serve.py` startup (browser opening suppressed) | HTTP **200**: `/api/health`, `/`, `/static/app.js`, `/static/style.css` and authenticated `/api/labs` (14 mappings); engine LangGraph | [Startup result](evidence/windows-startup.json), [server log](evidence/windows-startup-server.txt) |
| Local account/runtime preservation during startup check | File hashes unchanged; startup used disposable accounts and database storage | [Startup result](evidence/windows-startup.json) |
| File relocation and source preservation against initial HEAD | Every one of the **168** originally tracked files maps to an existing destination; original college data and report PDF preserved | [Relocation audit](evidence/relocation-audit.json) |
| Markdown links and local rendering | Root and supporting Markdown relative links checked; README rendered locally with markdown-it-py and table support | [Link audit](evidence/relative-links.json), [render result](evidence/readme-render.json) |

The first application run produced **52 passes and 1 failure** because `test_no_demo_branding_in_ui` used Windows default cp1252 decoding for UTF-8 UI source files. The test now specifies UTF-8; the full rerun above passed. The relocated JSON report endpoint also reads UTF-8 explicitly. No lab algorithm was changed. The supplied suite's conftest selects temporary application storage and template generation; standalone governance/dashboard tests use temporary directories. A brief Windows file-release delay on initial startup cleanup was handled by waiting one second after server termination before cleanup.

Installation reused the supplied lock as constraints and both existing dependency files. It proves the installed packages satisfy those inputs; it does **not** prove a fresh online installation or all supported Python versions. Exact Windows installation and execution commands are in the [root README](../../README.md).

## Relocation and Git reconciliation

Initial `git status --short` showed fourteen staged assignment renames and no other tracked edits. The application and documentation still occupied the original inner `Course_Project` folder. There was no second application copy to merge. The lock was IDE `cmd.exe` PID 13832, identified by its exact working directory in the old GrantOffice folder; only that project terminal was stopped. Git ownership was handled with command-scoped `safe.directory`, without changing global configuration.

Whole application and Lab_Support directories were moved, including ignored local environments and office runtime. All fourteen import preambles now target `Course-Project/code/Lab_Support`. Existing module-local fixture/runtime paths remain correct. Centralized application documentation, HTML links, Windows launcher messages, migration guidance, verification script output and the authenticated report reader now resolve the new locations. Empty old directories were removed only after their contents moved. Compose mounts the centralized docs read-only at `/docs` so the container can read the mapping too; Docker execution was not tested. `.gitattributes` prevents Windows line-ending conversion of original binary reports and college artifacts.

The original application hash manifest is preserved as [historical-app-manifest.json](evidence/historical-app-manifest.json). Its hashes describe its original archive paths/content, not the reorganized submission. Historical test evidence is retained separately with its original dates/environment in [evidence provenance](evidence/README.md).

## Limits and missing artifacts

No live Ollama/Qwen inference, live OpenAlex/Crossref requests, fresh browser walkthrough, genuine-call authorization or agency submission was performed. Startup used template mode; test model/network responses are controlled fixtures. Labs 5–7 and 14 were imported but their connector-backed entry demonstrations were not executed; Lab 6's interactive approval prompt was not exercised. Their supplied integration tests remain covered by the passing suite. Tests establish software behavior under those inputs, not scientific accuracy, official eligibility or human acceptance.

The supplied Chapter 13 conversion references `images/image1.png`, `images/image2.png` and `images/media`, but those files and the original DOCX are absent. Its inventory now identifies those missing assets instead of linking to unavailable files. No separate worklet canvas, lab review sheet or original team evaluation sheet is present. Team division and institutional data-sharing scope still need confirmation.

The original final report PDF is unchanged. Its historical Linux results and former path wording are not current Windows evidence; the editable Markdown source points to this verification record and uses current paths. A newly rendered final PDF was not generated. See the [submission checklist](../../README.md#submission-checklist).
