"""Inspect the Git index without printing secrets. Run after explicit staging."""
from pathlib import Path
import re
import subprocess
import zipfile
import io

ROOT = Path(__file__).resolve().parents[1]
GIT = ['git', '-c', 'safe.directory=' + ROOT.as_posix(), '-C', str(ROOT)]
paths = subprocess.check_output(GIT + ['ls-files', '-z']).decode().split('\0')
patterns = {
    'private key': rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
    'GitHub token': rb'(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,})',
    'provider token': rb'(?:gsk_|sk-proj-)[A-Za-z0-9_-]{20,}',
    'credentialed MongoDB URI': rb'mongodb(?:\+srv)?://[^\s<>:@]+:[^\s<>@]+@',
}
local_secrets = []
env = ROOT / 'backend/.env'
if env.exists():
    for line in env.read_text(encoding='utf-8-sig').splitlines():
        if '=' not in line or line.lstrip().startswith('#'):
            continue
        name, value = line.split('=', 1)
        value = value.strip().strip('"\'')
        if any(key in name.upper() for key in ['KEY', 'TOKEN', 'PASSWORD', 'MONGODB_URI', 'MONGO_URI']) and len(value) >= 12:
            local_secrets.append(value.encode())
failures = []
for name in filter(None, paths):
    parts = Path(name).parts
    if (Path(name).name.startswith('.env') and Path(name).name != '.env.example') or any(p in parts for p in ['node_modules', '.venv', '.npm-cache', '__pycache__']) or name.startswith(('backend/data/', 'langgraph_edition/runtime/')):
        failures.append((name, 'private/generated path'))
    blob = subprocess.check_output(GIT + ['show', ':' + name])
    # Inspect XML/text inside office files as well as ordinary staged text.
    payloads = [blob]
    if name.endswith(('.docx', '.xlsx', '.pptx', '.zip')):
        try:
            with zipfile.ZipFile(io.BytesIO(blob)) as archive:
                payloads += [archive.read(n) for n in archive.namelist() if n.endswith(('.xml', '.txt', '.json', '.env'))]
        except zipfile.BadZipFile:
            failures.append((name, 'invalid archive'))
    for label, pattern in patterns.items():
        if any(re.search(pattern, data) for data in payloads):
            failures.append((name, label))
    if any(secret in data for secret in local_secrets for data in payloads):
        failures.append((name, 'matches configured local secret'))
print('Staged/tracked files inspected:', len(list(filter(None, paths))))
for name, label in failures:
    print('FINDING:', name, '-', label)
print('Findings:', len(failures), '(secret values never printed)')
raise SystemExit(bool(failures))
