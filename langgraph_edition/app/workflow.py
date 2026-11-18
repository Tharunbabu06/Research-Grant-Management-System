import sqlite3,threading,time,copy,os
from typing import TypedDict,Any
from langgraph.graph import StateGraph,START,END
from langgraph.types import interrupt,Command
from langgraph.checkpoint.sqlite import SqliteSaver
from . import store,review
from .connector import Connector,deadline_open,call_verified
from .models import ToolQuery
from .skills import format_skill,SPECIALISTS
os.environ.setdefault('LANGGRAPH_STRICT_MSGPACK','true')
MUTATION_LOCK=threading.RLock()
class State(TypedDict,total=False):
 run_id:str;actor:dict;plan:dict;plan_hash:str;status:str;attempts:int
 candidates:list;selected_call:dict;literature:list;literature_status:dict;prior:list;evidence:list
 narrative:str;narrative_override:str;budget:dict;prechecks:list;checks:list
 limitations:list;package:dict;package_hash:str;decision:dict;llm:dict
 started:float;elapsed_seconds:float;thread_id:str;fault:str;review_refresh:bool

def tools(s):return Connector(s['actor'],s['run_id'])
def check(name,ok,detail):return {'name':name,'passed':bool(ok),'detail':detail}
def traced(name,fn):
 def node(s):
  start=time.perf_counter();out=fn(s)
  store.audit(s['run_id'],s['actor']['username'],'agent.'+name,{'input_state_hash':store.digest(s),'output':out,'seconds':round(time.perf_counter()-start,4)})
  return out
 return node

def discover(s):
 p=s['plan'];c=tools(s);calls=c.read(ToolQuery(resource='calls',mode=p['mode'],query='',limit=100))
 candidates=c.candidates(calls,p)
 good=[x['call'] for x in candidates if not x['rejected'] and (not p['call_id'] or x['call']['id']==p['call_id'].replace('DEMO-','SAMPLE-'))]
 return {'candidates':candidates,'selected_call':good[0] if good else {}}
def literature(s):
 c=tools(s);p=s['plan']
 hits,status=c.search_literature((p['area']+' '+p['title'])[:500],p.get('public_literature_query',''))
 prior=c.read(ToolQuery(resource='prior',query=p['title'],limit=3))
 return {'literature':hits,'prior':prior,'literature_status':status}
def draft(s):
 p=s['plan'];c=tools(s);call=s.get('selected_call',{})
 evidence=c.evidence(p['evidence_ids']+([call.get('evidence_id','')] if call else []))
 policies=c.read(ToolQuery(resource='policies',limit=100)) if p['mode']=='real' else []
 policy=next((x for x in policies if x['id']==call.get('policy_id')),None)
 if policy:evidence+=c.evidence([policy['evidence_id']])
 llm=c.draft_suggestion({'title':p['title'],'area':p['area'],'objectives':p['objectives'],'methodology':p['methodology'],'call':{k:call.get(k) for k in ('title','eligibility_rules','template_sections','excerpt')},'sources':[{'id':x['id'],'title':x['title'],'abstract':x['abstract'][:1800],'source':x['sources'][0]} for x in s['literature']]})
 refs='\n'.join(f"[{x['id']}] {x['title']} ({x['year']}); DOI: {x['doi'] or 'not supplied'}. Evidence: {x['sources'][0]['file']}, {x['sources'][0]['sheet']}, row {x['sources'][0]['row']}." for x in s['literature'])
 timeline='\n'.join([f'Months 1–{max(1,p["months"]//3)}: data permissions, requirements and baseline.',f'Months {max(1,p["months"]//3)+1}–{max(2,2*p["months"]//3)}: implementation and iterative evaluation.',f'Months {max(2,2*p["months"]//3)+1}–{p["months"]}: final evaluation, documentation and reporting.']) if p['months']>=3 else 'Months 1–'+str(p['months'])+': scoped feasibility, implementation and review milestones; PI to refine.'
 text=f"{p['title']}\n\nAI-ASSISTED WORKING DRAFT\n\nObjectives\n"+'\n'.join(f'{i+1}. {x}' for i,x in enumerate(p['objectives']))+f"\n\nMethodology\n{p['methodology']}\n\nTimeline\n{timeline}\n\nFunder profile\n{SPECIALISTS[p['funding_type']]['focus']}\n\nRelated work and source evidence\n{refs or 'No matching publication evidence found.'}\n\nGap and novelty\nThe retrieved literature records identify related work; they do not establish global novelty. Full-text review and a wider literature search are required before making novelty claims.\n\nExpected outputs (proposed)\nA documented prototype, evaluation report and reproducibility materials. No performance or preliminary result is asserted."
 if llm['text']:text+='\n\nLLM-assisted research development — faculty review required\n'+llm['text']
 return {'narrative':s.get('narrative_override') or text,'evidence':list({x['id']:x for x in evidence}.values()),'llm':llm,'limitations':['Literature retrieval uses publication metadata and available abstracts. Review the underlying papers before making scientific claims.','Novelty is pending expert review.','No external application has been submitted.']}
