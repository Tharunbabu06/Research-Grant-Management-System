'use strict';

const { tokenize, cosine, termFreq } = require('./core').util;
const { catalog, publications } = require('./college-data');
function doiKey(doi) {
  let value = String(doi || '');
  try { value = decodeURIComponent(value); } catch { /* Keep malformed escapes as source evidence. */ }
  return value.trim().toLowerCase().replace(/^doi:\s*/, '').replace(/^https?:\/\/(dx\.)?doi\.org\//, '').trim();
}

const authorNames = (value) => String(value || '').split(/[,|;]/).map((name) => name.trim()).filter(Boolean);
const normalizeArchiveText = (value) => String(value || '').normalize('NFKC').toLowerCase()
  .replace(/[^\p{L}\p{N}]+/gu, ' ').trim();

function collegeRecord(entry) {
  return {
    id:entry.id, title:entry.title, authors:authorNames(entry.authors), authorsDisplay:entry.authors,
    home_authors:entry.home_authors, year:entry.year, venue:entry.venue, doi:doiKey(entry.doi),
    abstract:entry.abstract, source:'College archive', evidenceLevel:entry.abstract ? 'abstract' : 'metadata',
    provenance:entry.sources, conflicts:entry.conflicts, identityReview:entry.identityReview, retrieval:'college',
  };
}

// Archive browsing is metadata matching, not scientific relevance retrieval.
// This synchronous path never calls OpenAlex, Crossref or any other provider.
function archiveSearch(query, { page = 1, pageSize = 20, field = 'all' } = {}) {
  const fields = ['title', 'authors', 'home_authors', 'doi', 'venue', 'year'];
  if (field !== 'all' && !fields.includes(field)) {
    throw Object.assign(new Error('Unsupported archive search field'), { status:400 });
  }
  const positiveInteger = (value, fallback) => Number.isSafeInteger(Number(value)) && Number(value) > 0 ? Number(value) : fallback;
  page = positiveInteger(page, 1);
  pageSize = Math.min(positiveInteger(pageSize, 20), 100);
  const text = String(query || '').trim().slice(0, 200);
  const selectedFields = field === 'all' ? fields : [field];
  const matches = publications.filter((entry) => !entry.mock).map((entry) => {
    const matchedFields = selectedFields.filter((name) => {
      const needle = normalizeArchiveText(name === 'doi' ? doiKey(text) : text);
      if (!needle) return false;
      const values = name === 'authors' || name === 'home_authors' ? authorNames(entry[name]) : [entry[name]];
      return values.some((value) => normalizeArchiveText(name === 'doi' ? doiKey(value) : value).includes(needle));
    });
    return { entry, matchedFields };
  }).filter(({ matchedFields }) => !text || matchedFields.length)
    .sort((a, b) => a.entry.id < b.entry.id ? -1 : a.entry.id > b.entry.id ? 1 : 0);
  const total = matches.length;
  const offset = (page - 1) * pageSize;
  const items = matches.slice(offset, offset + pageSize).map(({ entry, matchedFields }) => ({ ...collegeRecord(entry), matchedFields }));
  return { items, total, displayed:items.length, page, pageSize, totalPages:Math.ceil(total / pageSize),
    hasNext:offset + items.length < total, hasPrevious:page > 1 && total > 0,
    query:text, field, source:'College archive', sources:{ college:total, openalex:'not_requested', crossref:'not_requested' } };
}

// Proposal/topic retrieval intentionally excludes author, venue and year matches.
// Retain its cosine threshold and top-eight default independently of archive browsing.
function localSearch(query, limit = 8) {
  const q = termFreq(tokenize(query));
  return publications.filter((entry) => !entry.mock).map((entry) => {
    const score = cosine(q, termFreq(tokenize(`${entry.title} ${entry.abstract} ${entry.tags}`)));
    return { ...entry, score };
  }).filter((entry) => entry.score >= 0.12).sort((a, b) => b.score - a.score).slice(0, limit).map((entry) => ({
    ...collegeRecord(entry),
    tags: tokenize(query).filter((word) => tokenize(entry.title + ' ' + entry.abstract).includes(word)),
    source: 'College archive', evidenceLevel: entry.abstract ? 'abstract' : 'metadata',
    provenance: entry.sources, conflicts:entry.conflicts, identityReview:entry.identityReview,
    similarity: entry.score, retrieval: 'college',
  }));
}

async function search(query, { request = fetch, key = process.env.OPENALEX_API_KEY, sleep } = {}) {
  const text = String(query || '').trim().slice(0, 200);
  const items = text ? localSearch(text) : [];
  const sources = { openalex: 'not_requested', crossref: 'not_requested', college: items.length };
  if (!text) return { items, sources, query: text };
  sources.openalex = 'key_missing';
  sources.crossref = 'not_attempted';
  const diagnostics={openalex:{code:key?'not_requested':'key_missing',message:key?'Not yet requested':'OpenAlex key is not configured. Configure OPENALEX_API_KEY for public topic retrieval.'},crossref:{code:'not_requested'}};
  const byDoi = new Map(items.filter((record) => record.doi).map((record) => [record.doi, record]));
  if(key) try {
    const url = new URL('https://api.openalex.org/works');
    url.search = new URLSearchParams({ search: text, per_page: '8' }).toString();
    const result=await require('./provider-http').jsonRequest(url.toString(),{request,sleep,headers:{Authorization:`Bearer ${key}`}});
    diagnostics.openalex=result.diagnostic;
    const data=result.data;
    if(!data || !Array.isArray(data.results)) {if(data)diagnostics.openalex={code:'malformed_response',message:'OpenAlex response has no results array.'};throw new Error('Provider metadata unavailable');}
    if(data.results.length && !data.results.some(work=>/^https:\/\/openalex.org\/W\d+$/.test(work?.id||'') && work.title)){diagnostics.openalex={code:'malformed_response',message:'OpenAlex returned no valid work records.'};throw new Error('Invalid work records');}
    sources.openalex = data.results.length ? 'ok' : 'no_results';
    for (const work of data.results) {
      if (!/^https:\/\/openalex.org\/W\d+$/.test(work.id || '') || !work.title) continue;
      const doi = doiKey(work.doi);
      if (doi && byDoi.has(doi)) { byDoi.get(doi).alsoIndexedBy = 'OpenAlex'; continue; }
      if (items.some((record) => record.id === work.id)) continue;
      const words = Object.entries(work.abstract_inverted_index || {}).flatMap(([word, positions]) =>
        (Array.isArray(positions)?positions:[]).map((position) => [position, word]));
      const abstract = words.sort((a, b) => a[0] - b[0]).map((entry) => entry[1]).join(' ');
      const record = { id: work.id, title: work.title,
        authors: (work.authorships || []).map((item) => item.author?.display_name).filter(Boolean),
        year: work.publication_year, venue: work.primary_location?.source?.display_name || '',
        doi, abstract, tags: tokenize(text), source: 'OpenAlex', url: work.id,
        evidenceLevel: abstract ? 'abstract' : 'metadata', retrieval: 'openalex', similarity: null };
      items.push(record);
      if (doi) byDoi.set(doi, record);
    }
  } catch { sources.openalex = 'unavailable'; }
  const targets = items.filter((item) => item.doi).slice(0, 4);
  let enriched = 0;const crossrefIssues=[];
  for (const item of targets) {
    try {
      const metadata=await require('./provider-http').jsonRequest(`https://api.crossref.org/works/${encodeURIComponent(item.doi)}`,{request,sleep,timeout:5000,headers:{'User-Agent':'GrantOffice/3.0 (research metadata)'}});
      diagnostics.crossref=metadata.diagnostic;
      if(!metadata.data)crossrefIssues.push(metadata.diagnostic);
      const result=metadata.data?.message;
      if (doiKey(result?.DOI) !== item.doi) {if(metadata.data)crossrefIssues.push({code:'malformed_response',message:'Crossref DOI did not match the requested record.'});throw new Error('DOI mismatch');}
      item.venue ||= result['container-title']?.[0] || '';
      item.crossref = { doi: item.doi, publisher: result.publisher || '', retrievedAt: new Date().toISOString() };
      enriched += 1;
    } catch { /* Preserve the original record and show provider outcome. */ }
  }
  if (targets.length) sources.crossref = enriched === targets.length ? 'ok' : enriched ? 'partial' : 'unavailable';
  if(targets.length)diagnostics.crossref={code:enriched===targets.length?'ok':enriched?'partial':crossrefIssues[0]?.code||'unavailable',message:enriched===targets.length?'DOI metadata enriched independently of OpenAlex.':'Some DOI metadata could not be retrieved; original source records retained.',failures:crossrefIssues};
  return { items, sources, diagnostics, query: text };
}

module.exports = { search, localSearch, archiveSearch, doiKey, counts: {
  publications: catalog.publications.length, awards: catalog.grants.filter((entry) => entry.status === 'Historical award').length,
  applications: catalog.grants.filter((entry) => entry.status !== 'Historical award').length,
} };
