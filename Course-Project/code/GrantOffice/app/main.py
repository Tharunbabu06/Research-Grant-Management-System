from fastapi import FastAPI,HTTPException,Depends,Request,Response,UploadFile,File,Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse,StreamingResponse
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter,defaultdict
from io import BytesIO,StringIO
import json,secrets,time,zipfile,csv,html,hashlib,re,threading
from . import store,review
from .models import *
from .connector import Connector,CATALOG,deadline_open,call_verified
from .skills import plan_skill
from .workflow import execute,MUTATION_LOCK
store.init()
app=FastAPI(title='Grant Office · Research Grant Management',version='2.0.0')
ATTEMPTS=defaultdict(list)
def fail(message,code=400):raise HTTPException(code,message)
@app.middleware('http')
async def guard(request,call_next):
 if request.method in ('POST','PUT','DELETE','PATCH') and request.headers.get('X-Grant-Office')!='1':return Response('Missing same-origin request header',status_code=403)
 response=await call_next(request)
 response.headers['X-Content-Type-Options']='nosniff';response.headers['Referrer-Policy']='same-origin';response.headers['X-Frame-Options']='DENY';response.headers['Cache-Control']='no-store'
 response.headers['Content-Security-Policy']="default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'"
 return response
def actor(request:Request):
 token=request.cookies.get('grant_session','')
 with store.connect() as c:r=c.execute('SELECT username FROM sessions WHERE token=? AND expires>?',(hashlib.sha256(token.encode()).hexdigest(),time.time())).fetchone()
 if not r:fail('Please sign in.',401)
 u=store.user(r['username'])
 if not u:fail('Account not found',401)
 return store.public_user(u)
def office(u):
 if u['role'] not in ('research_office','dean'):fail('Research Office or Dean role required.',403)
def get_run(rid,u):
 r=store.load_run(rid)
 if not r or not store.permitted(u,r):fail('Proposal not found or not accessible.',404)
 return r
@app.get('/api/health')
def health():return {'status':'ok','engine':'LangGraph','external_submission':'disabled; manual agency portal submission only'}
@app.post('/api/login')
def login(d:Login,request:Request,response:Response):
 key=(request.client.host,d.username);ATTEMPTS[key]=[t for t in ATTEMPTS[key] if t>time.time()-300]
 if len(ATTEMPTS[key])>=10:fail('Too many attempts. Try again in five minutes.',429)
 ATTEMPTS[key].append(time.time());u=store.user(d.username)
 if not u or not store.verify(d.password,u['password']):fail('Incorrect username or password. Check your username and current password; use reset_faculty_password.bat if the faculty password is unavailable.',401)
 ATTEMPTS.pop(key,None);token=secrets.token_urlsafe(32)
 with store.connect() as c:c.execute('INSERT INTO sessions VALUES(?,?,?)',(hashlib.sha256(token.encode()).hexdigest(),u['username'],time.time()+8*3600))
 response.set_cookie('grant_session',token,httponly=True,samesite='strict',secure=request.url.scheme=='https',max_age=8*3600)
 store.audit('',u['username'],'auth.login',{});return store.public_user(u)
@app.post('/api/logout')
def logout(request:Request,response:Response,u=Depends(actor)):
 with store.connect() as c:c.execute('DELETE FROM sessions WHERE token=?',(hashlib.sha256(request.cookies.get('grant_session','').encode()).hexdigest(),))
 response.delete_cookie('grant_session');return {'ok':True}
@app.get('/api/me')
def me(u=Depends(actor)):return u
@app.post('/api/password')
def password(d:PasswordChange,u=Depends(actor)):
 if not store.verify(d.current,store.user(u['username'])['password']):fail('Current password incorrect.',403)
 with store.connect() as c:
  c.execute('UPDATE users SET password=? WHERE username=?',(store.password_hash(d.new),u['username']));c.execute('DELETE FROM sessions WHERE username=?',(u['username'],))
 store.audit('',u['username'],'auth.password_changed',{});return {'ok':True}
