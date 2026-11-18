import { useEffect, useState } from 'react';
import { endpoints } from '../lib/api';
import { Card, Table } from './ui';
import { compactMoney, money } from '../lib/format';

export default function CollegeData({ details = false }) {
  const [data, setData] = useState(null);
  const [error, setError] = useState('');
  useEffect(() => {
    let active = true;
    (details ? endpoints.collegeGrants() : endpoints.college())
      .then((result) => { if (active) setData(details ? result : { metrics:result }); })
      .catch(() => { if (active) setError('College data could not be loaded.'); });
    return () => { active = false; };
  }, [details]);
  if (!data) return <p className="tiny">{error || 'Loading college archive…'}</p>;
  const m = data.metrics;
  return <div className="archive-summary" style={{ marginBottom:16 }}>
    <div className="grid g4 summary-strip" style={{ gap:12, marginBottom:12 }}>
      {[
        ['College publications', m.publications, 'Established catalog; identity review retained'],
        ['College awards', m.awards, 'Detailed historical awards'],
        ['College sanctioned value', compactMoney(m.sanctionedInr), money(m.sanctionedInr)],
        ['College applications', m.applications, 'Outcome unknown; excluded from awards'],
      ].map(([label, value, foot]) => <div key={label} className="card stat">
        <div className="stat-label">{label}</div><div className="stat-value">{value}</div><div className="stat-foot">{foot}</div>
      </div>)}
    </div>
    <p className="tiny">College archive totals exclude applications, mock data and legacy summaries. Historical register values remain separate while overlaps are reviewed.</p>
    {details && <>
      <Card title="College grant catalog" subtitle="Sanctioned amounts and received funds are separate. Applications have no confirmed outcome." padded={false}>
        <Table columns={[
          { key:'id', label:'Record', render:(g) => <span className="strong">{g.id}</span> },
          { key:'title', label:'Project and source', render:(g) => <><div className="row-title">{g.title}</div><div className="row-sub">{g.investigators} · {g.agency}</div><div className="tiny">{g.source.file} · {g.source.sheet} · row {g.source.row}</div></> },
          { key:'year', label:'Year' },
          { key:'amount_inr', label:'Award / requested', align:'right', render:(g) => g.amount_inr == null ? 'Unknown' : money(g.amount_inr) },
          { key:'received_inr', label:'Received', align:'right', render:(g) => g.received_inr == null ? 'Unknown' : money(g.received_inr) },
          { key:'status', label:'Classification' },
        ]} rows={[...data.awards, ...data.applications]} rowKey={(g) => g.id} />
      </Card>
      <p className="tiny">{m.reconciliation.candidates.length} possible overlaps with the historical register; {m.reconciliation.conflicts.length} repeated-register group(s) require review. No combined total is calculated.</p>
      <Card title="Funding overlap review" padded={false}>
        <Table columns={[
          { key:'id', label:'References' }, { key:'message', label:'Review before combining records' },
        ]} rows={[
          ...m.reconciliation.candidates.map((c) => ({ id:`${c.projectId} / ${c.grantId}`, message:`Register ${c.registerYear}: ${money(c.registerInr)}; college ${c.collegeYear}: ${money(c.collegeInr)}. PI and agency comparison required.` })),
          ...m.reconciliation.conflicts.map((c) => ({ id:c.ids.join(' / '), message:`${c.title}: ${c.amountsInr.map(money).join(' / ')}. ${c.reason}` })),
          ...m.reconciliation.statusConflicts.map((c) => ({ id:c.projectId, message:`${c.sourceNote} ${c.reason}` })),
        ]} rowKey={(item) => item.id} />
      </Card>
      <Card title="Data review" padded={false}>
        <Table columns={[
          { key:'source', label:'Source' }, { key:'message', label:'Issue retained from the source catalog' },
        ]} rows={m.issues} rowKey={(item) => `${item.source}-${item.message}`} />
      </Card>
    </>}
  </div>;
}
