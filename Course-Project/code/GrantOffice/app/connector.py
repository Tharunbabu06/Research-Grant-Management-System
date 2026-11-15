"""Single governed source boundary, shared by graph tools and authenticated HTTP routes."""
import json,re,math,hashlib,os
from datetime import datetime,timezone,timedelta
from concurrent.futures import ThreadPoolExecutor
from . import store
from .models import ToolQuery
CATALOG=json.loads((store.ROOT/'data/catalog.json').read_text(encoding='utf-8'))
STOP=set('the a an and for to of in on with using based research project study development ai'.split())
def words(t):return [w for w in re.findall(r'[a-z0-9]+',t.lower()) if len(w)>2 and w not in STOP]
def embed(t):
 # Offline feature-hashing embedding, not a pretrained semantic model.
 v={}
 for w in words(t):
  h=int(hashlib.sha256(w.encode()).hexdigest()[:8],16)%2048;v[h]=v.get(h,0)+1
 norm=math.sqrt(sum(x*x for x in v.values())) or 1
 return {k:x/norm for k,x in v.items()}
def similarity(a,b):return sum(v*b.get(k,0) for k,v in a.items())
def rank(items,q,key):
 a=embed(q);results=[]
 for r in items:
  score=similarity(a,embed(key(r)))
  if score>0 or not q:results.append({**r,'relevance':round(score,4)})
 return sorted(results,key=lambda r:r['relevance'],reverse=True)
def deadline_open(c):
 try:return datetime.fromisoformat(c['deadline'].replace('Z','+00:00'))>datetime.now(timezone.utc)
 except (ValueError,TypeError,KeyError,AttributeError):return False
def call_verified(call):
 try:
  stamp=datetime.fromisoformat(call.get('verified_at',''))
  now=datetime.now(timezone.utc)
  return bool(call.get('verified_by')) and not call.get('mock') and now-timedelta(days=7)<stamp<=now
 except (ValueError,TypeError):
  return False

class Connector:
 def __init__(self,actor,run_id=''):self.actor=actor;self.run_id=run_id
 def read(self,q:ToolQuery):
  if q.resource=='publications':
   rows=CATALOG['publications'];rows=[x for x in rows if not q.tag or q.tag.lower() in (x['tags']+' '+x['cycle']).lower()]
   out=rank(rows,q.query,lambda x:x['title']+' '+x['abstract']+' '+x['tags'])[:q.limit]
  elif q.resource=='history':out=rank(CATALOG['grants'],q.query,lambda x:x['title']+' '+x['agency'])[:q.limit]
  elif q.resource=='calls':
   rows=demo_calls() if q.mode in ('sandbox','demo') else store.registry('calls')
   if q.tag:rows=[x for x in rows if x['funding_type']==q.tag]
   out=rank(rows,q.query,lambda x:x['title']+' '+' '.join(x['areas']))[:q.limit]
  elif q.resource=='policies':out=store.registry('policies')[:q.limit]
  elif q.resource=='prior':
   with store.connect() as c:rows=[dict(r) for r in c.execute('SELECT * FROM runs')]
   rows=[r for r in rows if store.permitted(self.actor,r) and r['id']!=self.run_id]
   out=rank([{'id':r['id'],'title':json.loads(r['state']).get('plan',{}).get('title',''),'status':r['status']} for r in rows],q.query,lambda r:r['title'])[:q.limit]
  else:
   with store.connect() as c:rows=[dict(r) for r in c.execute('SELECT * FROM evidence')]
   out=[json.loads(r['body']) for r in rows if store.permitted(self.actor,r)][:q.limit]
  store.audit(self.run_id,self.actor['username'],'connector.read',{'input':q.model_dump(),'output_ids':[x.get('id') for x in out]})
  return out
 def evidence(self,ids):
  out=[]
  with store.connect() as c:
   for ident in ids:
    r=c.execute('SELECT * FROM evidence WHERE id=?',(ident,)).fetchone()
    if r:
     body=json.loads(r['body'])
     shared=body['kind'] in ('guideline','policy') and (any(c.get('evidence_id')==ident for c in store.registry('calls')) or any(p.get('evidence_id')==ident for p in store.registry('policies')))
     if shared or store.permitted(self.actor,dict(r)):out.append(body)
  store.audit(self.run_id,self.actor['username'],'connector.evidence',{'ids':ids,'found':[x['id'] for x in out]});return out
 def calculate(self,lines):
  rows=[{**x,'total_inr':x['quantity']*x['unit_inr']} for x in lines]
  result={'lines':rows,'total_inr':sum(x['total_inr'] for x in rows),'currency':'INR','basis':'Integer INR: quantity × unit cost; no implicit tax or overhead.'}
  store.audit(self.run_id,self.actor['username'],'tool.calculate_budget',{'input':lines,'output':result});return result
 def candidates(self,calls,plan,parallel=True):
  def score(c):
   relevance=similarity(embed(plan['area']+' '+plan['title']),embed(c['title']+' '+' '.join(c['areas'])))
   reasons=[]
   if not deadline_open(c):reasons.append('deadline closed or unknown')
   if plan['months']>c['duration_months']:reasons.append('duration exceeds call')
   if c['funding_type']!=plan['funding_type']:reasons.append('funding type mismatch')
   if not relevance:reasons.append('no topical match')
   if plan['mode']=='real' and not call_verified(c):reasons.append('unverified or stale source')
   return {'call':c,'score':round(relevance,4),'rejected':reasons}
  if parallel:
   with ThreadPoolExecutor(max_workers=4) as pool:out=list(pool.map(score,calls))
  else:out=list(map(score,calls))
  out.sort(key=lambda x:(bool(x['rejected']),-x['score'],x['call']['id']))
  store.audit(self.run_id,self.actor['username'],'tool.select_candidates',{'output':[{'id':x['call']['id'],'score':x['score'],'rejected':x['rejected']} for x in out]})
  return out
 def search_literature(self,local_query,public_query,limit=6):
  import copy
  from .literature import lookup
  local=copy.deepcopy(self.read(ToolQuery(resource='publications',query=local_query,limit=limit)))
  external,status=lookup(public_query.strip(),local)
  store.audit(self.run_id,self.actor['username'],'tool.literature_sources',
              {'status':status,'result_ids':[x['id'] for x in local+external]})
  return local+external,status
 def draft_suggestion(self,context):
  from .llm import Gateway,DraftOutput
  return Gateway(self.actor,self.run_id).generate('proposal',context,DraftOutput)
 def answer(self,question,resource='publications',mode='real',use_llm=True):
  from .llm import Gateway,AnswerOutput
  query=re.sub(r'\b(find|show|historical|grants|publications|research|papers|please|about|our|college)\b',' ',question,flags=re.I).strip()
  rows=self.read(ToolQuery(resource=resource,query=query,mode=mode,limit=6))
  sources=[]
  for x in rows:
   sources.append({'id':x['id'],'title':x.get('title',''),'year':x.get('year',''),'abstract':x.get('abstract','')[:1800],'agency':x.get('agency',''),'status':x.get('status',''),'amount_inr':x.get('amount_inr'),'source':x.get('sources',x.get('source',{}))})
  result=Gateway(self.actor,self.run_id).generate('assistant',{'question':question,'sources':sources},AnswerOutput) if use_llm and sources else {'used':False,'mode':'retrieval','notice':'Retrieved evidence only; no LLM answer generated.'}
  if not result.get('used'):result['text']='Found '+str(len(rows))+' matching records. Review the sources below. '+('Historical records are not current funding opportunities.' if resource=='history' else 'The supplied evidence does not establish global novelty.')
  return {'answer':result,'records':rows,'resource':resource}