@app.post('/api/users')
def create_user(d:UserCreate,u=Depends(actor)):
 office(u)
 d.username=d.username.strip().lower()
 if store.user(d.username):fail('Username already exists.')
 with store.connect() as c:c.execute('INSERT INTO users VALUES(?,?,?,?,?)',(d.username,d.name,d.role,d.department,store.password_hash(d.password)))
 store.audit('',u['username'],'auth.user_created',{'username':d.username,'role':d.role,'department':d.department});return {'ok':True}
@app.get('/api/dashboard')
def dashboard(u=Depends(actor)):
 with store.connect() as c:runs=[dict(x) for x in c.execute('SELECT * FROM runs ORDER BY updated DESC')]
 runs=[r for r in runs if store.permitted(u,r)]
 pipeline=[]
 for r in runs:
  s=json.loads(r.pop('state'));p=s.get('plan',{});r.update(title=p.get('title',''),mode=p.get('mode',''),budget=s.get('budget',{}).get('total_inr',0),deadline=s.get('selected_call',{}).get('deadline'),checks=s.get('checks',[]));pipeline.append(r)
 awards=[x for x in CATALOG['grants'] if x['status']=='Historical award']
 return {'publications':len(CATALOG['publications']),'awards':len(awards),'applications':len(CATALOG['grants'])-len(awards),'sanctioned_inr':sum(x['amount_inr'] or 0 for x in awards),'pipeline':pipeline,'by_year':dict(Counter(x['cycle'] for x in CATALOG['publications'])),'by_agency':dict(Counter(x['agency'] for x in awards)),'issues':CATALOG['issues'],'real_calls':len([x for x in store.registry('calls') if deadline_open(x) and call_verified(x)]),'audit_valid':store.audit_verify(),'metric_scope':'Historical totals use the 19 detailed award rows only; not legacy DOC, applied amounts or duplicate summaries.'}
@app.get('/api/catalog/{kind}')
def catalog(kind:str,q:str='',u=Depends(actor)):
 if kind not in ('publications','grants','legacy','issues','inventory','raw_rows'):fail('Unknown catalog')
 if kind=='raw_rows':office(u)
 rows=CATALOG[kind]
 if q:rows=[r for r in rows if q.casefold() in json.dumps(r,ensure_ascii=False).casefold()]
 return {'total':len(rows),'records':rows}
@app.get('/api/catalog/{kind}/csv')
def export_catalog(kind:str,u=Depends(actor)):
 if kind not in ('publications','grants'):fail('Unknown export')
 if kind=='raw_rows':office(u)
 rows=CATALOG[kind];buf=StringIO();fields=list(dict.fromkeys(key for row in rows for key in row));writer=csv.DictWriter(buf,fieldnames=fields)
 writer.writeheader()
 for row in rows:
  def safe(v):
   t=json.dumps(v,ensure_ascii=False) if isinstance(v,(dict,list)) else str(v or '')
   return "'"+t if t.startswith(('=','+','-','@')) else t
  writer.writerow({k:safe(v) for k,v in row.items()})
 return Response(buf.getvalue(),media_type='text/csv',headers={'Content-Disposition':f'attachment; filename={kind}.csv'})
@app.post('/api/connector/read')
def connector(q:ToolQuery,u=Depends(actor)):return Connector(u).read(q)
@app.post('/api/planner/clarify')
def clarify(payload:dict,u=Depends(actor)):
 text=str(payload.get('prompt',''))[:4000]
 return {'questions':['What research area, proposed title and intended outcomes should this grant support?','Which funding type, project duration and itemized budget should the plan use?','Do you consent to using your profile/publications, and is this a practice or an institutional application?'],'suggestion':'Fill the intake form, then edit objectives and methodology before locking the plan.','prompt':text}
