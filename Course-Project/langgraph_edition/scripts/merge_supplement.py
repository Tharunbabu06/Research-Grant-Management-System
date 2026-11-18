"""Reconcile the college CSV exports with the original workbook catalog."""
import csv
import hashlib
import re
import unicodedata
from collections import defaultdict


def key(value):
    return ' '.join(re.findall(r'\w+', unicodedata.normalize('NFKC', value).casefold()))


def doi_key(value):
    from urllib.parse import unquote
    value = unquote(str(value or '')).strip().casefold()
    value = re.sub(r'^doi:\s*', '', value)
    # Do not "repair" DOI suffixes: different nonempty DOIs require review.
    return re.sub(r'^https?://(?:dx\.)?doi\.org/', '', value).strip()


def reconcile_grants(records, issues, review):
    """Exact, conservative reconciliation; no cross-lifecycle financial aggregation."""
    canonical, reliable = {}, {}
    for record in records:
        ref = key(record.get('sanction_reference', ''))
        signature = (key(record['title']), key(record['agency']), key(record['investigators']),
                     str(record['year']), record.get('amount_inr'), record['status'])
        lifecycle = 'application' if record['status'].startswith('Applied') else 'award'
        identity = (lifecycle, ref) if ref else signature
        prior = reliable.get(ref) if ref else None
        if prior and prior['status'] != record['status']:
            review.append({'reason':'Same grant reference has conflicting lifecycle/status; kept separate.', 'record':record})
        if identity in canonical:
            current = canonical[identity]
            if any(current.get(field) != record.get(field) for field in ('amount_inr', 'status', 'title', 'agency', 'investigators', 'year')):
                review.append({'reason':'Grant identifier has conflicting fields; original retained.', 'record':record})
                issues.append({'source':record['id'], 'severity':'warning', 'message':'Conflicting grant reference; manual review required.'})
                continue
            sources = current.setdefault('sources', [current['source']] if current.get('source') else [])
            for source in record.get('sources', [record['source']] if record.get('source') else []):
                if source not in sources:sources.append(source)
            for field, value in record.items():
                if field in ('id', 'source', 'sources', 'aliases', 'conflicts'):continue
                if current.get(field) in (None, '') and value not in (None, ''):
                    current[field] = value
                elif value not in (None, '') and current.get(field) != value:
                    conflict = {'field':field, 'value':value, 'source':record.get('source'), 'sources':record.get('sources', [])}
                    if conflict not in current.setdefault('conflicts', []):current['conflicts'].append(conflict)
            if record['id'] != current['id'] and record['id'] not in current.setdefault('aliases', []):
                current['aliases'].append(record['id'])
        else:
            # Amount/status disagreements without a reliable ID remain distinct and flagged.
            for other in canonical.values():
                if (key(other['title']),key(other['agency']),key(other['investigators']),str(other['year'])) == signature[:4]:
                    review.append({'reason':'Possible grant duplicate with different amount or status; kept separate.', 'record':record, 'candidate':other['id']})
            canonical[identity] = record
            if ref:reliable[ref] = record
    return list(canonical.values())


def read(path):
    with path.open(encoding='utf-8-sig', newline='') as source:
        yield from enumerate(csv.reader(source), 1)


