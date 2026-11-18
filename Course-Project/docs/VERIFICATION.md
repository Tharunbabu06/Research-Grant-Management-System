# Fresh verification record

Executed 18 November 2026 on Windows. Main runtime: Node 24.11.1, npm 11.6.2, Git 2.45.1.windows.1. Standard-library lab runner: Python 3.10.11. Clean independent environment: Python 3.12.10 installed from the preserved requirements-lock.txt, with pytest 9.1.1, LangGraph 1.2.18 and Pydantic 2.14.1.

## Fresh automated checks

| Command and working directory | Actual result | Scope |
| --- | --- | --- |
| `npm test` in backend | 50 passed; 0 failed, skipped or cancelled | Main Node API/engine; includes 15 correctness regressions |
| `npm run lint -- --max-warnings 0` in frontend | 0 errors; 0 warnings | Existing ESLint rules unchanged |
| `npm run build` in frontend | Passed, 43 transformed modules | Production compilation, not a browser test |
| `python Course-Project/tools/verify_labs.py` from root | 140/140 assertions across 14 labs | Script traces checked by notebook acceptance cells |
| `python -m pytest -q` in langgraph_edition, clean Python 3.12 | 66 passed, no warnings | Independent Python app; temporary state |
| `python -m pytest -q` in Course-Project/code/Lab_Support, clean Python 3.12 | 70 passed, no warnings | Earlier distinct lab-support implementation |
| `python Course-Project/tools/check_docs.py` from root | Passed after documentation completion | Current relative file links; historical internal links/URL fetches excluded |
| `python Course-Project/tools/check_repository.py` after explicit staging | Recorded in repository audit | Index hygiene and safe secret scan, no values printed |

Counts are separate, not summed. Repeated runs and the Python edition's mapping of existing tests are not additional unique cases. All original test assertions and lint rules remain enabled.

## Installation and failures resolved

- A fresh temporary Python 3.12 virtual environment installed the exact preserved lock successfully. The same environment ran both Python suites above. No global packages or source requirements were changed.
- An initial dependency dry-run under Python 3.10 failed on packages requiring a supported newer interpreter. It does not establish a broken Python 3.12 lock. Use the documented Python 3.12 environment.
- The older installed Python 3.10 environment initially produced one UTF-8 decoding failure: 65 passed/1 failed. Enabling PYTHONUTF8=1 yielded 66 passed with one anyio-plugin PytestRemovedIn10Warning. Its earlier lab-support run passed 70 with the same warning. Clean locked Python 3.12 runs above have no warnings. These reruns are not added to totals.
- The supplied lab runner failed on Windows because its TemporaryDirectory exited before the process left that directory. It now restores cwd before cleanup. Assertions and notebook outputs were not weakened or regenerated; all 140 assertions pass.
- Both Node lockfiles passed `npm ci --dry-run --ignore-scripts --no-audit --no-fund`; installed dependencies ran the tests/build. This is a lock consistency check, not a claim of fresh Node dependency installation in a clean machine.

## Browser and startup: fresh versus prior

Fresh Microsoft Edge check opened the current built public login page at the running local backend, captured only [public branding](screenshots/current/login-brand-2026-11-18.png), and recorded zero page runtime errors. This is not a fresh authenticated full-route test. Main /api/health currently reports healthy local JSON and MongoDB not_configured.

Prior same-day correctness verification (before this documentation update) exercised 11 main routes and nine proposal tabs at 1440/820/390px, authenticated downloads, profile counts, working-cost correction, approval invalidation, Restore refresh and isolated HTTP restart. These are retained prior results, not newly repeated here. Fresh Node regressions separately exercise those core contracts and process restart without touching operational state. The original working application paths remain intact.

## Mocked, live, blocked and unexecuted checks

| Category | Actual scope |
| --- | --- |
| Mocked/controlled | Provider classifications/retries/Crossref independence; model output/failure contracts; Windows transient/persistent rename failure; Mongo connected-store cases in existing tests |
| Fresh local live | Built-app public login/health, Edge branding capture, full offline suites, clean Python lock installation and document generation/inspection |
| Prior external live | OpenAlex diagnostic 401 and public-topic probe 503 during earlier 18 November correctness work; no success/key validity inferred |
| Not executed in this update | External provider calls, live MongoDB, Ollama/Groq quality, full authenticated browser route rerun, actual funding submission and institutional acceptance |
| Native Word rendering | Earlier COM attempt blocked with 0x80070520; Word-native layout for the final course report is not claimed verified |

No fresh persistent-state warning appeared in the passing Node run. Lock ownership behind the old EPERM warning remains unknown; persistent failure handling is covered deterministically. Anyio's old-environment warning is reported above rather than suppressed.

## Final report and export checks

The editable [report source](../Final_Report/GrantOffice_Technical_Report.md) is approximately 3500 words. `node Course-Project/tools/render_report.js` creates genuine DOCX OOXML and PDF from that source, separately from application saved-proposal exports. Backend docx/PDFKit dependencies and an installed Unicode TTF are required; no model, Office or Python is required at generation runtime.

DOCX ZIP integrity, all XML parsing, budget/governance tables and repeated-header metadata were checked. The report PDF was opened with temporary PyMuPDF, text/source/team/fixture values extracted, all pages rendered into a contact sheet and inspected for clipping/tables/page breaks. No text bounding box lies outside a page. Document page count and final review outcome are recorded in the repository audit. Native Word rendering remains blocked/unverified as stated above. The temporary PDF inspection tool is not an application dependency.

The fresh 50-test Node suite also verifies real current/historical proposal DOCX/PDF headers, authenticated access and snapshot immutability. Earlier rendered saved-proposal exports included a 90-row, seven-page budget test; that rendering was not rerun as part of this documentation update.

## CI

The first remote run passed dependency installation but failed one mocked model-adapter test (49 passed, 1 failed): the CI-only GRANT_LLM=template setting disabled the adapter despite the test enabling AURA_LLM around its fetch mock. The corrected workflow uses GRANT_LLM=ollama and defaults AURA_LLM=off. The exact corrected environment passes all 50 tests locally without a live model. Assertions were preserved. Node 24-compatible v6 actions and a pinned Ubuntu 24.04 runner replace deprecated action runtimes and the moving image label. See the repository audit for the initial failed run; the final delivery records the subsequent remote result.

[Offline GitHub Actions](../../.github/workflows/verify.yml) installs locked dependencies on Node 24/Python 3.12 and runs the corresponding suites, lab traces and current documentation/hygiene checks. No live API credentials, MongoDB Atlas or Ollama are required. Locally validated commands are documented above. Remote CI success is not claimed until its run is observed; Ubuntu execution itself is not a local Windows result.

## Academic-layout relocation verification - 19 November 2026

The real backend/frontend now live under Course-Project, alongside the independent Python edition, tools and launcher scripts. Updated CI, links, tooling roots and startup instructions use the new locations. Root Assignments and its notebooks are unchanged.

Fresh relocated checks: backend 50 passed/0 failed/skipped; frontend lint 0 errors/warnings; production build passed; all fourteen supplied scripts passed 140/140 trace assertions. Private state and .env were moved intact, verified by before/after hashes without displaying their contents. The existing backend and Vite were stopped only to release Windows directory locks, then restarted on their original ports. Sign-in sessions expire on restart. Independent Python and browser/batch checks are recorded in the relocation audit. Earlier dated results remain historical rather than being added to these totals.
