# Limitations and future work

| Status | Finding |
| --- | --- |
| Implemented/tested | Main workflow, ownership, budgets, counts, exports and Restore have offline regressions, not institutional certification. |
| Implemented/live unverified | MongoDB auth/network/recovery/mirror need infrastructure; current local mode is JSON. |
| Implemented/quality unverified | Ollama/Qwen and explicit Groq have controlled response/outage tests; no fresh live quality result. |
| Provider failure | Prior OpenAlex checks returned 401/503. No fresh live Crossref success is claimed. |
| Persistence boundary | JSON assumes one writer; fallback-created accounts/sessions are memory-only; no distributed JSON/Mongo transaction. |
| Historical gap | Recalled input cannot be reconstructed; missing old context stays unavailable. |
| Policy boundary | Practice calls/rates/quotations are synthetic. Legacy cap-helper compatibility is marked for policy review. |
| Rendering boundary | Native Word COM rendering was blocked; DOCX structure and PDF rendering are separately checked. |
| Dependency warning | Installed anyio pytest plugin emits PytestRemovedIn10Warning; assertions remain enabled. |
| Course completion | Division and independent confirmation of team details need a filled document. Marks/signatures remain blank. |
| Attribution | No new license or broader source-data redistribution permission. |

Future work: approved live-call ingestion; authentic agency/ethics policy/quotations; expert entailment/novelty review; campus SSO and production sessions/passwords; institutional security review, HTTPS, backups/recovery; agreed production engine/storage; pending identity/financial conflict review; live integration and genuine-call college acceptance. No measured speed improvement, external submission or production deployment is claimed.
