import { useToast } from '../context/ToastContext';
import { useEffect, useMemo, useState } from 'react';
import { endpoints } from '../lib/api';
import { useApp } from '../context/AppContext';
import { Badge, Btn, Card, Loading, Modal, Table } from '../components/ui';
import { Icon } from '../components/icons';
import { compactMoney, money } from '../lib/format';
import { BudgetEditor } from '../components/BudgetEditor';
import CollegeData from '../components/CollegeData';

const STATUS = <Badge tone="green" dot>Approved</Badge>;

export default function Projects() {
  const { actor } = useApp();
  const toast = useToast();
  const [data, setData] = useState(null);
  const [year, setYear] = useState('all');
  const [dept, setDept] = useState('all');
  const [faculty, setFaculty] = useState('all');
  const [q, setQ] = useState('');
  const [selected, setSelected] = useState(null);
  const [budget, setBudget] = useState([]);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const query = '?' + new URLSearchParams({ q, year, department:dept, faculty });
  const load = () => endpoints.projects(query).then(setData).catch((failure) => setError(failure.message));
  useEffect(() => {
    let active = true;
    const timer = setTimeout(() => endpoints.projects(query).then((result) => { if (active) { setData(result); setError(''); } })
      .catch((failure) => { if (active) setError(failure.message); }), 200);
    return () => { active = false; clearTimeout(timer); };
  }, [query]);

  const cleanActor = useMemo(() => {
    return String(actor?.Name || actor?.name || '')
      .replace(/^(Dr\.|Prof\.|Mr\.|Mrs\.|Ms\.)\s*/i, '')
      .toLowerCase()
      .trim();
  }, [actor]);

  const projects = data?.projects || [];
  const myResearcherId = data?.faculties.find((p) => p.id === actor?.id || p.idAliases.includes(actor?.id) ||
    p.aliases.some((name) => name.replace(/^(Dr\.|Prof\.|Mr\.|Mrs\.|Ms\.)\s*/i, '').toLowerCase().trim() === cleanActor))?.id;

  const myCount = data?.myResearcher?.historicalRegisterCount ?? 0;

  const open = (project) => {
    setSelected(project);
    setBudget(project.budgetLines?.length ? project.budgetLines : [{ requirement: '', cost: '' }]);
  };

  const save = async () => {
    setSaving(true);
    try {
      const res = await endpoints.saveProjectBudget(selected.id, budget);
      toast.push(`Budget saved for ${selected.id} — ${money(res.total)}.`, 'ok');
      setSelected(res.project);
      setBudget(res.project.budgetLines?.length ? res.project.budgetLines : [{ requirement: '', cost: '' }]);
      load();
    } catch (err) {
      toast.push(err.message, 'err');
    } finally {
      setSaving(false);
    }
  };

  if (!data && error) return <Card title="Project portfolio unavailable"><p className="callout danger" role="alert">{error}</p><Btn onClick={load}>Retry</Btn></Card>;
  if (!data) return <Loading label="Loading the historical project portfolio…" />;

  const s = data.summary;

  return (
    <>
      <div className="page-head">
        <div style={{ flex: 1 }}>
          <div className="eyebrow">Institutional portfolio · Historical register</div>
          <h1 className="page-title">Historical Projects</h1>
          <p className="page-sub">
            Historical register rows from 2020-21 to 2023-24, with faculty budgets. College awards and applications appear separately below; overlapping records require review before totals can be combined.
          </p>
        </div>
        <div className="chips">
          <Badge tone="green" dot>{s.approved} registered approved</Badge>
          <Badge tone="indigo">Historical register</Badge>
          <Badge tone="gray">{s.years.length} academic years</Badge>
        </div>
      </div>

      <div className="grid g4 summary-strip" style={{ gap: 12, marginBottom: 16 }}>
        <div className="card stat"><div className="stat-icon tone-indigo"><Icon name="layers" size={15} /></div><div className="stat-label">Projects</div><div className="stat-value">{s.count}</div><div className="stat-foot">historical award records</div></div>
        <div className="card stat"><div className="stat-label">Register row value</div><div className="stat-value">{compactMoney(s.totalLakh * 100000)}</div><div className="stat-foot">{s.totalLakh.toFixed(2)} lakh; overlap review pending</div></div>
        <div className="card stat"><div className="stat-label">Funding agencies</div><div className="stat-value">{s.agencies}</div><div className="stat-foot">SERB · VGST · MeitY · AICTE · DST</div></div>
        <div className="card stat"><div className="stat-label">Departments</div><div className="stat-value">{s.departments}</div><div className="stat-foot">cross-institutional</div></div>
      </div>

      {/* Filter toolbar */}
      <div className="filter-toolbar" role="search" aria-label="Historical register and catalog filters">
        <select aria-label="Academic year" className="select" style={{ width: 140 }} value={year} onChange={(e) => setYear(e.target.value)}>
          <option value="all">All years</option>
          {data.years.map((y) => <option key={y} value={y}>{y}</option>)}
        </select>

        <select aria-label="Department" className="select" style={{ width: 170 }} value={dept} onChange={(e) => setDept(e.target.value)}>
          <option value="all">All departments</option>
          {data.departments.map((d) => <option key={d} value={d}>{d}</option>)}
        </select>

        {/* Dynamic Faculty select pulled live from active storage User collection */}
        <select aria-label="Institutional researcher" className="select" style={{ width: 220 }} value={faculty} onChange={(e) => setFaculty(e.target.value)}>
          <option value="all">All institutional researchers</option>
          {(data.faculties || []).map((f) => (
            <option key={f.id || f.Name} value={f.id}>
              {f.Name} ({f.Dept})
            </option>
          ))}
        </select>

        {cleanActor && (
          <Btn
            size="sm"
            variant={faculty === myResearcherId ? 'primary' : 'ghost'}
            icon="user"
            onClick={() => {
              if (faculty === myResearcherId) {
                setFaculty('all');
              } else {
                setFaculty(myResearcherId || actor?.Name || actor?.name);
              }
            }}
            title="Filter to projects where you are involved"
          >
            My Grants ({myCount})
          </Btn>
        )}

        <div style={{ position: 'relative', flex: '1 1 200px' }}>
          <Icon name="search" size={14} style={{ position: 'absolute', left: 10, top: 10, color: 'var(--faint)' }} />
          <input aria-label="Search projects" className="input" style={{ paddingLeft: 30 }} placeholder="Search title, PI, co-investigator, agency or reference ID" value={q} onChange={(e) => setQ(e.target.value)} />
        </div>

        {(year !== 'all' || dept !== 'all' || faculty !== 'all' || q) && (
          <Btn size="sm" variant="ghost" onClick={() => { setYear('all'); setDept('all'); setFaculty('all'); setQ(''); }}>
            Reset
          </Btn>
        )}

        <span className="tiny">{projects.length} register rows; {data.catalogProjects?.length || 0} catalog records shown</span>
      </div>

      <Card className="historical-results" padded={false}>
        <Table
          columns={[
            { key: 'year', label: 'Year', width: 92, render: (p) => <Badge tone="gray">{p.year}</Badge> },
            { key: 'department', label: 'Dept', width: 80, render: (p) => <span className="strong" style={{ fontSize: 11.5 }}>{p.department}</span> },
            {
              key: 'title',
              label: 'Project & Investigators',
              render: (p) => (
                <>
                  <div className="row-title">{p.title}</div>
                  <div className="row-sub">
                    <b>PI:</b> {(p.pi || []).join(' · ')}
                    {p.coPIs && p.coPIs.length > 0 && <span> · <b>Co-PI:</b> {p.coPIs.join(' · ')}</span>}
                  </div>
                </>
              ),
            },
            { key: 'agency', label: 'Funding agency', render: (p) => <span style={{ fontSize: 12 }}>{p.agency}</span> },
            { key: 'amountLakh', label: 'Amount', align: 'right', render: (p) => <span className="num">{p.amountLakh ? `₹${p.amountLakh.toFixed(2)} L` : 'In-kind'}</span> },
            { key: 'status', label: 'Status', align: 'right', render: () => STATUS },
            { key: 'go', label: '', align: 'right', render: (p) => <Btn size="sm" variant="ghost" iconRight="chevronRight" onClick={() => open(p)}>Budget</Btn> },
          ]}
          rows={projects}
          rowKey={(p) => p.id}
          empty="No projects match this filter."
        />
      </Card>

      <div style={{ marginTop:24 }}><CollegeData /></div>
      {error && <p role="alert">{error}</p>}
      {!projects.length && !data.catalogProjects?.length && <p>No recorded projects for this search. Publications are listed separately in Faculty Profiles.</p>}
      <Card className="catalog-results" title="College grants and applications" subtitle="Actual catalog records matching the same filters. Applications are separate from sanctioned awards; overlapping register rows are retained for review." padded={false}>
        <Table columns={[
          { key:'id', label:'Reference' },
          { key:'title', label:'Project and investigators', render:(p) => <><div className="row-title">{p.title}</div><div className="row-sub">{p.investigators}</div><div className="tiny">{p.source?.file} / {p.source?.sheet} / row {p.source?.row}</div></> },
          { key:'agency', label:'Agency' }, { key:'year', label:'Year' }, { key:'status', label:'Classification' },
          { key:'amount_inr', label:'Recorded INR', align:'right', render:(p) => p.amount_inr == null ? 'Unknown' : money(p.amount_inr) },
        ]} rows={data.catalogProjects || []} empty="No recorded college grants or applications match this search." />
      </Card>
      {/* Budget modal */}
      {selected && (
        <Modal
          open={Boolean(selected)}
          title={`Faculty Budget — ${selected.id}`}
          subtitle={`${selected.title} · ${selected.year} · ${selected.department} · ${selected.agency}`}
          onClose={() => setSelected(null)}
          width={640}
        >
          <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
            <p style={{ margin: 0, fontSize: 12.5, color: 'var(--muted)' }}>
              Faculty-owned budget breakdown in rupees. Saved to the active institutional store.
            </p>
            <BudgetEditor lines={budget} onChange={setBudget} />
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 10, marginTop: 10 }}>
              <Btn variant="ghost" onClick={() => setSelected(null)} disabled={saving}>Cancel</Btn>
              <Btn variant="primary" icon="check" onClick={save} disabled={saving}>
                {saving ? 'Saving…' : 'Save Budget'}
              </Btn>
            </div>
          </div>
        </Modal>
      )}
    </>
  );
}
