# User and demonstration guide

Use a new disposable practice record. Do not alter operational proposals or approved history for a demonstration.

1. Follow [setup](SETUP.md); sign in using classroom authentication. Absent MongoDB must show local JSON and unavailable Mongo counts.
2. Search archive title/author/department/year, inspect source rows and pagination. Offline browsing needs no key; public topic search shows separate provider outcomes.
3. Inspect Projects, My Grants and Faculty Profiles. Distinguish papers, proposal releases and sanctioned awards; inspect conflicts and canonical PI/co-PI links.
4. Create a labeled practice proposal with consent, public keywords, methodology and categorized whole-INR costs. Review/lock its plan. Never use private material as public keywords.
5. Inspect provenance, AI disclosure, saved inputs, charges, cap denominators and checks. Passed checks should not show remediation. Minimum failure must block without increasing costs.
6. Inspect proposed alternatives. Only confirmed acceptance changes working costs, clearing stale package/review and requiring validation again.
7. Use an authorized reviewer. Inspect the package/checksum and record a decision. Internal approval creates no external submission, paper or award.
8. Download current/historical Word/PDF and Markdown/CSV. Check amounts, versions and disclosures.
9. Read Restore's selected version, replacement scope and missing fields. Cancel first. On the disposable record only, confirm as an authorized role and inspect audit/history. Faculty must not gain rollback authority.
10. Reopen the profile. Several versions remain one proposal; revisions invalidate approval. Another faculty user must not see private details.

## Exact TEST calculation without saving a record

From backend:

```sh
node -e "const b=require('./src/budget-rules'); console.log(b.computeBudget([{category:'personnel',amount:250000},{category:'equipment',amount:150000},{category:'consumables',amount:50000}],{overheadPct:15,contingencyPct:5}));"
```

Expected direct/overhead/contingency/total: **450000 / 67500 / 22500 / 540000**. These are TEST rules; real configured practice calls may differ. Regressions separately assert minimum failure and cap bases.

Restart checks use isolated AURA_DATA_DIR/GRANT_DATA_DIR, never deleted working databases. Automated tests already use separate processes/stores. Main sessions expire on restart; sign in again.
