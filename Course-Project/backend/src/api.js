'use strict';

/**
 * HTTP API for the AURA console.
 */
const express = require('express');
const crypto = require('crypto');
const sessions = new Map();
const {
  config, db, util, connector, skills, specialists, runtime,
} = require('./core');
const engine = require('./engine');
const { AGENTS, CALLS, LITERATURE, POLICIES, USERS, INSTITUTION, DOCUMENT_REGISTER, COMPLIANCE_RULES } = require('./seed');

const { money } = util;

function actorFrom(req) { return req.actor || null; }
function canRead(actor,run) {return Boolean(run && require('./proposal-activity').canRead(actor,run));}

function createApp() {
  const app = express();
  app.use(express.json({ limit: '2mb' }));
  app.use((req, res, next) => {
    res.setHeader('X-Content-Type-Options', 'nosniff');
    res.setHeader('Referrer-Policy', 'same-origin');
    if (req.path.startsWith('/api')) res.setHeader('Cache-Control', 'no-store');
    const token = (req.get('authorization') || '').replace(/^Bearer /, '');
    const session = sessions.get(token);
    if (session && session.expires > Date.now()) req.actor = USERS.find((user) => user.id === session.id);
    const publicRoutes = ['/api/health', '/api/bootstrap', '/api/auth/login', '/api/users'];
    if (req.path.startsWith('/api') && !(req.method === 'GET' && publicRoutes.includes(req.path)) && req.path !== '/api/auth/login' && !req.actor) {
      return res.status(401).json({ error: 'authentication_required' });
    }
    if (req.path.startsWith('/api/runs/') && req.actor) {
      const run = db.getRun(req.path.split('/')[3]);
      if (run && !canRead(req.actor, run)) return res.status(404).json({ error: 'not_found' });
    }
    next();
  });

  const mutationLocks=new Set();
  const wrap=(fn)=>(req,res,next)=>{
    const runId=/^\/api\/runs\/([^/]+)/.exec(req.path)?.[1];const mutation=runId&&req.method!=='GET';
    if(mutation&&mutationLocks.has(runId))return res.status(409).json({message:'Another change to this proposal is in progress; reload before retrying.'});
    if(mutation)mutationLocks.add(runId);
    return Promise.resolve().then(()=>fn(req,res,next)).catch(next).finally(()=>{if(mutation)mutationLocks.delete(runId);});
  };

  app.get('/api/health', wrap(async (req, res) => {
    const mongo = await persistence.status();
    res.json({
      status: db.storageStatus().writeError ? 'degraded' : 'healthy',
      uptime: process.uptime(),
      timestamp: util.nowIso(),
      version: '1.2.0',
      store:'file', activeStorage:'local_json',
      mongo,
      llm: { configured: groq.isGroqConfigured(), provider: groq.provider(), model: groq.GROQ_MODEL },
    });
  }));

  app.get('/api/bootstrap', wrap(async (req, res) => {
    const people = await persistence.people();
    const mongo = await persistence.status();
    res.json({
      institution: INSTITUTION,
      workspace: 'Practice workflow',
      agents: AGENTS,
      users: people.map((p) => ({
        id: p.id,
        name: p.Name,
        role: p.Role,
        title: p.title,
        dept: p.Dept,
        email: p.email,
        permissions: p.permissions,
        runsCount: p.runsCount,
      })),
      people,
      specialists: Object.values(specialists.SPECIALISTS).map((s) => ({ id: s.id, label: s.label, description: s.description, sections: s.sections, scheme: s.scheme.requiredFields })),
      graph: engine.GRAPH,
      skills: { plan: skills.PLAN_SCHEMA, format: skills.FORMAT_SCHEMA },
      metrics: engine.metrics.computeMetrics(req.actor),
      config: { retryBudget: config.retryBudget, reviewBufferDays: config.reviewBufferDays, stepDelayMs: config.stepDelayMs, connectorHeader: config.connectorTokenHeader },
      connector: connector.catalog(),
      counts: { calls: CALLS.length, literature: LITERATURE.length, policies: POLICIES.length, rules: COMPLIANCE_RULES.length, documents: DOCUMENT_REGISTER.length },
      mongo,
      llm: { configured: groq.isGroqConfigured(), provider: groq.provider(), model: groq.GROQ_MODEL, drafting: require('./llm-drafting').isEnabled() },
      now: util.nowIso(),
    });
  }));

const database = require('./database');
const groq = require('./model');
const persistence = require('./persistence');
const llmDrafting = require('./llm-drafting');

  /* --------------------------------- auth ---------------------------------- */
  app.post('/api/auth/login', wrap(async (req, res) => {
    const { email, username, userId, password } = req.body || {};
    const identifier = String(email || username || userId || '').trim().toLowerCase();

    // Check MongoDB User model first, then fallback to seed USERS
    let user = await database.findUserByIdOrEmail(identifier);
    if (!identifier || !user || user.isActive === false) {
      user = USERS.find((u) =>
        u.id.toLowerCase() === identifier ||
        (u.email && u.email.toLowerCase() === identifier) ||
        u.name.toLowerCase().includes(identifier)
      ) || (userId ? USERS.find((u) => u.id === userId) : null);
    }

    if (!user) {
      return res.status(401).json({ error: 'invalid_credentials', message: 'User account not found. Please select an institutional account.' });
    }

    if (typeof password !== 'string' || password !== (user.password || 'password123')) {
      return res.status(401).json({ error: 'invalid_password', message: 'Incorrect password.' });
    }

    const uid = user.userId || user.id || `usr-${Date.now()}`;
    const name = user.Name || user.name;
    const role = user.Role || user.role;
    const dept = user.Dept || user.department;
    const emailAddr = user.email;

    const token = crypto.randomBytes(32).toString('hex');
    sessions.set(token, { id: uid, expires: Date.now() + 8 * 3600000 });
    db.audit({ actor: name, agent: 'coordinator', phase: 'auth', intent: 'User authenticated', action: 'auth.login', inputs: { role }, outputs: { userId: uid }, result: 'success' });

    res.json({
      success: true,
      token,
      user: {
        id: uid,
        Name: name,
        Role: role,
        Dept: dept,
        email: emailAddr,
        name,
        role,
        dept,
        department: dept,
        title: user.title,
        permissions: user.permissions,
      },
    });
  }));

  app.get('/api/auth/me', wrap(async (req, res) => {
    const actor = actorFrom(req);
    res.json({
      user: {
        id: actor.id,
        Name: actor.Name || actor.name,
        Role: actor.Role || actor.role,
        Dept: actor.Dept || actor.department,
        email: actor.email,
        name: actor.name,
        role: actor.role,
        department: actor.department,
        dept: actor.department,
        title: actor.title,
        permissions: actor.permissions,
      },
    });
  }));

  app.post('/api/auth/logout', (req, res) => {
    const actor = actorFrom(req);
    db.audit({ actor: actor.name, agent: 'coordinator', phase: 'auth', intent: 'User signed out', action: 'auth.logout', inputs: {}, outputs: {}, result: 'success' });
    sessions.delete((req.get('authorization') || '').replace(/^Bearer /, ''));
    res.json({ success: true, message: 'Logged out successfully' });
  });

  /* ------------------------------- users / faculty ------------------------ */
  app.get('/api/users', wrap(async (req, res) => {
    const people = await persistence.people();
    if (!req.actor) return res.json({ users: people.map((person) => ({ id: person.id, Name: person.Name, Role: person.Role, Dept: person.Dept, title: person.title })), source: 'local directory' });
    const mongoStatus = await persistence.status();
    res.json({
      source: mongoStatus.connected ? 'mongodb' : 'fallback',
      orm: 'mongoose',
      model: 'User',
      collection: 'users',
      total: people.length,
      users: people,
      mongo: mongoStatus,
      schema: {
        model: 'User',
        collection: 'users',
        required: ['Name', 'Role', 'Dept', 'email'],
        roleEnum: ['dean', 'pi', 'faculty', 'research_office', 'admin'],
        fields: {
          Name: { type: 'String', required: true, description: 'Faculty full name with academic honorific' },
          Role: { type: 'String', required: true, enum: ['dean', 'pi', 'faculty', 'research_office', 'admin'], description: 'Institutional access role' },
          Dept: { type: 'String', required: true, description: 'Academic department or school' },
          email: { type: 'String', required: true, unique: true, description: 'Institutional email address' },
          password: { type: 'String', default: 'password123' },
          title: { type: 'String', description: 'Academic designation / administrative office' },
          userId: { type: 'String', description: 'Institutional user identifier' },
          permissions: { type: '[String]', description: 'Governed RBAC permission tokens' },
          careerStage: { type: 'String', enum: ['assistant', 'associate', 'professor', 'n/a'], default: 'associate' },
          expertise: { type: '[String]', description: 'Domain keywords for grant matching' },
          monthlyCost: { type: 'Number', default: 150000 },
          isActive: { type: 'Boolean', default: true },
        },
        links: ['runs.actorRef', 'runs.approval.decidedByRef', 'audit_events.actorRef', 'versions.approvedByRef'],
      },
    });
  }));

  app.get('/api/users/:id', wrap(async (req, res) => {
    const detail = await persistence.person(req.params.id);
    if (!detail) return res.status(404).json({ error: 'not_found', message: 'Person not found' });
    res.json(detail);
  }));

  app.get('/api/people', wrap(async (req, res) => {
    res.json({ people: await persistence.people(), mongo: await persistence.status() });
  }));

  app.get('/api/people/:id', wrap(async (req, res) => {
    const detail = await persistence.person(req.params.id);
    if (!detail) return res.status(404).json({ error: 'not_found', message: 'Person not found' });
    res.json(detail);
  }));

  app.get('/api/mongo/status', wrap(async (req, res) => {
    res.json(await persistence.status());
  }));

  app.get('/api/mongo/schemas', wrap(async (req, res) => {
    const models = require('./models');
    const mongoose = models.mongoose;
    const modelKeys = ['User', 'Project', 'Run', 'AuditEvent', 'Version'];
    const schemasInfo = {};

    for (const key of modelKeys) {
      const model = models[key];
      if (!model || !model.schema) continue;
      const paths = {};
      for (const [pathname, schemaType] of Object.entries(model.schema.paths)) {
        paths[pathname] = {
          instance: schemaType.instance,
          required: Boolean(schemaType.isRequired),
          enumValues: schemaType.enumValues || null,
          defaultValue: typeof schemaType.defaultValue === 'function' ? '(computed)' : schemaType.defaultValue,
        };
      }
      let count = null;
      if (database.isConnected()) {
        try {
          count = await model.countDocuments();
        } catch {
          count = null;
        }
      }
      schemasInfo[key] = {
        modelName: key,
        collectionName: model.collection?.name || key.toLowerCase() + 's',
        paths,
        pathCount: Object.keys(paths).length,
        documentCount: count,
      };
    }

    res.json({
      connected: database.isConnected(),
      database: database.status(),
      orm: 'mongoose',
      models: schemasInfo,
      sampleSchema: {
        model: 'User',
        code: `const mongoose = require('mongoose');

const UserSchema = new mongoose.Schema({
  Name: { type: String, required: [true, 'Name is required'], trim: true },
  Role: {
    type: String,
    required: [true, 'Role is required'],
    enum: ['dean', 'pi', 'faculty', 'research_office', 'admin'],
    trim: true,
    lowercase: true,
  },
  Dept: { type: String, required: [true, 'Department is required'], trim: true },
  email: {
    type: String,
    required: [true, 'Email is required'],
    unique: true,
    trim: true,
    lowercase: true,
    match: [/^\S+@\S+\.\S+$/, 'Valid email required'],
  },
  password: { type: String, default: 'password123' },
  title: { type: String, trim: true },
  userId: { type: String, trim: true, sparse: true },
  permissions: { type: [String], default: [] },
  expertise: { type: [String], default: [] },
  careerStage: { type: String, enum: ['assistant', 'associate', 'professor', 'n/a'], default: 'associate' },
  monthlyCost: { type: Number, default: 150000 },
  isActive: { type: Boolean, default: true },
}, { timestamps: true });

module.exports = mongoose.models.User || mongoose.model('User', UserSchema);`,
      },
    });
  }));


  app.post('/api/users', wrap(async (req, res) => {
    if (!actorFrom(req)?.permissions?.includes('review:approve')) return res.status(403).json({ error: 'forbidden' });
    const { Name, Role, Dept, email, password, title, careerStage, expertise } = req.body || {};

    if (!Name || !Role || !Dept || !email) {
      return res.status(400).json({
        error: 'missing_fields',
        message: 'Name, Role, Dept, and email are required fields',
        schema: { Name: 'String (required)', Role: 'String (dean/pi/faculty/research_office)', Dept: 'String (required)', email: 'String (required)' },
      });
    }

    try {
      if (database.isConnected()) {
        const created = await database.User.create({
          Name,
          Role,
          Dept,
          email,
          password: password || 'password123',
          title: title || (Role === 'dean' ? 'Dean, Research & Development' : 'Faculty Researcher'),
          careerStage: careerStage || 'associate',
          expertise: expertise || [],
          userId: `usr-${Date.now().toString(36)}`,
        });
        // Keep the in-process actor registry in sync so x-actor-id works immediately.
        USERS.push({
          id: created.userId,
          name: created.Name,
          Name: created.Name,
          role: created.Role,
          department: created.Dept,
          dept: created.Dept,
          email: created.email,
          title: created.title,
          permissions: created.permissions,
        });
        return res.status(201).json({ success: true, user: created });
      }

      // Memory creation fallback
      const newUser = {
        id: `usr-${Date.now().toString(36)}`,
        Name,
        Role,
        Dept,
        email,
        name: Name,
        role: Role,
        department: Dept,
        dept: Dept,
        title: title || (Role === 'dean' ? 'Dean, Research & Development' : 'Faculty Researcher'),
        permissions: Role === 'dean' ? ['run:create', 'run:read:all', 'review:approve', 'package:view', 'audit:read', 'version:rollback', 'metrics:read'] : ['run:create', 'run:read:own', 'draft:edit', 'package:view'],
      };
      USERS.push(newUser);
      res.status(201).json({ success: true, user: newUser, persistence:'memory_only_not_durable',warning:'Fallback account exists only until restart. Configure MongoDB for durable runtime account administration.' });
    } catch (err) {
      res.status(err.status || 400).json({ error: 'creation_failed', message: err.message });
    }
  }));

  /* -------------------------------- projects ------------------------------- */
  const projectStore = require('./project-store');
  const researchers = require('./researcher-directory');

  app.get('/api/researchers', wrap(async (req, res) => {
    const directory = await researchers.currentDirectory();
    const people = directory.search(req.query.q, req.query.includeReview !== '1').map(({ provenance, publicationIds, projectRecordIds, ...p }) =>
      ({ ...p, ...require('./proposal-activity').activity(directory,p,db.state.runs,req.actor), evidenceKinds:[...new Set(provenance.map((e) => e.kind))] }));
    res.json({ people, total:people.length, unresolvedCount:directory.unresolved.length, source:'institutional researcher directory' });
  }));
  app.get('/api/researchers/:id', wrap(async (req, res) => {
    const directory = await researchers.currentDirectory();
    const person = directory.resolve(req.params.id);
    if (!person) return res.status(404).json({ error:'not_found' });
    res.json({ person, ...require('./proposal-activity').activity(directory,person,db.state.runs,req.actor),
      publications:require('./college-data').publications.filter((p) => person.publicationIds.includes(p.id)),
      projects:directory.projectRecords.filter((p) => p.researcherIds.includes(person.id)),
      projectGroups:directory.projectGroups.filter((g) => g.sourceIds.some((id) => person.projectRecordIds.includes(id))),
      metricScope:'Applications separate. Reviewed source-linked awards count once. Unresolved overlaps remain separate; original values and conflicts are retained without a combined financial total.' });
  }));

  app.get('/api/projects', wrap(async (req, res) => {
    const { year, department, q, faculty, my } = req.query;
    const actor = actorFrom(req);
    // If 'my=true' or 'my=1', filter to the authenticated faculty member's name
    const targetFaculty = (my === 'true' || my === '1') ? actor?.id : faculty;
    const directory = await researchers.currentDirectory();
    const matched = directory.filterProjects(directory.projectRecords, { year, department, q, faculty:targetFaculty });
    const projects = matched.filter((p) => p.recordKind === 'historical_register');
    const faculties = directory.search('', true).map(({ provenance, publicationIds, projectRecordIds, ...p }) => p);
    res.json({
      projects,
      myResearcher:directory.resolve(actor?.id) || null,
      catalogProjects:matched.filter((p) => p.recordKind !== 'historical_register'),
      faculties,
      summary: await projectStore.summary(),
      college: require('./college-data').metrics(),
      reconciliation: directory.reconciliation,
      years: [...new Set(directory.projectRecords.map((p) => p.year))].sort().reverse(),
      departments: [...new Set(directory.projectRecords.map((p) => p.department))].sort(),
      filter: { faculty: targetFaculty || null, year: year || null, department: department || null },
      source: database.isConnected() ? 'mongodb' : 'local',
    });
  }));

  app.get('/api/faculties', wrap(async (req, res) => {
    const directory = await researchers.currentDirectory();
    const faculties = directory.search(req.query.q, true).map(({ provenance, publicationIds, projectRecordIds, ...p }) => p);
    res.json({
      faculties,
      total: faculties.length,
      source: 'institutional researcher directory',
    });
  }));

  app.get('/api/projects/:id', wrap(async (req, res) => {
    const project = await projectStore.getProject(req.params.id);
    if (!project) return res.status(404).json({ error: 'not_found', message: 'Project not found' });
    res.json({ project });
  }));

  app.put('/api/projects/:id/budget', wrap(async (req, res) => {
    const actor = actorFrom(req);
    const lines = Array.isArray(req.body?.lines) ? req.body.lines : [];
    try {
      const saved = await projectStore.saveBudget(req.params.id, lines, actor);
      db.audit({ actor: actor.name, actorId: actor.id, agent: 'faculty', phase: 'budget', intent: `Faculty entered budget for ${req.params.id}`, action: 'project.budget.save', inputs: { lines: lines.length }, outputs: { total: saved.total }, result: 'saved' });
      res.json({ success: true, ...saved });
    } catch (err) {
      res.status(err.status || 400).json({ error: 'budget_save_failed', message: err.message });
    }
  }));

  /* ------------------------------- groq llm ------------------------------- */
  app.get('/api/llm/status', wrap(async (req, res) => {
    const stats = await groq.status();
    const runs = db.state.runs.reduce((acc, r) => {
      if (!r.llm) return acc;
      acc.sections += r.llm.sectionsFromLLM || 0;
      acc.promptTokens += r.llm.promptTokens || 0;
      acc.completionTokens += r.llm.completionTokens || 0;
      acc.fallbacks += r.llm.fallbacks || 0;
      return acc;
    }, { sections: 0, promptTokens: 0, completionTokens: 0, fallbacks: 0 });
    res.json({
      ...stats,
      provider: groq.provider(),
      status: stats.configured ? 'active' : 'api_key_pending_in_env',
      drafting: llmDrafting.isEnabled(),
      concurrency: Number(process.env.AURA_LLM_CONCURRENCY || 1),
      runs,
    });
  }));

  app.post('/api/llm/generate', wrap(async (req, res) => {
    const { prompt, systemPrompt, maxTokens, temperature, json } = req.body || {};
    if (!prompt) return res.status(400).json({ error: 'prompt_required' });
    const result = await groq.callGroq({
      prompt,
      systemPrompt,
      maxTokens: maxTokens || 600,
      temperature,
      json: Boolean(json),
      reasoningEffort: 'low',
    });
    res.json(result);
  }));

  /* ------------------------------- intake -------------------------------- */
  app.post('/api/intake/clarify', (req, res) => {
    const { request = '', params = {} } = req.body || {};
    res.json(engine.clarify({ request, params: { ...params, consent: params.consent ?? req.body?.consent } }));
  });

  app.post('/api/plan/preview', (req, res) => {
    const { request = '', params = {} } = req.body || {};
    const clarified = engine.clarify({ request, params: { ...params, consent: true } });
    const specialist = specialists.getSpecialist(clarified.clarified.fundingType === 'industry' ? 'industry' : clarified.clarified.fundingType === 'international' ? 'international' : 'government');
    const plan = skills.buildPlan({
      researchArea: clarified.clarified.researchArea,
      keywords: clarified.clarified.keywords,
      callId: 'pending',
      callTitle: `${clarified.clarified.fundingType || 'government'} call (to be matched)`,
      domain: specialist.id,
      requestedBudget: clarified.clarified.requestedBudget,
      durationMonths: clarified.clarified.durationMonths,
      sections: params.sections && params.sections.length ? params.sections.filter((s) => specialist.sections.includes(s)) : specialist.sections,
      retryBudget: config.retryBudget,
    });
    res.json({ clarified: clarified.clarified, plan, specialist: { id: specialist.id, label: specialist.label, description: specialist.description } });
  });

  /* -------------------------------- runs --------------------------------- */
  app.post('/api/runs', wrap(async (req, res) => {
    const actor = actorFrom(req);
    const { request = '', params = {}, consent = false, faults = [], sections = [] } = req.body || {};
    const check = engine.clarify({ request, params: { ...params, consent } });
    if (!check.complete) return res.status(422).json({ error: 'intake_incomplete', intake: check });
    if (params.researcherIds !== undefined) {
      const directory = await researchers.currentDirectory();
      params.researcherIds = researchers.validateSelection(directory, params.researcherIds);
      params.researcherSelection = params.researcherIds.map((id) => ({ id, name:directory.resolve(id).Name }));
    }
    if (params.budgetLines && (!Array.isArray(params.budgetLines) || params.budgetLines.some(l=>!String(l.requirement||'').trim() || !Number.isSafeInteger(Number(l.cost)) || Number(l.cost)<=0 || (l.category && !['personnel','equipment','consumables','travel','other'].includes(l.category))))) return res.status(422).json({message:'Each budget line requires a description, positive whole-INR amount and valid expense category.'});
    const run = await engine.startRun({ request, params, consent, actorId: actor.id, faults });
    if (Array.isArray(sections) && sections.length) run.sections = sections;
    res.status(201).json({ run: engine.serializeRun(run) });
  }));

  app.get('/api/runs', (req, res) => {
    const { status, q, mine } = req.query;
    const actor = actorFrom(req);
    let runs = [...db.state.runs].filter((run) => canRead(actor, run)).reverse();
    if (mine === 'true' || mine === '1') {
      runs = runs.filter((r) => r.actorId === actor.id || (r.actor && r.actor.id === actor.id));
    }
    if (status) runs = runs.filter((r) => r.status === status);
    if (q) runs = runs.filter((r) => `${r.id} ${r.params?.researchArea || ''} ${r.draft?.title || ''}`.toLowerCase().includes(String(q).toLowerCase()));
    res.json({ runs: runs.map(engine.summarizeRun) });
  });

  app.get('/api/runs/:id', (req, res) => {
    const run = db.getRun(req.params.id);
    if (!run) return res.status(404).json({ error: 'not_found', message: 'Run not found' });
    res.json({ run: engine.serializeRun(run) });
  });

  app.post('/api/runs/:id/resume', wrap(async (req, res) => {
    const run = db.getRun(req.params.id);
    if (!run) return res.status(404).json({ error: 'not_found' });
    const updated = await engine.resumeRun(run);
    res.json({ run: engine.serializeRun(updated) });
  }));

  /**
   * Lab 12 — faculty revision before the Dean sees the package. The PI may
   * rewrite one or more sections; the revision is re-validated, re-packaged and
   * returned to the approval queue.
   */
  app.put('/api/runs/:id/draft', wrap(async (req, res) => {
    const run = db.getRun(req.params.id);
    if (!run) return res.status(404).json({ error: 'not_found' });
    const actor = actorFrom(req);
    const canEdit = actor.id === run.actor?.id || actor.role === 'admin';
    if (!canEdit) return res.status(403).json({ error: 'forbidden', message: 'Only the owning PI may revise this draft.' });
    if (!['published','awaiting_review', 'changes_requested', 'needs_human'].includes(run.status)) {
      return res.status(409).json({ error: 'not_revisable', message: `Run is "${run.status}"; revisions are accepted before Dean sign-off.` });
    }
    const edits = Array.isArray(req.body?.sections) ? req.body.sections : [];
    if (!edits.length) return res.status(422).json({ error: 'no_sections', message: 'Provide at least one section revision.' });

    const revised = structuredClone(run.draft);
    const applied = [];
    for (const edit of edits) {
      const section = revised?.sections?.find((s) => s.key === edit.key);
      const text = String(edit.text || '').trim();
      if (!section) return res.status(422).json({ error: 'unknown_section', message: `Unknown section "${edit.key}".` });
      const words = text.split(/\s+/).filter(Boolean).length;
      if (!words) return res.status(422).json({ error: 'empty_section', message: `Section "${edit.key}" cannot be empty.` });
      const unit = run.plan?.units?.find((u) => u.key === edit.key);
      if (unit && words < unit.minWords) {
        return res.status(422).json({ error: 'section_too_short', message: `Section "${edit.key}" needs at least ${unit.minWords} words.` });
      }
      section.paragraphs = [{ text, claimIds: [] }];
      section.wordCount = words;
      section.updatedBy = `faculty:${actor.name}`;
      section.facultyEdited = true;
      revised.claims = (revised.claims || []).filter((c) => c.sectionKey !== edit.key);
      applied.push(edit.key);
    }
    require('./proposal-activity').invalidate(run,'Faculty revised the narrative');
    run.draft = revised;
    run.draft.version = (run.draft.version || 1) + 1;
    run.draft.wordCount = run.draft.sections.reduce((a, s) => a + s.wordCount, 0);
    run.draft.citations = require('./core').skills.citationIndex(run.draft);
    run.draft.facultyRevisedAt = util.nowIso();
    run.draft.facultyRevisedBy = actor.name;
    run.updatedAt = util.nowIso();
    run.status = 'changes_requested';
    db.audit({ runId: run.id, actor: actor.name, actorId: actor.id, actorEmail: actor.email, agent: 'drafting', phase: 'revision', intent: `Faculty revised ${applied.length} section(s) before Dean review`, action: 'draft.revise', inputs: { sections: applied }, outputs: { draftVersion: run.draft.version }, result: 'revised' });

    const updated = await engine.resumeRun(run);
    res.json({ run: engine.serializeRun(updated), revised: applied });
  }));

  app.post('/api/runs/:id/inject', wrap(async (req, res) => {
    const run = db.getRun(req.params.id);
    if (!run) return res.status(404).json({ error: 'not_found' });
    if (['published', 'rejected'].includes(run.status)) return res.status(409).json({ error: 'immutable', message: 'A published or rejected run cannot be fault-injected.' });
    run.faults = req.body?.faults || [];
    engine.injectFaults(run, runtime.createContext(run, run.actor));
    const updated = await engine.resumeRun(run);
    res.json({ run: engine.serializeRun(updated) });
  }));

  app.put('/api/runs/:id/budget',wrap(async(req,res)=>{
    const run=structuredClone(db.getRun(req.params.id)),actor=req.actor;
    if(!run)return res.status(404).json({error:'not_found'});
    if(run.status==='running')return res.status(409).json({message:'Wait for active execution to finish before changing costs.'});
    if(run.actor?.id!==actor.id&&!actor.permissions.includes('review:approve'))return res.status(403).json({error:'forbidden'});
    const lines=req.body?.lines;
    if(req.body?.confirm!==true||!Array.isArray(lines)||!lines.length||lines.some(l=>!String(l.requirement||'').trim()||!Number.isSafeInteger(Number(l.cost))||Number(l.cost)<=0||!['personnel','equipment','consumables','travel','other'].includes(l.category)))return res.status(422).json({message:'Confirm positive whole-INR line amounts and explicit categories.'});
    if(!run.discovery?.selectedCall||!run.params)return res.status(409).json({message:'This historical snapshot lacks call/input context. Export its saved content or create a new proposal; current context will not be substituted.'});
    const before=structuredClone(run.budget);if(!before)return res.status(409).json({message:'Wait for a selected funding call and budget.'});
    require('./proposal-activity').invalidate(run,'Faculty explicitly corrected the working budget');
    run.budgetBeforeFault=null;run.faults=[];run.budgetAlternatives=[];
    run.budgetChanges=run.budgetChanges||[];run.budgetChanges.push({at:util.nowIso(),by:actor.id,before,submitted:structuredClone(lines)});
    run.params.budgetLines=structuredClone(lines);run.params.requestedBudget=lines.reduce((sum,l)=>sum+Number(l.cost),0);
    run.budget.lines=lines.map((l,i)=>({id:`b-faculty-${i+1}`,category:l.category,item:l.requirement,amount:Number(l.cost),quantity:1,unitCost:Number(l.cost),basis:'Explicit faculty correction; original input and approved history retained'}));
    run.budget.facultyOwned=true;run.budget.flags=[];run.budget.justification=[];
    await require('./agents').budget.run(runtime.createContext(run,run.actor));run.stage='validation';
    db.state.runs[db.state.runs.findIndex(r=>r.id===run.id)]=run;
    db.audit({runId:run.id,actor:actor.name,actorId:actor.id,action:'budget.correct',result:'review_required'});db.persist();
    res.json({run:engine.serializeRun(run)});
  }));
  app.post('/api/runs/:id/budget/accept', wrap(async(req,res)=>{
    const run=structuredClone(db.getRun(req.params.id)),actor=req.actor;
    if(!run)return res.status(404).json({error:'not_found'});
    if(run.status==='running')return res.status(409).json({message:'Wait for active execution to finish before changing costs.'});
    if(run.actor?.id!==actor.id && !actor.permissions.includes('review:approve'))return res.status(403).json({error:'forbidden'});
    const alternative=(run.budgetAlternatives||[]).find(a=>a.id===req.body?.alternativeId);
    if(!alternative || req.body?.confirm!==true)return res.status(422).json({message:'Choose and explicitly confirm a recorded budget alternative.'});
    if(alternative.sourceBudgetHash!==util.sha256(JSON.stringify({lines:run.budget.lines,rules:run.budget.rules})))return res.status(409).json({message:'This alternative is stale. Recompute it against the current working budget.'});
    const before=structuredClone(run.budget);
    require('./proposal-activity').invalidate(run,'Faculty accepted budget alternative '+alternative.id);
    run.budget.lines=structuredClone(alternative.lines);
    run.params.budgetLines=alternative.lines.map(l=>({requirement:l.item,cost:l.amount,category:l.category}));
    run.budgetBeforeFault=null;run.faults=[];run.budgetAlternatives=[];
    run.budgetChanges=run.budgetChanges||[];run.budgetChanges.push({at:util.nowIso(),by:actor.id,alternativeId:alternative.id,before});
    run.params.requestedBudget=run.params.budgetLines.reduce((sum,l)=>sum+l.cost,0);
    await require('./agents').budget.run(runtime.createContext(run,run.actor));run.stage='validation';
    db.state.runs[db.state.runs.findIndex(r=>r.id===run.id)]=run;
    db.audit({runId:run.id,actor:actor.name,actorId:actor.id,action:'budget.alternative.accept',inputs:{alternativeId:alternative.id},result:'review_required'});
    db.persist();res.json({run:engine.serializeRun(run)});
  }));

  app.post('/api/runs/:id/review', wrap(async (req, res) => {
    const run = db.getRun(req.params.id);
    if (!run) return res.status(404).json({ error: 'not_found' });
    const actor = actorFrom(req);
    const { decision = 'approve', notes = '', edits = null, expectedChecksum } = req.body || {};
    if (expectedChecksum !== run.package?.checksum) return res.status(409).json({ error: 'stale_package', message: 'Reload the current package before review.' });
    const updated = engine.governance.approveRun(run, actor, { decision, notes, edits });
    res.json({ run: engine.serializeRun(updated) });
  }));

  app.post('/api/runs/:id/rollback', wrap(async (req, res) => {
    const run = db.getRun(req.params.id);
    if (!run) return res.status(404).json({ error: 'not_found' });
    const actor = actorFrom(req);
    const updated = engine.governance.rollbackRun(run, req.body?.versionId, actor);
    res.json({ run: engine.serializeRun(updated) });
  }));

  app.get('/api/runs/:id/audit', (req, res) => {
    const events = db.state.audit.filter((a) => a.runId === req.params.id).reverse().slice(0, 300);
    res.json({ events });
  });

  app.get('/api/runs/:id/files/:name', wrap(async(req,res)=>{
    const run=db.getRun(req.params.id);
    if(!run || !canRead(req.actor,run))return res.status(404).json({error:'not_found'});
    let saved=run,version=run.publishedVersion||run.package?.version||'working';
    const approvedVersion=db.state.versions.find(v=>v.runId===run.id&&v.v===run.publishedVersion&&v.checksum===run.package?.checksum);
    if(approvedVersion)saved=approvedVersion.snapshot;
    else if(req.query.version===undefined&&run.package&&(run.package.artifactHash!==require('./proposal-activity').fingerprint(run) || (run.package.contextHash && run.package.contextHash!==require('./proposal-activity').contextFingerprint(run))))return res.status(409).json({message:'Current package is stale; revalidate or export a saved historical version.'});
    if(req.query.version!==undefined){
      const selected=db.state.versions.find(v=>v.runId===run.id&&(v.id===req.query.version||String(v.v)===req.query.version));
      if(!selected)return res.status(404).json({error:'version_not_found'});
      saved=selected.snapshot;version=selected.v;
    }
    if(!saved.package)return res.status(409).json({message:'No saved package available; revalidate before exporting.'});
    const format=/^proposal\.(docx|pdf)$/.exec(req.params.name)?.[1];
    if(format){
      const exports=require('./exports');
      const bytes=await exports.generate(format,saved,{runId:run.id,version,status:saved.approvals?.decision==='approved'?'Internally approved proposal':'Proposal awaiting approval'});
      res.setHeader('Content-Type',exports.mime[format]);
      res.setHeader('Content-Disposition',`attachment; filename="${run.id}-v${version}-proposal.${format}"`);
      return res.send(bytes);
    }
    const file=saved.package.files?.find(f=>f.name===req.params.name);
    if(!file)return res.status(404).json({error:'not_found'});
    res.setHeader('Content-Type',file.mime||'text/plain');res.setHeader('Content-Disposition',`attachment; filename="${file.name}"`);res.send(file.content);
  }));

  /* ------------------------------ catalogue ------------------------------ */
  app.get('/api/agents', (req, res) => {
    const metrics = engine.metrics.computeMetrics();
    res.json({ agents: AGENTS.map((a) => ({ ...a, activity: metrics.agents.find((m) => m.id === a.id) })) });
  });

  app.get('/api/calls', (req, res) => {
    const { fundingType, agency, status, q } = req.query;
    const calls = CALLS.filter((c) => (!fundingType || c.fundingType === fundingType) && (!agency || c.agency === agency) && (!status || c.status === status) && (!q || `${c.title} ${c.agency} ${c.tags.join(' ')}`.toLowerCase().includes(String(q).toLowerCase())))
      .map((c) => ({ ...c, daysLeft: util.daysBetween(util.today(), c.deadline), active: c.verified && c.status === 'open' && util.daysBetween(util.today(), c.deadline) >= 0 }));
    res.json({ calls });
  });

  app.get('/api/calls/:id', (req, res) => {
    const call = CALLS.find((c) => c.id === req.params.id);
    if (!call) return res.status(404).json({ error: 'not_found' });
    res.json({ call: { ...call, daysLeft: util.daysBetween(util.today(), call.deadline) } });
  });

  app.get('/api/literature', wrap(async (req, res) => {
    const result = await require('./research-sources').search(req.query.q);
    res.json({ literature: result.items, ...result });
  }));
  app.get('/api/college', (req, res) => res.json(require('./college-data').metrics()));
  app.get('/api/college/publications', wrap((req, res) => {
    const { q, page, pageSize, field } = req.query;
    res.json(require('./research-sources').archiveSearch(q, { page, pageSize, field }));
  }));
  app.get('/api/college/grants', (req, res) => {
    const college = require('./college-data');
    res.json({ awards:college.awards, applications:college.applications, metrics:college.metrics() });
  });
  app.get('/api/college/review', (req, res) => res.json(require('./college-data').review || { status:'missing_or_stale' }));

  app.get('/api/policies', (req, res) => res.json({ policies: POLICIES, rules: COMPLIANCE_RULES }));

  app.get('/api/connector', (req, res) => {
    res.json({ catalog: connector.catalog(), log: [...db.state.connectorLog].reverse().slice(0, 60), stats: { calls: db.state.connectorLog.length, sources: connector.catalog().sources.length } });
  });

  app.post('/api/connector/invoke', (req, res) => {
    if (!req.actor.permissions.includes('review:approve')) return res.status(403).json({ error: 'forbidden' });
    const { endpoint, args = {} } = req.body || {};
    if (!endpoint) return res.status(400).json({ error: 'endpoint_required' });
    const result = connector.invoke(endpoint, args, { token: config.connectorToken, actor: actorFrom(req).name, agent: 'console', purpose: 'manual-probe' });
    if (!result.ok) return res.status(result.error.code === 'unauthorized' ? 401 : 400).json(result);
    res.json(result);
  });

  app.get('/api/skills', (req, res) => res.json({ skills: [skills.PLAN_SCHEMA, skills.FORMAT_SCHEMA], note: 'Both skills are case-agnostic: the plan skill is invoked for every funding type, and the format skill renders every completed run.' }));

  /* ------------------------------- metrics -------------------------------- */
  app.get('/api/metrics', (req, res) => res.json(engine.metrics.computeMetrics(req.actor)));

  app.get('/api/audit', (req, res) => {
    const limit = Number(req.query.limit || 100);
    const { runId, agent, level } = req.query;
    let events = [...db.state.audit].filter((event) => req.actor?.permissions?.includes('run:read:all') || (event.runId && canRead(req.actor, db.getRun(event.runId)))).reverse();
    if (runId) events = events.filter((e) => e.runId === runId);
    if (agent) events = events.filter((e) => e.agent === agent);
    if (level) events = events.filter((e) => e.level === level);
    res.json({ events: events.slice(0, limit), total: events.length });
  });

  app.get('/api/versions', (req, res) => {
    const versions = [...db.state.versions].filter((version) => canRead(req.actor, db.getRun(version.runId))).reverse().map(({ snapshot, ...rest }) => ({...rest,missingSnapshotFields:['params','plan','discovery','literature','sourceRecords','documents','validation','acceptance'].filter(key=>snapshot?.[key]==null)}));
    res.json({ versions });
  });

  /* --------------------------------- demo --------------------------------- */
  app.post('/api/demo', wrap(async (req, res) => {
    if (!engine.governance.canApprove(actorFrom(req))) return res.status(403).json({ error: 'forbidden' });
    const seed = require('./seed-demo');
    const created = await seed.seedDemo({ force: Boolean(req.body?.force), actorId: actorFrom(req).id });
    res.json(created);
  }));

  app.use('/api', (req, res) => res.status(404).json({ error: 'not_found', message: `No route for ${req.method} ${req.originalUrl}` }));

  app.use((err, req, res, next) => {
    console.error('[api]', err.message);
    res.status(err.status || 500).json({ error: err.code || 'internal_error', message: err.message });
  });

  return app;
}

module.exports = { createApp, actorFrom };
