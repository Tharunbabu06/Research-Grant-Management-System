# Repository update audit

Prepared 18 November 2026 against the actual working GrantOffice project. Current verification: [course verification](VERIFICATION.md); [documentation index](README.md); [final report](../Final_Report/README.md).

## Initial repository and source audit

The open workspace had no Git metadata. A separate existing checkout at Research_Grant_Management_System_Submission was clean on main, origin https://github.com/Tharunbabu06/Research-Grant-Management-System.git. Its HEAD and the remote HEAD both resolved to dcc714166cfdccc3813770f80c391943aabcc7f5. Only its Git history/metadata was copied into the current application root. No nested repository or duplicate runnable application was initialized; the original checkout was left untouched. A command-scoped safe.directory override accommodates the sandbox account's different Windows ownership without global Git configuration changes.

Reference audit found Reasearch-grant-management-system-main (1).zip and its already-extracted course originals. The exact requested (1)(1).zip spelling was not present. The (1).zip provided reference structure only. Four course-original documents plus the original problem-statement DOCX match the ZIP byte for byte. Current application source, records and lockfiles are authoritative.

## Intended publication changes

- Root README, Assignments and Course-Project are direct GitHub-root entries. Existing Course-Project/backend/frontend paths remain intact; the independent Python edition is langgraph_edition.
- Updated professional README, current architecture/setup/data/identity/demo/scope/verification/limitations docs and index; added a substantive editable report and real DOCX/PDF.
- Current branding screenshot is genuine and cropped to exclude personal/private content. Older screenshots/reports are explicitly historical.
- Preserved all supplied fourteen scripts/notebooks and their original outputs. Preserved the earlier repository's fourteen independent programs plus Lab_Support code/tests. Retained older reports/evidence under labeled history.
- Existing earlier app location Course-Project/code/GrantOffice is represented by current authoritative langgraph_edition, rather than publishing another duplicate application. Git history retains original content.
- Added offline CI, current relative-link checker, staged-secret/hygiene checker and report renderer. Fixed only the lab runner's Windows cwd-before-cleanup order and added lint/link commands to verify.bat.
- All current working correctness/UI implementation is included as intended application source; no historical operational state/accounts or private proposal content is published. Detailed local operational audits remain locally present and ignored; the public correctness summary uses fixtures.

## Verification and remaining details

Fresh: Node 50 passed; lint 0 errors/0 warnings; build passed; 140/140 lab trace assertions; clean Python 3.12 application 66 passed and earlier support 70 passed without warnings. Node dependency dry-runs passed. Fresh Edge public-login capture had zero page errors. Full authenticated browser/provider checks remain prior/unexecuted as distinguished in [verification](VERIFICATION.md).

Team 13 and names/USNs follow the supplied transcription. Available originals are blank; independent confirmation and division remain pending. Course reviewer marks/signatures are not fabricated. The original template campus text is preserved unchanged.

Current local MongoDB is absent; OpenAlex's prior 401/503 outcome is unresolved. JSON single-writer and memory-only fallback account/session limits remain. Native Word COM rendering is blocked; binary structural/PDF rendering checks are separate. No license, scientific result, performance improvement or production deployment is invented.

## Final delivery record

Target: https://github.com/Tharunbabu06/Research-Grant-Management-System ; branch main. Commit/push results are recorded after the final staged review. No force push, destructive checkout, ownership transfer or approval-form submission is authorized or used.

Final document checks: genuine DOCX ZIP/XML passed with seven tables; PDF rendered/inspected without clipped text or broken tables. Relative-link check passed for 19 maintained documents and 287 file links. Staged/tracked secret/hygiene scan inspected 412 files with zero findings. Original application inputs, approved records, lab implementations and course originals remained unchanged. Six inherited Git whitespace findings were normalized in four source files without changing behavior or styles.

Final rendered PDF: 10 pages; all pages inspected.

## Verified publication receipt

