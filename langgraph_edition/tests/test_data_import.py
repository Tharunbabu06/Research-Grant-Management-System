"""Ingestion contracts use isolated files, never the live catalog or account stores."""
import hashlib
import json
from pathlib import Path
import sys
import zipfile
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from archive_import import import_archive
from merge_supplement import doi_key, merge, reconcile_grants


def publication(ident='PUB-1', doi='10.1000/abc', **values):
    record = dict(id=ident, doi=doi, title='Research study', authors='A Author', year='2024',
                  sources=[dict(file='first.xlsx', sheet='Master', row=2)],
                  home_authors='', department='', type='', venue='', url='', abstract='', tags='')
    record.update(values)
    return record


def bundle(records):
    return dict(publications=records, grants=[], legacy=[], issues=[], inventory=[])


def test_normalized_doi_exports_and_complementary_fields(tmp_path):
    assert doi_key(' DOI: https://DX.doi.org/10.1000%2FABC ') == '10.1000/abc'
    first = publication(abstract='Approved abstract')
    second = publication('PUB-2', 'https://doi.org/10.1000/ABC', abstract='', venue='Journal',
                         sources=[dict(file='copy.csv', sheet='CSV export', row=4)])
    data = bundle([first, second])
    merge(tmp_path, data, str)
    assert len(data['publications']) == 1
    result = data['publications'][0]
    assert result['id'] == 'PUB-1'
    assert result['abstract'] == 'Approved abstract' and result['venue'] == 'Journal'
    assert len(result['sources']) == 2
    again = json.dumps(data['publications'], sort_keys=True)
    merge(tmp_path, data, str)
    assert json.dumps(data['publications'], sort_keys=True) == again


def test_distinct_dois_are_never_title_merged_and_id_conflicts_retained(tmp_path):
    data = bundle([publication(), publication('PUB-2', '10.1000/different'),
                   publication('PUB-1', '10.1000/conflict')])
    merge(tmp_path, data, str)
    assert len(data['publications']) == 2
    assert data['review_records'][0]['record']['doi'] == '10.1000/conflict'
    assert data['review_records'][0]['record']['sources'][0]['row'] == 2
    # A suspected typo must not be normalized into a different DOI.
    assert doi_key('10.1007/978981-96-6843-4_13') != doi_key('10.1007/978-981-96-6843-4_13')


def test_missing_doi_fallback_is_conservative_and_conflicts_retained(tmp_path):
    data = bundle([publication(doi=''), publication('PUB-2', '', authors='Other Author'),
                   publication('PUB-3', '', year='2025'),
                   publication('PUB-4', '', abstract='Complementary abstract'),
                   publication('PUB-5', '', abstract='Different abstract')])
    merge(tmp_path, data, str)
    assert len(data['publications']) == 3
    first = data['publications'][0]
    assert first['abstract'] == 'Complementary abstract'
    assert first['conflicts'][0]['value'] == 'Different abstract'


def grant(ident='G1', **values):
    record = dict(id=ident, title='Project', agency='Agency', investigators='PI', year='2024',
                  amount_inr=100, status='Historical award', source=dict(file='grants.xlsx', sheet='Awards', row=2))
    record.update(values)
    return record


def test_grants_retain_conflicts_lifecycle_and_provenance():
    review, issues = [], []
    records = [grant(), grant('G2', source=dict(file='grants.csv', sheet='CSV export', row=3)),
               grant('G3', amount_inr=200), grant('A1', status='Applied (outcome unknown)')]
    result = reconcile_grants(records, issues, review)
    assert len(result) == 3 and result[0]['id'] == 'G1'
    assert len(result[0]['sources']) == 2
    assert len(review) >= 2
    review, issues = [], []
    result = reconcile_grants([grant(sanction_reference='REF-1'),
        grant('G2', sanction_reference='REF-1', amount_inr=200)], issues, review)
    assert len(result) == 1 and result[0]['amount_inr'] == 100
    assert review[0]['record']['amount_inr'] == 200 and issues


@pytest.mark.parametrize('name', ['data/../../escape', '/absolute', 'C:/escape',
    'data/..\\..\\escape', 'data/../escape', 'data/.. /escape', 'data/NUL.txt'])
def test_archive_paths_are_rejected_before_extraction(tmp_path, name):
    live = tmp_path/'live'; live.mkdir(); (live/'catalog.json').write_text('{}')
    archive = tmp_path/'input.zip'
    with zipfile.ZipFile(archive, 'w') as out:
        out.writestr('data/first.txt', 'safe')
        out.writestr(name, 'unsafe')
    with pytest.raises(ValueError):import_archive(archive, live, tmp_path/'stage')
    assert not list((tmp_path/'stage').glob('**/first.txt'))


def test_archive_twice_is_unchanged_and_changed_uploads_are_held(tmp_path):
    live = tmp_path/'live'; live.mkdir()
    catalog = live/'catalog.json'; catalog.write_text('{"publications":[],"grants":[]}')
    before = hashlib.sha256(catalog.read_bytes()).hexdigest()
    archive = tmp_path/'input.zip'
    with zipfile.ZipFile(archive, 'w') as out:out.writestr('data/catalog.json', catalog.read_bytes())
    for _ in range(2):
        result = import_archive(archive, live, tmp_path/'stage')
        assert result['status'] == 'unchanged' and result['added_records'] == 0
        assert result['catalog_after_sha256'] == before
    with zipfile.ZipFile(archive, 'w') as out:
        out.writestr('data/catalog.json', '{"untrusted":true}')
        out.writestr('data/new.csv', 'title\nnew record')
    result = import_archive(archive, live, tmp_path/'stage')
    assert result['status'] == 'review_required'
    assert [f['comparison'] for f in result['files']] == ['changed', 'new']
    assert hashlib.sha256(catalog.read_bytes()).hexdigest() == before


def test_supplement_title_alone_cannot_merge_grants_or_drop_doc(tmp_path):
    (tmp_path/'History_Details.csv').write_text('2023-24,,,,,,\n1,Dept,Project,Other PI,Agency,2.0,Completed\n')
    data = bundle([]); data['grants'] = [grant()]; data['legacy'] = [dict(id='DOC-1', text='Original DOC evidence')]
    merge(tmp_path, data, str)
    assert len(data['legacy']) == 2
    assert data['legacy'][0]['text'] == 'Original DOC evidence'
    assert 'related_sources' not in data['grants'][0]
    assert data['review_records']
