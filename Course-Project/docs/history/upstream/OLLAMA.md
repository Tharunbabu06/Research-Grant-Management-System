# Local LLM integration

The model is used in two places:

1. **Proposal drafting:** the gateway receives the locked objectives/methodology, selected-call requirements and retrieved publication metadata/abstracts. It returns a typed abstract, methodology, risk list and supporting source IDs.
2. **Research assistant:** the connector retrieves scoped institutional evidence, then asks the local model to explain it and cite source IDs. If no evidence is found, the app does not invent an answer.

Both paths use Ollama's `/api/chat` endpoint with a JSON schema in `format`. Responses are parsed through Pydantic. Citation IDs must be a subset of the records actually supplied to the model. Missing/unknown citations or malformed structure trigger at most one additional attempt; failures fall back explicitly. Network failures do not trigger an unbounded retry.

Schema validation and source-ID checks do not prove that every generated sentence is correct. Drafts remain marked for faculty review. The LLM cannot alter the budget, execute arbitrary code, authorize a release or submit to an agency.

## Windows setup

- Install Ollama from https://ollama.com/download/windows.
- Start the Ollama application.
- Run `setup_llm.bat`; it executes `ollama pull qwen2.5:3b`.
- In Office settings, choose the installed model and automatic/local-model mode.
- Click **Check connection** to check installed model availability.
- Click **Test model response** to generate and validate an actual response against a small synthetic connection-check source.
- Alternatively run `check_llm.bat` and read its `used` result.

The model download is separate from the project ZIP. No paid API key is needed. Hardware speed and available memory determine latency. The default limits are two generation attempts, 70 seconds per request, 1,400 output tokens and an 8,192-token context setting. The overall agent runtime also checks its execution budget.

## Settings and privacy

Provider choices: `auto`, `ollama`, `template`. The default is `auto`; automatic mode uses the configured model only when Ollama reports it installed. It does not silently choose an unrelated model.

The endpoint is fixed to `http://127.0.0.1:11434`. Requests set `trust_env=False` so college source text is not sent through a machine-wide HTTP proxy. No cloud LLM endpoint is configured. Do not expose Ollama's local API publicly.

Office/Dean can configure the model; faculty can see its status. Environment variables `GRANT_LLM` and `OLLAMA_MODEL`, when explicitly set by the system owner, override the saved settings. `start_ollama.bat` sets the local-model mode for its process. Use the normal `start.bat` for settings-driven automatic mode.

## Verification evidence

Automated tests cover valid structured generation, malformed output repair, unknown citation rejection, timeout handling, disabled/unavailable-model fallback, configuration permissions and LLM-backed graph execution using controlled HTTP responses. They do not download or execute model weights. Run the live connection check on the target machine before claiming live LLM verification.

Official API references consulted: https://docs.ollama.com/api/chat and https://docs.ollama.com/capabilities/structured-outputs .
