'use strict';

// Read-only adapter. The institutional catalog is shared with the Python edition.
// Project documents and their saved budgets remain in their existing store.
const catalog = require('../../langgraph_edition/data/catalog.json');
const fs = require('fs');
const crypto = require('crypto');
const path = require('path');
const catalogFile = path.resolve(__dirname, '../../langgraph_edition/data/catalog.json');
const reviewFile = path.resolve(__dirname, '../../langgraph_edition/data/reconciliation.json');
const review = fs.existsSync(reviewFile) ? JSON.parse(fs.readFileSync(reviewFile, 'utf8')) : null;
const reviewValid = review?.catalog_sha256 === crypto.createHash('sha256').update(fs.readFileSync(catalogFile)).digest('hex');
const { PROJECTS } = require('./projects');
const normalize = (value) => String(value || '').normalize('NFKC').toLowerCase().replace(/[^\p{L}\p{N}]+/gu, ' ').trim();
const amount = (value) => Number.isSafeInteger(value) && value >= 0 ? value : 0;
const publicationReviews = reviewValid ? review.pending_publications.map((p) => ({
  id:p.id, title:p.title, doi:p.doi, sources:p.sources,
  candidateIds:catalog.publications.filter((existing) => normalize(existing.title) === normalize(p.title)).map((existing) => existing.id),
  message:'Source rebuild exposes a distinct DOI spelling previously collapsed by a suffix repair. Candidate retained for review; established ID and count preserved.',
})) : [];
const publications = catalog.publications.map((p) => ({ ...p,
  sources:reviewValid ? review.publication_sources[p.id] || p.sources : p.sources,
  conflicts:reviewValid ? review.publication_conflicts[p.id] || [] : [],
  identityReview:publicationReviews.filter((item) => item.candidateIds.includes(p.id)),
}));
const awards = catalog.grants.filter((g) => !g.mock && g.status === 'Historical award').map((g) => ({ ...g,
  ...(g.related_sources?.length ? { related_sources_status:'Unverified legacy candidate links retained from the earlier importer; excluded from identity and financial calculations.' } : {}),
}));
const applications = catalog.grants.filter((g) => !g.mock && g.status === 'Applied (outcome unknown)');

function similarity(a, b) {
  const left = new Set(normalize(a).split(' ')), right = new Set(normalize(b).split(' '));
  const intersection = [...left].filter((word) => right.has(word)).length;
  return intersection / new Set([...left, ...right]).size;
}

function reconcile(projects = PROJECTS, comparisonAwards = awards) {
  const candidates = [];
  for (const project of projects) {
    for (const grant of comparisonAwards) {
      // This only nominates review candidates. No fuzzy match changes identity or totals.
      if (similarity(project.title, grant.title) < 0.72) continue;
      const registerInr = Math.round(project.amountLakh * 100000);
      candidates.push({ projectId:project.id, grantId:grant.id,
        disposition:'possible_overlap_review_required',
        registerYear:project.year, collegeYear:grant.year,
        registerAgency:project.agency, collegeAgency:grant.agency,
        registerInvestigators:[...(project.pi || []), ...(project.coPIs || [])], collegeInvestigators:grant.investigators,
        registerInr, collegeInr:grant.amount_inr, differenceInr:registerInr - grant.amount_inr,
        status:grant.status, source:grant.source,
        reason:'No common sanction identifier; compare title, PI, agency, academic/calendar year and amount before combining.' });
    }
  }
  const conflicts = [];
  for (let i = 0; i < projects.length; i += 1) {
    for (const other of projects.slice(i + 1)) {
      const current = projects[i];
      if (normalize(current.title) === normalize(other.title) && current.year === other.year
          && normalize(current.agency) === normalize(other.agency)
          && normalize((current.pi || []).join(' ')) === normalize((other.pi || []).join(' '))) {
        conflicts.push({ ids:[current.id, other.id], title:current.title,
          amountsInr:[Math.round(current.amountLakh * 100000), Math.round(other.amountLakh * 100000)],
          reason:'Same title, PI, agency and year; different amounts may be instalments or conflicting summaries. Excluded from any combined unique total.' });
      }
    }
  }
  const statusConflicts = [];
  for (const project of projects) {
    for (const evidence of reviewValid ? review.legacy_evidence : []) {
      if (normalize(evidence.title) === normalize(project.title) && /cancel|not.*receiv/i.test(evidence.notes || '')) {
        statusConflicts.push({ projectId:project.id, registeredStatus:project.status, sourceNote:evidence.notes, sources:evidence.sources,
          reason:'Source note requires status review; stored approval and budget references are preserved.' });
      }
    }
  }
  return { candidates, conflicts, statusConflicts, combinedCount:null, combinedSanctionedInr:null,
    scope:'Registers remain separate. Candidate overlaps and ambiguous register rows prohibit an institution-wide combined total.' };
}

function metrics() {
  const financialIssues = awards.flatMap((g) => {
    const issues = [];
    if (g.nonrecurring_inr > 0 && g.nonrecurring_inr < 100 && g.amount_inr >= 100000) {
      issues.push({ source:g.id, severity:'warning', message:'Source non-recurring component has ambiguous units (1 or 3.5 in the worksheet); raw cell retained. Sanctioned total uses the explicit sanctioned-INR column.' });
    }
    if (/not yet/i.test(g.notes || '') && g.received_inr > 0) {
      issues.push({ source:g.id, severity:'warning', message:'Receipt note says not yet received but the received amount is positive. Both source values retained for review.' });
    }
    return issues;
  });
  return { publications:catalog.publications.filter((p) => !p.mock).length,
    awards:awards.length, applications:applications.length,
    sanctionedInr:awards.reduce((sum, g) => sum + amount(g.amount_inr), 0),
    receivedInr:awards.reduce((sum, g) => sum + amount(g.received_inr), 0),
    receivedUnknown:awards.filter((g) => g.received_inr == null).length,
    requestedInr:applications.reduce((sum, g) => sum + amount(g.amount_inr), 0),
    source:'langgraph_edition/data/catalog.json',
    amountBasis:'Sanctioned amount_inr from detailed Historical award rows only. Received amounts are separate; null means unknown. Applications, legacy summaries, register rows and mocks are excluded.',
    provenanceReferences:publications.reduce((sum, p) => sum + p.sources.length, 0),
    publicationReviews,
    issues:[...catalog.issues.filter((issue) => issue.severity === 'warning'), ...financialIssues,
      ...publicationReviews.map((p) => ({ source:p.id, severity:'warning', message:p.message })),
      ...(!reviewValid ? [{ source:'Provenance review', severity:'warning', message:'Provenance sidecar is missing or stale; established catalog remains authoritative.' }] : [])],
    reconciliation:reconcile() };
}

module.exports = { catalog, publications, awards, applications, metrics, reconcile, review:reviewValid ? review : null };
