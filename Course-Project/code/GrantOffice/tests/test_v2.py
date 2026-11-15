"""Version 2 regression and worklet checks. All model responses here are controlled test fixtures."""
import json,sys,subprocess,threading,time,importlib.util
from pathlib import Path
import pytest,httpx
from test_acceptance import login,start,intake,decision
from app import store
from app.main import app
from app.llm import Gateway,DraftOutput,AnswerOutput
from app.connector import Connector,demo_calls
from app.models import Intake
from app.auth import reset_password
H={'X-Grant-Office':'1'}

def test_username_case_and_whitespace(client):
 assert client.post('/api/login',json={'username':'  F  ','password':'test-only-password'},headers=H).status_code==200

def test_password_reset_preserves_records_and_revokes_sessions(client):
 login(client,'f');r=start(client)
 other=__import__('fastapi.testclient',fromlist=['TestClient']).TestClient(app);login(other,'o')
 res=other.post('/api/users/f/reset-password',json={'password':'replacement-password-2026'},headers=H);assert res.status_code==200
 assert client.get('/api/me').status_code==401
 assert client.post('/api/login',json={'username':'f','password':'test-only-password'},headers=H).status_code==401
 assert client.post('/api/login',json={'username':'F','password':'replacement-password-2026'},headers=H).status_code==200
 assert client.get('/api/runs/'+r['id']).status_code==200
 reset_password('f','test-only-password','test-cleanup')

def test_faculty_cannot_reset_other_accounts(client):
 login(client,'f');assert client.post('/api/users/h/reset-password',json={'password':'not-authorized-reset'},headers=H).status_code==403

def test_local_recovery_without_data_loss(client):
 login(client,'f');r=start(client)
 reset_password('f','local-reset-password','local-system-operator')
 assert store.load_run(r['id'])['state']['plan']['title']==r['state']['plan']['title']
 reset_password('f','test-only-password','test-cleanup')

def test_setup_preserves_existing_credentials_and_account_passwords(tmp_path):
 env=__import__('os').environ.copy();env['GRANT_DATA_DIR']=str(tmp_path)
 script=store.ROOT/'scripts/setup_users.py'
 subprocess.run([sys.executable,str(script)],env=env,check=True,capture_output=True)
 first=(tmp_path/'FIRST_LOGIN.txt').read_text()
 subprocess.run([sys.executable,str(script)],env=env,check=True,capture_output=True)
 assert (tmp_path/'FIRST_LOGIN.txt').read_text()==first
 assert 'Demo ' not in first

def test_institutional_default_and_legacy_input():
 args=intake();args.pop('mode');assert Intake(**args).mode=='real'
 assert Intake(**intake(mode='demo')).mode=='sandbox'

def test_no_demo_branding_in_ui():
 js=(store.ROOT/'static/app.js').read_text(encoding='utf-8');html=(store.ROOT/'static/index.html').read_text(encoding='utf-8')
 assert 'demo' not in js.lower() and 'demo' not in html.lower()
 assert "mode:'real'" in js and 'SAMPLE' in js

def model_ready(monkeypatch):
 monkeypatch.setenv('GRANT_LLM','ollama');monkeypatch.setenv('OLLAMA_MODEL','qwen2.5:3b')
 def get(*args,**kwargs):
  assert kwargs['trust_env'] is False
  return httpx.Response(200,json={'models':[{'name':'qwen2.5:3b'}]},request=httpx.Request('GET',args[0]))
 monkeypatch.setattr(httpx,'get',get)

def response(payload):
 return httpx.Response(200,json={'message':{'content':json.dumps(payload)},'eval_count':80,'prompt_eval_count':200},request=httpx.Request('POST','http://127.0.0.1:11434/api/chat'))

def test_llm_structured_grounded_success(monkeypatch):
 model_ready(monkeypatch);calls=[]
 def post(url,**kw):
  calls.append(kw);assert kw['trust_env'] is False;assert 'properties' in kw['json']['format']
  return response({'abstract':'A proposed monitoring feasibility study grounded in [PUB-1].','methodology':'Compare a candidate approach with a baseline on held-out synthetic data, informed by [PUB-1].','risks':['Evidence is metadata only; novelty remains unconfirmed.'],'evidence_ids':['PUB-1']})
 monkeypatch.setattr(httpx,'post',post)
 g=Gateway(store.public_user(store.user('f')));out=g.generate('proposal',{'title':'A proposed study','sources':[{'id':'PUB-1','title':'Retained institutional record'}]},DraftOutput)
 assert out['used'] and out['mode']=='ollama' and out['tokens']['output']==80 and len(calls)==1

def test_llm_hallucinated_citation_rejected_with_bounded_retry(monkeypatch):
 model_ready(monkeypatch);calls=[]
 def post(*args,**kw):calls.append(1);return response({'answer':'Unsupported statement [MADE-UP].','evidence_ids':['MADE-UP']})
 monkeypatch.setattr(httpx,'post',post)
 out=Gateway(store.public_user(store.user('f'))).generate('assistant',{'sources':[{'id':'PUB-1'}]},AnswerOutput)
 assert not out['used'] and len(calls)==2

