# Version 2 verification — 28 October 2026

## Automated software checks

This section records the original ZIP baseline. The current merged build has its own results in `acceptance-results.xml` and `lab_verification.json`.

**50 tests passed in 8.70 seconds**, using Python 3.12 and the supplied locked dependencies. `scripts/verify_labs.py` produced `docs/acceptance-results.xml` and `docs/lab_verification.json`; all fourteen software capability groups have passing mapped checks. Tests use isolated temporary databases and do not erase office records.

Coverage includes username normalization, password recovery, session revocation, preservation of proposal records, idempotent account setup, role and department permissions, consent, planning, typed tool and submission contracts, provenance, retrieval, current-call restrictions, both parallel graph stages, validation gates, bounded repair, plan drift, human approval, version rollback and persistent checkpoint reconstruction.

Local-LLM tests cover structured drafting and assistant responses, retry after malformed output, unknown citation rejection, timeout fallback, configuration permissions and integration with the LangGraph proposal pipeline. Successful model responses in automated tests are **controlled HTTP fixtures**, not live model inference. They test application behavior and cannot establish scientific accuracy or model quality.

Institutional-evidence tests also use explicitly synthetic fixtures. Passing them does not establish that a genuine agency call or official college policy was supplied.

The preserved source catalog contains 529 unique publications, 19 detailed historical awards and 2 applications, plus 115 legacy document text chunks and 12 import notes. Text chunks are not award counts.

## Browser checks

Headless Chromium exercised the FastAPI interface at desktop width 1440 and mobile width 390:

- Faculty login with uppercase and surrounding whitespace; password visibility.
- Institutional mode by default; explicit sample proposal loading.
- Consent, editable plan, graph execution, budget and validation display.
- Faculty approval restriction, HoD approval and released package download.
- Catalog, calls, evidence, assistant, settings and fourteen-lab navigation.
- Grounded retrieval and evidence/policy administration.
- Office password recovery followed by successful faculty login with the new password.
- Local-model controls and fourteen verification cards.
- Mobile document overflow and JavaScript error checks.

The complete browser workflow passed. Screenshots and the altered test account database are excluded from the ZIP.

## Parallel behavior

Barrier-based tests confirm concurrent execution of the discovery/literature and budget/compliance graph stages. The earlier seven-candidate scoring benchmark (ten repetitions, median including audit write) measured serial 1.052 ms versus threaded 1.817 ms, with identical rankings and rejection reasons. Threads were slower for this small CPU-bound fixture; no general speedup is claimed. Re-measure against the intended workload using `scripts/benchmark.py`.

## Re-run

On Windows, run `verify_14_labs.bat`. Alternatively:

```sh
python scripts/verify_labs.py
python scripts/doctor.py
python scripts/benchmark.py
```

For the optional browser checks, use a fresh, expendable installation with generated accounts and the server stopped:

```sh
python -m pip install playwright
python -m playwright install chromium
python scripts/ui_smoke.py
```

That browser script creates sample proposals and synthetic evidence and resets the test faculty password. Do not run it against the operational database. It expects initial credentials from `runtime/FIRST_LOGIN.txt`; use a fresh test installation for each complete run.

## Remaining acceptance

Native Windows execution, Docker startup, live Ollama generation, actual agency submission, external live-call ingestion, a formal institutional security assessment, broad accessibility certification and PI acceptance of real proposal quality were not verified here. The local launchers are supplied but do not imply those environments were executed.

On the college computer, install the local model with `setup_llm.bat`, then run `check_llm.bat` or Office settings → Test model generation. Supply genuine current funding-call and policy evidence and perform named-human review before institutional use. Lab 14's real-case capstone and the worklet's human-editing and workload latency KPIs require that local pilot.
