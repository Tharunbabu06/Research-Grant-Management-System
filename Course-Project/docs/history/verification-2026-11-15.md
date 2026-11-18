# Verification record

Executed on Linux, Node 24.22.1, npm 11.9, Python 3.12. Date: 15 November 2026.

| Check | Result | Scope |
|---|---|---|
| Original reference backend suite | 9/9 passed | Complete pipeline, typed budget, governance, eligibility, bounded repair and connectors |
| Merged backend suite | 18/18 passed | Original 9 plus 9 integration/regression tests |
| Frontend production build | Passed | Vite compiles 37 source modules |
| Supplied lab acceptance checks | 140/140 passed across 14 scripts | Scripts executed in isolated directories; final notebook acceptance cells applied to captured output |
| Preserved Python/LangGraph edition | 53/53 passed | Existing pytest suite; one dependency deprecation warning |
| Built-app HTTP startup smoke | Passed | Built frontend served, login, bootstrap, project register, college counts, literature and model status |
| Browser visual smoke test | Blocked | Chromium could not start: sandbox environment prohibited its local socket |
| Live OpenAlex, Crossref, Ollama, MongoDB Atlas | Not executed | Provider behavior tested using mocked responses and outage cases |
| Native Windows scripts | Not executed | Batch files supplied for local verification; tests ran on Linux |

The lab checks are the supplied output/trace assertions, not 140 additional independent API integration tests. The 9 original backend tests are included within the merged 18; do not add these counts together. Upstream screenshots and earlier output files are historical evidence, not fresh screenshots of this merge.

## Commands

From the root:

```sh
npm --prefix backend ci
npm --prefix frontend ci
npm --prefix backend test
npm --prefix frontend run build
python tools/verify_labs.py
```

For the preserved application, install its requirements in a separate Python environment, change into langgraph_edition, and run `python -m pytest -q`.

## New regression cases

1. Fabricated tokens, absent passwords and spoofed actor headers cannot authenticate.
2. Faculty cannot read or edit another faculty run.
3. Budget edits survive store reload and reject invalid cost/ownership.
4. OpenAlex/Crossref records normalize and deduplicate DOI identities without leaking the OpenAlex key to Crossref.
5. Outages differ from a successful search returning no results.
6. Local model adapter sends the expected request and reports connection failure.
7. Public keywords and methodology persist in createRun.
8. Stale or changed packages cannot be approved; downloads require a session; invalid batched edits leave the draft unchanged; internal approval never submits externally.
9. Bench-loop narrative preserves the supplied engineering methodology without unrelated clinical/template software claims.

## Local demo checklist

- Run setup.bat and start.bat; sign in using a demo account.
- Inspect the dashboard and menus on a desktop and phone-width window. Confirm the Practice workflow label.
- Edit a permitted project's budget, restart the server and confirm the total persists.
- Search the literature page without a key, then with your valid OpenAlex key. Confirm both source outcomes and DOI links; inspect an abstract and provenance.
- Enter a proposed bench-loop project, public keywords, methodology and consent. Review the plan, create a run and inspect source and fallback status.
- Sign in as a different faculty member: the first user's run must not be accessible.
- Sign in as Dean; open and inspect the complete package, record a decision and download the proposal. Confirm external submission remains false.
- With Ollama running, check provider status and generate a test response. Inspect whether each section used the model or a template.
- Keep authentic funding-call source evidence and quotations separate from practice fixtures before planning an institutional pilot.
