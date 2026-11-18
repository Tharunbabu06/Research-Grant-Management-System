import { useEffect, useState } from 'react';
import { endpoints } from '../lib/api';
import {money} from '../lib/format';
import { useApp } from '../context/AppContext';
import { Badge, Btn, Card, Modal, Table } from '../components/ui';

export default function People() {
  const {navigate}=useApp();
  const [data, setData] = useState(null);
  const [q, setQ] = useState('');
  const [includeReview, setIncludeReview] = useState(false);
  const [detail, setDetail] = useState(null);
  const [selected, setSelected] = useState(null);
  const [error, setError] = useState('');
  const [publicationLimit, setPublicationLimit] = useState(20);
  useEffect(() => {
    let active = true;
    const timer = setTimeout(() => endpoints.researchers('?' + new URLSearchParams({ q, includeReview:includeReview ? '1' : '0' }))
      .then((result) => { if (active) { setData(result); setError(''); } })
      .catch((failure) => { if (active) setError(failure.message); }), 200);
    const interval=setInterval(()=>endpoints.researchers('?' + new URLSearchParams({q,includeReview:includeReview?'1':'0'})).then(result=>{if(active)setData(result);}).catch(failure=>{if(active)setError(failure.message);}),5000);
    return () => { active = false; clearTimeout(timer); clearInterval(interval); };
  }, [q, includeReview]);
  useEffect(()=>{if(!selected)return;let active=true;const timer=setInterval(()=>endpoints.researcher(selected.id).then(result=>{if(active)setDetail(result);}).catch(failure=>{if(active)setError(failure.message);}),4000);return()=>{active=false;clearInterval(timer);};},[selected]);
  async function open(person) {
    setSelected(person); setDetail(null); setPublicationLimit(20);
    try { setDetail(await endpoints.researcher(person.id)); }
    catch (failure) { setError(failure.message); }
  }
  const projectCount = (p) => p.projectCount == null ? `${p.definiteProjectCount} definite; overlap review required` : p.projectCount;
  return <>
    <div className="page-head"><div><div className="eyebrow">Institution</div><h1 className="page-title">Faculty Profiles</h1>
      <p className="page-sub">Research identities, publications and recorded projects. Confirmed faculty and source-supported institutional researchers are distinguished from identities awaiting affiliation review.</p></div></div>
    <Card title="Institutional researcher directory" subtitle="Directory inclusion does not create a login account or grant approval permissions.">
      <input className="input" aria-label="Search faculty names and aliases" placeholder="Search name, alias or department" value={q} onChange={(e) => setQ(e.target.value)} />
      <label className="tiny"><input type="checkbox" checked={includeReview} onChange={(e) => setIncludeReview(e.target.checked)} /> Include identities awaiting affiliation review</label>
      {error && <p role="alert">{error}</p>}
      <p className="tiny">{data ? `${data.total} matching profiles ? ${data.unresolvedCount} unresolved author references retained for review` : 'Loading directory?'}</p>
      <Table columns={[
        { key:'Name', label:'Researcher', render:(p) => <><div className="row-title">{p.Name}</div><div className="row-sub">{p.Dept}</div></> },
        { key:'identityStatus', label:'Identity evidence', render:(p) => <Badge tone={p.confirmedFaculty ? 'green' : p.eligibleForProposal ? 'indigo' : 'amber'}>{p.identityStatus.replaceAll('_', ' ')}</Badge> },
        { key:'publicationCount', label:'Research publications' },
        {key:'proposalCounts',label:'Proposals created / internally approved',render:p=>`${p.proposalCounts?.created ?? 0} / ${p.proposalCounts?.internallyApproved ?? 0}`},
        {key:'fundedAwardCount',label:'Funded projects/awards'},
        { key:'projectCount', label:'Recorded projects', render:projectCount },
        { key:'applicationCount', label:'Applications' },
        { key:'open', label:'', render:(p) => <Btn variant="ghost" size="sm" onClick={() => open(p)}>Open profile</Btn> },
      ]} rows={data?.people || []} empty="No matching institutional researcher profiles." />
    </Card>
    <Modal open={Boolean(selected)} onClose={() => setSelected(null)} title={selected?.Name} subtitle={selected?.Dept} width={840}>
      {selected && <>
        <dl className="kv"><dt>Researcher ID</dt><dd className="mono">{selected.id}</dd><dt>Aliases</dt><dd>{(detail?.person || selected).aliases.join(' ? ')}</dd>
          <dt>Evidence</dt><dd>{selected.identityStatus.replaceAll('_', ' ')}</dd><dt>Projects</dt><dd>{projectCount(selected)}</dd>
          <dt>Applications</dt><dd>{selected.applicationCount}</dd></dl>
        {!detail && <p>Loading linked records?</p>}
        {detail && <>
          <h3>Proposals</h3><p className="tiny">{detail.proposalScope}</p>
          <p className="tiny">Proposals created: {detail.proposalCounts.created} ? Awaiting review: {detail.proposalCounts.awaitingReview} ? Internally approved proposals: {detail.proposalCounts.internallyApproved}</p>
          <Table columns={[{key:'title',label:'Title'},{key:'facultyRole',label:'Faculty role'},{key:'budget',label:'Budget',align:'right'},
            {key:'status',label:'Status',render:p=>p.internallyApproved?'Internally approved proposal':p.status},
            {key:'publishedVersion',label:'Version / review',render:p=>`${p.publishedVersion || 'Working'} / ${p.review?.decision || 'Not approved'}`},
            {key:'open',label:'',render:p=><Btn size="sm" onClick={()=>navigate(`/runs/${p.id}`)}>Open proposal</Btn>}]} rows={detail.proposals} empty="No proposal details visible to your account." />
          <h3>Recorded grants and projects</h3>
          {!detail.projects.length && <p>No recorded projects. Publications do not establish a grant or project.</p>}
          <Table columns={[
            { key:'id', label:'Reference' }, { key:'title', label:'Title' }, { key:'recordKind', label:'Classification' }, { key:'agency', label:'Agency' },{key:'amount',label:'Recorded INR',align:'right',render:p=>p.amount_inr!=null?money(p.amount_inr):p.amountLakh!=null?money(p.amountLakh*100000):'Unknown'},{key:'source',label:'Source',render:p=>p.source?`${p.source.file} / ${p.source.sheet} / row ${p.source.row}`:'Historical project register'},
          ]} rows={detail.projects} empty="No recorded projects" />
          {detail.projectGroups.filter(group=>group.financialConflicts?.length).map(group=><p className="callout warn" key={group.id}>Same award counted once ({group.sourceIds.join(' / ')}). Conflicting recorded values retained: {group.financialConflicts.map(conflict=>`${money(conflict.registerInr)} register / ${money(conflict.catalogInr)} catalog`).join('; ')}. No combined sanctioned value is calculated.</p>)}
          {selected.reviewProjectIds.length > 0 && <p className="tiny">Overlapping source rows are shown for review; their values and counts are not added into a combined unique total.</p>}
          <h3>{selected.publicationCount} linked publications</h3>
          <Table columns={[
            { key:'title', label:'Title' }, { key:'year', label:'Year' }, { key:'id', label:'Record ID' },
          ]} rows={detail.publications.slice(0, publicationLimit)} empty="No resolved publication links in this catalog." />
          {publicationLimit < detail.publications.length && <Btn onClick={() => setPublicationLimit((n) => n + 20)}>Load more publications</Btn>}
          <details><summary>Identity evidence and source provenance</summary>{detail.person.provenance.map((e, i) => <p key={i} className="tiny">{e.kind} ? {e.recordId || e.source} ? {e.name || ''} {(e.sources || []).map((s) => `${s.file} / ${s.sheet} / row ${s.row}`).join('; ')}</p>)}</details>
        </>}
      </>}
    </Modal>
  </>;
}
