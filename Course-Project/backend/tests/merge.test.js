'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('fs');
const os = require('os');
const path = require('path');
process.env.AURA_DATA_DIR = fs.mkdtempSync(path.join(os.tmpdir(), 'grantoffice-merge-'));
process.env.AURA_STEP_DELAY = '0';
process.env.AURA_LLM = 'off';
process.env.MONGODB_URI = '';
const { db } = require('../src/core');
const engine = require('../src/engine');
const { createApp } = require('../src/api');
const research = require('../src/research-sources');
let server, base;
test.before(async () => {
  db.load(); server = createApp().listen(0, '127.0.0.1');
  await new Promise((resolve) => server.once('listening', resolve));
  base = 'http://127.0.0.1:' + server.address().port;
});
test.after(async () => {
  await new Promise((resolve) => server.close(resolve));
  fs.rmSync(process.env.AURA_DATA_DIR, { recursive: true, force: true });
});
async function api(route, { token, method = 'GET', body, actor } = {}) {
  return fetch(base + '/api' + route, { method, headers: {
    'Content-Type': 'application/json', ...(token ? { Authorization: 'Bearer ' + token } : {}),
    ...(actor ? { 'x-actor-id': actor } : {}),
  }, body: body ? JSON.stringify(body) : undefined });
}
async function login(id) {
  const response = await api('/auth/login', { method: 'POST', body: { userId: id, password: 'password123' } });
  assert.equal(response.status, 200); return (await response.json()).token;
}

test('institutional author search is case-insensitive and counts all 109 supplied records', () => {
  const publications = require('../src/college-data').publications;
  const expected = publications.filter((p) => /uday/i.test(p.authors)).map((p) => p.id).sort();
  assert.equal(expected.length, 109);
  for (const query of ['Uday', 'uday', 'UDAY']) {
    const result = research.archiveSearch(query, { field:'authors' });
    assert.equal(result.total, expected.length);
    assert.equal(result.items.length, 20);
    assert.equal(result.displayed, 20);
    assert.equal(result.totalPages, 6);
    assert.ok(result.items.every((p) => p.matchedFields.includes('authors')));
    assert.equal(research.archiveSearch(query).total, expected.length);
  }
});

test('archive pagination includes every matching ID exactly once in stable order', () => {
  const expected = require('../src/college-data').publications.filter((p) => /uday/i.test(p.authors)).map((p) => p.id).sort();
  const ids = [];
  for (let page = 1; page <= 7; page += 1) {
    const result = research.archiveSearch('uday', { page, pageSize:17, field:'authors' });
    assert.equal(result.total, expected.length);
    assert.equal(result.hasNext, page < 7);
    assert.equal(result.hasPrevious, page > 1);
    ids.push(...result.items.map((p) => p.id));
  }
  assert.equal(new Set(ids).size, ids.length);
  assert.deepEqual(ids, expected);
  assert.equal(research.archiveSearch('uday', { page:8, pageSize:17 }).items.length, 0);
  assert.equal(research.archiveSearch('', { pageSize:1000 }).pageSize, 100);
  assert.equal(research.archiveSearch('uday', { page:-1, pageSize:'bad' }).page, 1);
});

test('archive matches normalized names and retains original authors and source references', () => {
  const plain = research.archiveSearch('Uday Kulkarni', { field:'authors', pageSize:100 });
  const punctuated = research.archiveSearch('  UDAY...    KULKARNI  ', { field:'authors', pageSize:100 });
  assert.ok(plain.total > 0);
  assert.deepEqual(punctuated.items.map((p) => p.id), plain.items.map((p) => p.id));
  const record = plain.items.find((p) => p.id === 'PUB-116970');
  const original = require('../src/college-data').publications.find((p) => p.id === record.id);
  assert.equal(record.authorsDisplay, original.authors);
  assert.equal(record.authors[0], 'Uday Kulkarni.');
  assert.equal(record.authors.length, 6);
  assert.deepEqual(record.provenance, original.sources);
  for (const separator of [',', '|', ';']) {
    const publications = require('../src/college-data').publications;
    const field = publications.some((p) => p.authors.includes(separator)) ? 'authors' : 'home_authors';
    const source = publications.find((p) => String(p[field]).includes(separator));
    assert.ok(source, `Catalog fixture contains ${separator} separators`);
    const name = source[field].split(/[,|;]/)[0].trim();
    const result = research.archiveSearch(name, { field, pageSize:100 });
    assert.ok(result.total > 0);
    assert.ok(result.items.every((p) => p.authors.every((author) => !/[,|;]/.test(author))));
  }
});

