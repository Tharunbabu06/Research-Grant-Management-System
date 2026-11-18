# Frontend lint review and fixes

Reviewed on 18 November 2026. Initial result: **70 errors and 3 warnings**. Final result: **0 errors and 0 warnings**. No lint rules were changed or disabled, no suppressions were added, and no existing tests or assertions were changed. The old dependency suppression in the fetch hook was removed.

## Possible runtime / React behavior findings

Paths are relative to `frontend/src`; locations describe the original snapshot.

| Rule | File / component | Count | Practical risk | Fix |
| --- | --- | ---: | --- | --- |
| `react-hooks/rules-of-hooks` | `pages/runTabsA.jsx` / `DraftTab` | 2 errors | Conditional memo hooks can change hook order when draft data arrives or disappears and crash the mounted tab. | Run both hooks unconditionally with empty-map fallbacks, then preserve the original empty-state return. |
| `react-hooks/rules-of-hooks` | `pages/runTabsB.jsx` / `ComplianceTab` | 1 error | Same hook-order risk when compliance results arrive or disappear. | Compute groups safely before the original empty-state return. |
| `react-hooks/set-state-in-effect` | `components/ui.jsx` / original `useApi` | 1 error | Synchronous loading-state updates in the effect cause an extra render. A pre-existing suppression also concealed its dynamic dependency contract. | Move to `hooks/useApi.js`, memoize its caller's loader, use explicit dependencies, and derive pending/loading from the current request generation. Preserve request cancellation, polling, retained refresh data, errors and reload. |
| `react-hooks/exhaustive-deps` | `pages/FacultyDashboard.jsx` | 2 warnings | Memoized PI counts omit helper dependencies; fragile if helper inputs change. Existing name dependencies already covered current helper input. | Memoize the unchanged helpers against the actor's cleaned name and depend on them explicitly. |
| `react-hooks/exhaustive-deps` | `pages/runTabsB.jsx` / `AuditTab` | 1 warning | A new empty-array fallback invalidates memoization each render while logs are missing; unnecessary work. | Memoize the logs fallback against `run.logs`. |

## Cleanup and development-tool findings

| Rule | File | Count | Practical risk | Fix |
| --- | --- | ---: | --- | --- |
| `react-refresh/only-export-components` | `App.jsx` | 2 errors | Context/hook exports share a component module, making Fast Refresh boundaries unreliable. | Move context and hook to `context/AppContext.js`; update all internal consumers. |
| `react-refresh/only-export-components` | `components/ui.jsx` | 2 errors | Hooks share a component module, making Fast Refresh boundaries unreliable. | Move toast context/hook to `context/ToastContext.js`, and request hook to `hooks/useApi.js`. Keep the provider and all presentation components. |
| `no-empty` | `App.jsx` | 1 error | The intentionally tolerated logout failure has no explanation. | Explain that local sign-out continues when the server endpoint is unavailable. The catch behavior is unchanged. |
| `no-useless-escape` | `pages/Login.jsx` | 4 errors | JavaScript consumes regex escapes in the displayed schema example. This is display content, not authentication validation. | Use `String.raw` for the unchanged schema source text so intended backslashes display literally. |

### All unused-variable findings

Every row below is `no-unused-vars`. These bindings were unused by executable UI behavior. Risks are maintenance noise and misleading/dead bindings, rather than a demonstrated runtime failure. Only unused imports, context/prop bindings, constants and unused pure derived values were removed. Unread state values now use omitted destructuring slots: Dean audit fetching/state updates and login schema metadata fetching/state updates remain intact.

| File | Count | Original unused bindings | Practical risk |
| --- | ---: | --- | --- |
| `App.jsx` | 4 | `React`, `setToken`, `Loading`, `subtitle` | Unused imports/bindings obscure active code; no direct failure identified. |
| `components/BudgetEditor.jsx` | 1 | `React` | Unused imports/bindings obscure active code; no direct failure identified. |
| `components/CollegeData.jsx` | 1 | `React` | Unused imports/bindings obscure active code; no direct failure identified. |
| `components/icons.jsx` | 1 | `React` | Unused imports/bindings obscure active code; no direct failure identified. |
| `pages/DeanDashboard.jsx` | 8 | `React`, `date`, `money`, `statusMeta`, `Progress`, `bootstrap`, `audit`, `published` | Unread audit state and unused derived/imported values; requests and setters retained. |
| `pages/FacultyDashboard.jsx` | 8 | `React`, `date`, `pct`, `statusMeta`, `timeAgo`, `Progress`, `bootstrap`, `publishedCount` | Unused imports/bindings obscure active code; no direct failure identified. |
| `pages/Login.jsx` | 2 | `React`, `schemaMeta` | Unread schema state and unused React import; metadata request and setter retained. |
| `pages/Research.jsx` | 1 | `React` | Unused imports/bindings obscure active code; no direct failure identified. |
| `pages/aura-agents.jsx` | 2 | `Table`, `navigate` | Unused imports/bindings obscure active code; no direct failure identified. |
| `pages/aura-audit.jsx` | 1 | `React` | Unused imports/bindings obscure active code; no direct failure identified. |
| `pages/aura-dashboard.jsx` | 1 | `React` | Unused imports/bindings obscure active code; no direct failure identified. |
| `pages/aura-governance.jsx` | 2 | `React`, `StatusPill` | Unused imports/bindings obscure active code; no direct failure identified. |
| `pages/aura-intake.jsx` | 2 | `React`, `compactMoney` | Unused imports/bindings obscure active code; no direct failure identified. |
| `pages/aura-people.jsx` | 1 | `React` | Unused imports/bindings obscure active code; no direct failure identified. |
| `pages/aura-platform.jsx` | 1 | `React` | Unused imports/bindings obscure active code; no direct failure identified. |
| `pages/aura-projects.jsx` | 2 | `React`, `navigate` | Unused imports/bindings obscure active code; no direct failure identified. |
| `pages/aura-rundetail.jsx` | 7 | `React`, `dateTime`, `duration`, `money`, `pct`, `NODE_ICON`, `status` | Unused imports/bindings obscure active code; no direct failure identified. |
| `pages/aura-runs.jsx` | 6 | `React`, `compactMoney`, `date`, `dateTime`, `statusMeta`, `Tabs` | Unused imports/bindings obscure active code; no direct failure identified. |
| `pages/runTabsA.jsx` | 3 | `React`, `duration`, `Btn` | Unused imports/bindings obscure active code; no direct failure identified. |
| `pages/runTabsB.jsx` | 3 | `duration`, `STATUS_TONE`, `actor` | Unused imports/bindings obscure active code; no direct failure identified. |

