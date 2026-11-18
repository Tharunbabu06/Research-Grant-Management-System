
'use strict';
const crypto=require('crypto');
const hash=value=>crypto.createHash('sha256').update(JSON.stringify(value)).digest('hex');
function fingerprint(run) {return hash({sections:run.draft?.sections,budget:run.budget?.lines,rules:run.budget?.rules,totals:run.budget?.totals,call:run.discovery?.selectedCall,plan:run.plan,documents:run.documents});}
function contextFingerprint(run){return hash({params:run.params,sourceRecords:run.sourceRecords});}
function isApproved(run) {
  if(run.status!=='published'||run.approvals?.decision!=='approved'||run.package?.status!=='approved')return false;
  return run.restoreScope?.exactHistoricalSnapshot ? run.restoreScope.fingerprint===fingerprint(run) && run.restoreScope.contextHash===contextFingerprint(run) : run.package.artifactHash===fingerprint(run) && (!run.package.contextHash || run.package.contextHash===contextFingerprint(run));
}
function canRead(actor,run){return !!actor&&(actor.permissions?.includes('run:read:all')||run.actor?.id===actor.id);}
function activity(directory,person,runs,actor) {
 const linked=runs.filter(r=>directory.resolve(r.actor?.id)?.id===person.id || (r.params?.researcherIds||[]).some(id=>directory.resolve(id)?.id===person.id));
 const visible=linked.filter(r=>canRead(actor,r));
 const proposals=visible.map(r=>({id:r.id,title:r.draft?.title||r.params?.researchArea,status:r.status,budget:r.budget?.formatted?.total||null,
   facultyRole:directory.resolve(r.actor?.id)?.id===person.id?'Owner / PI':'Research collaborator',
   internallyApproved:isApproved(r),awaitingReview:r.status==='awaiting_review',publishedVersion:r.publishedVersion,
   review:r.approvals?{decision:r.approvals.decision,decidedBy:r.approvals.decidedBy,decidedAt:r.approvals.decidedAt}:null,
   versions:(r.versions||[]).map(v=>({v:v.v,at:v.at,status:v.status})),updatedAt:r.updatedAt}));
 return {proposals,proposalCounts:{created:proposals.length,awaitingReview:proposals.filter(p=>p.awaitingReview).length,internallyApproved:proposals.filter(p=>p.internallyApproved).length},
   proposalScope:'Unique visible proposals, not versions; private proposals excluded. Internal approval is not a scholarly publication or funded award.'};
}
function invalidate(run,reason) {
 run.approvals={...(run.approvals||{}),decision:null,decidedBy:null,decidedAt:null,decidedById:null,decidedByEmail:null,notes:null,invalidatedAt:new Date().toISOString(),reason,history:structuredClone(run.approvals?.history||[])};
 run.package=null;run.acceptance=null;run.publishedVersion=null;run.completedAt=null;
 if(run.rollback){run.restoreHistory=run.restoreHistory||[];run.restoreHistory.push(structuredClone(run.rollback));run.rollback=null;}run.restoreScope=null;
 if(run.declaration)run.declaration={...run.declaration,status:'pending',signedBy:null,signedById:null};
 run.validation={...(run.validation||{}),report:null};run.status='changes_requested';run.updatedAt=new Date().toISOString();
}
module.exports={fingerprint,contextFingerprint,isApproved,canRead,activity,invalidate};
