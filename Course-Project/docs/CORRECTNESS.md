# Correctness and governance evidence

Public summary of current code and reproducible tests. Detailed operational audits remain locally retained and excluded from publication.

| Concern | Implemented behavior | Source evidence |
| --- | --- | --- |
| Budget preservation | Immutable inputs, categories; no silent scaling/minimum inflation | [Engine](../backend/src/engine.js), [agents](../backend/src/agents.js) |
| Monetary arithmetic | Whole INR, rational percentages/half-up rounding, explicit charge permissions and bases | [Budget rules](../backend/src/budget-rules.js) |
| Financial alternatives | Separate proposals; confirmed acceptance; stale fingerprint rejection; approval invalidation | [API](../backend/src/api.js) |
| Identity/counts | Stable IDs, retained duplicate sources/conflicts; distinct activity | [Directory](../backend/src/researcher-directory.js), [activity](../backend/src/proposal-activity.js) |
| Persistence | Unique atomic writes, bounded Windows retries, surfaced failure | [Writer](../backend/src/atomic-store.js), [core](../backend/src/core.js) |
| Providers | Safe missing/rejected/rate/timeout/network/malformed diagnostics and Retry-After | [HTTP adapter](../backend/src/provider-http.js), [sources](../backend/src/research-sources.js) |
| Exports | Genuine saved-version DOCX/PDF, auth, MIME and immutable hashes | [Renderer](../backend/src/exports.js) |
| Restore | Authorized confirmed deep-copy snapshot; missing context stays unavailable | [Engine](../backend/src/engine.js), [UI](../frontend/src/pages/aura-rundetail.jsx) |

## Budget fixture and policy boundaries

TEST input: personnel INR 250000 + equipment INR 150000 + consumables INR 50000 = INR 450000 direct. Explicit TEST rates of 15% overhead and 5% contingency on direct yield INR 67500 and INR 22500, total INR 540000. A higher minimum fails without changing costs. These rates are not agency policy.

Categories: personnel, equipment, consumables, travel, other. Legacy unclassified input cannot truthfully pass category caps. Charges round half up once to whole INR using rational intermediates; up to six fractional percentage digits are supported. Missing rates are zero; charge-disallowed flags take precedence. Charge bases: direct or direct excluding equipment. Category denominators: direct or total.

The standalone old core.tools.capReport signature retains a compatibility assumption when its denominator settings are absent; output is marked requiresPolicyReview, not official policy. Runtime typed tools use explicit rules. Historical approved figures are not rewritten. A recalled original amount cannot be reconstructed from available evidence; no missing input is invented. Working corrections retain before/after costs and invalidate current validation/package/approval. Old snapshots missing call context cannot borrow current rules.

## Approval, exports and Restore

Backend identifiers stay compatible; labels say internally approved proposals. Artifact/context hashes bind review to opened content. Exports use selected saved package/narrative/budget, without model generation or current-field substitution. Existing Markdown/CSV remain authenticated. `?version=1` selects history; stale current exports return 409.

Restore requires version:rollback authority, rejects active execution, and explains selected version, scope and missing fields before confirmation. Deep copies protect original versions. Exact historical approval provenance is retained as history, never a new review. Subsequent edits clear current approval.

[Correctness regressions](../backend/tests/correctness.test.js) cover all these paths as part of the fresh 50-test suite, including private-profile visibility, restart and persistent-write HTTP failure. Prior live OpenAlex checks returned 401/503; MongoDB is locally absent. No successful live provider, institutional acceptance or scientific truth claim follows from mocks. See [verification](VERIFICATION.md).
