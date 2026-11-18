@echo off
setlocal
cd /d "%~dp0"
where node >nul 2>nul
if errorlevel 1 (echo Install Node.js 22.13 or newer first. & pause & exit /b 1)
node -e "if(Number(process.versions.node.split('.')[0])<22)process.exit(1)"
if errorlevel 1 (echo Node.js 22.13 or newer is required. & pause & exit /b 1)
if not exist backend\.env copy backend\.env.example backend\.env >nul
call npm --prefix backend ci
if errorlevel 1 goto failed
call npm --prefix frontend ci
if errorlevel 1 goto failed
call npm --prefix frontend run build
if errorlevel 1 goto failed
echo Setup complete. Configure backend\.env, then run start.bat.
pause
exit /b 0
:failed
echo Setup failed. Read the error above before starting.
pause
exit /b 1
