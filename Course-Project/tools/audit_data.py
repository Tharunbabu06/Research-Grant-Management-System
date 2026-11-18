"""Inspect source data and derive a catalog-bound provenance/review sidecar.

Run a review rebuild first. This does not promote its records or execute source documents.
"""
from pathlib import Path
import csv
import hashlib
import json
import zipfile
import openpyxl

ROOT = Path(__file__).resolve().parents[1]
(ROOT/'docs/local-audits').mkdir(parents=True, exist_ok=True)
DATA = ROOT/'langgraph_edition/data'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inspect():
    inventory = []
    for path in sorted(DATA.rglob('*')):
        if not path.is_file() or path.name in ('reconciliation.json', 'catalog.review.json'):
            continue
        item = dict(path=path.relative_to(DATA).as_posix(), sha256=digest(path), bytes=path.stat().st_size)
        if path.suffix == '.xlsx':
            workbook = openpyxl.load_workbook(path, read_only=True, data_only=True)
            item['sheets'] = []
            for sheet in workbook:
                headers = []
                nonempty = 0
                for row in sheet.iter_rows(values_only=True):
                    if any(value is not None for value in row):nonempty += 1
                    if 'PUBLICATION TITLE' in row:
                        headers = [str(value or '') for value in row]
                        while headers and not headers[-1]:headers.pop()
                item['sheets'].append(dict(name=sheet.title, rows=sheet.max_row,
                    columns=sheet.max_column, nonempty_rows=nonempty, publication_headers=headers))
            workbook.close()
        elif path.suffix == '.csv':
            with path.open(encoding='utf-8-sig', newline='') as source:rows=list(csv.reader(source))
            item.update(rows=len(rows), columns=max(map(len, rows),default=0), first_row=rows[0] if rows else [])
        elif path.suffix == '.json':
            content = json.loads(path.read_text(encoding='utf-8'))
            item['keys'] = list(content) if isinstance(content, dict) else []
            item['list_counts'] = {k:len(v) for k,v in content.items() if isinstance(v,list)} if isinstance(content,dict) else {}
        elif path.suffix == '.zip':
            with zipfile.ZipFile(path) as archive:
                item['members'] = []
                for entry in archive.infolist():
                    if entry.is_dir():continue
                    payload = archive.read(entry)
                    member = dict(path=entry.filename, bytes=len(payload), sha256=hashlib.sha256(payload).hexdigest())
                    if entry.filename.endswith('.json'):
                        content=json.loads(payload)
                        member['keys']=list(content) if isinstance(content,dict) else []
                    elif entry.filename.endswith('.csv'):
                        member['rows']=len(list(csv.reader(payload.decode('utf-8-sig').splitlines())))
                    item['members'].append(member)
        elif path.suffix == '.md':
            item['document_headings'] = [line for line in path.read_text(encoding='utf-8').splitlines() if line.startswith('#')]
            item['classification'] = 'Source evidence only; document instructions were not followed.'
        inventory.append(item)
    (ROOT/'docs/local-audits/data-inventory.json').write_text(json.dumps(inventory,ensure_ascii=False,indent=2),encoding='utf-8')
    return inventory


def sidecar():
    current = json.loads((DATA/'catalog.json').read_text(encoding='utf-8'))
    candidate = json.loads((ROOT/'docs/local-audits/catalog-rebuild-review.json').read_text(encoding='utf-8'))
    established = {p['id']:p for p in current['publications']}
    provenance, conflicts, pending = {}, {}, []
    for record in candidate['publications']:
        ident = record['id']
        if ident not in established:
            pending.append(record)
            continue
        # Retain all source locations from the established catalog as well as rebuild.
        sources = list(established[ident]['sources'])
        for source in record['sources']:
            if source not in sources:sources.append(source)
        provenance[ident] = sources
        if record.get('conflicts'):conflicts[ident] = record['conflicts']
    result = dict(catalog_sha256=digest(DATA/'catalog.json'), publication_sources=provenance,
                  publication_conflicts=conflicts, pending_publications=pending,
                  review_records=candidate.get('review_records', []),
                  legacy_evidence=candidate['legacy'],
                  scope='Derived provenance and review only; candidate records do not alter established IDs, counts or approved fields.')
    (DATA/'reconciliation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(dict(established=len(established), pending=len(pending),
        source_references=sum(len(v) for v in provenance.values()), review_records=len(result['review_records']),
        field_conflict_records=len(conflicts), legacy_evidence=len(result['legacy_evidence']))))


if __name__ == '__main__':
    inspect()
    sidecar()