@app.post('/api/plans')
def create_plan(i:Intake,u=Depends(actor)):
 if not i.consent:fail('Explicit profile/publication consent is required.')
 if not i.lines:fail('Add at least one budget item with its basis.')
 p=plan_skill(i);ident=secrets.token_hex(12)
 with store.connect() as c:c.execute('INSERT INTO plans VALUES(?,?,?,?,?)',(ident,u['username'],u['department'],p.model_dump_json(),store.now()))
 store.audit('',u['username'],'plan.draft',{'id':ident,'plan':p.model_dump()});return {'id':ident,'plan':p.model_dump(),'hash':store.digest(p.model_dump())}
@app.put('/api/plans/{ident}')
def update_plan(ident:str,i:Intake,u=Depends(actor)):
 with store.connect() as c:
  r=c.execute('SELECT * FROM plans WHERE id=?',(ident,)).fetchone()
  if not r or r['owner']!=u['username']:fail('Plan not found',404)
  p=plan_skill(i);c.execute('UPDATE plans SET body=? WHERE id=?',(p.model_dump_json(),ident))
 store.audit('',u['username'],'plan.revise',{'id':ident,'plan':p.model_dump()});return {'id':ident,'plan':p.model_dump()}
@app.post('/api/plans/{ident}/run')
def start(ident:str,u=Depends(actor)):
 with MUTATION_LOCK:
  with store.connect() as c:r=c.execute('SELECT * FROM plans WHERE id=?',(ident,)).fetchone()
  if not r or r['owner']!=u['username']:fail('Plan not found',404)
  p=json.loads(r['body'])
  if not p['consent'] or not p['lines']:fail('Consent and a budget are required.')
  rid=secrets.token_hex(12);s={'run_id':rid,'actor':u,'plan':p,'plan_hash':store.digest(p),'thread_id':rid,'attempts':0,'status':'running','started':time.time()}
  with store.connect() as c:c.execute('INSERT INTO runs(id,owner,department,status,state,created,updated) VALUES(?,?,?,?,?,?,?)',(rid,u['username'],u['department'],'running',json.dumps(s),store.now(),store.now()))
  store.audit(rid,u['username'],'plan.locked',{'plan':p,'hash':s['plan_hash']})
  try:return execute(rid,s)
  except Exception as e:fail('Run saved at checkpoint; inspect audit and retry. '+str(e)[:200],500)
@app.get('/api/runs/{rid}')
def run(rid:str,u=Depends(actor)):
 r=get_run(rid,u)
 if r['state']['plan']['mode']=='real' and r['state'].get('narrative'):
  r['draft_review']={'hash':review.draft_hash(r['state']),**review.assessments(r['state'])}
 return r

@app.post('/api/runs/{rid}/draft-review')
def draft_review(rid:str,d:DraftReview,u=Depends(actor)):
 with MUTATION_LOCK:
  r=get_run(rid,u);s=r['state']
  if s['plan']['mode']!='real' or r['status']!='blocked' or not s.get('selected_call') or not s.get('narrative'):
   fail('This run has no blocked institutional draft to review.',409)
  fingerprint=review.draft_hash(s)
  if d.expected_hash!=fingerprint:fail('Draft changed. Reload and review again.',409)
  if d.kind=='pi':
   if r['owner']!=u['username']:fail('Only the proposal owner can confirm the PI review.',403)
   if d.rules:fail('Use an office eligibility review to assess rules.')
  else:
   office(u)
   call=s['selected_call']
   required={str(i) for i in range(1,len(call['eligibility_rules'])+1)}
   if set(d.rules)!=required:fail('Assess each eligibility rule separately.')
   allowed={x['id'] for x in s['evidence'] if x['kind']=='eligibility'}
   if any(item.status=='pass' and item.evidence_id not in allowed for item in d.rules.values()):
    fail('Every passing rule needs an eligibility evidence ID attached to this draft.')
  reviews=review.assessments(s)
  reviews[d.kind]={**d.model_dump(),'actor':u['username'],'recorded_at':store.now()}
  store.register('draft_reviews',rid+':'+fingerprint,reviews)
  store.audit(rid,u['username'],'human.draft_review',reviews[d.kind])
  s.update(thread_id=rid+'-'+secrets.token_hex(5),review_refresh=True,status='running',started=time.time())
  store.save_state(rid,s)
  return execute(rid,s)

