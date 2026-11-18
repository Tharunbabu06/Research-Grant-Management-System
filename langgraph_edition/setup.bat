@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
  set "GRANT_PY=python"
) else (
  set "GRANT_PY=py -3"
)
%GRANT_PY% -c "import sys; assert (3,11) <= sys.version_info[:2] <= (3,13), 'Use Python 3.11, 3.12 or 3.13'"
if errorlevel 1 goto fail
if not exist ".venv\Scripts\python.exe" %GRANT_PY% -m venv .venv
if errorlevel 1 goto fail
.venv\Scripts\python.exe -m pip install --upgrade pip
if errorlevel 1 goto fail
.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
if errorlevel 1 goto fail
.venv\Scripts\python.exe scripts\setup_users.py
if errorlevel 1 goto fail
echo.
echo Setup complete. Open runtime\FIRST_LOGIN.txt for your unique passwords.
echo Run start.bat to open Grant Office.
exit /b 0
:fail
echo.
echo Setup failed. Install Python 3.12 with Add Python to PATH enabled.
echo Internet is needed for the first dependency installation.
echo See docs\WINDOWS_SETUP.md for troubleshooting.
pause
exit /b 1
