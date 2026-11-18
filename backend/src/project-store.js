'use strict';

const database = require('./database');
const Project = require('./models/Project');
const { PROJECTS, YEARS, DEPARTMENTS } = require('./projects');

const fs = require('fs');
const path = require('path');
const budgetFile = () => path.join(require('./core').config.dataDir, 'project-budgets.json');
function savedBudgets() {
  if (!fs.existsSync(budgetFile())) return {};
  return JSON.parse(fs.readFileSync(budgetFile(), 'utf8'));
}
function overlay(project) { return project ? { ...project, ...(savedBudgets()[project.id] || {}) } : null; }

const ready = () => database.isConnected();

function normalizeBudget(lines = []) {
  return lines
    .map((l) => ({
      requirement: String(l.requirement || '').trim(),
      cost: Number(l.cost),
      ...(l.category ? { category:l.category } : {}),
    }))
    .filter((l) => l.requirement && l.cost > 0);
}

async function seedProjects() {
  if (!ready()) return { seeded: false, count: PROJECTS.length };
  let upserted = 0;
  for (const p of PROJECTS) {
    const res = await Project.updateOne(
      { projectId: p.id },
      {
        $setOnInsert: {
          projectId: p.id,
          year: p.year,
          department: p.department,
          title: p.title,
          pi: p.pi,
          coPIs: p.coPIs || [],
          agency: p.agency,
          amountLakh: p.amountLakh,
          amountNote: p.amountNote,
          approved: true,
          status: 'approved',
          budgetLines: [],
          budgetTotal: 0,
        },
      },
      { upsert: true },
    );
    if (res.upsertedCount) upserted += 1;
  }
  return { seeded: true, count: PROJECTS.length, upserted };
}

async function listProjects(filters = {}) {
  let rows;
  if (ready()) {
    const docs = await Project.find({}).sort({ year: -1, projectId: 1 }).lean();
    rows = docs.map((d) => ({
      id:d.projectId, year:d.year, department:d.department, title:d.title, pi:d.pi || [], coPIs:d.coPIs || [],
      agency:d.agency, amountLakh:d.amountLakh, amountNote:d.amountNote,
      approved:d.approved, status:d.status, budgetLines:d.budgetLines || [], budgetTotal:d.budgetTotal || 0,
      budgetUpdatedBy:d.budgetUpdatedBy, budgetUpdatedAt:d.budgetUpdatedAt,
    }));
  } else rows = PROJECTS.map(overlay);
  if (!Object.values(filters).some((value) => value && value !== 'all')) return rows;
  const directory = require('./researcher-directory').buildDirectory({ projects:rows });
  return directory.filterProjects(directory.projectRecords.filter((p) => p.recordKind === 'historical_register'), filters);
}

// Compatibility helper: researcher choices are deliberately separate from User accounts.
async function getFacultiesFromDB() {
  return (await require('./researcher-directory').currentDirectory()).search('', true);
}


async function getProject(id) {
  if (ready()) {
    const d = await Project.findOne({ projectId: id }).lean();
    if (d) {
      return {
        id: d.projectId, year: d.year, department: d.department, title: d.title,
        pi: d.pi, coPIs: d.coPIs, agency: d.agency, amountLakh: d.amountLakh,
        amountNote: d.amountNote, approved: true, status: 'approved',
        budgetLines: d.budgetLines || [], budgetTotal: d.budgetTotal || 0,
        budgetUpdatedBy: d.budgetUpdatedBy, budgetUpdatedAt: d.budgetUpdatedAt,
      };
    }
  }
  return overlay(PROJECTS.find((p) => p.id === id));
}

async function saveBudget(id, lines, actor) {
  const project = await getProject(id);
  if (!project) throw Object.assign(new Error('Project not found'), { status: 404 });
  const directory=await require('./researcher-directory').currentDirectory();
  const person=directory.resolve(actor?.id);
  const identity=directory.projectRecords.find(p=>p.id===project.id);
  if (!actor || (!actor.permissions?.includes('review:approve') && (!person || !identity?.researcherIds.includes(person.id)))) {
    throw Object.assign(new Error('Only the project investigator or Research Office can edit this budget'), { status: 403 });
  }
  if (!Array.isArray(lines) || lines.some((line) => !String(line.requirement || '').trim() || !Number.isSafeInteger(Number(line.cost)) || Number(line.cost) <= 0)) {
    throw Object.assign(new Error('Each requirement needs a positive whole-INR cost'), { status: 422 });
  }
  const clean = normalizeBudget(lines);
  const total = clean.reduce((a, l) => a + l.cost, 0);
  if (ready()) {
    const res = await Project.updateOne(
      { projectId: id },
      {
        $set: {
          budgetLines: clean,
          budgetTotal: total,
          budgetUpdatedBy: actor ? actor.name : 'faculty',
          budgetUpdatedAt: new Date(),
        },
      },
    );
    if (!res.matchedCount) {
      const err = new Error('Project not found');
      err.status = 404;
      throw err;
    }
  }
  if (!ready()) {
    const budgets = savedBudgets();
    budgets[id] = { budgetLines: clean, budgetTotal: total, budgetUpdatedBy: actor.name, budgetUpdatedAt: new Date().toISOString() };
    fs.mkdirSync(path.dirname(budgetFile()), { recursive: true });
    require('./atomic-store').writeJson(budgetFile(), budgets);
  }
  return { project: await getProject(id), total };
}

async function summary() {
  const projects = await listProjects();
  const totalLakh = projects.reduce((a, p) => a + (Number(p.amountLakh) || 0), 0);
  const byYear = {};
  for (const p of projects) {
    byYear[p.year] = byYear[p.year] || { count: 0, amountLakh: 0 };
    byYear[p.year].count += 1;
    byYear[p.year].amountLakh += Number(p.amountLakh) || 0;
  }
  return {
    count: projects.length,
    approved: projects.length,
    totalLakh: Math.round(totalLakh * 1000) / 1000,
    metricScope: 'Historical register row values; not a unique institution-wide sanctioned total. College catalog is separate pending overlap review.',
    agencies: [...new Set(projects.map((p) => p.agency))].length,
    departments: [...new Set(projects.map((p) => p.department))].length,
    years: YEARS,
    byYear,
  };
}

module.exports = { seedProjects, listProjects, getProject, saveBudget, summary, normalizeBudget, getFacultiesFromDB, YEARS, DEPARTMENTS };
