'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('fs');
const os = require('os');
const path = require('path');
const { execFileSync } = require('node:child_process');
process.env.AURA_DATA_DIR = fs.mkdtempSync(path.join(os.tmpdir(), 'grantoffice-researchers-'));
process.env.AURA_STEP_DELAY = '0';
process.env.AURA_LLM = 'off';
process.env.MONGODB_URI = '';
const { buildDirectory, currentDirectory, normalize, validateSelection } = require('../src/researcher-directory');
const college = require('../src/college-data');
const { db } = require('../src/core');
const { createApp } = require('../src/api');
const database = require('../src/database');
let server, base, token;
test.before(async () => {
  db.load(); server = createApp().listen(0, '127.0.0.1');
  await new Promise((resolve) => server.once('listening', resolve));
  base = 'http://127.0.0.1:' + server.address().port;
  const response = await request('/auth/login', { method:'POST', body:{ userId:'usr-suneeta-v-budihal', password:'password123' } });
  assert.equal(response.status, 200); token = (await response.json()).token;
});
test.after(async () => {
  await new Promise((resolve) => server.close(resolve));
  fs.rmSync(process.env.AURA_DATA_DIR, { recursive:true, force:true });
});
function request(route, { method = 'GET', body, authenticated = false } = {}) {
  return fetch(base + '/api' + route, { method, headers:{ 'Content-Type':'application/json',
    ...(authenticated ? { Authorization:'Bearer ' + token } : {}) }, body:body ? JSON.stringify(body) : undefined });
}

test('source-backed researchers are distinct and publication counts use resolved full identities', () => {
  const d = buildDirectory();
  const kulkarni = d.resolve('Uday Kulkarni'), muddapur = d.resolve('Uday Muddapur');
  assert.ok(kulkarni?.eligibleForProposal && muddapur?.eligibleForProposal);
  assert.notEqual(kulkarni.id, muddapur.id);
  assert.ok(kulkarni.provenance.some((p) => p.kind === 'faculty_export_home_author'));
  assert.ok(muddapur.provenance.some((p) => p.kind === 'college_investigator'));
  for (const person of [kulkarni, muddapur]) {
    const expected = college.publications.filter((p) => [p.authors, p.home_authors].some((value) =>
      value.split(/[,;|]/).some((name) => normalize(name) === normalize(person.Name)))).map((p) => p.id).sort();
    assert.deepEqual(person.publicationIds, expected);
    assert.equal(person.publicationCount, expected.length);
  }
  assert.equal(kulkarni.projectCount, 0);
  const grants = college.catalog.grants.filter((g) => g.investigators.split(/[,;|]/).some((name) => normalize(name) === normalize(muddapur.Name)));
  assert.equal(muddapur.projectCount, grants.filter((g) => g.status === 'Historical award').length);
  assert.deepEqual(muddapur.projectRecordIds, grants.map((g) => g.id).sort());
  assert.ok(kulkarni.publicationCount < require('../src/research-sources').archiveSearch('uday').total);
});

test('home-author students and external coauthors do not acquire faculty or proposal eligibility', () => {
  const input = { confirmed:[{ id:'faculty-known', Name:'Dr. Mira Rao', aliases:['M Rao'], Dept:'Science' }],
    projects:[], grants:[], publications:[{ id:'P1', authors:'Mira Rao|Student Person|External Collaborator',
      home_authors:'Mira Rao;Student Person', department:'Science', sources:[{ file:'Student Papers.csv', sheet:'Students', row:2 }] }] };
  const d = buildDirectory(input);
  assert.equal(d.resolve('Mira Rao').id, 'faculty-known');
  assert.equal(d.resolve('Student Person').eligibleForProposal, false);
  assert.equal(d.resolve('Student Person').confirmedFaculty, false);
  assert.equal(d.resolve('External Collaborator'), null);
  assert.ok(d.unresolved.some((row) => row.name === 'External Collaborator' && row.recordId === 'P1'));
  assert.deepEqual(d.search('', true).map((p) => p.id), ['faculty-known']);
  assert.throws(() => validateSelection(d, [d.resolve('Student Person').id]), /eligible institutional/);
  assert.throws(() => validateSelection(d, ['nonexistent']), /eligible institutional/);
});