Source/documentation commit: **b3e67ebd681c85ec0ad8e2492cf98bd7bca013c5** (`Prepare current GrantOffice course repository, final report and offline verification`). Published successfully to **origin/main** at the authorized [GitHub repository](https://github.com/Tharunbabu06/Research-Grant-Management-System). `git ls-remote origin refs/heads/main` matched that exact commit after push.

The first transfer failed with HTTP 408. A non-force retry using command-scoped HTTP/1.1 and a larger request buffer succeeded; no remote URL, history or ownership was rewritten. This small publication receipt is a separate documentation follow-up commit.

The [initial Actions run](https://github.com/Tharunbabu06/Research-Grant-Management-System/actions/runs/44367311959) subsequently failed: 49 backend tests passed and one failed because the workflow selected template-only mode while an existing mocked local-model test temporarily enabled model calls. No test assertion was weakened. The workflow now uses GRANT_LLM=ollama with AURA_LLM=off by default; the model test enables requests only around its mock. The exact corrected CI environment passed all 50 backend tests locally, with no live model required.

Action definitions were checked against the official v6 action.yml files: checkout, setup-node and setup-python use Node 24. These versions replace the deprecated Node 20 action runtime versions. Ubuntu is pinned to 24.04 to avoid the moving ubuntu-latest image migration warning. Remote rerun results and final commit are reported in the delivery message; local and remote evidence remain separate.

## README presentation and team correction

Simplified the root README to match the requested numbered course-project structure with compact tables and direct links. The team explicitly corrected the USNs: NT Basavaraj is 01FE23BCI113 and K. Rohith is 01FE23BCI031; Soujanya Tikare and K. Tharun Babu remain unchanged. Updated the editable report and regenerated its DOCX/PDF to keep the current deliverables consistent. Historical originals remain unchanged.

## Requested academic layout - 19 November 2026

Moved the real backend and frontend into Course-Project, matching the requested top-level README.md / requirements.txt / .gitignore / Assignments / Course-Project layout. The independent Python edition, existing launchers and tools also moved inside Course-Project; earlier lab support remains there. GitHub automation and Git attributes remain necessary hidden root entries. No application copy or nested Git repository was created.

Updated current Markdown links, CI working directories/cache paths, verification/tool roots, source-location display metadata and report binaries. Course-issued originals, notebooks, backend/frontend dependency locks and operational records are retained. Detailed local audits moved into ignored docs/local-audits; secrets, node_modules and runtime/test data remain excluded.

The old backend/Vite and prior isolated verification process were stopped to release Windows folder locks, then the main backend and Vite restarted from the new paths. Whole-file hashes confirmed all three existing private state/config files were unchanged. Local checks after relocation: 50 backend tests; frontend lint zero findings; production build; 140/140 lab trace assertions. Further actual browser/Python/batch results and push receipt are reported below.

Relocation completion checks: the separate Python application passed all 66 tests and earlier lab support passed all 70 tests in the clean Python 3.12 environment. The moved Windows verify.bat completed successfully from repository root, including Node tests, frontend lint/build, labs and documentation links; this rerun is not added as a separate test total. Edge loaded both the built app on port 3000 and Vite on port 5173 with HTTP 200, visible branding and zero page runtime errors. Health reported healthy/local_json. All 289 current relative links resolve. The current report binaries were regenerated after path updates and structurally checked.

## Dashboard image and confirmed division - 19 November 2026

Replaced the root README branding strip with a genuine matching faculty-dashboard capture from the running app, since the pasted screenshot was not exposed as a local asset. The screenshot contains only the requested faculty identity/dashboard aggregates, without credentials, tokens or proposal narrative. Added a separate Division column showing B-DIV for all four members and synchronized the current report and team-status documentation. Blank originals remain unchanged.

## Exactly five root entries - 20 November 2026

Added a final Documentation Links table to the README with relative links to Assignments, project documentation and the final report in its folder/formats. Moved root .github and .gitattributes into Course-Project, preserving their contents. The tracked root now consists only of Assignments, Course-Project, .gitignore, README.md and requirements.txt; GitHub's default directories-first/name ordering matches the requested screenshot. Local .git metadata remains necessary and is not a published repository entry.

Automatic GitHub Actions is disabled because GitHub requires workflow definitions at repository-root .github/workflows. The definition is retained under Course-Project/.github/workflows, local verification scripts remain working, and current documentation now states this limitation. Previous successful CI runs are retained as historical results. Application code, operational data and course originals are unchanged.
