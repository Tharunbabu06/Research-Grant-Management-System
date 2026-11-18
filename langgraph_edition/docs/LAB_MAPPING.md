# Fourteen-lab implementation and acceptance map

This maps the final integrated software to the supplied Chapter 13. It is not a claim that the college has performed the real-case capstone acceptance. Real calls/policies and institutional sign-off were absent from the uploaded data.

| Lab | Implementation / artifact | Verification and qualification |
|---|---|---|
| 1 — Agent vs chatbot | Intake, `/planner/clarify`, plan preview, revision loop; `notebooks/Lab01_Planner.ipynb` | At least two clarifying questions; editable objectives and methodology; not a one-shot final answer |
| 2 — Tools | `Connector.read`, `calculate`, `candidates`; typed schemas | Costs computed by Python tools; lookups carry source IDs; negative costs rejected |
| 3 — Reusable skills | `plan_skill(Intake) -> Plan`, `format_skill(state) -> package` | Reused with distinct topics/profiles; request/plan and formatted submission schemas validated |
| 4 — Memory/retrieval | Checkpoint state separated from catalog/history; tag filters; 2,048-d hashing embeddings; scoped prior-run search | Tag and similarity tests; lexical feature embeddings, not pretrained semantic embeddings |
| 5 — Connector | Single governed Connector + authenticated `/api/connector/read` | All specialist source access through it; explicit MCP-style interface, not MCP protocol transport |
| 6 — Governed runtime | Audit inputs/output hashes/results, SqliteSaver, 240-second budget, bounded repair, checkpoint resume | Persistent checkpoint is reconstructed in a separate graph instance during tests; process restart smoke check included |
| 7 — Full node graph | `workflow.py` executable StateGraph with branches, merges, validation and human interrupt | End-to-end test reaches review only after all checks pass |
| 8 — Parallel workers | Graph parallel stages; per-call ThreadPoolExecutor fan-out; deterministic merge | Barrier-based tests verify both parallel graph stages overlap; the benchmark checks identical ranking quality between serial/parallel scoring. Actual speed depends on workload; no fabricated speedup KPI |
| 9 — Evidence grounding | Source row provenance; retained guideline/policy records; evidence table; literal bibliographic record references | Real pipeline blocks without evidence. Metadata supports relevance only, not global novelty or paper findings |
| 10 — Resilience | Diagnosis-specific budget-total repair; bounded retries; fail-closed escalation | Injected inconsistent total repaired once; over-ceiling budget remains blocked |
| 11 — Tested build | `python -m pytest -q`; validated artifact gate | All checks required before assembly/review; negative and permission tests included |
| 12 — Governance | Role/department permissions, private evidence, package-hash approval, immutable versions, restore, metrics, audit | Cross-department reads and faculty approvals denied; edit resets approval; rollback changes exported package |
| 13 — Specialists | Government/industry/international profile registry; call-specific cost limits and sections | Practice calls for all three profiles; exact real norms supplied through the registry, never inferred |
| 14 — Capstone | Local runnable UI + connector + graph + datasets + export + tests + walkthrough | Practice workflow can complete in one session. Real institutional capstone acceptance remains pending genuine current source documents, named review and user evaluation |

## Worklet KPIs

1. **100% validation checks pass before review:** enforced in control flow. Blocked proposals do not count as successes and cannot be approved.
2. **Evidence for every package:** package contains plan/source evidence, literature row references and cost basis. Real verification is manual and must be within seven days. Generic planned objectives are labelled proposals; no performance results or global-novelty claims are invented.
3. **Zero autonomous consequential external actions:** no external submission endpoint exists. Internal release requires reviewer authority and exact hash match.
4. **Rollback:** restores an internal approved version. Export follows the restored version. External portal actions cannot be undone by this application.
5. **Light human editing for a real case:** not yet measured; requires a college-run pilot with actual call requirements and human review time tracking.
6. **Parallel latency improvement:** measured with the supplied benchmark, not asserted universally. Small local CPU-bound fixture scoring may be slower with threads; parallel independent graph stages are still correctly joined.

## Remaining institution-owned acceptance work

Obtain real funder forms and policy documents; confirm faculty identity and profile permissions; map every actual call's requirements and required document kinds; review department codes and historical inconsistencies; evaluate the narrative with the PI; test office backup/restore and accessibility on the target Windows computer; decide whether the local pilot is ready for wider deployment.

## Included software verification

Run `verify_14_labs.bat` (or `python scripts/verify_labs.py`). The script runs isolated tests and maps actual results to all fourteen labs in `docs/lab_verification.json`, displayed in the dashboard under Worklet verification. The delivery run passed 50 tests. See `TEST_REPORT.md` for what was tested and the remaining live-model and institutional acceptance steps.
