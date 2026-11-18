@echo off
setlocal
cd /d "%~dp0"
call npm --prefix backend test
if errorlevel 1 exit /b 1
call npm --prefix frontend run lint -- --max-warnings 0
if errorlevel 1 exit /b 1
call npm --prefix frontend run build
if errorlevel 1 exit /b 1
python tools\verify_labs.py
if errorlevel 1 exit /b 1
python tools\check_docs.py
if errorlevel 1 exit /b 1
echo Verification passed.
pause
