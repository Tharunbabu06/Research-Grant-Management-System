"""Stage and compare an archive. Never trust or execute instructions in source data.

Identical uploads are audited without rewriting the catalog. Changed/new files are
held for review: they cannot replace source files or approved application records.
"""
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import stat
import zipfile


def sha(data):
    return hashlib.sha256(data).hexdigest()


def safe_members(archive, destination):
    root = destination.resolve()
    seen = set()
    total = 0
    members = []
    for info in archive.infolist():
        name = info.filename.replace('\\', '/')
        rel = PurePosixPath(name)
        total += info.file_size
        if (name.startswith('/') or re.match(r'^[A-Za-z]:', name)
                or any(part in ('..', '') or ':' in part or part.endswith((' ', '.'))
                       or re.fullmatch(r'(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(\..*)?', part, re.I)
                       for part in rel.parts)
                or stat.S_ISLNK(info.external_attr >> 16)
                or info.file_size > 100_000_000 or total > 300_000_000):
            raise ValueError(f'Unsafe archive member: {name}')
        target = (root / str(rel)).resolve()
        if not target.is_relative_to(root) or target == root:
            raise ValueError(f'Archive path escapes staging: {name}')
        normalized = str(target).casefold()
        if normalized in seen:
            raise ValueError(f'Duplicate archive path: {name}')
        seen.add(normalized)
        members.append((info, target, rel))
    return members


def import_archive(archive_path, data_dir, staging_dir):
    archive_path, data_dir, staging_dir = map(Path, (archive_path, data_dir, staging_dir))
    digest = sha(archive_path.read_bytes())
    stage = staging_dir / digest
    # A staging destination must never be the live data tree or contain it.
    live, staged = data_dir.resolve(), stage.resolve()
    if staged.is_relative_to(live) or live.is_relative_to(staged):
        raise ValueError('Staging must be separate from the live data directory')
    before = sha((data_dir / 'catalog.json').read_bytes())
    files = []
    with zipfile.ZipFile(archive_path) as archive:
        members = safe_members(archive, stage)
        if not any(not info.is_dir() for info, _, _ in members):
            raise ValueError('Archive contains no dataset files')
        # Validate every member before extracting any. Staging parents may not be symlinks.
        for info, target, rel in members:
            if info.is_dir():
                continue
            if rel.parts[0] != 'data':
                raise ValueError('Expected a data/ archive root')
            local = data_dir.joinpath(*rel.parts[1:])
            payload = archive.read(info)
            uploaded = sha(payload)
            existing = sha(local.read_bytes()) if local.is_file() else None
            category = 'identical' if uploaded == existing else 'changed' if existing else 'new'
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(payload)
            files.append({'path':str(rel), 'bytes':len(payload), 'uploaded_sha256':uploaded,
                          'existing_sha256':existing, 'comparison':category})
    after = sha((data_dir / 'catalog.json').read_bytes())
    result = {'archive':str(archive_path.resolve()), 'archive_sha256':digest,
              'status':'unchanged' if all(f['comparison'] == 'identical' for f in files) else 'review_required',
              'added_records':0, 'catalog_before_sha256':before, 'catalog_after_sha256':after,
              'files':files}
    staging_dir.mkdir(parents=True, exist_ok=True)
    with (staging_dir / 'imports.jsonl').open('a', encoding='utf-8') as out:
        out.write(json.dumps(result, ensure_ascii=False) + '\n')
    (staging_dir / 'comparison.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    return result
