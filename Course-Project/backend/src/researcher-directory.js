'use strict';

// Research identities are not Users. This module never writes accounts or permissions.
const crypto = require('crypto');
const { FACULTY } = require('./faculty');
const college = require('./college-data');
const { PROJECTS } = require('./projects');
const normalize = (value) => String(value || '').normalize('NFKC').toLowerCase()
  .replace(/^(?:dr|professor|prof|mrs|mr|ms)(?:\.\s*|\s+)/, '').replace(/[^\p{L}\p{N}]+/gu, ' ').trim().replace(/\s+/g, ' ');
const names = (value) => String(value || '').split(/[,;|]/).map((s) => s.trim()).filter(Boolean);
function investigators(value) {
  return names(String(value || '').replace(/\bco[\s-]*(?:pi|investigator)\s*[:\-]?/ig, ';')
    .replace(/(\S)\s+(?=(?:Dr|Prof|Mr|Ms|Mrs)\.?\s)/g, '$1;'));
}
const stableId = (name) => 'res-' + crypto.createHash('sha256').update(normalize(name)).digest('hex').slice(0, 16);

function buildDirectory({ confirmed = FACULTY, publications = college.publications, grants = college.catalog.grants, projects = PROJECTS } = {}) {
  const records = new Map(), index = new Map(), alternateIds = new Map(), unresolved = [];
  const addIdAlias = (record, id) => {
    if (id === record.id) return;
    if (!alternateIds.has(id)) alternateIds.set(id, new Set());
    alternateIds.get(id).add(record.id);
    if (!record.idAliases.includes(id)) record.idAliases.push(id);
  };
  const addAlias = (record, name) => {
    const key = normalize(name);
    if (!key) return;
    if (!record.aliases.includes(name)) record.aliases.push(name);
    if (!index.has(key)) index.set(key, new Set());
    index.get(key).add(record.id);
    // A source-derived ID remains resolvable when later confirmed records add an ID.
    addIdAlias(record, stableId(name));
  };
  const resolve = (value) => {
    if (records.has(value)) return records.get(value);
    if (alternateIds.has(value)) {
      const ids = alternateIds.get(value);
      return ids.size === 1 ? records.get([...ids][0]) : null;
    }
    const ids = index.get(normalize(value));
    return ids?.size === 1 ? records.get([...ids][0]) : null;
  };
  function add(name, evidence, { id, department = '', confirmedFaculty = false, eligible = false, email = '', aliases = [] } = {}) {
    if (!normalize(name)) return null;
    // Exact documented aliases only. No first-name, surname or fuzzy person merges.
    let record = resolve(name);
    if (id && record?.confirmedFaculty && record.id !== id && (!email || !record.email || email.toLowerCase() !== record.email.toLowerCase())) {
      // Distinct confirmed IDs without a shared email cannot establish a person merge.
      record = null;
    }
    if (!record) {
      const key = id || stableId(name);
      record = records.get(key) || { id:key, Name:name, Dept:department, email, aliases:[], provenance:[],
        confirmedFaculty:false, eligibleForProposal:false, idAliases:[], publicationIds:[], projectRecordIds:[] };
      records.set(key, record);
    }
    record.confirmedFaculty ||= confirmedFaculty;
    record.eligibleForProposal ||= eligible || confirmedFaculty;
    if (id && id !== record.id && !records.has(id)) {
      addIdAlias(record, id);
    }
    if (!record.Dept && department) record.Dept = department;
    if (!record.email && email) record.email = email;
    for (const alias of [name, ...aliases]) addAlias(record, alias);
    if (evidence && !record.provenance.some((e) => JSON.stringify(e) === JSON.stringify(evidence))) record.provenance.push(evidence);
    return record;
  }
  // Existing institutional records take precedence and retain their stable IDs.
  for (const faculty of confirmed) {
    add(faculty.Name, { kind:'confirmed_faculty', source:faculty.directorySource || 'Course-Project/backend/src/faculty.js', id:faculty.id },
      { id:faculty.id, department:faculty.Dept, email:faculty.email, aliases:faculty.aliases || [], confirmedFaculty:true });
  }
  for (const publication of publications.filter((p) => !p.mock)) {
    const facultyLocations = publication.sources.filter((s) => /(?:^|[- ])faculty(?: papers)?(?:\.|$| )/i.test(s.file) || /^faculty(?: papers)?$/i.test(s.sheet));
    for (const name of names(publication.home_authors)) {
      add(name, { kind:'home_author', recordId:publication.id, name, sources:publication.sources },
        { department:publication.department, eligible:facultyLocations.length > 0 });
      if (facultyLocations.length) add(name, { kind:'faculty_export_home_author', recordId:publication.id, name, sources:facultyLocations }, { eligible:true });
    }
  }
  for (const grant of grants.filter((g) => !g.mock)) {
    for (const name of investigators(grant.investigators)) {
      add(name, { kind:'college_investigator', recordId:grant.id, name, sources:[grant.source].filter(Boolean) }, { department:grant.department, eligible:true });
    }
  }
  for (const project of projects) {
    for (const name of [...(project.pi || []), ...(project.coPIs || [])]) {
      add(name, { kind:'register_investigator', recordId:project.id, name, source:'historical project register' }, { department:project.department, eligible:true });
    }
  }
  // Link only exact full names or documented aliases. Unresolved coauthors gain no faculty status.
  for (const publication of publications.filter((p) => !p.mock)) {
    const linked = new Set();
    for (const name of [...names(publication.authors), ...names(publication.home_authors)]) {
      const person = resolve(name);
      if (person) {
        linked.add(person.id);
        addAlias(person, name);
      } else unresolved.push({ kind:'unresolved_author', recordId:publication.id, name, sources:publication.sources });
    }
    for (const id of linked) records.get(id).publicationIds.push(publication.id);
  }
  const projectRecords = [
    ...projects.map((p) => ({ ...p, pi:p.pi || [], coPIs:p.coPIs || [], recordKind:'historical_register', investigatorNames:[...(p.pi || []), ...(p.coPIs || [])] })),
    ...grants.filter((g) => !g.mock).map((g) => ({ ...g, recordKind:g.status.startsWith('Applied') ? 'application' : g.status === 'Historical award' ? 'sanctioned_award' : 'historical_summary',
      investigatorNames:investigators(g.investigators), pi:investigators(g.investigators), coPIs:[], amountLakh:g.amount_inr == null ? null : g.amount_inr / 100000 })),
  ];
  for (const project of projectRecords) {
    project.researcherIds = [...new Set(project.investigatorNames.map((name) => resolve(name)?.id).filter(Boolean))];
    project.piResearcherIds=[...new Set(project.pi.map(name=>resolve(name)?.id).filter(Boolean))];
    project.coPiResearcherIds=[...new Set(project.coPIs.map(name=>resolve(name)?.id).filter(Boolean))];
    for (const id of project.researcherIds) records.get(id).projectRecordIds.push(project.id);
  }
  const reconciliation = college.reconcile(projects, grants.filter((g) => !g.mock && g.status === 'Historical award'));
  // Exact composite matches can share a derived group while every source ID remains intact.
  const groups = new Map(), groupFor = new Map();
  for (const project of projectRecords) {
    const amount = project.amount_inr ?? (project.amountLakh == null ? null : Math.round(project.amountLakh * 100000));
    const lifecycle = project.recordKind === 'application' ? 'application' : project.recordKind === 'historical_summary' ? 'summary' : 'project';
    const complete = project.title && project.agency && project.year && amount != null && project.researcherIds.length > 0 &&
      project.investigatorNames.every((name) => resolve(name));
    const key = complete ? JSON.stringify([lifecycle, normalize(project.title), normalize(project.agency),
      [...project.researcherIds].sort(), String(project.year), amount]) : project.recordKind + ':' + project.id;
    if (!groups.has(key)) groups.set(key, { id:'project-group-' + crypto.createHash('sha256').update(key).digest('hex').slice(0, 16), sourceIds:[] });
    const group = groups.get(key);
    if (!group.sourceIds.includes(project.id)) group.sourceIds.push(project.id);
    groupFor.set(project.id, group);
  }
  // Reviewed against the original legacy register export and detailed award sheet.
  // These are record-specific links, not a general title/first-name merge rule.
  const reviewed=[['PRJ-2223-01','GRANT-3','LEGACY-CSV-16'],['PRJ-2223-07','GRANT-9','LEGACY-CSV-22']];
  for(const [registerId,awardId,evidenceId] of reviewed) {
    const left=projectRecords.find(p=>p.id===registerId),right=projectRecords.find(p=>p.id===awardId);
    const source=college.review?.legacy_evidence?.find(e=>e.id===evidenceId);
    const year=left?.year?.match(/^(\d{4})-(\d{2})$/);
    const yearSupported=year && [year[1],year[1].slice(0,2)+year[2]].includes(String(right?.year));
    if(!left||!right||!source||source.year!==left.year||!yearSupported||normalize(left.title)!==normalize(right.title)||
      !left.researcherIds.length||JSON.stringify([...left.researcherIds].sort())!==JSON.stringify([...right.researcherIds].sort()))continue;
    const group=groupFor.get(left.id),other=groupFor.get(right.id);
    for(const id of other.sourceIds) {if(!group.sourceIds.includes(id))group.sourceIds.push(id);groupFor.set(id,group);}
    group.reviewedEvidence={evidenceId,sources:source.sources,scope:'Same award identity; original year, agency and amount discrepancies retained'};
    group.financialConflicts=left.amountLakh*100000!==right.amount_inr ? [{registerInr:left.amountLakh*100000,catalogInr:right.amount_inr}] : [];
  }
  reconciliation.confirmedLinks = reconciliation.candidates.filter((c) => groupFor.get(c.projectId) === groupFor.get(c.grantId))
    .map((c) => ({ projectId:c.projectId, grantId:c.grantId, basis:groupFor.get(c.projectId).reviewedEvidence || 'Exact normalized title, agency, resolved investigators, year and INR amount', amountConflict:c.differenceInr !== 0, registerInr:c.registerInr, catalogInr:c.collegeInr }));
  const reviewEdges = [...reconciliation.candidates.filter((c) => groupFor.get(c.projectId) !== groupFor.get(c.grantId))
    .map((c) => [c.projectId, c.grantId]), ...reconciliation.conflicts.map((c) => c.ids)];
  const reviewGroups = new Set(reviewEdges.flat().map((id) => groupFor.get(id)?.id));
  const reviewIds = new Set(projectRecords.filter((p) => reviewGroups.has(groupFor.get(p.id)?.id) && !groupFor.get(p.id)?.reviewedEvidence).map((p) => p.id));
  for (const record of records.values()) {
    record.publicationIds = [...new Set(record.publicationIds)].sort();
    record.projectRecordIds = [...new Set(record.projectRecordIds)].sort();
    record.publicationCount = record.publicationIds.length;
    const linked = projectRecords.filter((p) => p.researcherIds.includes(record.id));
    record.historicalRegisterCount=linked.filter(p=>p.recordKind==='historical_register').length;
    record.fundedAwardCount=new Set(linked.filter(p=>p.recordKind==='sanctioned_award').map(p=>groupFor.get(p.id).id)).size;
    record.applicationCount = linked.filter((p) => p.recordKind === 'application').length;
    record.definiteProjectCount = new Set(linked.filter((p) => ['historical_register', 'sanctioned_award'].includes(p.recordKind) && !reviewIds.has(p.id))
      .map((p) => groupFor.get(p.id).id)).size;
    record.reviewProjectIds = linked.filter((p) => reviewIds.has(p.id)).map((p) => p.id);
    // A combined unique count cannot be asserted for unresolved overlapping source rows.
    record.projectCount = record.reviewProjectIds.length ? null : record.definiteProjectCount;
    record.identityStatus = record.confirmedFaculty ? 'confirmed_faculty' : record.eligibleForProposal ? 'institutional_evidence' : 'affiliation_review';
    record.Role = record.confirmedFaculty ? 'faculty' : record.eligibleForProposal ? 'researcher' : 'researcher_candidate';
    record.title = record.confirmedFaculty ? 'Institutional faculty' : 'Research identity; source evidence retained';
    record.aliases.sort();
    record.idAliases.sort();
  }
  for (const [key, ids] of index) if (ids.size > 1) unresolved.push({ kind:'ambiguous_alias', name:key, candidateIds:[...ids] });
  const people = [...records.values()].sort((a, b) => a.id.localeCompare(b.id));
  function search(q = '', eligibleOnly = false) {
    const text = normalize(q);
    return people.filter((p) => (!eligibleOnly || p.eligibleForProposal) && (!text ||
      [p.id, p.Name, p.Dept, p.email, ...p.aliases].some((v) => normalize(v).includes(text))));
  }
  function filterProjects(rows, { q = '', faculty, year, department } = {}) {
    const person = resolve(faculty);
    const text = normalize(q);
    const matchingPeople = new Set(search(q).map((p) => p.id));
    return rows.filter((p) => (!year || year === 'all' || p.year === year) && (!department || department === 'all' || p.department === department) &&
      (!faculty || faculty === 'all' || (person ? p.researcherIds.includes(person.id) : p.investigatorNames.some((n) => normalize(n) === normalize(faculty)))) &&
      (!text || [p.id, p.title, p.agency, p.department, p.sanction_reference, ...p.investigatorNames].some((v) => normalize(v).includes(text)) || p.researcherIds.some((id) => matchingPeople.has(id))));
  }
  return { people, unresolved, projectRecords, projectGroups:[...new Set([...groupFor.values()])], reconciliation, resolve, search, filterProjects };
}

