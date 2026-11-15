@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" call setup.bat
if errorlevel 1 exit /b 1
.venv\Scripts\python.exe scripts\check_llm.py --generate
pause
