"""Copy prior local accounts and project history into a fresh installation. Never overwrite either database."""
from pathlib import Path
import sqlite3,shutil,socket,tempfile
root=Path(__file__).resolve().parents[1]
with socket.socket() as s:
 if s.connect_ex(('127.0.0.1',8000))==0:raise SystemExit('Stop the running server before migration. Also stop any instance on a different port.')
old=Path(input('Previous GrantOffice folder path: ').strip().strip('"')).expanduser().resolve()
source=old/'runtime';dest=root/'runtime'
if old==root:raise SystemExit('Choose the previous installation, not this folder.')
if not (source/'office.sqlite').is_file():raise SystemExit('No prior runtime/office.sqlite was found at that location.')
if dest.exists() and any(dest.iterdir()):raise SystemExit('This installation already contains runtime data. No files were changed. Keep both copies and follow ../../docs/UPGRADE.md.')
with tempfile.TemporaryDirectory(dir=root,prefix='runtime-import-') as td:
 tmp=Path(td)
 for file in source.glob('*.sqlite'):
  with sqlite3.connect(file) as src,sqlite3.connect(tmp/file.name) as dst:src.backup(dst)
 if (source/'evidence_files').exists():shutil.copytree(source/'evidence_files',tmp/'evidence_files')
 if (source/'FIRST_LOGIN.txt').exists():shutil.copy2(source/'FIRST_LOGIN.txt',tmp/'FIRST_LOGIN.txt')
 dest.mkdir(exist_ok=True)
 for file in tmp.iterdir():shutil.move(str(file),str(dest/file.name))
print('Accounts, proposals, checkpoints and attachments copied. The original folder is unchanged.')
print('Run start.bat. Existing passwords still apply; use reset_faculty_password.bat if needed.')
