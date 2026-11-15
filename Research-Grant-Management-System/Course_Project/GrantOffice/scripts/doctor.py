import sys,importlib.metadata
from pathlib import Path
print('Python:',sys.version)
for package in ['fastapi','uvicorn','langgraph','langgraph-checkpoint-sqlite','langchain-core','openpyxl','olefile','pytest']:
 try:print(package,importlib.metadata.version(package))
 except importlib.metadata.PackageNotFoundError:print(package,'MISSING; run setup.bat')
root=Path(__file__).resolve().parents[1]
print('Catalog present:',(root/'data/catalog.json').is_file())
print('First-run login file:',(root/'runtime/FIRST_LOGIN.txt').is_file())
print('No cloud LLM API key is required. Ollama is optional.')
