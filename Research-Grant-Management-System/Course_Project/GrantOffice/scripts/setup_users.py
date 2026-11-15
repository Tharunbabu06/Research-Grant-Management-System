"""Create missing office accounts without changing existing passwords or overwriting saved credentials."""
import sys,secrets,os
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app import store
ACCOUNTS=[('faculty','Faculty Member','faculty','SOCSE'),('hod','Head of Department','hod','SOCSE'),('office','Research Office','research_office','R&D'),('dean','Dean R&D','dean','R&D'),('ece_faculty','Faculty Member — ECE','faculty','SOECE')]
def setup():
 store.init();created=[]
 for username,name,role,dep in ACCOUNTS:
  old=store.user(username)
  if old:
   if old['name'].startswith('Demo '):
    with store.connect() as c:c.execute('UPDATE users SET name=? WHERE username=?',(name,username))
   continue
  password=secrets.token_urlsafe(14)
  with store.connect() as c:c.execute('INSERT INTO users VALUES(?,?,?,?,?)',(username,name,role,dep,store.password_hash(password)))
  created.append(f'{username:<15} {password}   [{role}, {dep}]')
 if created:
  path=store.DATA/'FIRST_LOGIN.txt'
  with path.open('a',encoding='utf-8') as f:
   if path.stat().st_size==0:f.write('GRANT OFFICE — INITIAL ACCOUNT CREDENTIALS\nKeep this file private. Password changes make the old entry invalid.\nUse reset_faculty_password.bat if the faculty password is unavailable.\n\n')
   f.write('\n'.join(created)+'\n')
  try:os.chmod(path,0o600)
  except OSError:pass
  print('New account credentials saved to runtime/FIRST_LOGIN.txt. Existing accounts are unchanged.')
 else:print('Existing accounts retained. If faculty sign-in fails, run reset_faculty_password.bat; no proposal data will be removed.')
if __name__=='__main__':setup()
