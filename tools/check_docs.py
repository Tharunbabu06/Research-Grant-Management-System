"""Check relative file links in the maintained documentation (standard library)."""
from pathlib import Path
import json
import re
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
CURRENT = [
    ROOT / 'README.md', ROOT / 'Assignments/README.md',
    ROOT / 'Assignments/LEGACY_LABS.md', ROOT / 'Course-Project/README.md',
    ROOT / 'Course-Project/Final_Report/README.md',
    ROOT / 'Course-Project/Final_Report/GrantOffice_Technical_Report.md',
    ROOT / 'Course-Project/evidence/README.md',
    ROOT / 'Course-Project/docs/screenshots/README.md',
    ROOT / 'Course-Project/docs/history/README.md',
    ROOT / 'docs/REPOSITORY_UPDATE_REPORT.md',
] + [ROOT / 'Course-Project/docs' / name for name in [
    'README.md', 'ARCHITECTURE.md', 'SETUP.md', 'DATA_AND_IDENTITIES.md',
    'CORRECTNESS.md', 'USER_GUIDE.md', 'VERIFICATION.md', 'SCOPE_MAPPING.md',
    'LIMITATIONS.md',
]]


def check():
    failures, checked = [], 0
    for document in CURRENT:
        if not document.is_file():
            failures.append({'document': str(document.relative_to(ROOT)), 'target': 'missing document'})
            continue
        content = re.sub(r'```.*?```', '', document.read_text(encoding='utf-8'), flags=re.S)
        for match in re.finditer(r'!?\[[^\]]*\]\((<[^>]+>|[^)]+)\)', content):
            target = match.group(1).strip().strip('<>')
            parts = urlsplit(target)
            if parts.scheme or parts.netloc or not parts.path:
                continue
            checked += 1
            path = (document.parent / unquote(parts.path)).resolve()
            if not path.is_relative_to(ROOT) or not path.exists():
                failures.append({'document': document.relative_to(ROOT).as_posix(), 'target': target})
    return {'documents': len(CURRENT), 'relative_links_checked': checked, 'failures': failures,
            'scope': 'Maintained documents; unchanged historical/reference links excluded; external URLs and heading anchors not fetched.'}


if __name__ == '__main__':
    result = check()
    print(json.dumps(result, indent=2))
    raise SystemExit(bool(result['failures']))
