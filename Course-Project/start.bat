@echo off
setlocal
cd /d "%~dp0backend"
if not exist node_modules (echo Run setup.bat from the parent folder first. & pause & exit /b 1)
if not exist .env copy .env.example .env >nul
echo Open http://localhost:3000 after the server starts. Press Ctrl+C to stop.
call npm start
if errorlevel 1 pause
