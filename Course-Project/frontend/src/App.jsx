import { useEffect, useMemo, useState } from 'react';
import { endpoints, getActorId, setActorId, getToken, clearAuth } from './lib/api';
import { initials } from './lib/format';
import { Icon } from './components/icons';
import UniversityBrand from './components/UniversityBrand';
import { Badge, Btn, ToastProvider } from './components/ui';
import Dashboard from './pages/aura-dashboard';
import Projects from './pages/aura-projects';
import Intake from './pages/aura-intake';
import Runs from './pages/aura-runs';
import RunDetail from './pages/aura-rundetail';
import Agents from './pages/aura-agents';
import Calls from './pages/aura-calls';
import Platform from './pages/aura-platform';
import Governance from './pages/aura-governance';
import Audit from './pages/aura-audit';
import Login from './pages/Login';
import Research from './pages/Research';
import People from './pages/aura-people';

import { AppContext } from './context/AppContext';

function useHashRoute() {
  const [hash, setHash] = useState(() => window.location.hash || '#/projects');
  useEffect(() => {
    const onChange = () => setHash(window.location.hash || '#/projects');
    window.addEventListener('hashchange', onChange);
    if (!window.location.hash) window.location.hash = '#/projects';
    return () => window.removeEventListener('hashchange', onChange);
  }, []);
  const path = (hash.replace(/^#/, '') || '/projects').split('?')[0];
  const parts = path.split('/').filter(Boolean);
  const navigate = (to) => {
    const next = to.startsWith('#') ? to : `#${to.startsWith('/') ? '' : '/'}${to}`;
    if (window.location.hash === next) setHash(next);
    window.location.hash = next;
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };
  return { path, parts, navigate };
}

export default function App() {
  const route = useHashRoute();
  const [bootstrap, setBootstrap] = useState(null);
  const [error, setError] = useState(null);
  const [actorId, setActor] = useState(getActorId());
  const [token, setAuthToken] = useState(() => getToken());

  useEffect(() => {
    endpoints.bootstrap().then(setBootstrap).catch(setError);
  }, []);

  useEffect(() => {
    if (actorId) {
      setActorId(actorId);
    }
  }, [actorId]);

  const actor = useMemo(
    () => bootstrap?.users?.find((u) => u.id === actorId) || bootstrap?.users?.[0] || null,
    [bootstrap, actorId]
  );

  useEffect(() => {
    const expired = () => { setAuthToken(''); setActor(null); };
    window.addEventListener('grantoffice:expired', expired);
    return () => window.removeEventListener('grantoffice:expired', expired);
  }, []);

  const isDean = ['dean','research_office','admin'].includes(actor?.role);
  const can = (perm) => Boolean(actor?.permissions?.includes(perm));

  const refreshBootstrap = () => endpoints.bootstrap().then(setBootstrap).catch(() => {});

  const handleLogout = async () => {
    try {
      await endpoints.logout();
    } catch {
      // Clear the local session even if the logout endpoint is unavailable.
    }
    clearAuth();
    setAuthToken(null);
    setActor(null);
    window.location.hash = '#/projects';
  };

  const handleLoginSuccess = (user) => {
    setActor(user.id);
    setActorId(user.id);
    setAuthToken(getToken());
    route.navigate('/projects');
    refreshBootstrap();
  };

  if (error) {
    return (
      <div className="page" style={{ maxWidth: 560, paddingTop: 80 }}>
        <div className="callout danger">
          <Icon name="alert" />
          <div>
            <b>Cannot reach the AURA API.</b>
            <p style={{ margin: '4px 0 0' }}>
              {error.message}. Start the backend with <span className="mono">npm start</span> in <span className="mono">backend/</span>.
            </p>
          </div>
        </div>
        <Btn style={{ marginTop: 14 }} icon="refresh" onClick={() => window.location.reload()}>Retry</Btn>
      </div>
    );
  }

  if (!bootstrap) {
    return (
      <div className="startup">
        <div>
          <div className="brand-mark" style={{ margin: '0 auto 14px', width: 44, height: 44, fontSize: 16 }}>GO</div>
          <div className="strong" style={{ fontSize: 16 }}>Loading GrantOffice…</div>
          <div className="tiny" style={{ marginTop: 6, color: 'var(--muted)' }}>Connecting to governed connector and statutory catalog</div>
        </div>
      </div>
    );
  }

  // If not authenticated, display institutional login view
  if (!token) {
    return <Login onLoginSuccess={handleLoginSuccess} />;
  }

  const active = route.parts[0] || 'projects';
  const counts = {
    activeRuns: bootstrap.metrics.totals.runs - bootstrap.metrics.totals.published - bootstrap.metrics.totals.rejected,
    awaiting: bootstrap.metrics.totals.awaitingReview,
  };

  const TITLES = {
    projects: ['Historical Projects', 'All approved institutional grants · Year, department, PI, agency, budget'],
    dashboard: isDean
      ? ['Dean R&D Executive Dashboard', 'Institutional Grant Portfolio & Authority Sign-Off Gate']
      : ['Faculty Research Dashboard', `Personal Proposal Workspace · ${actor?.name || 'Faculty Member'}`],
    runs: isDean ? ['All Institutional Runs', 'Every proposal across departments'] : ['My Proposals & Runs', 'Active drafts, reviews, and approved submissions'],
    new: ['New Proposal Intake', 'Intake brief → planner clarification → 8-agent execution'],
    calls: ['Funding Calls', 'Course practice call catalogue'],
    agents: ['Eight-Agent Architecture', 'The 8-agent operating model and guardrails'],
    governance: ['Approvals & Versions', 'Human authority sign-off gate and reversible rollback'],
    audit: ['Execution Audit Trail', 'Immutable intent → action → result runtime log'],
    research: ['Literature & Novelty', 'OpenAlex, Crossref and the college archive'],
    people: ['Faculty Profiles', 'Institutional researcher directory'],
    platform: ['Platform & Runtime', 'Governed connector, typed tools, and 14-lab architecture'],
  };

  const [title] = TITLES[active] || TITLES.dashboard;

  const NAV = [
    {
      label: 'Workspace',
      items: [
        {
          id: 'dashboard',
          label: isDean ? 'Dean Dashboard' : 'Faculty Dashboard',
          icon: isDean ? 'shield' : 'dashboard',
          to: '/dashboard',
        },
        { id: 'projects', label: 'Projects', icon: 'layers', to: '/projects' },
        {
          id: 'runs',
          label: isDean ? 'Institutional Runs' : 'My Proposals',
          icon: 'file',
          to: '/runs',
          countKey: 'activeRuns',
        },
        { id: 'new', label: 'New proposal', icon: 'sparkles', to: '/new' },
        { id: 'calls', label: 'Funding calls', icon: 'search', to: '/calls' },
      ],
    },
    {
      label: 'Analysis & Review',
      items: [
        { id: 'research', label: 'Literature & Novelty', icon: 'search', to: '/research' },
        { id: 'people', label: 'Faculty Profiles', icon: 'users', to: '/people' },
        { id: 'agents', label: '8 Agents & Stages', icon: 'bot', to: '/agents' },
        {
          id: 'governance',
          label: isDean ? 'Sign-Off & Releases' : 'Approvals & Status',
          icon: 'shield',
          to: '/governance',
          countKey: isDean ? 'awaiting' : undefined,
        },
        { id: 'audit', label: 'Audit trail', icon: 'activity', to: '/audit' },
        { id: 'platform', label: 'Platform & Labs', icon: 'layers', to: '/platform' },
      ],
    },
  ];

  const ctx = {
    ...bootstrap,
    bootstrap,
    actor,
    actorId,
    setActor,
    isDean,
    can,
    navigate: route.navigate,
    refreshBootstrap,
    handleLogout,
  };

  return (
    <AppContext.Provider value={ctx}>
      <ToastProvider>
        <div className="shell">
          <aside className="sidebar">
            <div className="brand">
              <div className="brand-mark">GO</div>
              <div>
                <div className="brand-name">GrantOffice</div>
                <div className="brand-sub">Grant Console</div>
              </div>
            </div>

            {NAV.map((group) => (
              <nav className="nav-group" aria-label={group.label} key={group.label}>
                <div className="nav-label">{group.label}</div>
                {group.items.map((item) => (
                  <a
                    key={item.id}
                    className={`nav-item ${active === item.id ? 'active' : ''}`}
                    aria-current={active === item.id ? 'page' : undefined}
                    href={`#${item.to}`}
                  >
                    <Icon name={item.icon} size={16} />
                    <span>{item.label}</span>
                    {item.countKey && counts[item.countKey] > 0 && (
                      <span className="nav-count">{counts[item.countKey]}</span>
                    )}
                  </a>
                ))}
              </nav>
            ))}

            <div className="sidebar-foot">
              <div className="who">
                <div className="avatar">
                  {initials(actor?.name)}
                </div>
                <div style={{ minWidth: 0, flex: 1 }}>
                  <div className="who-name" style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {actor?.name}
                  </div>
                  <div className="who-role" style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {actor?.title}
                  </div>
                </div>
              </div>
              <div style={{ display: 'flex', gap: 6, padding: '8px 8px 0', alignItems: 'center' }}>
                <Badge tone={isDean ? 'violet' : 'indigo'} dot>
                  {isDean ? 'Dean R&D' : 'Faculty PI'}
                </Badge>
                <div style={{ flex: 1 }} />
                <button
                  type="button"
                  className="btn ghost sm"
                  style={{ color: '#f87171', padding: '3px 8px', fontSize: 11 }}
                  onClick={handleLogout}
                  title="Sign out of AURA"
                >
                  <Icon name="logOut" size={12} /> Sign out
                </button>
              </div>
              <div className="sidebar-note">
                {bootstrap.institution.short} · {bootstrap.counts.calls} calls · {bootstrap.counts.literature} sources
              </div>
            </div>
          </aside>

          <div className="main">
            <header className="topbar">
              <div className="crumbs">
                <span>GrantOffice</span>
                <span className="sep">/</span>
                <b>{title}</b><Badge tone="teal">Practice workflow</Badge>
              </div>
              <div className="topbar-spacer" />

              <div className="topbar-account">
              {/* Role badge */}
              <Badge tone={isDean ? 'violet' : 'indigo'} lg dot>
                {isDean ? 'Dean R&D Authority' : 'Faculty Researcher'}
              </Badge>

              <span className="tiny muted">{actor?.name}</span>
              <Btn variant="primary" size="sm" icon="plus" onClick={() => route.navigate('/new')}>
                New proposal
              </Btn>

              <button
                type="button"
                className="btn ghost sm"
                onClick={handleLogout}
                title="Sign out"
                aria-label="Sign out"
                style={{ padding: '6px 10px' }}
              >
                <Icon name="logOut" size={14} />
              </button>
              </div>
              <UniversityBrand />
            </header>

            <main className="page">
              {active === 'dashboard' && <Dashboard />}
              {active === 'projects' && <Projects />}
              {active === 'runs' && (route.parts[1] ? <RunDetail id={route.parts[1]} /> : <Runs />)}
              {active === 'new' && <Intake />}
              {active === 'research' && <Research />}
              {active === 'people' && <People />}
              {active === 'calls' && <Calls />}
              {active === 'agents' && <Agents />}
              {active === 'governance' && <Governance />}
              {active === 'audit' && <Audit />}
              {active === 'platform' && <Platform />}
              {!['people', 'research', 'dashboard', 'projects', 'runs', 'new', 'calls', 'agents', 'governance', 'audit', 'platform'].includes(active) && (
                <div className="empty">
                  <div className="strong">Page not found</div>
                  <Btn style={{ marginTop: 12 }} onClick={() => route.navigate('/dashboard')}>Back to dashboard</Btn>
                </div>
              )}
            </main>
          </div>
        </div>
      </ToastProvider>
    </AppContext.Provider>
  );
}
