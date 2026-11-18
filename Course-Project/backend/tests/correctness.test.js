 'use strict';
const test=require('node:test'),assert=require('node:assert/strict'),fs=require('fs'),os=require('os'),path=require('path');
const {execFileSync}=require('node:child_process');
const directoryPath=fs.mkdtempSync(path.join(os.tmpdir(),'grantoffice-correctness-test-'));
process.env.AURA_DATA_DIR=directoryPath;process.env.MONGODB_URI='';process.env.MONGO_URI='';process.env.AURA_STEP_DELAY='0';process.env.AURA_LLM='off';
const {db,runtime,tools,config}=require('../src/core'),engine=require('../src/engine'),agents=require('../src/agents');
const {USERS,CALLS}=require('../src/seed'),researchers=require('../src/researcher-directory'),activity=require('../src/proposal-activity');
const arithmetic=require('../src/budget-rules');
const pi=USERS.find(u=>u.id==='usr-saroja-v-siddamal'),dean=USERS.find(u=>u.id==='usr-krishnan');
const params={researchArea:'Federated learning for diabetic retinopathy screening in rural primary care',keywords:['federated learning','diabetic retinopathy'],fundingType:'government',requestedBudget:5800000,durationMonths:36,careerStage:'associate',institutionType:'university',humanSubjects:true,sites:4,sampleSize:2400};
const inputLines=[{requirement:'Personnel',category:'personnel',cost:250000},{requirement:'Equipment',category:'equipment',cost:150000},{requirement:'Consumables',category:'consumables',cost:50000}];
let server,base,token,otherToken,approved;
async function api(route,{method='GET',body,auth=token}={}){return fetch(base+'/api'+route,{method,headers:{'Content-Type':'application/json',...(auth?{Authorization:'Bearer '+auth}:{})},body:body===undefined?undefined:JSON.stringify(body)});}
test.before(async()=>{db.load();server=require('../src/api').createApp().listen(0,'127.0.0.1');await new Promise(r=>server.once('listening',r));base='http://127.0.0.1:'+server.address().port;
 for(const [userId,save]of [[pi.id,t=>token=t],['usr-suneeta-v-budihal',t=>otherToken=t]]){const r=await api('/auth/login',{method:'POST',auth:'',body:{userId,password:'password123'}});assert.equal(r.status,200);save((await r.json()).token);}
 approved=engine.createRun({request:params.researchArea,params,consent:true,actorId:pi.id});db.addRun(approved);await engine.execute(approved);assert.equal(approved.status,'awaiting_review');engine.governance.approveRun(approved,dean,{});
});
test.after(async()=>{await new Promise(r=>server.close(r));});
test('explicit categories reconcile exact fixture, permissions and cap denominators; absent charges stay zero',()=>{
 const lines=inputLines.map(l=>({category:l.category,amount:l.cost}));const rules={overheadPct:15,contingencyPct:5,categoryCaps:{personnel:{pct:50,base:'direct'},equipment:{pct:30,base:'total'}}};
 const t=arithmetic.computeBudget(lines,rules);assert.equal(t.direct,450000);assert.equal(t.overhead,67500);assert.equal(t.contingency,22500);assert.equal(t.total,540000);
 const caps=arithmetic.capReport(lines,rules);assert.equal(caps[0].amount,250000);assert.equal(caps[0].denominator,450000);assert.equal(caps[0].status,'over');assert.equal(caps[1].denominator,540000);assert.equal(caps[1].amount,150000);
 assert.equal(arithmetic.computeBudget(lines,{}).total,450000);assert.equal(arithmetic.computeBudget(lines,{...rules,overheadAllowed:false,contingencyAllowed:false}).total,450000);
 assert.equal(arithmetic.computeBudget([{category:'other',amount:3}],{overheadPct:50}).overhead,2);
 assert.throws(()=>arithmetic.computeBudget([{category:'other',amount:1.5}],{}),/whole INR/);
});
test('faculty input snapshot is preserved; high minimum fails and ceiling alternatives never silently change amounts',async()=>{
 const run=engine.createRun({request:params.researchArea,params:{...params,budgetLines:inputLines,requestedBudget:450000},consent:true,actorId:pi.id});
 const call=structuredClone(CALLS[0]);call.id='TEST-RULES';call.agency='TEST, not an agency policy';call.budgetMin=600000;call.budgetMax=500000;call.budgetRules={overheadPct:15,contingencyPct:5,salaryCapPct:45,equipmentCapPct:40,capBase:'direct'};
 run.discovery={selectedCall:call};run.draft=structuredClone(approved.draft);const original=JSON.stringify(run.inputSnapshot);
 await agents.budget.run(runtime.createContext(run,run.actor));assert.equal(run.budget.totals.total,540000);assert.equal(run.budget.totals.categories.personnel,250000);
 const costs=JSON.stringify(run.budget.lines);agents.budget.fitCeiling(run);agents.budget.enforceCaps(run);assert.equal(JSON.stringify(run.budget.lines),costs);assert.ok(run.budgetAlternatives.length);
 agents.compliance.reevaluate(run);const floor=run.compliance.checks.find(c=>c.id==='chk-budget-floor');assert.equal(floor.status,'fail');assert.equal(floor.severity,'blocking');assert.equal(JSON.stringify(run.inputSnapshot),original);
 assert.ok(run.compliance.checks.filter(c=>c.status==='pass').every(c=>c.remediation===null));
});
test('Saroja documented aliases resolve, Bhusare stays separate, no invented papers, and reviewed overlaps count awards once',()=>{
 const d=researchers.buildDirectory();const person=d.resolve(pi.id);assert.equal(d.resolve('Saroja Siddamal').id,person.id);assert.notEqual(d.resolve('Saroja S Bhusare')?.id,person.id);assert.equal(person.publicationCount,0);
 assert.equal(person.historicalRegisterCount,2);assert.equal(person.fundedAwardCount,2);assert.equal(person.projectCount,2);assert.equal(person.projectRecordIds.length,4);
 assert.equal(d.projectGroups.filter(g=>g.sourceIds.some(id=>person.projectRecordIds.includes(id))).length,2);
 const pair=d.reconciliation.confirmedLinks.find(l=>l.grantId==='GRANT-3');assert.equal(pair.registerInr,1568000);assert.equal(pair.catalogInr,1568600);assert.equal(pair.amountConflict,true);
 const split=researchers.buildDirectory({confirmed:[{id:'a',Name:'Saroja V Siddamal',aliases:['Saroja Siddamal']},{id:'b',Name:'Saroja S Bhusare'}],publications:[],grants:[],projects:[]});assert.notEqual(split.resolve('Saroja Siddamal').id,split.resolve('Saroja S Bhusare').id);
});
test('unique approved proposal counts are independent of versions, papers and awards; private details stay private',async()=>{
 const d=researchers.buildDirectory(),p=d.resolve(pi.id);let x=activity.activity(d,p,[approved],pi);assert.deepEqual(x.proposalCounts,{created:1,awaitingReview:0,internallyApproved:1});
 engine.governance.rollbackRun(approved,1,dean);x=activity.activity(d,p,[approved],pi);assert.equal(approved.versions.length,2);assert.equal(x.proposalCounts.created,1);assert.equal(x.proposalCounts.internallyApproved,1);
 const isolated=researchers.buildDirectory({confirmed:[{id:'TEST-FACULTY',Name:'TEST faculty'}],publications:[],grants:[],projects:[]});const fixture=structuredClone(approved);fixture.actor.id='TEST-FACULTY';const noAwards=activity.activity(isolated,isolated.resolve('TEST-FACULTY'),[fixture],{id:'TEST-FACULTY',permissions:[]});assert.equal(noAwards.proposalCounts.internallyApproved,1);assert.equal(isolated.resolve('TEST-FACULTY').publicationCount,0);assert.equal(isolated.resolve('TEST-FACULTY').fundedAwardCount,0);
 assert.equal(activity.activity(d,p,[approved],USERS.find(u=>u.id==='usr-suneeta-v-budihal')).proposals.length,0);
 const visible=await api('/researchers/'+pi.id,{auth:otherToken});assert.equal((await visible.json()).proposals.length,0);
 const profile=await (await api('/researchers/'+pi.id)).json();assert.equal(profile.proposalCounts.created,1);assert.equal(profile.person.publicationCount,0);
 const projects=await(await api('/projects?my=true')).json();assert.equal(projects.projects.length,2);assert.equal(projects.myResearcher.fundedAwardCount,2);
});
test('restore permission, exact snapshot and immutable original history; edits remove current internal approval',()=>{
 const version=db.state.versions.find(v=>v.runId===approved.id&&v.v===1);const original=JSON.stringify(version);
 assert.throws(()=>engine.governance.rollbackRun(approved,1,pi),/permission/);
 approved.draft.sections[0].paragraphs[0].text='Temporary working change';assert.equal(JSON.stringify(version),original);
 engine.governance.rollbackRun(approved,1,dean);assert.deepEqual(approved.draft,version.snapshot.draft);assert.deepEqual(approved.budget,version.snapshot.budget);assert.equal(activity.isApproved(approved),true);
 const active=structuredClone(approved);active.status='running';assert.throws(()=>engine.governance.rollbackRun(active,1,dean),/active execution/);
 assert.equal(JSON.stringify(version),original);approved.draft.sections[0].paragraphs[0].text+=' changed';assert.equal(activity.isApproved(approved),false);
 engine.governance.rollbackRun(approved,1,dean);
});
test('current and older authenticated DOCX/PDF exports are real formats, immutable and never replaced by working content',async()=>{
 const before=JSON.stringify(approved.package),v1=db.state.versions.find(v=>v.runId===approved.id&&v.v===1),old=JSON.stringify(v1);
 approved.draft.title='Unpackaged working title must not leak';
 for(const format of ['docx','pdf'])for(const suffix of ['', '?version=1']){
  const r=await api('/runs/'+approved.id+'/files/proposal.'+format+suffix);assert.equal(r.status,200);assert.match(r.headers.get('content-type'),format==='pdf'?/application\/pdf/:/wordprocessingml/);
  const bytes=Buffer.from(await r.arrayBuffer());assert.ok(bytes.subarray(0,4).equals(Buffer.from(format==='pdf'?'%PDF':'PK\x03\x04','binary')));
  fs.writeFileSync(path.join(directoryPath,'proposal'+(suffix?'historical':'current')+'.'+format),bytes);
 }
 assert.equal(JSON.stringify(approved.package),before);assert.equal(JSON.stringify(v1),old);
 assert.equal((await api('/runs/'+approved.id+'/files/proposal.docx',{auth:otherToken})).status,404);
 assert.equal((await api('/runs/'+approved.id+'/files/proposal.pdf?version=999')).status,404);
 assert.equal((await api('/runs/'+approved.id+'/files/proposal.pdf',{auth:''})).status,401);
 engine.governance.rollbackRun(approved,1,dean);
});
test('explicit budget correction and alternative acceptance invalidate packages and approval without changing saved inputs or versions',async()=>{
 const before=JSON.stringify(approved.inputSnapshot),version=db.state.versions.find(v=>v.runId===approved.id&&v.v===1),history=JSON.stringify(version);
 const r=await api('/runs/'+approved.id+'/budget',{method:'PUT',body:{lines:inputLines,confirm:true}});assert.equal(r.status,200);const saved=(await r.json()).run;approved=db.getRun(approved.id);
 assert.equal(saved.budget.totals.direct,450000);assert.equal(saved.package,null);assert.equal(saved.approvals.decision,null);assert.equal(activity.isApproved(saved),false);assert.equal(JSON.stringify(saved.inputSnapshot),before);assert.equal(JSON.stringify(version),history);
 assert.equal((await api('/runs/'+approved.id+'/files/proposal.docx')).status,409);
 assert.equal((await api('/runs/'+approved.id+'/budget',{method:'PUT',auth:otherToken,body:{lines:inputLines,confirm:true}})).status,404);
 assert.equal((await api('/runs/'+approved.id+'/budget',{method:'PUT',body:{lines:[{requirement:'Negative',category:'other',cost:-1}],confirm:true}})).status,422);
 agents.budget.fitCeiling(approved); // No mutation even if already within the ceiling.
 const alternative=approved.budgetAlternatives.at(-1);const accept=await api('/runs/'+approved.id+'/budget/accept',{method:'POST',body:{alternativeId:alternative.id,confirm:true}});assert.equal(accept.status,200);assert.equal(approved.package,null);assert.equal(JSON.stringify(approved.inputSnapshot),before);
});
test('atomic writes retry Windows rename locks and surface persistent failures while retaining the last valid state',()=>{
 const atomic=require('../src/atomic-store');const file=path.join(directoryPath,'atomic.json');atomic.writeJson(file,{value:1});const rename=fs.renameSync;let attempts=0;
 try{fs.renameSync=(...args)=>{if(attempts++<2)throw Object.assign(new Error('locked'),{code:'EPERM'});return rename(...args);};atomic.writeJson(file,{value:2});assert.equal(attempts,3);
 fs.renameSync=()=>{throw Object.assign(new Error('locked'),{code:'EPERM'});};assert.throws(()=>atomic.writeJson(file,{value:3}),/last valid file retained/);assert.deepEqual(JSON.parse(fs.readFileSync(file)),{value:2});
 const previous=fs.readFileSync(config.stateFile,'utf8');assert.throws(()=>db.persist(),/write failed/);assert.equal(fs.readFileSync(config.stateFile,'utf8'),previous);
 }finally{fs.renameSync=rename;}
});
test('runs, versions, input/faculty links, audit and project budgets survive a separate process restart',async()=>{
 await require('../src/project-store').saveBudget('PRJ-2223-01',[{requirement:'Saved expense',cost:12000,category:'other'}],pi);db.persist();
 const code=`const {db}=require('./src/core');db.load();(async()=>{const p=await require('./src/project-store').getProject('PRJ-2223-01');console.log('VERIFY:'+JSON.stringify({runs:db.state.runs.length,versions:db.state.versions.length,input:db.state.runs[0].inputSnapshot,owner:db.state.runs[0].actor.id,audit:db.state.audit.length,budget:p.budgetTotal}));})();`;
 const output=execFileSync(process.execPath,['-e',code],{cwd:path.join(__dirname,'..'),env:{...process.env,AURA_DATA_DIR:directoryPath,MONGODB_URI:'',MONGO_URI:''},encoding:'utf8'});const data=JSON.parse(output.split('VERIFY:')[1].trim());
 assert.ok(data.runs);assert.ok(data.versions);assert.ok(data.audit);assert.equal(data.owner,pi.id);assert.equal(data.budget,12000);assert.ok(data.input.params);
});
test('old snapshots do not silently borrow current context during restore or export',async()=>{
 const version=db.state.versions.find(v=>v.runId===approved.id&&v.v===1);
 const legacy={id:'TEST-LEGACY-VERSION',runId:approved.id,v:999,status:'published',checksum:version.checksum,snapshot:structuredClone(version.snapshot)};
 for(const key of ['params','plan','discovery','literature','sourceRecords','documents','validation','acceptance'])delete legacy.snapshot[key];
 db.state.versions.push(legacy);const original=JSON.stringify(legacy);
 const current=db.getRun(approved.id);engine.governance.rollbackRun(current,legacy.id,dean);
 assert.equal(current.params,null);assert.equal(current.discovery,null);assert.ok(current.restoreScope.missingFields.includes('params'));assert.equal(JSON.stringify(legacy),original);
 assert.equal((await api('/runs/'+current.id)).status,200);
 assert.equal((await api('/runs/'+current.id+'/files/proposal.pdf?version=999')).status,200);
 assert.equal((await api('/runs/'+current.id+'/budget',{method:'PUT',body:{lines:inputLines,confirm:true}})).status,409);
 engine.governance.rollbackRun(current,1,dean);
});
test('concurrent edits are rejected and staged budget computation never exposes a partially changed working record',async()=>{
 const id=approved.id,current=db.getRun(id);const before=JSON.stringify(current.budget);const original=agents.budget.run;let unlock,started;
 const gate=new Promise(r=>unlock=r),entered=new Promise(r=>started=r);
 agents.budget.run=async ctx=>{started();await gate;return original(ctx);};
 try{
  const first=api('/runs/'+id+'/budget',{method:'PUT',body:{lines:inputLines,confirm:true}});await entered;
  assert.equal(JSON.stringify(db.getRun(id).budget),before);assert.ok(db.getRun(id).package);
  assert.equal((await api('/runs/'+id+'/budget',{method:'PUT',body:{lines:inputLines,confirm:true}})).status,409);
  unlock();assert.equal((await first).status,200);approved=db.getRun(id);assert.equal(approved.budget.totals.direct,450000);assert.equal(approved.package,null);
 }finally{unlock();agents.budget.run=original;}
});
test('HTTP storage failures are reported instead of acknowledging a save',async()=>{
 const before=await(await api('/projects/PRJ-2223-01')).json();const rename=fs.renameSync;
 try{fs.renameSync=()=>{throw Object.assign(new Error('locked'),{code:'EPERM'});};
 const response=await api('/projects/PRJ-2223-01/budget',{method:'PUT',body:{lines:[{requirement:'Must not save',cost:999,category:'other'}]}});assert.equal(response.status,503);assert.equal((await response.json()).error,'budget_save_failed');
 }finally{fs.renameSync=rename;}
 const after=await(await api('/projects/PRJ-2223-01')).json();assert.deepEqual(after,before);
});
test('malformed store startup refuses an empty overwrite',()=>{
 const invalid=fs.mkdtempSync(path.join(os.tmpdir(),'grantoffice-corrupt-test-'));const file=path.join(invalid,'state.json');fs.writeFileSync(file,'broken original data');
 assert.throws(()=>execFileSync(process.execPath,['-e',"require('./src/core').db.load()"],{cwd:path.join(__dirname,'..'),env:{...process.env,AURA_DATA_DIR:invalid},stdio:'pipe'}));assert.equal(fs.readFileSync(file,'utf8'),'broken original data');
});
test('backend readiness never claims success when its TCP port is already occupied',()=>{
 let failure;try{execFileSync(process.execPath,['index.js'],{cwd:path.join(__dirname,'..'),env:{...process.env,PORT:String(server.address().port),MONGODB_URI:'',MONGO_URI:''},encoding:'utf8'});}catch(error){failure=error;}
 assert.ok(failure);assert.equal(failure.status,1);assert.match(failure.stderr,/EADDRINUSE/);assert.ok(!failure.stdout.includes('GrantOffice listening'));
});
test('provider classifications, bounded retries and Retry-After never leak keys or disable independent Crossref',async()=>{
 const {jsonRequest}=require('../src/provider-http');const fake=(status,headers)=>async()=>({ok:false,status,headers:{get:()=>headers}});
 assert.equal((await jsonRequest('https://example.test',{request:fake(401),sleep:async()=>{}})).diagnostic.code,'authentication_rejected');
 let slept=[],calls=0;let response=await jsonRequest('https://example.test',{request:async()=>{calls++;return{ok:false,status:429,headers:{get:()=> '1'}};},sleep:async n=>slept.push(n)});assert.equal(calls,3);assert.deepEqual(slept,[1000,1000]);assert.equal(response.diagnostic.code,'rate_limited');
 assert.equal((await jsonRequest('https://example.test',{request:async()=>{throw Object.assign(new Error('SECRET'),{name:'TimeoutError'});},sleep:async()=>{}})).diagnostic.code,'timeout');
 response=await jsonRequest('https://example.test',{request:async()=>{throw new Error('SECRET');},sleep:async()=>{}});assert.equal(response.diagnostic.code,'network_error');assert.ok(!JSON.stringify(response).includes('SECRET'));
 assert.equal((await jsonRequest('https://example.test',{request:async()=>({ok:true,json:async()=>{throw new Error('bad');}})})).diagnostic.code,'malformed_response');
 const result=await require('../src/research-sources').search('xxyyzz',{key:'secret',request:async()=>({ok:false,status:403}),sleep:async()=>{}});assert.equal(result.diagnostics.openalex.code,'authentication_rejected');assert.ok(!JSON.stringify(result).includes('secret'));
 const research=require('../src/research-sources'),paper=require('../src/college-data').publications.find(p=>p.doi && p.title);
 const independent=await research.search(paper.title,{key:'secret',sleep:async()=>{},request:async(url)=>url.includes('openalex')?{ok:false,status:401}:{ok:true,json:async()=>({message:{DOI:decodeURIComponent(url.split('/works/')[1])}})}});
 assert.equal(independent.diagnostics.openalex.code,'authentication_rejected');assert.equal(independent.sources.crossref,'ok');assert.ok(independent.items.every(p=>p.source==='College archive'));
 const malformed=await research.search('xxyyzz',{key:'secret',sleep:async()=>{},request:async()=>({ok:true,json:async()=>({results:[{invalid:true}]})})});assert.equal(malformed.diagnostics.openalex.code,'malformed_response');
 assert.equal(require('../src/database').safeError(new Error('authentication failed secret')).code,'authentication_rejected');assert.equal(require('../src/database').safeError(new Error('ENOTFOUND secret')).code,'network_failure');
});
test.after(()=>console.log('CORRECTNESS_ARTIFACTS='+directoryPath));