def test_llm_malformed_json_then_repair(monkeypatch):
 model_ready(monkeypatch);calls=[]
 def post(*args,**kwargs):
  calls.append(1)
  return response({'wrong':'schema'}) if len(calls)==1 else response({'answer':'Evidence [PUB-1] is a retained publication record, not proof of novelty.','evidence_ids':['PUB-1']})
 monkeypatch.setattr(httpx,'post',post)
 out=Gateway(store.public_user(store.user('f'))).generate('assistant',{'sources':[{'id':'PUB-1'}]},AnswerOutput)
 assert out['used'] and out['attempts']==2

def test_llm_timeout_explicit_fallback(monkeypatch):
 model_ready(monkeypatch)
 def post(*a,**k):raise httpx.ReadTimeout('controlled timeout')
 monkeypatch.setattr(httpx,'post',post)
 out=Gateway(store.public_user(store.user('f'))).generate('assistant',{'sources':[]},AnswerOutput)
 assert not out['used'] and out['mode']=='template_fallback'

def test_llm_settings_role_boundary(client):
 login(client,'f');assert client.post('/api/llm/config',json={'provider':'auto','model':'qwen2.5:3b'},headers=H).status_code==403
 login(client,'o');assert client.post('/api/llm/config',json={'provider':'auto','model':'qwen2.5:3b'},headers=H).status_code==200

def test_assistant_retrieves_evidence(client):
 login(client,'f');r=client.post('/api/assistant',json={'question':'Find cardiovascular heart publications','use_llm':False},headers=H)
 assert r.status_code==200 and r.json()['records'];assert not r.json()['answer']['used']

def test_llm_assistant_endpoint_with_grounding(client,monkeypatch):
 model_ready(monkeypatch)
 def post(*a,**kw):
  context=json.loads(kw['json']['messages'][1]['content'].split('\n',1)[1]);ident=context['sources'][0]['id']
  return response({'answer':'The retained record ['+ident+'] supports topical relevance; inspect its source before making a scientific claim.','evidence_ids':[ident]})
 monkeypatch.setattr(httpx,'post',post);login(client,'f')
 out=client.post('/api/assistant',json={'question':'cardiovascular monitoring publications'},headers=H).json()
 assert out['answer']['used'] and out['records']

def test_full_graph_uses_structured_llm(client,monkeypatch):
 model_ready(monkeypatch)
 def post(*a,**kw):
  ctx=json.loads(kw['json']['messages'][1]['content'].split('\n',1)[1]);ident=ctx['sources'][0]['id']
  return response({'abstract':'A planned feasibility study using retained evidence ['+ident+'].','methodology':'Compare the proposed model with a reproducible baseline using held-out synthetic data ['+ident+'].','risks':['Full-text and novelty review remain necessary.'],'evidence_ids':[ident]})
 monkeypatch.setattr(httpx,'post',post);login(client,'f');r=start(client)
 assert r['status']=='awaiting_review' and r['state']['llm']['used']
 assert 'LLM-assisted research development' in r['state']['narrative']
 assert r['active_version']==0

def test_both_parallel_stages_really_overlap(client,monkeypatch):
 import app.workflow as w
 from langgraph.checkpoint.memory import InMemorySaver
 first=threading.Barrier(2);second=threading.Barrier(2)
 def wrap(fn,barrier):
  def run(s):barrier.wait(timeout=5);return fn(s)
  return run
 for name in ('discover','literature'):monkeypatch.setattr(w,name,wrap(getattr(w,name),first))
 for name in ('budget','compliance'):monkeypatch.setattr(w,name,wrap(getattr(w,name),second))
 g=w.make_graph(InMemorySaver());p=__import__('app.skills',fromlist=['plan_skill']).plan_skill(Intake(**intake())).model_dump();ident='parallel-'+str(time.time_ns())
 s={'run_id':ident,'actor':store.public_user(store.user('f')),'plan':p,'plan_hash':store.digest(p),'attempts':0,'started':time.time(),'thread_id':ident}
 out=g.invoke(s,{'configurable':{'thread_id':ident}})
 assert out['status']=='awaiting_review' and all(x['passed'] for x in out['checks'])

def test_repair_is_bounded_and_only_total_fault_is_repairable():
 from app.workflow import route_validation
 assert route_validation({'checks':[{'name':'Budget totals reconcile','passed':False}],'attempts':2})=='blocked'
 assert route_validation({'checks':[{'name':'Eligibility evidence','passed':False}],'attempts':0})=='blocked'

def test_plan_drift_blocks_validation(client):
 from app.workflow import validate
 login(client,'f');r=start(client);s=r['state'];s['plan']['months']+=1
 checks=validate(s)['checks'];assert any(x['name']=='Locked plan unchanged' and not x['passed'] for x in checks)

def test_formatter_rejects_invalid_package_schema(client):
 from app.skills import format_skill
 from pydantic import ValidationError
 login(client,'f');r=start(client);s=r['state'];s['budget']['total_inr']=-10
 with pytest.raises(ValidationError):format_skill(s)

def test_live_model_test_endpoint_permission(client,monkeypatch):
 login(client,'f');assert client.post('/api/llm/test',headers=H).status_code==403
 login(client,'o');out=client.post('/api/llm/test',headers=H)
 assert out.status_code==200 and out.json()['used'] is False

def test_sample_package_never_claims_official_authorization(client):
 login(client,'f');r=start(client);login(client,'h');r=decision(client,r).json()
 assert r['status']=='sandbox_released' and r['state']['package']['mode']=='sandbox'
 assert 'SAMPLE DATA' in r['state']['package']['watermark']