test('aliases and case resolve consistently, while confirmed homonyms remain ambiguous', () => {
  const d = buildDirectory();
  const person = d.people.find((p) => p.confirmedFaculty && p.aliases.some((name) => normalize(name) !== normalize(p.Name)));
  const alias = person.aliases.find((name) => normalize(name) !== normalize(person.Name));
  assert.equal(d.resolve(alias.toUpperCase()).id, person.id);
  assert.ok(d.search(alias.toUpperCase(), true).some((p) => p.id === person.id));
  assert.equal(d.resolve('UDAY KULKARNI').id, d.resolve('Uday Kulkarni').id);
  const ambiguous = buildDirectory({ confirmed:[
    { id:'same-1', Name:'Alex Rao', email:'one@example.test' },
    { id:'same-2', Name:'Alex Rao', email:'two@example.test' },
  ], publications:[], grants:[], projects:[] });
  assert.equal(ambiguous.people.length, 2);
  assert.equal(ambiguous.resolve('Alex Rao'), null);
  assert.ok(ambiguous.unresolved.some((p) => p.kind === 'ambiguous_alias'));
});

test('source identity IDs remain resolvable after later faculty confirmation', () => {
  const source = { projects:[], grants:[], publications:[{ id:'SOURCE-PUB', authors:'Lila Sen', home_authors:'Lila Sen',
    department:'Science', sources:[{ file:'Faculty.csv', sheet:'Faculty', row:2 }] }] };
  const before = buildDirectory({ ...source, confirmed:[] });
  const savedId = before.resolve('Lila Sen').id;
  const after = buildDirectory({ ...source, confirmed:[{ id:'existing-confirmed-id', Name:'Dr. Lila Sen' }] });
  assert.equal(after.people.length, 1);
  assert.equal(after.resolve(savedId).id, 'existing-confirmed-id');
  assert.ok(after.resolve(savedId).idAliases.includes(savedId));
  assert.deepEqual(validateSelection(after, [savedId]), [savedId]);
  assert.deepEqual(validateSelection(after, [savedId, 'existing-confirmed-id']), [savedId]);
});

test('rebuilding and active-store synchronization are idempotent and never mutate accounts or catalogs', async () => {
  const beforeCatalog = JSON.stringify(college.catalog), beforeUsers = JSON.stringify(database.SEED_USERS);
  const first = await currentDirectory(), second = await currentDirectory();
  assert.deepEqual(second.people, first.people);
  assert.deepEqual(second.projectRecords, first.projectRecords);
  assert.equal(new Set(first.people.map((p) => p.id)).size, first.people.length);
  assert.equal(new Set(first.projectRecords.map((p) => p.id)).size, first.projectRecords.length);
  assert.equal(JSON.stringify(college.catalog), beforeCatalog);
  assert.equal(JSON.stringify(database.SEED_USERS), beforeUsers);
  assert.ok(first.people.every((p) => !('permissions' in p) && !('password' in p)));
});

test('exact grant/register signatures share a project count while all original references remain', () => {
  const d = buildDirectory({ confirmed:[], publications:[],
    projects:[{ id:'REGISTER-1', title:'A recorded project', year:'2024', pi:['Dr. Mira Rao'], coPIs:[], agency:'Agency', amountLakh:1 }],
    grants:[{ id:'AWARD-1', title:'A recorded project', year:'2024', investigators:'Mira Rao', agency:'Agency', amount_inr:100000, status:'Historical award' },
      { id:'APPLICATION-1', title:'A recorded project', year:'2024', investigators:'Mira Rao', agency:'Agency', amount_inr:100000, status:'Applied (outcome unknown)' }] });
  const person = d.resolve('Mira Rao');
  assert.equal(person.projectCount, 1);
  assert.equal(person.applicationCount, 1);
  assert.deepEqual(person.projectRecordIds, ['APPLICATION-1', 'AWARD-1', 'REGISTER-1']);
  assert.ok(d.projectGroups.some((g) => g.sourceIds.includes('REGISTER-1') && g.sourceIds.includes('AWARD-1') && !g.sourceIds.includes('APPLICATION-1')));
  assert.equal(d.reconciliation.confirmedLinks.length, 1);
});

