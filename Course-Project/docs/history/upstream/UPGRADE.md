# Upgrade without losing existing office work

1. Stop the existing server using Ctrl+C and close the old server window.
2. Keep your entire old GrantOffice folder as a backup.
3. Extract the new ZIP into a **different folder**.
4. Before starting the new version, double-click **import_previous_data.bat** in the new folder.
5. Paste the path of the old GrantOffice folder when prompted. The script uses SQLite backup and copies evidence attachments into the new runtime. It does not modify the old installation.
6. Run **start.bat** from the new folder. Existing passwords remain unchanged; old generic display names are updated.
7. If the faculty password is unknown, stop the server, run **reset_faculty_password.bat**, choose a new password and restart.
8. Check that your pipeline and approved versions are visible. Use only the new server after verifying the upgrade.

If the new folder already contains runtime data, the import script refuses to overwrite it. Preserve both folders. Use a fresh extraction for migration, or ask the local system owner to reconcile both histories. Do not delete either runtime as a login fix.

The ZIP does not contain a ready-made account database or fixed shared password. This prevents accidentally distributing another user's project records or login secrets.

## What changed in login

- `Faculty`, `faculty` and `  FACULTY  ` resolve to the same username.
- Passwords remain case-sensitive. Spaces within a password are preserved; do not paste accidental spaces from another file.
- The password visibility button helps inspect input before sign-in.
- FIRST_LOGIN.txt records initial credentials, not every later password. A reset invalidates the old password and existing sessions.
- Re-running setup neither resets existing passwords nor overwrites the existing initial-credentials file.
- Account recovery changes only the selected account's password and sessions; proposal ownership, evidence, approvals and versions are preserved.

The precise cause of the reported faculty login failure cannot be established without the error message and local database. This release addresses username formatting and missing recovery, and includes tests for account resets and record retention; it does not claim the user's unknown password was recovered.
