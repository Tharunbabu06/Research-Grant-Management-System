# Setup and configuration

## Main Node/React app

Use Node 24. The supplied scripts require Node 22.13+; fresh checks used Node 24.11.1/npm 11.6.2 on Windows. From root:

```sh
npm --prefix Course-Project/backend ci
npm --prefix Course-Project/frontend ci
npm --prefix Course-Project/frontend run build
```

Copy [the safe example](../backend/.env.example) to Course-Project/backend/.env, preserving existing configuration. Start from backend so dotenv reads that file:

```sh
cd Course-Project/backend
npm start
```

Open http://localhost:3000. Windows Course-Project/setup.bat and Course-Project/start.bat provide the install/build/start path. Dependency installation needs network; offline workflow/tests need no keys, MongoDB Atlas or Ollama. A fresh clone ships no operational proposals.

Development: run `npm --prefix Course-Project/backend run dev` and `npm --prefix Course-Project/frontend run dev` in separate terminals; Vite uses http://localhost:5173 and proxies API port 3000. Rebuild before using the single-process console.

| Variable | Behavior |
| --- | --- |
| `PORT` | Backend port, default 3000; adjust Vite proxy if changed |
| `AURA_DATA_DIR` | Primary workflow directory; default Course-Project/backend/data |
| `AURA_LLM=off` | Deterministic offline template drafting |
| `GRANT_LLM` | ollama default; template disables model; groq explicitly selects cloud |
| `OLLAMA_MODEL` | Default qwen2.5:3b |
| `AURA_LLM_CONCURRENCY` | Default 1 |
| `AURA_LLM_SECTIONS` | Optional comma-separated model-drafted sections |
| `OPENALEX_API_KEY` | Optional server-side public metadata credential |
| `GROQ_API_KEY`, `GROQ_MODEL` | Explicit Groq cloud drafting |
| `MONGODB_URI` / `MONGO_URI` | Optional MongoDB; absent means JSON, not live MongoDB |
| `MONGODB_DB` | Default research_grant |
| `GRANTOFFICE_EXPORT_FONT` | Optional installed Unicode TTF for PDF |
| `AURA_STEP_DELAY`, `AURA_RETRY_BUDGET` | Pacing and bounded repair controls |

Install Ollama separately and run `ollama pull qwen2.5:3b` for local drafting. Weights are not bundled. Inspect model/template diagnostics; configuration does not guarantee successful generation. Explicit Groq sends drafting context off-device. Public search should contain only public keywords.

DOCX needs no Office installation. PDF detects Segoe UI on Windows or DejaVu Sans on Linux; otherwise configure an installed Unicode TTF. Missing fonts return a service error.

## Main verification

```sh
npm --prefix Course-Project/backend test
npm --prefix Course-Project/frontend run lint -- --max-warnings 0
npm --prefix Course-Project/frontend run build
python Course-Project/tools/verify_labs.py
python Course-Project/tools/check_docs.py
```

Labs need Python 3.10+ standard library. Set `PYTHONUTF8=1` and `PYTHONIOENCODING=utf-8` on Windows. Course-Project/verify.bat runs the checks above; it does not install/run the independent Python environment. Notebook rebuilding is optional; supplied outputs were not overwritten.

## Independent Python edition

Use a separate Python 3.12 environment; preserved setup accepts 3.11–3.13. From Course-Project/langgraph_edition:

```sh
python -m venv .venv
# Activate the virtual environment for your operating system.
python -m pip install -r requirements-lock.txt
python scripts/setup_users.py
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

PowerShell activation: `.venv/Scripts/Activate.ps1`; Linux/macOS: `source .venv/bin/activate`. Explicitly select Python 3.12 when multiple interpreters are installed. Windows setup.bat uses py -3 if present; verify that launcher selects a supported interpreter. Its initial passwords are in ignored runtime/FIRST_LOGIN.txt and differ from the Node demo password.

Storage uses `GRANT_DATA_DIR` or runtime/ SQLite/checkpoints. `AURA_DATA_DIR` does not configure this edition. In its environment run `python -m pytest -q`. Its lab mapping reuses those tests; do not count them twice. Earlier support tests run from Course-Project/code/Lab_Support with its requirements installed. [Verification](VERIFICATION.md) records executed environments.
