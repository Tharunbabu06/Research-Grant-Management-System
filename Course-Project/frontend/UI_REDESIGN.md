# GrantOffice frontend redesign

Implemented on 18 November 2026. Presentation changes only; no commit or push.

## Visual changes

- Warm off-white workspace, white panels, navy typography and restrained teal actions; system sans-serif fonts, modest rounding, subtle borders and no gradients or added assets.
- Light grouped navigation with consistent icons, an active-page rail and accessible page identification. Compact account, role, practice-workflow and sign-out controls remain available at every screen size.
- Compact Faculty and Dean headings preserve their original contextual text, actions and metrics. Metric grids use joined summary strips.
- Historical register and college catalog have separate visual treatments, source references, totals and overlap-review explanations. Project search, filters and result counts share one toolbar.
- Consistent tables, aligned monetary columns, restrained status badges, evidence records, agent panels, audit events and proposal tabs. Wide tables and workflow stages scroll inside their own containers.
- Sign-in has credentials on the left and the existing searchable account directory on the right; mobile stacks both panels.
- Proposal intake groups the existing fields into research brief, funding/budget and study/ethics sections. Help text, validation and consent remain present. Shared fields link labels and hints to native controls.
- Shared dialogs use the same borders, spacing and accessible names. Page animation was removed to prevent a stacking context from placing the top bar above dialogs.

## Preserved route and action inventory

| Existing destination | Existing controls and actions retained |
| --- | --- |
| Login | Credentials, practice-directory search and department chips, account selection, schema-inspector action, original source and authentication information |
| `#/dashboard` | Faculty and Dean role views, portfolio actions, funding calls, feedback, budget and sign-off controls |
| `#/projects` | Year/department/faculty filters, My Grants, query/reset, separate register/catalog counts, sources, budget editor and modal |
| `#/people` | Identity search/review inclusion, profile dialog, linked grants, publications and evidence |
| `#/runs` | Status filters, counts, query, proposal navigation and New proposal |
| `#/new` | Examples, every field and constraint, saved researcher selection, funding choices, budget lines, consent, failure injection, brief/plan steps, prepare/launch handlers |
| `#/calls` | Funding-type filter, query, verified/closed/unverified states and call dialogs |
| `#/research` | Archive/public mode, field selection, query, source metadata, abstracts, DOI/provenance disclosure and pagination |
| `#/agents` | All agent roles, stages, tools, inputs, outputs, activity and human-authority guardrails |
| `#/governance` | Approval queue, permission indicators, releases and rollback actions |
| `#/audit` | Query, level, agent, event limit and expandable evidence |
| `#/platform` | Connector, Skills, Models & data, Runtime & guardrails tabs, technical metadata, tool/model controls and dialogs |
| `#/runs/:id` | Overview, Discovery, Literature, Draft, Budget, Compliance, Evidence, Package and Audit tabs; workflow stages, downloads, revision, review, resume and rollback handlers |

No routes, navigation destinations, APIs, authentication implementation, calculations, data-fetching effects, state transitions, permissions, field constraints or event-handler expressions were changed.

## Files changed

All implementation files are in `frontend/src/`:

- `index.css`: design tokens and shared/responsive presentation for every screen.
- `App.jsx`: shell, account layout, navigation accessibility and startup presentation.
- `components/ui.jsx`: shared summary strips, table scrolling, dialog semantics, loading announcements and field-label/hint associations.
- `components/BudgetEditor.jsx`: scroll container, monetary alignment, input names and responsive action row.
- `components/CollegeData.jsx`: clearly separated archive summaries and monetary alignment.
- `pages/Login.jsx`: sign-in/directory layout and accessible native account buttons.
- `pages/FacultyDashboard.jsx`, `pages/DeanDashboard.jsx`: compact headings, existing actions and summary strips.
- `pages/aura-projects.jsx`, `pages/aura-runs.jsx`, `pages/aura-calls.jsx`, `pages/aura-audit.jsx`: coherent filters/results presentation.
- `pages/aura-intake.jsx`: visual form sections.
- `pages/aura-agents.jsx`: human-authority panel presentation.
- `pages/aura-governance.jsx`, `pages/aura-platform.jsx`, `pages/runTabsB.jsx`: shared metric-strip classes.
- `pages/aura-rundetail.jsx`: keyboard-focusable workflow scroll area and selected-decision accent.

`pages/Research.jsx`, `pages/aura-people.jsx` and other unchanged components receive the shared design through `index.css` and `components/ui.jsx`.

This report is `frontend/UI_REDESIGN.md`.

## Checks actually executed

- `npm.cmd run build` in `frontend`: **passed**, including the final source changes.
- `npm.cmd test` in `backend`: **35 passed, 0 failed**. Existing tests and assertions were unchanged.
- `npm.cmd run lint` in `frontend`: **fails on pre-existing findings**. Final ESLint API comparison reports **70 errors and 3 warnings**, versus 71 errors and 3 warnings in the original snapshot. No new diagnostics; use of React in the field helper removes one unused-import error. Existing hooks, unused-code and refresh-export findings were not changed.
- Headless Microsoft Edge with Playwright: all 11 main routes at **1440, 820 and 390px**; additional login/main-route checks at **320px**. No page-level horizontal overflow or browser runtime errors in these checks.
- Browser actions: real sign-in/sign-out with Dean and Faculty views; project search/reset; budget dialog add/edit/remove/cancel; faculty search/profile dialog; proposal example, fields, consent and failure-control disclosure; archive search, real empty result, next/previous pagination; all four platform tabs. Credential keyboard focus advances from identifier to password to sign-in.
- All **nine proposal-detail tabs** and approval dialogs at 1440, 820 and 390px were rendered using existing pipeline-test output intercepted **only in browser GET responses**. No test proposal was inserted into the running application's store. Checked screenshots and scroll behavior; no runtime errors or page overflow.
- Intercepted archive/bootstrap failures retained the original error text and retry behavior. Archive failure did not fabricate a zero-result count. A held bootstrap request displayed the original loading label and connector context.
- Source AST comparison with the pre-edit snapshot preserved all original event-handler expressions, control values, constraints, links and JSX text. Code outside JSX is unchanged, except the shared Field/Modal presentation helpers' accessible-ID handling. Those helpers were reviewed separately.
- No Git repository exists in the provided workspace. A temporary source snapshot, byte hashes and a unified diff were used for review instead. Backend source, frontend API/format helpers, package manifests/locks, tests, catalog inputs, schemas and environment/configuration files remain byte-identical to the snapshot.

Normal verification output includes `frontend/dist/`, Vite caches, regenerated `backend/.test-data/state.json` and `audit.jsonl`, and audit entries appended by the running backend during authorized login/browser checks. These are runtime/test artifacts; no backend source or application records were edited for the redesign.

## Remaining issues and verification limits

- No remaining redesign-specific visual defect was found in the inspected layouts. Wide tables, tabs and workflow stages intentionally scroll within their own containers.
- The existing login **Mongoose Schema** action does not display its inspector: the original caller omits the shared Modal's `open` prop. Confirmed in the browser and left unchanged to preserve the requested behavior/props. Inspector content remains in the source.
- Existing lint findings remain as described above.
- The frontend has no existing test script or frontend test suite. Browser verification and the production build covered the frontend.
- Live proposal launch, saved-budget writes, approval, rejection and rollback were not submitted during browser verification. Existing backend tests exercise pipeline, permissions, versioning, rollback and persistence. Public-provider/LLM calls were not run as part of the visual checks.