test('archive title, DOI, home author, venue, year and zero-result searches are accurate', () => {
  const record = require('../src/college-data').publications.find((p) => p.doi && p.venue && p.year && p.home_authors);
  for (const [field, query] of [['title', record.title], ['doi', 'https://doi.org/' + record.doi],
    ['venue', record.venue], ['year', record.year], ['home_authors', record.home_authors.split(/[,|;]/)[0]]]) {
    const result = research.archiveSearch(query, { field, pageSize:100 });
    assert.ok(result.total > 0, field);
    // Walk all pages if a broad venue/year query has more than 100 matches.
    const ids = result.items.map((p) => p.id);
    for (let page = 2; page <= result.totalPages; page += 1) {
      ids.push(...research.archiveSearch(query, { field, pageSize:100, page }).items.map((p) => p.id));
    }
    assert.ok(ids.includes(record.id), field);
  }
  const result = research.archiveSearch('zznonexistentpublication98234zz');
  assert.equal(result.total, 0); assert.equal(result.displayed, 0);
  assert.deepEqual(result.items, []); assert.equal(result.totalPages, 0);
  assert.equal(result.hasNext, false); assert.equal(result.hasPrevious, false);
  assert.equal(research.archiveSearch('...').total, 0);
  assert.equal(research.archiveSearch('').total, 527);
});

test('archive is offline while proposal topic retrieval keeps cosine ranking and threshold', async () => {
  const originalFetch = global.fetch;
  let requests = 0;
  global.fetch = async () => { requests += 1; throw new Error('External request forbidden'); };
  try {
    assert.equal(research.archiveSearch('uday').total, 109);
    assert.deepEqual(research.localSearch('uday'), []);
    const query = 'diabetic retinopathy';
    const results = research.localSearch(query);
    assert.ok(results.length > 0 && results.length <= 8);
    const { tokenize, termFreq, cosine } = require('../src/core').util;
    for (const item of results) {
      const source = require('../src/college-data').publications.find((p) => p.id === item.id);
      const expected = cosine(termFreq(tokenize(query)), termFreq(tokenize(`${source.title} ${source.abstract} ${source.tags}`)));
      assert.equal(item.similarity, expected);
      assert.ok(item.similarity >= 0.12);
    }
    assert.ok(results.every((item, index) => index === 0 || results[index - 1].similarity >= item.similarity));
    assert.deepEqual((await research.search('uday', { key:'' })).items, []);
    assert.equal(requests, 0);
  } finally { global.fetch = originalFetch; }
});

test('archive HTTP endpoint authenticates, paginates and never contacts public providers', async () => {
  assert.equal((await api('/college/publications?q=Uday')).status, 401);
  const token = await login('usr-krishnan');
  // fetch is also the local test client's transport; reject every non-local request.
  const originalFetch = global.fetch;
  let external = 0;
  global.fetch = (url, options) => {
    if (!String(url).startsWith(base + '/')) { external += 1; throw new Error('Public provider forbidden'); }
    return originalFetch(url, options);
  };
  try {
    const first = await (await api('/college/publications?q=Uday&field=authors&page=1&pageSize=20', { token })).json();
    const last = await (await api('/college/publications?q=Uday&field=authors&page=6&pageSize=20', { token })).json();
    assert.equal(first.total, 109); assert.equal(first.displayed, 20);
    assert.equal(last.total, 109); assert.equal(last.displayed, 9); assert.equal(last.hasNext, false);
    assert.ok(first.items.every((p) => p.source === 'College archive'));
    assert.equal(first.sources.openalex, 'not_requested');
    assert.equal(first.sources.crossref, 'not_requested');
    assert.equal((await api('/college/publications?field=unsupported', { token })).status, 400);
    const empty = await (await api('/college/publications?q=zznonexistentpublication98234zz', { token })).json();
    assert.equal(empty.total, 0); assert.equal(empty.displayed, 0);
    assert.equal(external, 0);
  } finally { global.fetch = originalFetch; }
});