def merge(folder, bundle, clean):
    bundle['grants'] = reconcile_grants(bundle['grants'], bundle['issues'], bundle.setdefault('review_records', []))
    publications = {}
    ids, dois = {}, {}
    titles = defaultdict(set)
    doi_only = defaultdict(list)
    review = bundle.setdefault('review_records', [])

    def hold(record, reason):
        entry = {'reason':reason, 'record':record}
        if entry not in review:
            review.append(entry)
        issue = {'source':record['id'], 'severity':'warning', 'message':reason}
        if issue not in bundle['issues']:
            bundle['issues'].append(issue)

    def is_doi(value):
        return re.fullmatch(r'(?:doi:\s*|https?://(?:dx\.)?doi\.org/)10\.\S+', value, re.I)

    def add(record):
        ident = record['id']
        doi = doi_key(record['doi'])
        signature = (key(record['title']), key(record['authors']), record['year'])
        by_id, by_doi = ids.get(ident), dois.get(doi) if doi else None
        if by_id and doi and publications[by_id]['doi'] and doi_key(publications[by_id]['doi']) != doi:
            hold(record, 'Publication ID has different nonempty DOIs; row retained for review, never title-merged.')
            return
        if by_id and by_doi and by_id != by_doi:
            hold(record, 'Publication ID and DOI refer to different records; row retained for review.')
            return
        candidate = by_doi or by_id
        if candidate:
            current = publications[candidate]
            if not by_doi and key(current['title']) != signature[0]:
                hold(record, 'Publication ID has a conflicting title; row retained for review.')
                return
            if not by_doi and not (doi and not current['doi']) and (
                    not signature[1] or not signature[2]
                    or key(current['authors']) != signature[1] or str(current['year']) != str(signature[2])):
                hold(record, 'Publication without a shared DOI has ambiguous author/year identity; row retained for review.')
                return
        elif signature[1] and signature[2] and len(titles[signature]) == 1 and (
                not doi or not publications[next(iter(titles[signature]))]['doi']):
            current = publications[next(iter(titles[signature]))]
        elif not doi and len(titles[signature]) > 1:
            hold(record, 'Publication without DOI matches multiple distinct DOI records; row retained for review.')
            return
        else:
            current = record
            publications[ident] = record
        current['doi'] = doi_key(current['doi'] or doi)
        if ident != current['id'] and ident not in current.setdefault('aliases', []):
            current['aliases'].append(ident)
        for field in ('title', 'authors', 'home_authors', 'department', 'year', 'type', 'venue', 'url', 'abstract', 'tags'):
            if not current.get(field):
                current[field] = record.get(field, '')
            elif record.get(field) and key(str(current[field])) != key(str(record[field])):
                conflict = {'field':field, 'value':record[field], 'sources':record['sources']}
                conflicts = current.setdefault('conflicts', [])
                if conflict not in conflicts:
                    conflicts.append(conflict)
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
            hold({'id':doi, 'sources':sources}, 'DOI-only row has no complete publication record.')
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
    for path in sorted(folder.glob('*_Details.csv')):
        cycle = ''
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
            # Title resemblance only nominates a candidate. It cannot establish an award.
            from decimal import Decimal, InvalidOperation
            try:
                amount = int(Decimal(clean(row[5]).replace(',', '')) * 100000)
            except InvalidOperation:
                amount = None
            exact = [g for g in matches if key(g['agency']) == key(agency)
                     and key(g['investigators']) == key(investigator)
                     and str(g['year']) == cycle and g['amount_inr'] == amount]
            if len(exact) == 1:
                sources = exact[0].setdefault('related_sources', [])
                if source not in sources:sources.append(source)
                continue
            signature = (cycle,key(title),key(investigator),key(agency),amount,clean(row[6]))
            if signature in legacy:
                legacy[signature]['sources'].append(source)
                continue
            legacy[signature] = {'id':f'LEGACY-CSV-{number}','title':title,'year':cycle,
                'department':clean(row[1]),'investigators':investigator,'agency':agency,
                'amount_as_recorded':clean(row[5]),'notes':clean(row[6]),
                'status':'Legacy historical record; excluded from sanctioned totals','sources':[source],
                'candidate_awards':[g['id'] for g in matches], 'mock':False}
            if matches:
                hold(legacy[signature], 'Possible grant overlap; agency, PI, cycle, amount or status requires review.')
    if legacy:
        # Keep original DOC evidence as well as the CSV transcription.
        existing = {g['id']:g for g in bundle['legacy']}
        existing.update({g['id']:g for g in legacy.values()})
        bundle['legacy'] = list(existing.values())
    for path in sorted(folder.glob('*.csv')):
        bundle['inventory'].append({'file':str(path.relative_to(folder.parent)),
            'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bytes':path.stat().st_size})