def demo_calls():
 rows=[]
 fixture=json.loads((store.ROOT/'data/mock/funding_calls_mock.json').read_text())
 for c in fixture['records']:
  rows.append({'id':c['mock_id'],'title':c['call_title'],'agency':c['agency'],'areas':c.get('research_areas',[]),'deadline':c['deadline']+'T23:59:59+05:30','funding_type':'government' if 'government' in c['funding_type'].lower() and 'non-government' not in c['funding_type'].lower() else 'industry','ceiling_inr':c.get('budget_ceiling',0),'duration_months':c.get('duration_months',24),'allowed_categories':{'personnel':4000000,'equipment':1000000,'travel':200000,'consumables':300000,'overheads':200000},'required_documents':['PI_CV'],'eligibility_rules':['SAMPLE: simulated appointment and eligibility only'],'template_sections':['Objectives','Methodology','Timeline'],'source_url':c['source']['source_url'],'locator':c['source']['source_locator'],'excerpt':c['source'].get('supporting_excerpt',''),'mock':True,'verified':False,'policy_id':'SAMPLE-POLICY','evidence_id':'SAMPLE-GUIDELINE'})
 # Explicit, long-lived sandbox fixtures. Original uploaded mocks remain unchanged.
 for i,kind in enumerate(['government','industry','international']):
  rows.append({'id':'SAMPLE-'+kind.upper(),'title':'SAMPLE ONLY · AI, digital health and secure systems research','agency':'Synthetic '+kind.title()+' Research Fund','areas':['Artificial Intelligence','machine learning','cardiovascular monitoring','digital health','cybersecurity','DDoS','agriculture','robotics'],'deadline':'2099-12-31T23:59:59+05:30','funding_type':kind,'ceiling_inr':5000000,'duration_months':36,'allowed_categories':{'personnel':3000000,'equipment':1500000,'travel':200000,'consumables':300000,'overheads':250000},'required_documents':[],'eligibility_rules':['Simulated eligibility only; no actual agency eligibility asserted.'],'template_sections':['Objectives','Methodology','Timeline'],'source_url':'https://example.invalid/grant-office-practice','locator':'Generated sandbox fixture v1','excerpt':'Invented testing rules: maximum INR 50 lakh, up to 36 months; no actual funding opportunity.','mock':True,'verified':False,'policy_id':'SAMPLE-POLICY','evidence_id':'SAMPLE-GUIDELINE'})
 return rows