test('college API and project metrics retain distinct canonical sources', async () => {
  assert.equal((await api('/college')).status, 401);
  assert.equal((await api('/college/grants')).status, 401);
  const token = await login('usr-krishnan');
  const response = await api('/college', { token });
  assert.equal(response.status, 200);
  const metrics = await response.json();
  assert.equal(metrics.publications, 527);
  assert.equal(metrics.awards, 19); assert.equal(metrics.applications, 2);
  assert.equal(metrics.sanctionedInr, 74489120);
  assert.equal(metrics.requestedInr, 1850000);
  assert.equal(metrics.receivedInr, 17726035); assert.equal(metrics.receivedUnknown, 4);
  assert.equal(metrics.provenanceReferences, 2442);
  assert.ok(metrics.issues.some((i) => i.source === 'GRANT-25' && /ambiguous units/.test(i.message)));
  assert.ok(metrics.issues.some((i) => i.source === 'GRANT-16' && /not yet received/.test(i.message)));
  assert.equal(metrics.publicationReviews[0].id, 'PUB-295052');
  assert.deepEqual(metrics.publicationReviews[0].candidateIds, ['PUB-295528']);
  assert.equal(metrics.reconciliation.combinedSanctionedInr, null);
  const data = await (await api('/college/grants', { token })).json();
  assert.equal(data.awards.length, 19); assert.equal(data.applications.length, 2);
  assert.equal(data.awards.reduce((sum, g) => sum + (g.amount_inr || 0), 0), metrics.sanctionedInr);
  assert.equal(data.awards.reduce((sum, g) => sum + (g.received_inr || 0), 0), metrics.receivedInr);
  assert.ok(data.awards.every((g) => g.source.file && g.source.sheet && g.source.row));
  const register = await (await api('/projects', { token })).json();
  assert.equal(register.projects.length, 30);
  assert.equal(register.college.sanctionedInr, metrics.sanctionedInr);
  assert.ok(register.reconciliation.candidates.some((c) => c.projectId === 'PRJ-2223-01' && c.grantId === 'GRANT-3' && c.differenceInr === -600));
  assert.deepEqual(register.reconciliation.conflicts[0].ids, ['PRJ-2021-02', 'PRJ-2021-07']);
  assert.ok(register.reconciliation.statusConflicts.some((c) => c.projectId === 'PRJ-2122-09' && /cancelled/i.test(c.sourceNote)));
  assert.equal(register.reconciliation.combinedCount, null);
  const publication = require('../src/college-data').catalog.publications.find((p) => /diabetic/i.test(p.title));
  assert.ok(publication);
  assert.ok(research.localSearch(publication.title, 30).some((p) => p.id === publication.id && p.provenance.length));
  const review = await (await api('/college/review', { token })).json();
  assert.equal(review.pending_publications.length, 1);
  assert.equal(review.legacy_evidence.length, 195);
  const previousKey = process.env.OPENALEX_API_KEY;
  delete process.env.OPENALEX_API_KEY;
  try {
    const response = await api('/literature?q=' + encodeURIComponent('Segmentation of Retina Images Using Deep Learning Model and Explainable AI'), { token });
    assert.equal(response.status, 200);
    const result = await response.json();
    assert.equal(result.sources.openalex, 'key_missing');
    const retained = result.items.find((p) => p.id === 'PUB-295528');
    assert.ok(retained && retained.provenance.length >= 5 && retained.identityReview.length === 1);
  } finally {
    if (previousKey === undefined) delete process.env.OPENALEX_API_KEY;
    else process.env.OPENALEX_API_KEY = previousKey;
  }
  assert.equal(research.doiKey(' DOI: https://DX.doi.org/10.1000%2FABC '), '10.1000/abc');
});
test('HTTP identity requires a valid server-side session', async () => {
  assert.equal((await api('/runs', { actor: 'usr-krishnan' })).status, 401);
  assert.equal((await api('/runs', { token: 'aura-tok-usr-krishnan-fake' })).status, 401);
  assert.equal((await api('/auth/login', { method: 'POST', body: { userId: 'usr-krishnan' } })).status, 401);
  const token = await login('usr-suneeta-v-budihal');
  assert.equal((await (await api('/auth/me', { token, actor: 'usr-krishnan' })).json()).user.id, 'usr-suneeta-v-budihal');
  await api('/auth/logout', { token, method: 'POST', body: {} });
  assert.equal((await api('/auth/me', { token })).status, 401);
});
test('faculty cannot read or edit another faculty run', async () => {
  const token = await login('usr-suneeta-v-budihal');
  const other = engine.createRun({ request: 'Example proposal', params: {}, actorId: 'usr-satyadhyan-chickerur' }); db.addRun(other);
  assert.equal((await api('/runs/' + other.id, { token })).status, 404);
  assert.equal((await api('/runs/' + other.id + '/draft', { token, method: 'PUT', body: { sections: [] } })).status, 404);
  const list = await (await api('/runs', { token })).json();
  assert.equal(list.runs.some((run) => run.id === other.id), false);
});
test('project budgets persist without MongoDB and enforce ownership', async () => {
  const token = await login('usr-suneeta-v-budihal');
  const lines = [{ requirement: 'Flow sensor', cost: 12500 }];
  const response = await api('/projects/PRJ-2223-01/budget', { token, method: 'PUT', body: { lines } });
  assert.equal(response.status, 200); assert.equal((await response.json()).project.budgetTotal, 12500);
  delete require.cache[require.resolve('../src/project-store')];
  assert.deepEqual((await require('../src/project-store').getProject('PRJ-2223-01')).budgetLines, lines);
  assert.equal((await api('/projects/PRJ-2324-02/budget', { token, method: 'PUT', body: { lines } })).status, 403);
  assert.equal((await api('/projects/PRJ-2223-01/budget', { token, method: 'PUT', body: { lines: [{ requirement: 'Bad cost', cost: -1 }] } })).status, 422);
});
test('OpenAlex and Crossref deduplicate DOI records and preserve statuses', async () => {
  const calls = [];
  const request = async (url, options) => {
    calls.push({ url, options });
    if (url.startsWith('https://api.openalex.org/')) return { ok: true, json: async () => ({ results: [
      { id: 'https://openalex.org/W100', title: 'Mock loop research', doi: 'https://doi.org/10.1234/test', abstract_inverted_index: { loop: [1], Mock: [0] } },
      { id: 'https://openalex.org/W101', title: 'Duplicate result', doi: 'https://doi.org/10.1234/test' },
    ] }) };
    assert.equal(options.headers.Authorization, undefined);
    return { ok: true, json: async () => ({ message: { DOI: '10.1234/test', publisher: 'Test publisher', 'container-title': ['Test journal'] } }) };
  };
  const result = await research.search('xxyyzz loop', { key: 'test-key', request });
  const item = result.items.find((record) => record.doi === '10.1234/test');
  assert.equal(result.items.filter((record) => record.doi === '10.1234/test').length, 1);
  assert.equal(item.abstract, 'Mock loop'); assert.equal(item.crossref.publisher, 'Test publisher');
  assert.equal(result.sources.openalex, 'ok'); assert.equal(result.sources.crossref, 'ok');
  assert.equal(calls[0].options.headers.Authorization, 'Bearer test-key');
  assert.equal(new URL(calls[0].url).searchParams.get('search'), 'xxyyzz loop');
  assert.equal((await research.search('mock loop', { key: '' })).sources.openalex, 'key_missing');
  assert.equal((await research.search('', { request: () => { throw new Error('unexpected'); } })).sources.openalex, 'not_requested');
});
test('source outages differ from successful zero-result searches', async () => {
  assert.equal((await research.search('xxyyzz', { key: 'test', request: async () => { throw new Error('offline'); } })).sources.openalex, 'unavailable');
  const result = await research.search('xxyyzz', { key: 'test', request: async () => ({ ok: true, json: async () => ({ results: [] }) }) });
  assert.equal(result.sources.openalex, 'no_results');
});
test('local model adapter calls Ollama and handles connection failure', async () => {
  const original = global.fetch; process.env.AURA_LLM = 'on'; const model = require('../src/model');
  try {
    global.fetch = async (url, options) => {
      assert.equal(url, 'http://127.0.0.1:11434/api/chat'); assert.equal(JSON.parse(options.body).model, 'qwen2.5:3b');
      return { ok: true, json: async () => ({ message: { content: '{"paragraphs":[]}' } }) };
    };
    assert.equal((await model.callGroq({ prompt: 'Example', json: true })).success, true);
    global.fetch = async () => { throw new Error('local unavailable'); };
    assert.equal((await model.callGroq({ prompt: 'Example' })).success, false);
  } finally { global.fetch = original; process.env.AURA_LLM = 'off'; }
});
test('public search terms and methodology survive createRun', () => {
  const run = engine.createRun({ request: 'Bench-top mock circulatory loop', params: { researchArea: 'Mock loop pressure and flow measurements', publicLiteratureQuery: 'mock circulatory loop', methodology: 'Calibrate pressure and flow using separate comparison runs.' }, consent: true });
  assert.equal(run.params.publicLiteratureQuery, 'mock circulatory loop'); assert.ok(run.params.methodology.startsWith('Calibrate'));
});