test('connected directory reads existing faculty and active project rows without creating User records', async () => {
  const Project = require('../src/models/Project');
  const originals = { connected:database.isConnected, users:database.User.find, projects:Project.find, create:database.User.create };
  let writes = 0;
  try {
    database.isConnected = () => true;
    database.User.find = () => ({ lean:async () => [{ userId:'existing-faculty', Name:'Prof. Lila Sen', Dept:'Science', email:'lila@example.test' }] });
    Project.find = () => ({ sort:() => ({ lean:async () => [{ projectId:'DB-PROJECT', title:'Stored project', pi:['Lila Sen'], coPIs:[], year:'2024', agency:'Agency', amountLakh:1, approved:true, status:'approved', budgetTotal:10 }] }) });
    database.User.create = () => { writes += 1; throw new Error('Directory cannot create accounts'); };
    const d = await currentDirectory();
    assert.equal(d.resolve('LILA SEN').id, 'existing-faculty');
    assert.equal(d.resolve('Lila Sen').confirmedFaculty, true);
    assert.ok(d.projectRecords.some((p) => p.id === 'DB-PROJECT' && p.researcherIds.includes('existing-faculty') && p.budgetTotal === 10));
    assert.equal(d.projectRecords.filter((p) => p.recordKind === 'historical_register').length, 1);
    assert.equal(writes, 0);
  } finally {
    database.isConnected = originals.connected; database.User.find = originals.users;
    Project.find = originals.projects; database.User.create = originals.create;
  }
});

test('project lookup includes PI, co-investigators, agency and record ID without publication-derived projects', async () => {
  const d = await currentDirectory();
  const person = d.resolve('Uday Muddapur');
  const linked = d.filterProjects(d.projectRecords, { faculty:person.id });
  assert.ok(linked.length > 0 && linked.every((p) => p.recordKind === 'sanctioned_award'));
  assert.deepEqual(d.filterProjects(d.projectRecords, { q:'UDAY MUDDAPUR' }).map((p) => p.id), linked.map((p) => p.id));
  assert.deepEqual(d.filterProjects(d.projectRecords, { faculty:d.resolve('Uday Kulkarni').id }), []);
  const withCoPI = d.projectRecords.find((p) => p.coPIs.length);
  for (const q of [withCoPI.id, withCoPI.coPIs[0], withCoPI.agency]) {
    assert.ok(d.filterProjects(d.projectRecords, { q }).some((p) => p.id === withCoPI.id));
  }
  const aliasPerson = d.people.find((p) => p.reviewProjectIds.length > 0 && p.aliases.length > 1);
  assert.ok(d.filterProjects(d.projectRecords, { q:aliasPerson.aliases[0].toUpperCase() }).length > 0);
  assert.equal(aliasPerson.projectCount, null); // Unresolved overlaps do not inflate unique totals.
  assert.ok(d.projectRecords.every((p) => !p.id.startsWith('PUB-')));
  const applications = d.projectRecords.filter((p) => p.recordKind === 'application');
  assert.equal(applications.length, college.applications.length);
});

