'use strict';

require('dotenv').config();
const mongoose = require('mongoose');
const User = require('./models/User');
const { facultyUsers, canonicalFaculty, FACULTY } = require('./faculty');

// No connection string is hard-coded. Set MONGODB_URI in backend/.env (see .env.example).
// When it is empty the app runs on the local JSON fallback store.
const DEFAULT_URI = '';

const SEED_USERS = [
  {
    Name: 'Dr. Uma Mudengudi', Role: 'dean', Dept: 'Office of Dean R&D',
    email: 'uma.mudengudi@mist.edu.in', title: 'Dean, Research & Development',
    userId: 'usr-krishnan', password: 'password123',
    permissions: ['run:create', 'run:read:all', 'review:approve', 'package:view', 'audit:read', 'version:rollback', 'metrics:read'],
  },
  ...facultyUsers().map((f) => ({
    Name: f.name, Role: 'faculty', Dept: f.department, email: f.email,
    title: f.title || 'Faculty Member', userId: f.id, password: 'password123',
    permissions: f.permissions,
  })),
  {
    Name: 'Research & Development Office', Role: 'research_office', Dept: 'Office of Dean R&D',
    email: 'grants.cell@mist.edu.in', title: 'Grants Cell & Compliance',
    userId: 'usr-research-office', password: 'password123',
    permissions: ['run:create', 'run:read:all', 'review:approve', 'package:view', 'audit:read', 'version:rollback'],
  },
  {
    Name: 'Platform Administrator', Role: 'admin', Dept: 'Central IT',
    email: 'admin@mist.edu.in', title: 'AURA Platform Administrator',
    userId: 'usr-admin', password: 'password123',
    permissions: ['run:create', 'run:read:all', 'review:approve', 'audit:read', 'version:rollback', 'metrics:read', 'connector:invoke'],
  },
];

let isConnected = false;
let connectedAt = null;
let lastError = null;
let outcome='not_attempted';
mongoose.connection.on('disconnected',()=>{isConnected=false;outcome='network_failure';lastError='MongoDB disconnected. Local JSON remains active.';});
const safeError=(err)=>{const text=String(err?.message||err||'');if(/auth|bad auth|authentication/i.test(text))return {code:'authentication_rejected',message:'MongoDB rejected authentication. Check the configured account and database access.'};if(/timeout|ENOTFOUND|ECONN|server selection|querySrv/i.test(text))return {code:'network_failure',message:'MongoDB could not be reached. Check network access, DNS and Atlas allowlist.'};return {code:'connection_failure',message:'MongoDB connection failed. Review server-side connection configuration.'};};

async function connectDB() {
  const uri = process.env.MONGODB_URI || process.env.MONGO_URI || DEFAULT_URI;
  if (!uri || uri.includes('<')) {
    outcome=uri?'placeholder_configuration':'not_configured';
    lastError = uri ? 'MONGODB_URI still contains a placeholder' : 'MONGODB_URI is not set';
    console.log('[MongoDB]', lastError, '— using durable local JSON fallback.');
    return false;
  }

  try {
    mongoose.set('strictQuery', false);
    await mongoose.connect(uri, {
      dbName: process.env.MONGODB_DB || 'research_grant',
      serverSelectionTimeoutMS: 15000,
      connectTimeoutMS: 15000,
    });
    isConnected = true;outcome='connected';
    connectedAt = new Date().toISOString();
    lastError = null;
    console.log(`[MongoDB] Connected to ${mongoose.connection.host}/${mongoose.connection.name}`);

    // Upsert institutional people so every actor/approver has a linked user row.
    // Existing rows are updated in place (e.g. a renamed Dean) by userId.
    let inserted = 0;
    for (const u of SEED_USERS) {
      const email = u.email.toLowerCase();
      const existing = await User.findOne({ $or: [{ userId: u.userId }, { email }] });
      if (existing) {
        // Existing institutional records remain authoritative.
      } else {
        await User.create({ ...u, email });
        inserted += 1;
      }
    }
    console.log(`[MongoDB] User collection ready (inserted ${inserted}, updated/kept ${SEED_USERS.length - inserted}).`);
    await User.syncIndexes().catch(() => {});
    return true;
  } catch (err) {
    const diagnostic=safeError(err);outcome=diagnostic.code;lastError=diagnostic.message;
    isConnected = false;
    console.warn(`[MongoDB] Connection notice: ${lastError}. Running with the local file store as fallback.`);
    return false;
  }
}

async function findUserByIdOrEmail(identifier) {
  if (!identifier) return null;
  const raw = String(identifier).trim();
  const idStr = raw.toLowerCase();

  if (isConnected) {
    try {
      const user = await User.findOne({
        $or: [
          { email: idStr },
          { userId: raw },
          { Name: new RegExp(`^${idStr.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}$`, 'i') },
        ],
      });
      if (user) return user;
    } catch {
      // fall through to memory
    }
  }

  return SEED_USERS.find(
    (u) => u.email.toLowerCase() === idStr || u.userId === raw || u.Name.toLowerCase() === idStr,
  ) || null;
}

async function getAllUsers() {
  if (isConnected) {
    try {
      const users = await User.find({ isActive: true }).sort({ Role: 1, Name: 1 });
      if (users.length) return users;
    } catch {
      // fall through
    }
  }
  return SEED_USERS;
}

function status() {
  return {
    configured: Boolean(process.env.MONGODB_URI || process.env.MONGO_URI || DEFAULT_URI),
    outcome, activeStorage:'local_json', mongoRole:'asynchronous workflow mirror when connected', projectStorage:isConnected?'mongodb':'local_json',
    persistence:{runs:true,versions:true,auditEvents:true,projectBudgets:true,facultyLinks:'in saved runs and source catalogs',accounts:'seed configuration without MongoDB; runtime account changes require MongoDB'},
    connected: isConnected,
    database: mongoose.connection?.name || process.env.MONGODB_DB || 'research_grant',
    host: mongoose.connection?.host || null,
    connectedAt,
    error: lastError,
    collections: ['users', 'runs', 'audit_events', 'versions'],
  };
}

module.exports = {
  connectDB,
  User,
  findUserByIdOrEmail,
  getAllUsers,
  SEED_USERS,
  isConnected: () => isConnected,
  status,
  safeError,
  mongoose,
};
