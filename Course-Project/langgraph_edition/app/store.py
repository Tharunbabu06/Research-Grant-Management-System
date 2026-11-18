from pathlib import Path
import os,sqlite3,json,hashlib,secrets,time
ROOT=Path(__file__).resolve().parents[1]
DATA=Path(os.getenv('GRANT_DATA_DIR',str(ROOT/'runtime')))
DATA.mkdir(parents=True,exist_ok=True)
DB=DATA/'office.sqlite'
def connect():
 c=sqlite3.connect(DB,timeout=30);c.row_factory=sqlite3.Row;c.execute('PRAGMA journal_mode=WAL');return c
def now():
 from datetime import datetime,timezone
 return datetime.now(timezone.utc).isoformat()
def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
def password_hash(p,salt=None):
 salt=salt or secrets.token_hex(16)
 return salt+':'+hashlib.scrypt(p.encode(),salt=salt.encode(),n=16384,r=8,p=1).hex()
def verify(p,h):return secrets.compare_digest(password_hash(p,h.split(':')[0]),h)
def init():
 with connect() as c:c.executescript('''
 CREATE TABLE IF NOT EXISTS users(username TEXT PRIMARY KEY,name TEXT,role TEXT,department TEXT,password TEXT);
 CREATE TABLE IF NOT EXISTS sessions(token TEXT PRIMARY KEY,username TEXT,expires REAL);
 CREATE TABLE IF NOT EXISTS plans(id TEXT PRIMARY KEY,owner TEXT,department TEXT,body TEXT,created TEXT);
 CREATE TABLE IF NOT EXISTS runs(id TEXT PRIMARY KEY,owner TEXT,department TEXT,status TEXT,state TEXT,created TEXT,updated TEXT,active_version INTEGER DEFAULT 0);
 CREATE TABLE IF NOT EXISTS versions(run_id TEXT,version INTEGER,body TEXT,hash TEXT,actor TEXT,created TEXT,PRIMARY KEY(run_id,version));
 CREATE TABLE IF NOT EXISTS audit(id INTEGER PRIMARY KEY AUTOINCREMENT,run_id TEXT,actor TEXT,action TEXT,body TEXT,created TEXT,previous TEXT,hash TEXT);
 CREATE TABLE IF NOT EXISTS registry(kind TEXT,id TEXT,body TEXT,PRIMARY KEY(kind,id));
 CREATE TABLE IF NOT EXISTS evidence(id TEXT PRIMARY KEY,owner TEXT,department TEXT,body TEXT);
 ''')
def user(name):
 with connect() as c:r=c.execute('SELECT * FROM users WHERE username=?',(name,)).fetchone()
 return dict(r) if r else None
def public_user(u):return {k:v for k,v in u.items() if k!='password'}
def permitted(u,r):return u['role'] in ('research_office','dean') or (u['role']=='hod' and u['department']==r['department']) or u['username']==r['owner']
def can_review(u,r):return u['role'] in ('research_office','dean') or (u['role']=='hod' and u['department']==r['department'])
def audit(run_id,actor,action,body):
 with connect() as c:
  c.execute('BEGIN IMMEDIATE');last=c.execute('SELECT hash FROM audit ORDER BY id DESC LIMIT 1').fetchone();prev=last[0] if last else 'GENESIS';stamp=now();record={'run_id':run_id,'actor':actor,'action':action,'body':body,'created':stamp,'previous':prev};h=digest(record)
  c.execute('INSERT INTO audit(run_id,actor,action,body,created,previous,hash) VALUES(?,?,?,?,?,?,?)',(run_id,actor,action,json.dumps(body),stamp,prev,h))
def load_run(rid):
 with connect() as c:r=c.execute('SELECT * FROM runs WHERE id=?',(rid,)).fetchone()
 if not r:return None
 d=dict(r);d['state']=json.loads(d['state']);return d
def save_state(rid,state):
 safe={k:v for k,v in state.items() if not k.startswith('__')}
 with connect() as c:c.execute('UPDATE runs SET state=?,status=?,updated=? WHERE id=?',(json.dumps(safe),safe.get('status','running'),now(),rid))
def register(kind,ident,body):
 with connect() as c:c.execute('INSERT OR REPLACE INTO registry VALUES(?,?,?)',(kind,ident,json.dumps(body)))
def registry_item(kind,ident):
 with connect() as c:
  row=c.execute('SELECT body FROM registry WHERE kind=? AND id=?',(kind,ident)).fetchone()
 return json.loads(row[0]) if row else None
def registry(kind):
 with connect() as c:return [json.loads(r[0]) for r in c.execute('SELECT body FROM registry WHERE kind=?',(kind,))]
def audit_verify():
 prev='GENESIS'
 with connect() as c:
  for r in c.execute('SELECT * FROM audit ORDER BY id'):
   body={k:r[k] for k in ('run_id','actor','action','created','previous')};body['body']=json.loads(r['body'])
   if r['previous']!=prev or digest(body)!=r['hash']:return False
   prev=r['hash']
 return True