test('approval rejects stale packages and downloads require the owning session', async () => {
  const run = engine.createRun({ request: 'Federated learning for diabetic retinopathy screening in rural primary care.', params: {
    researchArea: 'Federated learning for diabetic retinopathy screening in rural primary care', keywords: ['federated learning','diabetic retinopathy','medical imaging'],
    fundingType: 'government', requestedBudget: 5800000, durationMonths: 36, careerStage: 'associate', institutionType: 'university', humanSubjects: true, sites: 4, sampleSize: 2400,
  }, consent: true, actorId: 'usr-suneeta-v-budihal' });
  db.addRun(run); await engine.execute(run);
  assert.equal(run.status, 'awaiting_review');
  const dean = await login('usr-krishnan');
  assert.equal((await api(`/runs/${run.id}/review`, { token: dean, method: 'POST', body: { decision: 'approve', expectedChecksum: 'stale' } })).status, 409);
  assert.equal((await api(`/runs/${run.id}/files/proposal.md`)).status, 401);
  const owner = await login('usr-suneeta-v-budihal');
  const download = await api(`/runs/${run.id}/files/proposal.md`, { token: owner });
  assert.equal(download.status, 200); assert.match(await download.text(), /proposal|research/i);
  const before = structuredClone(run.draft);
  const edit = await api(`/runs/${run.id}/draft`, { token: owner, method: 'PUT', body: { sections: [
    { key: run.draft.sections[0].key, text: 'A proposed research study with faculty review. '.repeat(100) }, { key: 'unknown', text: 'Invalid edit' },
  ] } });
  assert.equal(edit.status, 422); assert.deepEqual(run.draft, before);
  run.draft.sections[0].paragraphs[0].text += ' A changed package.';
  assert.equal((await api(`/runs/${run.id}/review`, { token: dean, method: 'POST', body: { decision: 'approve', expectedChecksum: run.package.checksum } })).status, 409);
  run.draft = before;
  assert.equal((await api(`/runs/${run.id}/review`, { token: dean, method: 'POST', body: { decision: 'approve', expectedChecksum: run.package.checksum } })).status, 200);
  assert.equal(run.package.agencySubmission.submitted, false);
});
test('bench-loop drafting keeps the faculty engineering scope', async () => {
  const run = engine.createRun({ request: 'Bench-top mock circulatory loop and digital twin.', params: {
    researchArea: 'Bench-top mock circulatory loop and digital twin', keywords: ['engineering','digital twin','AI','health'],
    methodology: 'Use a pump and tubing with calibrated pressure and flow sensors. Reserve independent comparison runs.',
    fundingType: 'government', requestedBudget: 5800000, durationMonths: 36, careerStage: 'associate', institutionType: 'university', humanSubjects: false, sites: 1, sampleSize: 20,
  }, consent: true, actorId: 'usr-suneeta-v-budihal' });
  db.addRun(run); await engine.execute(run);
  assert.equal(run.status, 'awaiting_review');
  const text = run.draft.sections.map((s) => s.paragraphs.map((p) => p.text).join(' ')).join(' ');
  assert.match(text, /pump and tubing with calibrated pressure and flow sensors/);
  assert.doesNotMatch(text, /retinopathy|fundus|SimVascular|Vascular Database|clinical cohort/);
});
