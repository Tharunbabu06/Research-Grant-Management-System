@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
 python scripts\migrate_runtime.py
) else (
 py -3 scripts\migrate_runtime.py
)
pause