@app.post('/api/runs/{rid}/resume')
def resume(rid:str,u=Depends(actor)):
 with MUTATION_LOCK:
  r=get_run(rid,u)
  if r['status'] not in ('error','running'):fail('Only interrupted/error executions can resume here. Use the review action for approval.')
  return execute(rid)
@app.post('/api/runs/{rid}/decision')
def decide(rid:str,d:Decision,u=Depends(actor)):
 with MUTATION_LOCK:
  r=get_run(rid,u)
  if not store.can_review(u,r):fail('Only an authorized HoD, research office or Dean may approve.',403)
  if d.action=='approve' and r['state']['plan']['mode']=='real':office(u)
  if r['status']!='awaiting_review':fail('This proposal is not awaiting review.',409)
  if d.expected_hash!=r['state']['package_hash']:fail('Package changed. Reload and review.',409)
  if not deadline_open(r['state']['selected_call']):fail('The call deadline has passed. Revise and revalidate.',409)
  from .workflow import compliance
  current_checks=compliance(r['state'])['prechecks']
  if not all(x['passed'] for x in current_checks):fail('Evidence or source freshness no longer passes validation. Create a revised proposal with rechecked sources.',409)
  decision={**d.model_dump(),'actor':u['username']};store.audit(rid,u['username'],'human.decision',decision)
  return execute(rid,decision=decision)
@app.post('/api/runs/{rid}/revise')
def revise(rid:str,d:Revision,u=Depends(actor)):
 with MUTATION_LOCK:
  r=get_run(rid,u)
  if r['owner']!=u['username'] and not store.can_review(u,r):fail('Not authorized',403)
  s=copy_state(r['state']);s['plan']['lines']=[x.model_dump() for x in d.lines]
  if d.evidence_ids is not None:s['plan']['evidence_ids']=d.evidence_ids
  s['plan_hash']=store.digest(s['plan']);s['narrative_override']=d.narrative;s['thread_id']=rid+'-'+secrets.token_hex(5);s['attempts']=0;s['started']=time.time();s['status']='running'
  for k in ('decision','package','package_hash','review_refresh'):s.pop(k,None)
  with store.connect() as c:c.execute('UPDATE runs SET active_version=0 WHERE id=?',(rid,))
  store.save_state(rid,s);store.audit(rid,u['username'],'governance.revision_invalidates_approval',{'note':d.note,'new_plan_hash':s['plan_hash']});return execute(rid,s)
def copy_state(s):return json.loads(json.dumps(s))
@app.get('/api/runs/{rid}/versions')
def versions(rid:str,u=Depends(actor)):
 get_run(rid,u)
 with store.connect() as c:return [dict(x) for x in c.execute('SELECT version,hash,actor,created FROM versions WHERE run_id=? ORDER BY version DESC',(rid,))]
@app.post('/api/runs/{rid}/rollback/{version}')
def rollback(rid:str,version:int,u=Depends(actor)):
 with MUTATION_LOCK:
  r=get_run(rid,u)
  if not store.can_review(u,r):fail('Reviewer authority required',403)
  if r['status'] in ('running','awaiting_review','error'):fail('Complete or reject the current revision before restoring a release.',409)
  with store.connect() as c:
   v=c.execute('SELECT * FROM versions WHERE run_id=? AND version=?',(rid,version)).fetchone()
   if not v:fail('Version not found',404)
   restored=json.loads(v['body'])
   if restored['mode']=='real':office(u)
   state=copy_state(r['state'])
   state.update({'plan':restored['plan'],'plan_hash':restored['plan_hash'],'package':restored,'package_hash':v['hash'],'narrative':restored['narrative'],'budget':restored['budget'],'checks':restored['compliance'],'literature':restored['literature'],'evidence':restored['evidence'],'selected_call':restored['call'],'llm':restored.get('llm',{}),'status':'restored_release'})
   state.pop('narrative_override',None)
   state['decision']={'action':'approve','actor':v['actor'],'expected_hash':v['hash'],'note':'Restored approved release; see original approval audit.'}
   c.execute('UPDATE runs SET active_version=?,status=?,state=?,updated=? WHERE id=?',(version,'restored_release',json.dumps(state),store.now(),rid))
  store.audit(rid,u['username'],'governance.rollback',{'to_version':version,'hash':v['hash'],'scope':'Restores the internal approved package; cannot retract an external submission.'});return get_run(rid,u)
