from typing import Literal,Any
from pydantic import BaseModel,Field,ConfigDict,field_validator
class Strict(BaseModel):
 model_config=ConfigDict(extra='forbid')
 @field_validator('mode',check_fields=False,mode='before')
 @classmethod
 def legacy_mode(cls,v):return 'sandbox' if v=='demo' else v
class Login(Strict):
 username:str=Field(min_length=1,max_length=100)
 password:str=Field(min_length=1,max_length=200)
 @field_validator('username')
 @classmethod
 def normalized(cls,value):return value.strip().lower()
class BudgetLine(Strict):
 category:Literal['personnel','equipment','travel','consumables','overheads']
 description:str=Field(min_length=3,max_length=300)
 quantity:int=Field(ge=1,le=10000)
 unit_inr:int=Field(ge=0,le=100000000)
 basis:str=Field(min_length=5,max_length=500)
class Intake(Strict):
 prompt:str=Field(min_length=5,max_length=4000)
 title:str=Field(min_length=8,max_length=200)
 area:str=Field(min_length=3,max_length=300)
 funding_type:Literal['government','industry','international']='government'
 mode:Literal['sandbox','real']='real'
 consent:bool=False
 months:int=Field(default=12,ge=1,le=120)
 call_id:str=''
 objectives:list[str]=Field(default_factory=list,max_length=10)
 methodology:str=Field(default='',max_length=6000)
 lines:list[BudgetLine]=Field(default_factory=list,max_length=40)
 evidence_ids:list[str]=Field(default_factory=list,max_length=30)
 eligibility_note:str=Field(default='',max_length=2000)
 ethics_required:bool=False
 ethics_note:str=Field(default='',max_length=2000)
 public_literature_query:str=Field(default='',max_length=200)
class Plan(Strict):
 title:str
 area:str
 funding_type:str
 mode:str
 months:int
 call_id:str
 objectives:list[str]
 methodology:str
 lines:list[BudgetLine]
 consent:bool
 evidence_ids:list[str]
 eligibility_note:str
 ethics_required:bool
 ethics_note:str
 public_literature_query:str=''
 prompt:str
class ToolQuery(Strict):
 resource:Literal['publications','history','calls','policies','evidence','prior']
 query:str=Field(default='',max_length=500)
 tag:str=''
 mode:Literal['sandbox','real']='real'
 limit:int=Field(default=10,ge=1,le=100)
class Decision(Strict):
 action:Literal['approve','changes','reject']
 note:str=Field(min_length=5,max_length=3000)
 expected_hash:str
class RuleAssessment(Strict):
 status:Literal['pass','fail','unknown']
 evidence_id:str=''
 note:str=Field(min_length=5,max_length=1000)

class DraftReview(Strict):
 kind:Literal['pi','eligibility']
 expected_hash:str
 note:str=Field(min_length=5,max_length=3000)
 rules:dict[str,RuleAssessment]=Field(default_factory=dict)

class Revision(Strict):
 evidence_ids:list[str]|None=Field(default=None,max_length=30)
 narrative:str=Field(min_length=30,max_length=18000)
 lines:list[BudgetLine]=Field(min_length=1,max_length=40)
 note:str=Field(min_length=5,max_length=2000)
class Call(Strict):
 id:str=Field(pattern=r'^[A-Za-z0-9_-]{3,80}$')
 title:str=Field(min_length=8,max_length=300)
 agency:str=Field(min_length=3,max_length=200)
 funding_type:Literal['government','industry','international']
 areas:list[str]=Field(min_length=1,max_length=20)
 deadline:str
 ceiling_inr:int=Field(gt=0)
 duration_months:int=Field(ge=1,le=120)
 allowed_categories:dict[str,int]
 required_documents:list[str]
 eligibility_rules:list[str]=Field(min_length=1)
 template_sections:list[str]=Field(min_length=3)
 source_url:str
 locator:str=Field(min_length=3)
 excerpt:str=Field(min_length=20,max_length=15000)
 evidence_id:str
 policy_id:str
class Policy(Strict):
 id:str=Field(pattern=r'^[A-Za-z0-9_-]{3,80}$')
 title:str
 evidence_id:str
 rules:str=Field(min_length=20,max_length=10000)
class Evidence(Strict):
 title:str=Field(min_length=3,max_length=200)
 kind:Literal['guideline','policy','PI_CV','eligibility','ethics','narrative_review','other']
 text:str=Field(min_length=20,max_length=100000)
 source_url:str=Field(default='',max_length=1000)
 locator:str=Field(min_length=3,max_length=300)
class UserCreate(Strict):
 username:str=Field(pattern=r'^[a-zA-Z0-9_.-]{3,50}$')
 name:str=Field(min_length=3,max_length=100)
 password:str=Field(min_length=12,max_length=200)
 role:Literal['faculty','hod','research_office','dean']
 department:str=Field(min_length=2,max_length=80)
class PasswordChange(Strict):
 current:str
 new:str=Field(min_length=12,max_length=200)

class ResetPassword(Strict):
 password:str=Field(min_length=12,max_length=200)
class LLMConfig(Strict):
 provider:Literal['auto','ollama','template']='auto'
 model:str=Field(default='qwen2.5:3b',pattern=r'^[a-zA-Z0-9][a-zA-Z0-9._:/-]{0,100}$')
class AssistantRequest(Strict):
 question:str=Field(min_length=3,max_length=2000)
 resource:Literal['publications','history','calls']='publications'
 mode:Literal['sandbox','real']='real'
 use_llm:bool=True

class BudgetResult(Strict):
 lines:list[dict]
 total_inr:int=Field(ge=0)
 currency:Literal['INR']
 basis:str
class CheckResult(Strict):
 name:str
 passed:bool
 detail:str
class SubmissionPackage(Strict):
 plan:Plan
 title:str
 mode:Literal['real','sandbox']
 watermark:str
 narrative:str=Field(min_length=30)
 budget:BudgetResult
 compliance:list[CheckResult]
 literature:list[dict]
 evidence:list[dict]
 call:dict|None
 plan_hash:str
 specialist:dict
 limitations:list[str]
 llm:dict