def budget(s):
 b=tools(s).calculate(s['plan']['lines'])
 if s.get('fault')=='budget_total':b['total_inr']+=1
 return {'budget':b}
def compliance(s):
 p=s['plan'];call=s.get('selected_call',{});demo=p['mode'] in ('sandbox','demo');ev=s['evidence'];kinds={e['kind'] for e in ev}
 checks=[check('Profile consent',p['consent'],'Explicit permission to use the provided profile/publication history.'),check('Matched open call',bool(call) and deadline_open(call),'A current deadline with timezone and topical/type match is required.'),check('Duration within call',bool(call) and p['months']<=call.get('duration_months',0),'Requested months against selected call maximum.'),check('Literature evidence',bool(s['literature']),'At least one relevant institutional or external publication record; novelty is not asserted.')]
 if demo:checks.append(check('Sandbox isolation',call.get('mock',False),'Simulation rules only; never valid for an external submission.'))
 else:
  reviews=review.assessments(s)
  checks += [check('Source and freshness',call_verified(call),'Research-office source verification must be within seven days.'),check('Guideline evidence',any(x['id']==call.get('evidence_id') and x['kind']=='guideline' for x in ev),'Selected call requires a retained guideline excerpt.'),check('Institutional policy',any(x['kind']=='policy' for x in ev),'An approved institutional policy must be linked through the call.'),check('Required documents',set(call.get('required_documents',[])).issubset(kinds),'All required evidence document kinds must be present.'),check('Ethics evidence',not p['ethics_required'] or ('ethics' in kinds and bool(p['ethics_note'])),'Human/clinical-data projects require documented ethics status.'),check('PI draft review',bool(reviews.get('pi')),'The proposal owner must confirm this exact draft in Review & versions.')]
  checks += review.eligibility_checks(s,ev,reviews)
 return {'prechecks':checks}
def validate(s):
 p=s['plan'];call=s.get('selected_call',{});b=s['budget'];totals={}
 for line in b['lines']:totals[line['category']]=totals.get(line['category'],0)+line['quantity']*line['unit_inr']
 checks=s['prechecks']+[
 check('Locked plan unchanged',store.digest(p)==s['plan_hash'],'Plan hash must match the approved execution specification.'),
 check('Budget totals reconcile',b['total_inr']==sum(totals.values()),'All line products must sum exactly to the package total.'),
 check('Positive itemized budget',len(b['lines'])>0 and b['total_inr']>0,'At least one positive justified cost is required.'),
 check('Overall budget ceiling',bool(call) and b['total_inr']<=call.get('ceiling_inr',0),'No automatic adjustment of requested figures.'),
 check('Category ceilings',bool(call) and all(k in call.get('allowed_categories',{}) and v<=call['allowed_categories'][k] for k,v in totals.items()),'Category ceilings are taken from the selected call; disallowed categories fail.'),
 check('Required sections',all(x.lower() in s['narrative'].lower() for x in call.get('template_sections',['Objectives','Methodology','Timeline'])),'Presence check only; reviewer must assess substantive content.'),
 check('Run execution budget',time.time()-s['started']<240,'One run has a 240-second wall-clock budget and at most two repair attempts.')]
 failed=[x['name'] for x in checks if not x['passed']]
 return {'checks':checks,'status':'validated' if not failed else 'validation_failed','elapsed_seconds':round(time.time()-s['started'],3)}
def route_validation(s):
 failed=[c['name'] for c in s['checks'] if not c['passed']]
 if not failed:return 'assemble'
 if failed==['Budget totals reconcile'] and s.get('attempts',0)<2:return 'repair'
 return 'blocked'
