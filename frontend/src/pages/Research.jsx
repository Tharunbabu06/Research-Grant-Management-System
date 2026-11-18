import { useState } from 'react';
import { endpoints } from '../lib/api';
import { Badge, Btn, Card } from '../components/ui';

export default function Research() {
  const [query, setQuery] = useState('');
  const [result, setResult] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [mode, setMode] = useState('archive');
  const [field, setField] = useState('all');
  async function load(text, page = 1, searchField = field) {
    setBusy(true);
    setError('');
    try {
      const response = mode === 'archive'
        ? await endpoints.collegePublications({ q:text, page, field:searchField })
        : await endpoints.literature('?q=' + encodeURIComponent(text));
      setResult(response);
    } catch (failure) { setError(failure.message); }
    finally { setBusy(false); }
  }
  async function search(event) {
    event.preventDefault();
    if (mode === 'public' && !query.trim()) return;
    await load(query.trim());
  }
  const archive = mode === 'archive';
  const start = result?.total && result.items.length ? (result.page - 1) * result.pageSize + 1 : 0;
  return <>
    <div className="page-head"><div><div className="eyebrow">Research</div><h1 className="page-title">Literature & Novelty</h1><p className="page-sub">Browse institutional publications by name or metadata, or search public research topics.</p></div></div>
    <Card title="Search publications">
      <div style={{ display:'flex', gap:12, marginBottom:12, flexWrap:'wrap' }}>
        <label className="tiny">Search source
          <select className="select" value={mode} disabled={busy} onChange={(event) => { setMode(event.target.value); setResult(null); setError(''); }}>
            <option value="archive">College archive</option><option value="public">Public topic search</option>
          </select>
        </label>
        {archive && <label className="tiny">Search field
          <select className="select" value={field} disabled={busy} onChange={(event) => { setField(event.target.value); setResult(null); setError(''); }}>
            <option value="all">All archive fields</option><option value="authors">Authors</option>
            <option value="home_authors">Home authors</option><option value="title">Title</option>
            <option value="doi">DOI</option><option value="venue">Venue</option><option value="year">Year</option>
          </select>
        </label>}
      </div>
      <form onSubmit={search} className="research-search"><input className="input" aria-label={archive ? 'College archive search' : 'Public research keywords'} placeholder={archive ? 'Author, title, DOI, venue or year' : 'Public research keywords'} value={query} onChange={(event) => setQuery(event.target.value)} maxLength={200} required={!archive} /><Btn type="submit" variant="primary" disabled={busy}>{busy ? 'Searching…' : 'Search'}</Btn></form>
      <p className="tiny">{archive ? 'College archive searches stay local and work without API keys or internet access. Leave the query blank to browse all publications.' : 'These topic keywords are sent to OpenAlex when configured. Crossref completes DOI metadata. College topic matches remain ranked by scientific relevance.'}</p>
      {error && <p role="alert" className="callout danger">{error}</p>}
    </Card>
    {result?.diagnostics && <Card title="Provider diagnostics">{Object.entries(result.diagnostics).map(([provider,diagnostic])=><p key={provider} className="tiny"><b>{provider}</b>: {diagnostic.code} ? {diagnostic.message}{diagnostic.retryAfterMs ? ` ? retry after ${Math.ceil(diagnostic.retryAfterMs/1000)} seconds`:''}</p>)}</Card>}
    {result && <Card title={archive ? `${result.total} institutional matches` : `${result.items.length} topic records returned`} subtitle={archive ? `Showing ${start}–${start ? start + result.items.length - 1 : 0} of ${result.total} · ${result.query ? `Search: ${result.query}` : 'All publications'}` : `OpenAlex: ${result.sources.openalex} · Crossref: ${result.sources.crossref}`}>
      {!result.items.length && <p>No records returned. Try another name or broader keywords.</p>}
      {result.items.map((item) => <article className="source-item" key={item.id}>
        <h3>{item.title}</h3><p className="tiny">{[item.authorsDisplay || item.authors?.join(', '), item.year, item.venue].filter(Boolean).join(' · ')}</p>
        <Badge tone="teal">{item.source}</Badge> <Badge tone="gray">{item.evidenceLevel}</Badge>{item.crossref && <Badge tone="teal">Crossref metadata</Badge>}
        {item.abstract && <details><summary>Abstract</summary><p>{item.abstract}</p></details>}
        {item.doi && <p><a className="research-link" href={'https://doi.org/' + encodeURIComponent(item.doi)} target="_blank" rel="noreferrer">View DOI ↗</a></p>}
        {item.provenance && <details><summary>College source locations</summary>{item.provenance.map((source, index) => <p className="tiny" key={index}>{source.file} · {source.sheet} · row {source.row}</p>)}</details>}
      </article>)}
      {archive && result.total > 0 && <nav aria-label="Archive result pages" style={{ display:'flex', gap:12, alignItems:'center', marginTop:16 }}>
        <Btn disabled={busy || !result.hasPrevious} onClick={() => load(result.query, result.page - 1, result.field)}>Previous</Btn>
        <span className="tiny" aria-live="polite">Page {result.page} of {result.totalPages} · {result.items.length} displayed / {result.total} total matches</span>
        <Btn disabled={busy || !result.hasNext} onClick={() => load(result.query, result.page + 1, result.field)}>Next</Btn>
      </nav>}
    </Card>}
  </>;
}