@app.get('/api/runs/{rid}/audit')
def audit(rid:str,u=Depends(actor)):
 get_run(rid,u)
 with store.connect() as c:rows=[dict(r) for r in c.execute('SELECT * FROM audit WHERE run_id=? ORDER BY id',(rid,))]
 for x in rows:x['body']=json.loads(x['body'])
 return rows
@app.get('/api/runs/{rid}/package')
def package(rid:str,u=Depends(actor)):
 r=get_run(rid,u);s=r['state'];p=s.get('package')
 authorized=bool(r['active_version'])
 if authorized:
  with store.connect() as c:p=json.loads(c.execute('SELECT body FROM versions WHERE run_id=? AND version=?',(rid,r['active_version'])).fetchone()[0])
 if not p:fail('A validated package is not available. Resolve the failed checks first.',409)
 mark='SAMPLE DATA — NOT FOR SUBMISSION' if p['mode'] in ('sandbox','demo') else ('AUTHORIZED INTERNAL PACKAGE — SUBMIT MANUALLY' if authorized else 'DRAFT — NOT AUTHORIZED')
 doc='<!doctype html><meta charset="utf-8"><title>Grant proposal</title><style>body{font:16px/1.6 system-ui;max-width:900px;margin:40px auto;color:#183047}pre{white-space:pre-wrap;font:inherit}.mark{border:2px solid #b36a17;padding:16px}td,th{border:1px solid #bbb;padding:8px}table{border-collapse:collapse;width:100%}@media print{body{margin:15mm}}</style>'+f'<div class="mark">{mark}</div><h1>{html.escape(p["title"])}</h1><p>Version: {r["active_version"] or "draft"} · Package hash: {store.digest(p)}</p><pre>{html.escape(p["narrative"])}</pre><h2>Itemized budget (INR)</h2><table><tr><th>Item</th><th>Quantity</th><th>Unit cost</th><th>Total</th></tr>'
 for line in p['budget']['lines']:doc+=f'<tr><td>{html.escape(line["description"])}</td><td>{line["quantity"]}</td><td>{line["unit_inr"]:,}</td><td>{line["total_inr"]:,}</td></tr>'
 doc+=f'</table><h3>Total: INR {p["budget"]["total_inr"]:,}</h3><h2>Compliance</h2>'+''.join(f'<p>{"PASS" if x["passed"] else "FAIL"} — {html.escape(x["name"])}: {html.escape(x["detail"])}</p>' for x in p['compliance'])
 buf=BytesIO()
 with zipfile.ZipFile(buf,'w',zipfile.ZIP_DEFLATED) as z:
  z.writestr('proposal.html',doc);z.writestr('proposal.md',mark+'\n\n'+p['narrative']);z.writestr('package.json',json.dumps({**p,'authorization_status':mark,'version':r['active_version']},ensure_ascii=False,indent=2));z.writestr('compliance.json',json.dumps(p['compliance'],indent=2));z.writestr('evidence.json',json.dumps(p['evidence'],ensure_ascii=False,indent=2));z.writestr('literature.json',json.dumps(p['literature'],ensure_ascii=False,indent=2));z.writestr('audit.json',json.dumps(audit(rid,u),ensure_ascii=False,indent=2))
  b=StringIO();w=csv.DictWriter(b,fieldnames=list(p['budget']['lines'][0]));w.writeheader()
  for line in p['budget']['lines']:w.writerow({k:("'"+v if isinstance(v,str) and v.startswith(('=','+','-','@')) else v) for k,v in line.items()})
  z.writestr('budget.csv',b.getvalue());z.writestr('README.txt',mark+'\nOpen proposal.html and print to PDF if desired. The ZIP is an internal review package. Use the actual agency portal/template for final submission. This application never sends to an agency.\n')
  for e in p['evidence']:
   if e.get('attachment'):
    path=store.DATA/'evidence_files'/e['attachment']
    if path.is_file():z.write(path,'attachments/'+path.name)
 buf.seek(0);store.audit(rid,u['username'],'package.export',{'version':r['active_version'],'hash':store.digest(p)})
 return StreamingResponse(buf,media_type='application/zip',headers={'Content-Disposition':f'attachment; filename=grant_{rid}_v{r["active_version"]}.zip'})
