"""Run isolated acceptance tests and build an evidence-backed report for all fourteen software labs."""
from pathlib import Path
import subprocess,sys,json,xml.etree.ElementTree as ET,platform
from datetime import datetime,timezone
root=Path(__file__).resolve().parents[1];result=root/'docs/acceptance-results.xml'
if '--report-only' not in sys.argv:
 completed=subprocess.run([sys.executable,'-m','pytest','-q','--junitxml='+str(result)],cwd=root)
 if completed.returncode:raise SystemExit('Tests failed. The prior verification report has not been overwritten. Review the test output.')
tree=ET.parse(result);tests={x.attrib['name']:len(x.findall('failure'))+len(x.findall('error'))+len(x.findall('skipped'))==0 for x in tree.findall('.//testcase')}
entries=[
(1,'Planning and revision','Clarify missing inputs, preview objectives and revise before locking.',['test_clarifying_loop','test_two_reusable_plans'],''),
(2,'Typed tool use','Evidence queries and integer-INR calculations use governed tools.',['test_import_provenance_and_normalization','test_schema_negative_cost'],''),
(3,'Reusable skills','Typed planning and package-formatting skills work across topics and reject invalid outputs.',['test_two_reusable_plans','test_formatter_rejects_invalid_package_schema'],''),
(4,'Memory and retrieval','Checkpoint state is separate from tagged, similarity-ranked institutional history.',['test_tag_and_similarity_retrieval','test_persistent_checkpoint_reloads'], 'Similarity uses lexical hashing embeddings; full-text scientific review is still required.'),
(5,'Governed connector','Authenticated typed endpoints and scoped evidence access centralize source retrieval.',['test_anonymous_cannot_read','test_cross_department_denied','test_attachment_and_scope','test_raw_grant_rows_require_office_role'],'MCP-style interface; not an MCP wire-protocol server.'),
(6,'Runtime and recovery','Persist execution state, audit actions and recover the checkpoint in a new process.',['test_checkpoint_survives_new_process','test_audit_hash_chain'],''),
(7,'Executable node graph','Run discovery, literature, drafting, budget, compliance, validation and human review.',['test_workflow_review_approval_export','test_full_graph_uses_structured_llm'],'LLM success here uses controlled HTTP response fixtures; verify an installed model using Check model response.'),
(8,'Parallel work and merge','Both graph branches execute concurrently and candidate ranking matches serial scoring.',['test_both_parallel_stages_really_overlap','test_parallel_and_serial_candidate_quality'],'Concurrency is verified. The earlier seven-item CPU benchmark was slower with threads; production latency improvement is not asserted.'),
(9,'Evidence grounding','Retain citation provenance and reject unknown model-generated evidence IDs.',['test_llm_hallucinated_citation_rejected_with_bounded_retry','test_real_evidence_workflow_and_immutable_registry','test_public_literature_uses_openalex_and_crossref','test_literature_outage_preserves_local_records'],'Citations are structurally checked; authenticity, scientific truth and novelty require named-human review.'),
(10,'Diagnosis and bounded repair','Repair a miscomputed total without changing original costs; escalate unrepairable evidence failures.',['test_targeted_budget_repair','test_repair_is_bounded_and_only_total_fault_is_repairable','test_llm_malformed_json_then_repair'],''),
(11,'Tested acceptance gate','Reject plan drift and invalid budgets; build no package until every required check passes.',['test_plan_drift_blocks_validation','test_budget_ceiling_blocks_review','test_no_real_data_no_real_release'],''),
(12,'Governance and rollback','Enforce reviewer roles, exact-package approval, revision invalidation and restored-version exports.',['test_hash_bound_approval','test_changes_and_revision_invalidate','test_password_reset_preserves_records_and_revokes_sessions'],''),
(13,'Funding-profile specialists','Use government, industry and international framing with selected-call numerical requirements.',['test_specialist_profiles[industry]','test_specialist_profiles[international]'],'Actual agency norms and required forms must be entered from official sources.'),
(14,'Integrated office workflow','Complete the authenticated create, validate, review and export cycle.',['test_workflow_review_approval_export','test_real_evidence_workflow_and_immutable_registry','test_sample_package_never_claims_official_authorization'],'Software integration is tested. College acceptance on a genuine current call, live model quality, native Windows deployment and actual agency submission are not certified by automated tests.')]
labs=[]
for n,title,behavior,names,limit in entries:
 passed=all(tests.get(name,False) for name in names)
 labs.append({'number':n,'title':title,'behavior':behavior,'software_passed':passed,'evidence':'; '.join(names),'limit':limit})
report={'generated_at':datetime.now(timezone.utc).isoformat(),'environment':platform.system()+' · Python '+platform.python_version(),'tests_passed':sum(tests.values()),'tests_total':len(tests),'summary':f'{sum(tests.values())}/{len(tests)} automated tests passed. All fourteen software capabilities are mapped below; institutional dependencies are listed separately.','labs':labs,'live_llm_inference_verified_here':False}
if not all(x['software_passed'] for x in labs):raise SystemExit('Lab mapping contains missing/failed checks; report was not written.')
(root/'docs/lab_verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(report['summary'])