def repair(s):return {'budget':tools(s).calculate(s['plan']['lines']),'attempts':s.get('attempts',0)+1,'fault':''}
def blocked(s):return {'status':'blocked'}
def assemble(s):
 p=format_skill(s);return {'package':p,'package_hash':store.digest(p),'status':'awaiting_review'}
def gate(s):
 d=interrupt({'run_id':s['run_id'],'package_hash':s['package_hash'],'message':'Human authorization required. Approve, request changes or reject.'})
 if d.get('expected_hash')!=s['package_hash']:raise ValueError('Approval does not match this package')
 return {'decision':d,'status':{'approve':'authorized','changes':'changes_requested','reject':'rejected'}[d['action']]}
def route_gate(s):return 'publish' if s['decision']['action']=='approve' else END
def publish(s):
 # Recheck authority and deadline immediately before creating an internal release.
 actor=store.user(s['decision']['actor']);run=store.load_run(s['run_id'])
 if not actor or not store.can_review(actor,run) or (s['plan']['mode']=='real' and actor['role'] not in ('research_office','dean')):raise ValueError('Reviewer no longer authorized')
 if store.digest(s['package'])!=s['package_hash'] or not all(x['passed'] for x in s['checks']+compliance(s)['prechecks']) or not deadline_open(s['selected_call']):raise ValueError('Validation or deadline invalidated; revise and rerun')
 status='sandbox_released' if s['plan']['mode'] in ('sandbox','demo') else 'authorized_package'
 with store.connect() as c:
  c.execute('BEGIN IMMEDIATE')
  existing=c.execute('SELECT version FROM versions WHERE run_id=? AND hash=?',(s['run_id'],s['package_hash'])).fetchone()
  if existing:v=existing[0]
  else:
   v=c.execute('SELECT COALESCE(MAX(version),0)+1 FROM versions WHERE run_id=?',(s['run_id'],)).fetchone()[0]
   c.execute('INSERT INTO versions VALUES(?,?,?,?,?,?)',(s['run_id'],v,json_dump(s['package']),s['package_hash'],actor['username'],store.now()))
  c.execute('UPDATE runs SET active_version=? WHERE id=?',(v,s['run_id']))
 store.audit(s['run_id'],actor['username'],'governance.internal_release',{'version':v,'hash':s['package_hash'],'mode':s['plan']['mode'],'decision_note':s['decision']['note']})
 return {'status':status}
def json_dump(x):
 import json
 return json.dumps(x)
def make_graph(checkpointer):
 g=StateGraph(State)
 for name,fn in [('discovery',discover),('literature',literature),('draft',draft),('budget',budget),('compliance',compliance),('validate',validate),('repair',repair),('blocked',blocked),('assemble',assemble),('publish',publish)]:g.add_node(name,traced(name,fn))
 g.add_node('human_review',gate)
 g.add_conditional_edges(START,lambda state: ['budget','compliance'] if state.get('review_refresh') else ['discovery','literature'], ['budget','compliance','discovery','literature'])
 g.add_edge(['discovery','literature'],'draft')
 g.add_edge('draft','budget');g.add_edge('draft','compliance');g.add_edge(['budget','compliance'],'validate')
 g.add_conditional_edges('validate',route_validation,{'assemble':'assemble','repair':'repair','blocked':'blocked'});g.add_edge('repair','validate');g.add_edge('blocked',END)
 g.add_edge('assemble','human_review');g.add_conditional_edges('human_review',route_gate,{'publish':'publish',END:END});g.add_edge('publish',END)
 return g.compile(checkpointer=checkpointer)
CHECKPOINT=SqliteSaver(sqlite3.connect(store.DATA/'checkpoints.sqlite',check_same_thread=False,timeout=30))
GRAPH=make_graph(CHECKPOINT)
def execute(rid,payload=None,decision=None):
 with MUTATION_LOCK:
  run=store.load_run(rid);thread=run['state']['thread_id'];cfg={'configurable':{'thread_id':thread},'recursion_limit':35}
  try:
   result=GRAPH.invoke(Command(resume=decision) if decision else payload,cfg)
   state=dict(GRAPH.get_state(cfg).values);store.save_state(rid,state);return store.load_run(rid)
  except Exception as e:
   state=dict(GRAPH.get_state(cfg).values) or run['state'];state['status']='error';store.save_state(rid,state)
   store.audit(rid,run['owner'],'runtime.error',{'type':type(e).__name__,'message':str(e)[:1000]});raise
