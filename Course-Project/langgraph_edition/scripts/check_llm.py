import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app import store
from app.llm import status,Gateway,AnswerOutput
store.init();print(json.dumps(status(),indent=2))
if '--generate' in sys.argv:
 result=Gateway({'username':'local-system-check'}).generate('assistant',{'question':'Explain the source and cite its ID.','sources':[{'id':'LOCAL-CHECK','text':'Faculty drafts are reviewed by authorized research-office staff. Synthetic connection check only.'}]},AnswerOutput)
 print(json.dumps(result,indent=2))
 if not result['used']:raise SystemExit(1)
