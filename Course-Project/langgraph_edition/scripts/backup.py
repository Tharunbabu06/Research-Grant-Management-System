"""Stop the server first; safely backup persistent SQLite databases and retained evidence."""
from pathlib import Path
import sqlite3,zipfile,tempfile,datetime,shutil
root=Path(__file__).resolve().parents[1];runtime=root/'runtime';out=root/'backups';out.mkdir(exist_ok=True)
if not runtime.is_dir():raise SystemExit('No runtime data to back up yet.')
name=out/('grant-office-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S')+'.zip')
with tempfile.TemporaryDirectory() as tmp:
 p=Path(tmp)
 for src in runtime.glob('*.sqlite'):
  with sqlite3.connect(src) as s,sqlite3.connect(p/src.name) as d:s.backup(d)
 with zipfile.ZipFile(name,'w',zipfile.ZIP_DEFLATED) as z:
  for f in p.glob('*'):z.write(f,'runtime/'+f.name)
  if (runtime/'evidence_files').exists():
   for f in (runtime/'evidence_files').glob('*'):z.write(f,'runtime/evidence_files/'+f.name)
print(name)
print('Confidential backup includes accounts and proposal data. Store under institution-controlled access.')
