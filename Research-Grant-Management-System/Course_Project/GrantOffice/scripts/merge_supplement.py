"""Reconcile the college CSV exports with the original workbook catalog."""
import csv
import hashlib
import re
import unicodedata
from collections import defaultdict


def key(value):
    return ' '.join(re.findall(r'\w+', unicodedata.normalize('NFKC', value).casefold()))


def doi_key(value):
    value = re.sub(r'^(https?://(dx\.)?doi\.org/|doi:\s*)', '', value.strip().lower())
    # The workbook contains both spellings of the same chapter DOI.
    return value.replace('978981-96-6843-4_13', '978-981-96-6843-4_13')


def read(path):
    with path.open(encoding='utf-8-sig', newline='') as source:
        yield from enumerate(csv.reader(source), 1)


def merge(folder, bundle, clean):
    if not folder.is_dir():
        return
    publications = {}
    ids, dois = {}, {}
    titles = defaultdict(set)
    doi_only = defaultdict(list)

    def is_doi(value):
        return re.fullmatch(r'(?:doi:\s*|https?://(?:dx\.)?doi\.org/)10\.\S+', value, re.I)

    def add(record):
        ident = record['id']
        doi = doi_key(record['doi'])
        signature = (key(record['title']), key(record['authors']), record['year'])
        candidates = {item for item in (ids.get(ident), dois.get(doi)) if item}
        if len(candidates) > 1:
            bundle['issues'].append({'source':ident, 'severity':'warning',
                'message':'Publication ID and DOI refer to different records. Supplemental row held for manual review.'})
            return
        if candidates:
            current = publications[next(iter(candidates))]
            if key(current['title']) != signature[0]:
                bundle['issues'].append({'source':ident, 'severity':'warning',
                    'message':'Publication identifier has a conflicting title. Supplemental row held for manual review.'})
                return
        elif not doi and signature[1] and signature[2] and len(titles[signature]) == 1:
            current = publications[next(iter(titles[signature]))]
        else:
            current = record
            publications[ident] = record
        current['doi'] = doi_key(current['doi'] or doi)
        for field in ('authors', 'home_authors', 'department', 'year', 'type', 'venue', 'url', 'abstract', 'tags'):
            if not current[field]:
                current[field] = record[field]
        for source in record['sources']:
            if source not in current['sources']:
                current['sources'].append(source)
        ids[ident] = current['id']
        if doi:
            dois[doi] = current['id']
        titles[signature].add(current['id'])

    original_count = len(bundle['publications'])
    for record in bundle['publications']:
        if is_doi(record['title']):
            doi_only[doi_key(record['title'])].extend(record['sources'])
        else:
            add(record)
    original_unique = len(publications)
    for path in sorted(folder.glob('202*.csv')):
        headers = None
        for number, values in read(path):
            if 'PUBLICATION TITLE' in values:
                headers = values
                continue
            if headers is None:
                continue
            row = {name: clean(value) for name, value in zip(headers, values) if name}
            title = row.get('PUBLICATION TITLE')
            if not title:
                continue
            source = {'file':path.name,'sheet':'CSV export','row':number}
            if is_doi(title):
                doi_only[doi_key(title)].append(source)
                continue
            pid, doi = row.get('PUB ID', ''), doi_key(row.get('DOI', ''))
            ident = 'PUB-'+pid if pid else 'DOI-'+doi if doi else 'CSV-'+hashlib.sha256(
                (path.name+'|'+str(number)).encode()).hexdigest()[:16]
            add({'id':ident, 'title':title, 'doi':doi, 'authors':row.get('AUTHORS',''),
                 'home_authors':row.get('HOME AUTHORS',''), 'department':row.get('HOME AUTHOR DEPARTMENT',''),
                 'year':row.get('YEAR',''), 'type':row.get('ARTICLE TYPE',''), 'venue':row.get('SOURCE PUBLICATION',''),
                 'url':row.get('LINK',''), 'abstract':row.get('ABSTRACT',''), 'tags':row.get('TECHNOLOGYAREAS',''),
                 'cycle':path.name[:7], 'sources':[source],
                 'evidence_level':'uploaded_metadata_and_abstract_not_full_text','mock':False})
    for doi, sources in doi_only.items():
        if doi not in dois:
            bundle['issues'].append({'source':doi,'severity':'warning',
                'message':'DOI-only row has no complete publication record. Source retained for manual review.'})
            continue
        record = publications[dois[doi]]
        for source in sources:
            if source not in record['sources']:
                record['sources'].append(source)
    bundle['publications'] = list(publications.values())
    bundle['issues'].append({'source':'College CSV supplement','severity':'info',
        'message':f'Reconciled {original_count-original_unique} workbook duplicate(s) and added {len(publications)-original_unique} publication(s). Matching rows retain source locations.'})

    modern = defaultdict(list)
    for record in bundle['grants']:
        if record['status'] == 'Historical award':
            modern[key(record['title'])].append(record)
    legacy = {}
    cycle = ''
    for path in sorted(folder.glob('*_Details.csv')):
        for number, row in read(path):
            if len(row) < 7 or row[0].strip() == 'SN':
                continue
            if re.fullmatch(r'\d{4}-\d{2,4}', row[0].strip()):
                cycle = row[0].strip()
            title = clean(row[2])
            investigator = clean(row[3])
            agency = clean(row[4])
            if not title or not (investigator or agency):
                continue
            source = {'file':path.name,'sheet':'CSV export','row':number}
            matches = modern[key(title)]
            if len(matches) == 1:
                matches[0].setdefault('related_sources', []).append(source)
                continue
            signature = (cycle,key(title),key(investigator),key(agency))
            if signature in legacy:
                legacy[signature]['sources'].append(source)
                continue
            legacy[signature] = {'id':f'LEGACY-CSV-{number}','title':title,'year':cycle,
                'department':clean(row[1]),'investigators':investigator,'agency':agency,
                'amount_as_recorded':clean(row[5]),'notes':clean(row[6]),
                'status':'Legacy historical record; excluded from sanctioned totals','sources':[source]}
    if legacy:
        bundle['legacy'] = list(legacy.values())
    for path in sorted(folder.glob('*.csv')):
        bundle['inventory'].append({'file':str(path.relative_to(folder.parent)),
            'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bytes':path.stat().st_size})