Total: **57 unused-variable errors**. Together with 4 Fast Refresh, 4 escape, 3 hook-order, 1 empty-catch and 1 effect-state errors, this accounts for all **70 errors**. The dependency findings account for all **3 warnings**.

## Implementation and preservation

- New modules: `src/context/AppContext.js`, `src/context/ToastContext.js`, `src/hooks/useApi.js`.
- Hook/order/dependency fixes: `src/pages/runTabsA.jsx`, `src/pages/runTabsB.jsx`, `src/pages/FacultyDashboard.jsx`, `src/pages/aura-rundetail.jsx`.
- Existing context consumers now import from the dedicated modules. Remaining source edits remove unused bindings/imports and explain logout fallback behavior.
- The redesigned `src/index.css`, assets, layouts, controls, labels, event handlers, routes, form constraints and API contracts are preserved. All JSX trees across the 23 original JSX files were compared against the pre-edit snapshot and matched; the only normalization allowed was the `String.raw` tag around identical schema template source.
- API/format helpers, ESLint/Vite configuration, dependency manifests/locks, existing tests, backend source, schemas, catalogs and environment files remain byte-identical to the snapshot. No feature or request was removed to satisfy lint.
- No Git repository is present. Review used a temporary source snapshot, hashes and a unified diff.

## Actual verification results

| Check | Actual result |
| --- | --- |
| Frontend `npm.cmd run lint -- --max-warnings 0` | Passed: 0 errors, 0 warnings. |
| Frontend `npm.cmd run build` | Passed. |
| Backend `npm.cmd test` | 35 passed, 0 failed; emitted the persistence warning below. |
| Backend `node --test tests/pipeline.test.js` recheck | 9 passed, 0 failed; reproduced the persistence warning below. |
| Browser hook-transition regression | Draft and Compliance components remained mounted through three empty -> populated -> empty cycles. Their original empty states, populated content and Audit rendering worked without runtime errors. |
| Request-hook behavior comparison | All 12 scenarios passed against both the original hook and the updated hook: initial loading, success, unrelated rerender without fetching, retained data on refresh, error, retry/loading, recovery, resource switch, stale-response rejection, polling, polling stop and unmount cleanup. |
| Toast context | Existing provider/hook delivered its toast after the module split. |
| Full app browser checks | All 11 main routes at 1440, 820 and 390px; login mobile check; Dean and Faculty roles, sign-in/out, search/reset, archive empty results and pagination, profile/budget dialogs, proposal fields/consent/failure controls, all platform tabs. No runtime errors or page overflow. |
| Proposal-detail browser checks | All nine tabs and review dialogs at 1440, 820 and 390px. Existing pipeline-test records were supplied only through browser GET interception; no application proposal was created. No runtime errors or page overflow. |
| Source/UI review | JSX/control/content comparison passed; stylesheet and protected source/configuration/test files unchanged. No lint-disable comments remain in frontend source. |

## Unresolved findings and limits

- **No unresolved lint findings.**
- Backend pipeline tests log `EPERM: operation not permitted` while renaming a temporary state file into `backend/.test-data/state.json`. Both the full suite and isolated rerun still exit successfully with every assertion passing. The warning's cause was not resolved; backend persistence code is outside this frontend lint change and was not modified.
- The previously documented login Schema inspector omission is unrelated to lint and remains unchanged.
- There is no existing frontend test script/suite. Frontend behavior was verified in Microsoft Edge using the already-installed Python Playwright tooling, with temporary regression harnesses; no dependency was added.
- Browser verification did not save budgets or submit live proposal/approval/rollback operations. Existing backend tests cover the corresponding contracts, permissions and workflow.
- Tests regenerated their normal `.test-data` artifacts, and the running backend appended normal audit entries for browser sign-in checks. Build output was regenerated. These runtime outputs are separate from source edits.

No commit or push was performed.
