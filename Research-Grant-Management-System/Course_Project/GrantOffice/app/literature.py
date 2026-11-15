"""Optional public literature discovery for a user-supplied search query."""
import os
from urllib.parse import quote

import httpx


def lookup(query, local_records):
    if not query:
        return [], {'openalex':'not_requested', 'crossref':'not_requested'}
    api_key = os.getenv('OPENALEX_API_KEY')
    status = {'openalex':'key_missing', 'crossref':'not_attempted'}
    if not api_key:
        return [], status
    records = []
    existing = {row['doi'].lower(): row for row in local_records if row['doi']}
    with httpx.Client(timeout=5, follow_redirects=False) as client:
        try:
            response = client.get('https://api.openalex.org/works',
                params={'search':query, 'per_page':6,
                        'select':'id,doi,title,publication_year,abstract_inverted_index'},
                headers={'Authorization':f'Bearer {api_key}'})
            response.raise_for_status()
            results = response.json()['results']
            if not isinstance(results, list):
                raise ValueError('Unexpected OpenAlex results')
        except (httpx.HTTPError, ValueError, KeyError, TypeError):
            status['openalex'] = 'unavailable'
            return [], status
        status['openalex'] = 'ok' if results else 'no_results'
        seen = set()
        for work in results:
            work_id = work.get('id') or ''
            title = work.get('title')
            if not title or not work_id.startswith('https://openalex.org/W') or work_id in seen:
                continue
            seen.add(work_id)
            doi = (work.get('doi') or '').lower().removeprefix('https://doi.org/')
            source = {'file':'OpenAlex','sheet':'Works','row':work_id,'url':work_id}
            if doi and doi in existing:
                if source not in existing[doi]['sources']:
                    existing[doi]['sources'].append(source)
                continue
            abstract_index = work.get('abstract_inverted_index') or {}
            abstract = ' '.join(word for _, word in sorted(
                (position, word) for word, positions in abstract_index.items()
                for position in positions))
            record = {'id':'OPENALEX-'+work_id.rsplit('/',1)[-1], 'title':title,
                      'year':work.get('publication_year') or '', 'doi':doi,
                      'url':work_id, 'abstract':abstract, 'sources':[source],
                      'evidence_level':'abstract' if abstract else 'metadata',
                      'authors':'', 'venue':'', 'mock':False}
            records.append(record)
            if doi:
                existing[doi] = record
        dois = [record for record in records if record['doi']][:2]
        if dois:
            outcomes = []
            for record in dois:
                url = 'https://api.crossref.org/works/'+quote(record['doi'], safe='')
                try:
                    response = client.get(url)
                    response.raise_for_status()
                    metadata = response.json()['message']
                    if metadata.get('DOI','').lower() != record['doi']:
                        raise ValueError('Crossref DOI mismatch')
                    record['venue'] = (metadata.get('container-title') or [''])[0]
                    record['sources'].append({'file':'Crossref','sheet':'DOI metadata',
                        'row':record['doi'],'url':url})
                    outcomes.append(True)
                except (httpx.HTTPError, ValueError, KeyError, TypeError):
                    outcomes.append(False)
            status['crossref'] = 'ok' if all(outcomes) else 'partial' if any(outcomes) else 'unavailable'
    return records, status
