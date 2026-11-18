@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo First run: installing the local environment...
  call setup.bat
  if errorlevel 1 exit /b 1
)
.venv\Scripts\python.exe scripts\setup_users.py
if errorlevel 1 goto fail
echo.
echo Grant Office will open at http://127.0.0.1:8000
echo Initial passwords: runtime\FIRST_LOGIN.txt
echo Faculty recovery: reset_faculty_password.bat
echo Keep this window open. Press Ctrl+C to stop.
.venv\Scripts\python.exe scripts\serve.py
if errorlevel 1 goto fail
exit /b 0
:fail
echo.
echo Start failed. Read the error above and docs\WINDOWS_SETUP.md.
pause
exit /b 1