@app.get('/api/registry')
def registry(u=Depends(actor)):return {'calls':store.registry('calls'),'policies':store.registry('policies')}
@app.post('/api/policies')
def policy(p:Policy,u=Depends(actor)):
 office(u);ev=Connector(u).evidence([p.evidence_id])
 if not ev or ev[0]['kind']!='policy':fail('Attach a policy evidence record first.')
 if any(x['id']==p.id for x in store.registry('policies')):fail('Policy IDs are immutable. Create a new version ID.')
 d={**p.model_dump(),'verified_by':u['username'],'verified_at':store.now()};store.register('policies',p.id,d);store.audit('',u['username'],'policy.recorded',d);return d
@app.post('/api/calls')
def call(p:Call,u=Depends(actor)):
 office(u)
 try:deadline=datetime.fromisoformat(p.deadline.replace('Z','+00:00'))
 except ValueError:fail('Deadline must be ISO 8601 including timezone.')
 if deadline.tzinfo is None:fail('A timezone is required.')
 from urllib.parse import urlparse
 url=urlparse(p.source_url)
 if url.scheme!='https' or not url.hostname or url.hostname.endswith('.invalid') or url.hostname in ('localhost','127.0.0.1'):fail('Use the actual official HTTPS guideline URL.')
 ev=Connector(u).evidence([p.evidence_id])
 if not ev or ev[0]['kind']!='guideline' or ev[0]['source_url']!=p.source_url:fail('Attach matching guideline evidence first.')
 if not any(x['id']==p.policy_id for x in store.registry('policies')):fail('Select a recorded institutional policy.')
 if not set(p.allowed_categories).issubset({'personnel','equipment','travel','consumables','overheads'}) or any(v<0 for v in p.allowed_categories.values()):fail('Invalid category limits.')
 if any(x['id']==p.id for x in store.registry('calls')):fail('Call IDs are immutable. Use a fresh version ID for changed/rechecked guidelines.')
 d={**p.model_dump(),'verified_by':u['username'],'verified_at':store.now(),'verification_method':'Manual research-office attestation against retained guideline evidence','mock':False}
 store.register('calls',p.id,d);store.audit('',u['username'],'call.source_attested',d);return d
@app.post('/api/evidence')
def evidence(e:Evidence,u=Depends(actor)):
 ident='EV-'+secrets.token_hex(8);d={**e.model_dump(),'id':ident,'owner':u['username'],'department':u['department'],'sha256':hashlib.sha256(e.text.encode()).hexdigest(),'recorded_at':store.now(),'verification':'User-provided evidence; not automatically independently verified.'}
 with store.connect() as c:c.execute('INSERT INTO evidence VALUES(?,?,?,?)',(ident,u['username'],u['department'],json.dumps(d)))
 store.audit('',u['username'],'evidence.recorded',{'id':ident,'sha256':d['sha256']});return d
