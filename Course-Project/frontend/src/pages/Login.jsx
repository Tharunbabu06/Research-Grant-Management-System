import { useEffect, useMemo, useState } from 'react';
import { endpoints, setActorId, setToken } from '../lib/api';
import { Badge, Btn, Modal } from '../components/ui';
import { Icon } from '../components/icons';
import UniversityBrand from '../components/UniversityBrand';

export default function Login({ onLoginSuccess }) {
  const [users, setUsers] = useState([]);
  const [mongoMeta, setMongoMeta] = useState(null);
  const [, setSchemaMeta] = useState(null);
  const [loadingUsers, setLoadingUsers] = useState(true);

  const [identifier, setIdentifier] = useState('usr-krishnan');
  const [password, setPassword] = useState('password123');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);

  const [search, setSearch] = useState('');
  const [selectedDept, setSelectedDept] = useState('ALL');
  const [showSchemaModal, setShowSchemaModal] = useState(false);

  // Fetch live users and Mongoose schema metadata directly from MongoDB via Mongoose ORM
  useEffect(() => {
    let mounted = true;
    endpoints
      .users()
      .then((res) => {
        if (!mounted) return;
        setUsers(res.users || []);
        setMongoMeta(res.mongo || null);
        setSchemaMeta(res.schema || null);
      })
      .catch((err) => {
        if (!mounted) return;
        console.warn('Failed to load users from MongoDB:', err);
      })
      .finally(() => {
        if (mounted) setLoadingUsers(false);
      });

    return () => {
      mounted = false;
    };
  }, []);

  const doLogin = async (idOrEmail, pwd) => {
    setBusy(true);
    setError(null);
    try {
      const res = await endpoints.login({
        email: idOrEmail,
        password: pwd,
      });
      if (res.success && res.user) {
        setToken(res.token);
        setActorId(res.user.id);
        onLoginSuccess(res.user);
      }
    } catch (err) {
      setError(err.message || 'Authentication failed. Please verify credentials.');
    } finally {
      setBusy(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!identifier) return;
    doLogin(identifier, password);
  };

  const selectUser = (u) => {
    const loginKey = u.email || u.id;
    setIdentifier(loginKey);
    setPassword('password123');
    doLogin(u.id || u.email, 'password123');
  };

  // Distinct departments for filtering
  const departments = useMemo(() => {
    const set = new Set();
    users.forEach((u) => {
      if (u.Dept) set.add(u.Dept);
    });
    return ['ALL', ...Array.from(set).sort()];
  }, [users]);

  // Filtered list based on search and selected department
  const filteredUsers = useMemo(() => {
    const q = search.trim().toLowerCase();
    return users.filter((u) => {
      const matchDept = selectedDept === 'ALL' || u.Dept === selectedDept;
      const matchSearch =
        !q ||
        (u.Name && u.Name.toLowerCase().includes(q)) ||
        (u.email && u.email.toLowerCase().includes(q)) ||
        (u.Dept && u.Dept.toLowerCase().includes(q)) ||
        (u.Role && u.Role.toLowerCase().includes(q)) ||
        (u.title && u.title.toLowerCase().includes(q));
      return matchDept && matchSearch;
    });
  }, [users, selectedDept, search]);

  const roleTone = (role) => {
    if (role === 'dean') return 'violet';
    if (role === 'research_office') return 'teal';
    if (role === 'admin') return 'amber';
    return 'indigo';
  };

  const roleLabel = (role) => {
    if (role === 'dean') return 'Dean R&D';
    if (role === 'research_office') return 'Grants Cell';
    if (role === 'admin') return 'System Admin';
    return 'Faculty PI';
  };

  return (
    <div className="login-page">
      <div className="login-container">
        {/* Brand header */}
        <div className="login-brand">
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: 12, marginBottom: 8 }}>
            <div className="brand-mark" style={{ width: 44, height: 44, fontSize: 16 }}>
              GO
            </div>
            <div style={{ textAlign: 'left' }}>
              <div className="login-brand-name">
                GrantOffice
              </div>
              <div className="login-brand-sub">
                Research Grant Management System
              </div>
            </div>
          </div>
          <UniversityBrand><div className="login-institution">
            KLE Technological University · Local practice portal
          </div></UniversityBrand>
        </div>

        {/* Main Card */}
        <div className="login-layout">
          {/* Left panel: Live MongoDB Users Directory */}
          <div className="login-directory">
            {/* Header & Mongo live indicator */}
            <div className="login-directory-head">
              <div>
                <div className="eyebrow" style={{ color: 'var(--indigo)', marginBottom: 2 }}>
                  Practice account directory
                </div>
                <h3 style={{ margin: 0, fontSize: 16.5, color: 'var(--ink)' }}>
                  Institutional Accounts ({users.length})
                </h3>
              </div>
              <Btn
                size="sm"
                variant="ghost"
                icon="code"
                onClick={() => setShowSchemaModal(true)}
                title="View Mongoose Schema & MongoDB Collection"
                style={{ fontSize: 11, padding: '4px 8px' }}
              >
                Mongoose Schema
              </Btn>
            </div>

            {/* Live MongoDB Status Banner */}
            <div className="login-status">
              <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                <span
                  style={{
                    width: 7,
                    height: 7,
                    borderRadius: '50%',
                    background: '#10b981',
                    display: 'inline-block',

                  }}
                />
                <b>{mongoMeta?.connected?'MongoDB connected':'Local JSON storage'}</b> · Mongoose ORM (<span className="mono">User</span> schema)
              </div>
              <span className="mono" style={{ fontSize: 10, color: '#047857' }}>
                {mongoMeta?.database || 'research_grant'}.users
              </span>
            </div>

            {/* Search Input */}
            <div style={{ position: 'relative', marginBottom: 10 }}>
              <input
                type="text"
                className="input"
                aria-label="Search practice accounts"
                placeholder="Search faculty by name, department, or email…"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                style={{ fontSize: 12.5, paddingLeft: 30, height: 34 }}
              />
              <span style={{ position: 'absolute', left: 10, top: 9, color: 'var(--muted)', pointerEvents: 'none' }}>
                <Icon name="search" size={13} />
              </span>
              {search && (
                <button
                  onClick={() => setSearch('')}
                  aria-label="Clear account search"
                  style={{
                    position: 'absolute',
                    right: 8,
                    top: 8,
                    background: 'none',
                    border: 'none',
                    cursor: 'pointer',
                    color: 'var(--muted)',
                    fontSize: 12,
                  }}
                >
                  ✕
                </button>
              )}
            </div>

            {/* Department Filter Chips */}
            <div className="login-departments">
              {departments.map((dept) => (
                <button
                  key={dept}
                  type="button"
                  onClick={() => setSelectedDept(dept)}
                  className={`login-department ${selectedDept === dept ? 'on' : ''}`}
                >
                  {dept === 'ALL' ? `All (${users.length})` : dept}
                </button>
              ))}
            </div>

            {/* Faculty List (Live from MongoDB via Mongoose) */}
            <div
              style={{
                flex: 1,
                overflowY: 'auto',
                display: 'flex',
                flexDirection: 'column',
                gap: 8,
                paddingRight: 4,
              }}
            >
              {loadingUsers && (
                <div style={{ textAlign: 'center', padding: '36px 0', color: 'var(--muted)', fontSize: 13 }}>
                  <Icon name="refresh" size={18} className="spin" style={{ marginBottom: 8 }} />
                  <div>Loading institutional accounts…</div>
                </div>
              )}

              {!loadingUsers && filteredUsers.length === 0 && (
                <div style={{ textAlign: 'center', padding: '32px 12px', color: 'var(--muted)', fontSize: 12.5 }}>
                  No faculty match "{search}".
                  <div style={{ marginTop: 8 }}>
                    <Btn size="sm" variant="ghost" onClick={() => { setSearch(''); setSelectedDept('ALL'); }}>
                      Reset filters
                    </Btn>
                  </div>
                </div>
              )}

              {!loadingUsers &&
                filteredUsers.map((u) => {
                  const isCurrent = identifier === u.email || identifier === u.id;
                  return (
                    <button
                      type="button"
                      className={`login-user ${isCurrent ? 'selected' : ''}`}
                      key={u.id || u._id}
                      onClick={() => selectUser(u)}

                      onMouseEnter={(e) => {
                        if (!isCurrent) {
                          e.currentTarget.style.borderColor = '#818cf8';
                          e.currentTarget.style.background = '#fafafa';
                        }
                      }}
                      onMouseLeave={(e) => {
                        if (!isCurrent) {
                          e.currentTarget.style.borderColor = '#e2e8f0';
                          e.currentTarget.style.background = '#fff';
                        }
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 2 }}>
                        <span style={{ fontWeight: 650, fontSize: 13, color: 'var(--ink)' }}>{u.Name}</span>
                        <Badge tone={roleTone(u.Role)}>{roleLabel(u.Role)}</Badge>
                      </div>
                      <div style={{ fontSize: 11, color: 'var(--muted)', marginBottom: 2 }}>
                        {u.Dept} · <span className="mono">{u.email}</span>
                      </div>
                      {u.title && (
                        <div style={{ fontSize: 10.5, color: 'var(--ink-2)', lineHeight: 1.3 }}>
                          {u.title}
                        </div>
                      )}
                    </button>
                  );
                })}
            </div>

            <div className="login-directory-foot">
              <span>Showing {filteredUsers.length} of {users.length} accounts</span>
              <span className="mono">source: mongodb · orm: mongoose</span>
            </div>
          </div>

          {/* Right panel: Credentials Sign-In */}
          <div className="login-credentials">
            <div className="eyebrow" style={{ color: 'var(--indigo)', marginBottom: 2 }}>Governed Authentication</div>
            <h3 style={{ margin: '0 0 4px', fontSize: 20, color: 'var(--ink)' }}>Account Sign In</h3>
            <p style={{ margin: '0 0 20px', fontSize: 12.5, color: 'var(--muted)' }}>
              Sign in with institutional credentials or select an account from the institutional directory.
            </p>

            {error && (
              <div className="callout danger" style={{ marginBottom: 16, padding: '10px 12px' }}>
                <Icon name="alert" size={15} />
                <div style={{ fontSize: 12 }}>{error}</div>
              </div>
            )}

            <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              <div className="field">
                <label htmlFor="login-identifier">Institutional Email / User ID</label>
                <input
                  type="text"
                  id="login-identifier"
                  autoComplete="username"
                  className="input"
                  placeholder="e.g. uma.mudengudi@mist.edu.in"
                  value={identifier}
                  onChange={(e) => setIdentifier(e.target.value)}
                  required
                />
              </div>

              <div className="field">
                <label htmlFor="login-password">Password</label>
                <input
                  type="password"
                  id="login-password"
                  autoComplete="current-password"
                  className="input"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
                <span className="hint">
                  Default institutional password: <span className="mono">password123</span>
                </span>
              </div>

              <Btn
                variant="primary"
                size="lg"
                type="submit"
                disabled={busy}
                style={{ marginTop: 8 }}
                icon={busy ? 'refresh' : 'check'}
              >
                {busy ? 'Authenticating…' : 'Sign In to AURA'}
              </Btn>
            </form>

            <div
              style={{
                marginTop: 28,
                paddingTop: 16,
                borderTop: '1px solid var(--line)',
                fontSize: 11.5,
                color: 'var(--muted)',
                lineHeight: 1.5,
              }}
            >
              <b>Access Control Policy:</b> Sessions use the configured institutional account store; fallback accounts are seed configuration, not live MongoDB records. Actions are signed and recorded into immutable audit logs.
            </div>
          </div>
        </div>
      </div>

      {/* Mongoose Schema & Database Inspector Modal */}
      {showSchemaModal && (
        <Modal
          open={showSchemaModal}
          title="MongoDB Mongoose Schema Inspector"
          subtitle="Mongoose schema metadata; connection and active storage status shown separately"
          onClose={() => setShowSchemaModal(false)}
          width={760}
        >
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            {/* Live Connection Banner */}
            <div className="grid g4 summary-strip">
              <div className="card stat" style={{ padding: '10px 12px' }}>
                <div className="stat-label">ORM</div>
                <div className="stat-value" style={{ fontSize: 16 }}>Mongoose 9.x</div>
                <div className="stat-foot">Object-Document Mapper</div>
              </div>
              <div className="card stat" style={{ padding: '10px 12px' }}>
                <div className="stat-label">Database</div>
                <div className="stat-value mono" style={{ fontSize: 14 }}>{mongoMeta?.database || 'research_grant'}</div>
                <div className="stat-foot">MongoDB Atlas Cluster</div>
              </div>
              <div className="card stat" style={{ padding: '10px 12px' }}>
                <div className="stat-label">Collection</div>
                <div className="stat-value mono" style={{ fontSize: 14 }}>users</div>
                <div className="stat-foot">{users.length} configured accounts</div>
              </div>
              <div className="card stat" style={{ padding: '10px 12px' }}>
                <div className="stat-label">Status</div>
                <div className="stat-value" style={{ fontSize: 14, color: '#059669' }}>{mongoMeta?.connected?'Connected':'Fallback'}</div>
                <div className="stat-foot">{mongoMeta?.connected?'MongoDB connected':'Local JSON active'}</div>
              </div>
            </div>

            {/* Mongoose Schema Definition */}
            <div>
              <div className="stat-label" style={{ marginBottom: 6 }}>
                Mongoose User Schema (<span className="mono">backend/src/models/User.js</span>)
              </div>
              <pre
                className="code"
                style={{
                  background: '#0f172a',
                  color: '#e2e8f0',
                  padding: 14,
                  borderRadius: 10,
                  fontSize: 11.5,
                  maxHeight: 240,
                  overflowY: 'auto',
                  lineHeight: 1.45,
                }}
              >
{String.raw`const mongoose = require('mongoose');

const UserSchema = new mongoose.Schema({
  Name: {
    type: String,
    required: [true, 'Name is required'],
    trim: true,
  },
  Role: {
    type: String,
    required: [true, 'Role is required'],
    enum: ['dean', 'pi', 'faculty', 'research_office', 'admin'],
    trim: true,
    lowercase: true,
  },
  Dept: {
    type: String,
    required: [true, 'Department is required'],
    trim: true,
  },
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
  careerStage: {
    type: String,
    enum: ['assistant', 'associate', 'professor', 'n/a'],
    default: 'associate'
  },
  monthlyCost: { type: Number, default: 150000 },
  isActive: { type: Boolean, default: true },
}, { timestamps: true });

module.exports = mongoose.models.User || mongoose.model('User', UserSchema);`}
              </pre>
            </div>

            {/* Schema Required Fields Table */}
            <div>
              <div className="stat-label" style={{ marginBottom: 6 }}>
                Enforced Mongoose Schema Paths &amp; Constraints
              </div>
              <table className="table" style={{ fontSize: 11.5 }}>
                <thead>
                  <tr>
                    <th>Field Path</th>
                    <th>BSON / Mongoose Type</th>
                    <th>Required</th>
                    <th>Constraints &amp; Enums</th>
                    <th>Description</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td className="mono strong">Name</td>
                    <td className="mono">String</td>
                    <td><Badge tone="green">Required</Badge></td>
                    <td>trim: true</td>
                    <td>Faculty full name with academic honorific</td>
                  </tr>
                  <tr>
                    <td className="mono strong">Role</td>
                    <td className="mono">String</td>
                    <td><Badge tone="green">Required</Badge></td>
                    <td className="mono">['dean', 'pi', 'faculty', 'research_office', 'admin']</td>
                    <td>Institutional role for RBAC permissions</td>
                  </tr>
                  <tr>
                    <td className="mono strong">Dept</td>
                    <td className="mono">String</td>
                    <td><Badge tone="green">Required</Badge></td>
                    <td>trim: true</td>
                    <td>Academic department / school</td>
                  </tr>
                  <tr>
                    <td className="mono strong">email</td>
                    <td className="mono">String</td>
                    <td><Badge tone="green">Required</Badge></td>
                    <td className="mono">unique: true, lowercase: true</td>
                    <td>Institutional email address</td>
                  </tr>
                  <tr>
                    <td className="mono">userId</td>
                    <td className="mono">String</td>
                    <td><Badge tone="neutral">Optional</Badge></td>
                    <td className="mono">sparse: true</td>
                    <td>Canonical system identifier (e.g. usr-suneeta-v-budihal)</td>
                  </tr>
                  <tr>
                    <td className="mono">permissions</td>
                    <td className="mono">[String]</td>
                    <td><Badge tone="neutral">Default</Badge></td>
                    <td>Dynamic role tokens</td>
                    <td>RBAC capabilities (e.g. run:create, review:approve)</td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: 4 }}>
              <Btn variant="primary" onClick={() => setShowSchemaModal(false)}>
                Close Inspector
              </Btn>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
}
