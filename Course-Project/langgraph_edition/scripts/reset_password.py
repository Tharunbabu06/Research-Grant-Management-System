"""Local operator recovery. Requires OS access to the installation; never removes proposal data."""
import sys,getpass
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app import store
from app.auth import reset_password

def main():
 store.init();username=(sys.argv[1] if len(sys.argv)>1 else input('Username to recover: ')).strip().lower()
 if not store.user(username):raise SystemExit('Account not found. Run setup.bat first; existing accounts are preserved.')
 print('This changes only the selected password and signs that account out. Proposals and approvals are retained.')
 password=getpass.getpass('New password (at least 12 characters): ')
 if password!=getpass.getpass('Confirm new password: '):raise SystemExit('Passwords differ; nothing changed.')
 try:reset_password(username,password,'local-system-operator')
 except ValueError as e:raise SystemExit(str(e))
 print('Password updated. Sign in with the password you just entered. FIRST_LOGIN.txt may contain an older password.')
if __name__=='__main__':main()
