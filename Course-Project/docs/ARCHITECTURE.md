# Architecture and data flow

## Main application

[React entry](../frontend/src/App.jsx) calls authenticated [API helpers](../frontend/src/lib/api.js). Vite proxies `/api` to port 3000 in development. [Express startup](../backend/index.js) serves the built console on loopback and only reports readiness after successful binding.

[API routes](../backend/src/api.js) enforce opaque expiring bearer sessions, role permissions and ownership. Sessions are memory-only. Seed identities support classroom login, not verified campus identity. Researcher profiles do not confer authentication permissions.

[Engine](../backend/src/engine.js), [agents](../backend/src/agents.js) and [runtime](../backend/src/core.js) implement a JavaScript stage graph. Eight visible roles comprise coordinator, funding discovery, literature, drafting, budget, compliance, packaging and human review. The last role is a person.

1. Capture request, consent and immutable input snapshot; construct/lock the plan.
2. Discover eligible practice calls and retrieve literature, retaining provider/source labels.
3. Draft sections; enforce structured model/source contracts or record template fallback.
4. Compute categorized budget/compliance; validate totals, evidence, scope and required fields.
5. Apply bounded targeted repair. Financial alternatives require explicit acceptance; impossible cases block.
6. Prepare a checksum-bound package, wait for authorized review and save an internal version.
7. Export the selected saved package or confirm a scope-aware historical Restore. No external submission occurs.

## Storage and integrations

Primary workflow state is local JSON (`AURA_DATA_DIR`, default Course-Project/backend/data). [Atomic writer](../backend/src/atomic-store.js) flushes unique same-directory temporary files and retries transient Windows locks. Persistent failure is surfaced; corrupt JSON refuses startup. Audit and project-budget edits persist locally. One backend writer per directory is assumed.

[MongoDB](../backend/src/database.js) optionally supports account/project administration and asynchronous workflow mirroring. [Persistence diagnostics](../backend/src/persistence.js) distinguish absent configuration and safe connection failure categories. A connected mirror does not replace an acknowledged JSON write. Runtime-created fallback accounts are not durable.

[College adapter](../backend/src/college-data.js) reads the Python edition's catalog in place; operational stores are separate. [Research sources](../backend/src/research-sources.js) separate offline archive browsing from OpenAlex public-topic search and Crossref DOI metadata. [HTTP policy](../backend/src/provider-http.js) implements bounded transient retries and Retry-After.

[Model gateway](../backend/src/model.js) selects local Ollama/Qwen or explicit Groq. Structured/source-ID checks do not prove truth, entailment or novelty. Public search terms and optional cloud drafting context have different disclosure boundaries.

## Independent edition and labs

[Python app](../langgraph_edition/app/) uses FastAPI, real LangGraph stages and SQLite state/checkpoints under `GRANT_DATA_DIR`. It serves its own static UI on port 8000, not the React UI. No operational synchronization is implemented.

[Supplied labs](../../Assignments/scripts/) are standard-library demonstrations. [Earlier lab support](../code/Lab_Support/) supports retained earlier assignment programs. Neither establishes MCP wire compatibility or an installed OpenClaw runtime. Their checks have separate scope.
