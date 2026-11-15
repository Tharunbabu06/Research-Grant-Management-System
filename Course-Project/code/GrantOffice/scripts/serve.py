"""Open the browser only after this local server is ready; keep one authoritative address."""
import sys,socket,threading,time,webbrowser,urllib.request
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
def open_when_ready():
 opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
 for _ in range(80):
  try:
   with opener.open('http://127.0.0.1:8000/api/health',timeout=1) as r:
    if r.status==200:webbrowser.open('http://127.0.0.1:8000');return
  except OSError:pass
  time.sleep(.25)
if __name__=='__main__':
 with socket.socket() as check:
  if check.connect_ex(('127.0.0.1',8000))==0:raise SystemExit('Port 8000 is already in use. Stop the earlier Grant Office/server window before starting this version.')
 threading.Thread(target=open_when_ready,daemon=True).start()
 import uvicorn
 uvicorn.run('app.main:app',host='127.0.0.1',port=8000,workers=1)
