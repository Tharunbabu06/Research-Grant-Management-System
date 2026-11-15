# Windows setup and login recovery

## New installation

1. Install Python 3.12 (64-bit) with **Add Python to PATH** enabled.
2. Extract the entire ZIP. Open the inner **GrantOffice** folder containing start.bat.
3. Double-click **start.bat**. First launch installs pinned dependencies and creates missing accounts.
4. The browser opens at http://127.0.0.1:8000 after the server is ready. Keep the terminal window open.
5. Initial passwords are in **runtime/FIRST_LOGIN.txt**. Use the password belonging to the selected username.

| Username | Display name | Scope |
|---|---|---|
| faculty | Faculty Member | Own proposals/evidence |
| hod | Head of Department | SOCSE proposals |
| office | Research Office | Institution-wide review and account/source management |
| dean | Dean R&D | Institution-wide review and account/source management |
| ece_faculty | Faculty Member — ECE | Separate SOECE faculty scope |

These initial role accounts are not automatically verified identities of actual staff. The research office should create named accounts and assign authorized roles for college operations.

## Faculty login is failing

1. Stop the server with Ctrl+C.
2. Double-click **reset_faculty_password.bat**.
3. Choose a new password containing at least 12 characters, and enter it again.
4. Restart **start.bat**.
5. Sign in with username **faculty** and the new password you chose.

The recovery script requires access to the local installation and database. It does not delete proposals or change account roles. Never send passwords to another person merely to troubleshoot the app.

If you can sign in as office/Dean instead, use **Office settings → Recover an account**. Select faculty, enter and confirm the new password, and save. Existing faculty sessions are revoked.

## Common causes and messages

- **Incorrect username/password:** usernames are trimmed and case-insensitive; passwords are case-sensitive. FIRST_LOGIN.txt may contain an old initial password after you changed/reset it.
- **Too many attempts:** wait five minutes or have the research office reset the account. Local recovery should be performed with the server stopped.
- **Port 8000 already in use:** close the old server before starting this version. Use the same URL, 127.0.0.1:8000, rather than switching between localhost and 127.0.0.1 during a session.
- **start.bat not recognized:** terminal is in the wrong folder. In PowerShell use `.\start.bat`.
- **Python not found:** install Python 3.12, reopen the terminal, and verify `py -3.12 --version`.
- **Model not connected:** install/start Ollama and run setup_llm.bat. The rest of the app remains usable with explicit template/retrieval fallback.
- **Institutional proposal blocked:** use Budget & checks to identify missing official call, policy, eligibility or required evidence. Do not convert sample data into official facts to bypass the checks.

## VS Code commands

```powershell
cd "C:\path\to\GrantOffice"
.\setup.bat
.\start.bat
```

No virtual-environment activation is necessary. Launchers use `.venv\Scripts\python.exe` directly. No Node.js, npm or paid API key is required.

Existing installation? Follow **docs/UPGRADE.md** before the first launch to preserve your current work.