@app.post('/api/evidence/upload')
async def upload(title:str=Form(...),kind:str=Form(...),source_url:str=Form(''),locator:str=Form(...),excerpt:str=Form(...),file:UploadFile=File(...),u=Depends(actor)):
 ext=Path(file.filename or '').suffix.lower()
 if ext not in ('.pdf','.docx','.txt'):fail('Use PDF, DOCX or TXT evidence.')
 data=await file.read(8*1024*1024+1)
 if len(data)>8*1024*1024:fail('Maximum attachment size is 8 MB.')
 if (ext=='.pdf' and not data.startswith(b'%PDF')) or (ext=='.docx' and not data.startswith(b'PK')):fail('File signature does not match extension.')
 e=Evidence(title=title,kind=kind,text=excerpt,source_url=source_url,locator=locator);d=evidence(e,u)
 folder=store.DATA/'evidence_files';folder.mkdir(exist_ok=True);name=d['id']+ext;(folder/name).write_bytes(data);d['attachment']=name;d['attachment_sha256']=hashlib.sha256(data).hexdigest();d['original_filename']=Path(file.filename).name
 with store.connect() as c:c.execute('UPDATE evidence SET body=? WHERE id=?',(json.dumps(d),d['id']))
 return d
@app.get('/api/evidence')
def evidence_list(u=Depends(actor)):return Connector(u).read(ToolQuery(resource='evidence',limit=100))
@app.get('/api/system')
def system(u=Depends(actor)):
 import importlib.metadata
 from .llm import settings
 cfg=settings()
 return {'engine':'LangGraph '+importlib.metadata.version('langgraph'),'llm':cfg['provider'],'model':cfg['model'],'persistence':'SQLite + LangGraph SqliteSaver','audit_chain_valid':store.audit_verify(),'live_discovery':'Office-curated official calls with retained source evidence.','scope':'Institutional workspace; real releases require current guideline, policy and eligibility evidence.'}
@app.get('/api/llm/status')
def llm_status(u=Depends(actor)):
 from .llm import status
 return status()
@app.post('/api/llm/config')
def llm_config(d:LLMConfig,u=Depends(actor)):
 office(u);body={'id':'llm',**d.model_dump()};store.register('configuration','llm',body);store.audit('',u['username'],'llm.configuration',body)
 return body
@app.post('/api/assistant')
def assistant(d:AssistantRequest,u=Depends(actor)):
 return Connector(u).answer(d.question,d.resource,d.mode,d.use_llm)
@app.get('/api/users')
def users(u=Depends(actor)):
 office(u)
 with store.connect() as c:return [dict(x) for x in c.execute('SELECT username,name,role,department FROM users ORDER BY username')]
@app.post('/api/users/{username}/reset-password')
def reset_user(username:str,d:ResetPassword,u=Depends(actor)):
 office(u)
 from .auth import reset_password
 try:reset_password(username,d.password,u['username'])
 except ValueError as e:fail(str(e))
 for key in list(ATTEMPTS):
  if key[1]==username.strip().lower():ATTEMPTS.pop(key,None)
 return {'ok':True,'message':'Password updated and previous sessions revoked. Existing records preserved.'}
@app.get('/api/labs')
def labs(u=Depends(actor)):
 path=store.ROOT.parent.parent/'docs/evidence/lab_verification.json'
 return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {'labs':[],'notice':'Verification report is not present.'}
app.mount('/static',StaticFiles(directory=store.ROOT/'static'),name='static')
@app.get('/')
def home():return FileResponse(store.ROOT/'static/index.html')

@app.post('/api/llm/test')
def test_local_model(u=Depends(actor)):
 office(u)
 from .llm import Gateway,AnswerOutput
 return Gateway(u).generate('assistant',{'question':'Explain this source in one sentence and cite its ID.','sources':[{'id':'LOCAL-CHECK','title':'Connectivity check only','text':'Researchers prepare drafts; authorized office staff review and approve them. This synthetic text checks the model connection.'}]},AnswerOutput)
