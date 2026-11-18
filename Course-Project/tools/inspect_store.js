'use strict';
// Deliberately bypass connectDB(): the application's connection helper seeds users.
// This inspection issues reads only and never prints credentials or account contents.
const path = require('path');
const fs = require('fs');
require('../backend/node_modules/dotenv').config({ path:path.resolve(__dirname, '../backend/.env'), quiet:true });
const { MongoClient } = require('../backend/node_modules/mongodb');
const college = require('../backend/src/college-data');

(async () => {
  const uri = process.env.MONGODB_URI || process.env.MONGO_URI;
  const result = { mode:'read_only_no_seeding', configured:Boolean(uri), connected:false };
  let client;
  try {
    if (uri) {
      client = new MongoClient(uri, { serverSelectionTimeoutMS:5000, connectTimeoutMS:5000 });
      await client.connect();
      const db = client.db(process.env.MONGODB_DB || 'research_grant');
      const projects = await db.collection('projects').find({}, { projection:{
        _id:0, projectId:1, year:1, department:1, title:1, pi:1, coPIs:1, agency:1,
        amountLakh:1, approved:1, status:1, budgetTotal:1,
      } }).toArray();
      result.connected = true;
      result.projects = projects.map((p) => ({ ...p, id:p.projectId }));
      result.projectCount = projects.length;
      result.registerRowValueInr = projects.reduce((sum, p) => sum + Math.round((Number(p.amountLakh) || 0) * 100000), 0);
      result.reconciliation = college.reconcile(result.projects);
    }
  } catch (error) {
    result.failureCategory = error.name;
    result.note = 'Configured MongoDB was not reachable for read-only verification; no database writes were attempted.';
  } finally {
    if (client) await client.close();
  }
  const file = path.resolve(__dirname, '../docs/local-audits/live-store-inspection.json');
  fs.mkdirSync(path.dirname(file), { recursive:true });
  fs.writeFileSync(file, JSON.stringify(result, null, 2));
  console.log(JSON.stringify({ configured:result.configured, connected:result.connected,
    projectCount:result.projectCount, failureCategory:result.failureCategory }));
})().catch(() => { console.error('Read-only store inspection failed.'); process.exitCode = 1; });
