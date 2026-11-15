"""Lab 3: two reusable, schema-validated callable skills."""
from .models import Intake,Plan,SubmissionPackage
from . import store
SPECIALISTS={
 'government':{'focus':'Public value, reproducibility and measurable research outcomes','sections':['Objectives','Methodology','Timeline']},
 'industry':{'focus':'Prototype milestones, adoption assumptions and intellectual-property review','sections':['Objectives','Methodology','Timeline']},
 'international':{'focus':'Collaboration roles, data-transfer review and currency assumptions','sections':['Objectives','Methodology','Timeline']}}
def plan_skill(i:Intake)->Plan:
 d=i.model_dump()
 if not d['objectives']:d['objectives']=[f'Define a measurable baseline for {i.area}.','Develop and compare the proposed approach against the baseline.','Evaluate feasibility, limitations and reproducibility with documented evidence.']
 if not d['methodology']:d['methodology']='Agree data access and evaluation criteria; develop a reproducible baseline; implement the proposed approach; compare on held-out data; document limitations and a reproducible prototype. This is a proposed plan, not an established finding.'
 return Plan(**d)
def format_skill(state:dict)->dict:
 p=Plan(**state['plan'])
 result={'plan':p.model_dump(),'title':p.title,'mode':p.mode,'watermark':'SAMPLE DATA — NOT FOR SUBMISSION' if p.mode in ('sandbox','demo') else 'DRAFT — HUMAN AUTHORIZATION REQUIRED','narrative':state['narrative'],'budget':state['budget'],'compliance':state['checks'],'literature':state['literature'],'evidence':state['evidence'],'call':state.get('selected_call'),'plan_hash':state['plan_hash'],'specialist':SPECIALISTS[p.funding_type],'limitations':state.get('limitations',[]),'llm':state.get('llm',{})}

 return SubmissionPackage(**result).model_dump()