test('faculty/profile/project endpoints use the researcher directory and account endpoints remain separate', async () => {
  assert.equal((await request('/researchers')).status, 401);
  const profiles = await (await request('/researchers?q=UDAY', { authenticated:true })).json();
  const choices = await (await request('/faculties?q=uday', { authenticated:true })).json();
  const d = buildDirectory();
  for (const name of ['Uday Kulkarni', 'Uday Muddapur']) {
    const person = d.resolve(name);
    assert.ok(profiles.people.some((p) => p.id === person.id));
    assert.ok(choices.faculties.some((p) => p.id === person.id));
    const response = await request('/researchers/' + person.id, { authenticated:true });
    assert.equal(response.status, 200);
    const detail = await response.json();
    assert.equal(detail.person.publicationCount, detail.publications.length);
    assert.equal(detail.person.projectCount, person.projectCount);
  }
  const missing = d.resolve('Uday Kulkarni');
  const empty = await (await request('/projects?faculty=' + missing.id, { authenticated:true })).json();
  assert.equal(empty.projects.length + empty.catalogProjects.length, 0);
  const result = await (await request('/projects?q=' + encodeURIComponent('Uday Muddapur'), { authenticated:true })).json();
  assert.ok(result.catalogProjects.some((p) => p.researcherIds.includes(d.resolve('Uday Muddapur').id)));
  assert.equal(result.projects.length, 0);
  const users = await (await request('/users')).json();
  const accountIds = new Set(users.users.map((u) => u.id));
  assert.equal(accountIds.has(missing.id), false);
  assert.equal((await request('/auth/login', { method:'POST', body:{ userId:missing.id, password:'password123' } })).status, 401);
});

test('faculty selection survives HTTP creation, disk persistence and a fresh-process reload without changing owner permissions', async () => {
  const d = await currentDirectory();
  const selected = [d.resolve('Uday Kulkarni').id, d.resolve('Uday Muddapur').id];
  const body = { request:'Federated learning for diabetic retinopathy screening in rural primary care.', consent:true,
    params:{ researcherIds:selected, researchArea:'Federated learning for diabetic retinopathy screening in rural primary care',
      keywords:['federated learning', 'diabetic retinopathy', 'medical imaging'], fundingType:'government',
      requestedBudget:5800000, durationMonths:36, careerStage:'associate', institutionType:'university', humanSubjects:true, sites:4, sampleSize:2400 } };
  const response = await request('/runs', { authenticated:true, method:'POST', body });
  assert.equal(response.status, 201);
  const created = (await response.json()).run;
  assert.deepEqual(created.params.researcherIds, selected);
  assert.equal(created.actor.id, 'usr-suneeta-v-budihal');
  assert.equal(created.actor.role, 'faculty');
  const bad = await request('/runs', { authenticated:true, method:'POST', body:{ ...body, params:{ ...body.params, researcherIds:['unknown-profile'] } } });
  assert.equal(bad.status, 422);
  const deadline = Date.now() + 15000;
  while (!['awaiting_review', 'needs_human', 'failed'].includes(db.getRun(created.id).status) && Date.now() < deadline) {
    await new Promise((resolve) => setTimeout(resolve, 25));
  }
  assert.equal(db.getRun(created.id).status, 'awaiting_review');
  const fetched = await (await request('/runs/' + created.id, { authenticated:true })).json();
  assert.deepEqual(fetched.run.params.researcherIds, selected);
  assert.deepEqual(fetched.run.params.researcherSelection.map((p) => p.id), selected);
  const script = 'const {db}=require("./src/core");db.load();console.log(JSON.stringify(db.getRun(process.argv[1]).params.researcherIds));';
  const reloaded = JSON.parse(execFileSync(process.execPath, ['-e', script, created.id], { cwd:path.resolve(__dirname, '..'), encoding:'utf8', env:process.env }));
  assert.deepEqual(reloaded, selected);
  assert.equal(validateSelection(d, undefined, ['previously-saved-id'])[0], 'previously-saved-id');
  assert.equal((await request('/runs/' + created.id + '/review', { authenticated:true, method:'POST', body:{ decision:'approve', expectedChecksum:fetched.run.package.checksum } })).status, 403);
});