async function currentDirectory() {
  const store = require('./project-store');
  const database = require('./database');
  const projects = await store.listProjects();
  let confirmed = [...FACULTY];
  if (database.isConnected()) {
    const users = await database.User.find({ Role:{ $in:['faculty', 'pi', 'dean'] }, isActive:{ $ne:false } },
      { Name:1, Dept:1, email:1, userId:1 }).lean();
    // Account permissions and credentials are deliberately never copied into this directory.
    confirmed.push(...users.map((u) => ({ ...u, id:u.userId || String(u._id), directorySource:'existing institutional User record' })));
  }
  return buildDirectory({ confirmed, projects });
}

function validateSelection(directory, ids, previous = []) {
  if (ids === undefined) return previous;
  if (!Array.isArray(ids) || ids.some((id) => typeof id !== 'string' ||
      (!previous.includes(id) && !directory.resolve(id)?.eligibleForProposal))) {
    throw Object.assign(new Error('Select eligible institutional researchers from the directory'), { status:422 });
  }
  const seen = new Set();
  return ids.filter((id) => {
    const identity = directory.resolve(id)?.id || id;
    if (seen.has(identity)) return false;
    seen.add(identity);
    return true;
  });
}

module.exports = { buildDirectory, currentDirectory, normalize, investigators, validateSelection };
