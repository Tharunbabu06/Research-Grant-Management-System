@echo off
setlocal
cd /d "%~dp0"
where ollama >nul 2>nul
if errorlevel 1 (
 echo Install Ollama for Windows from https://ollama.com/download/windows
 echo Then reopen this window and run setup_llm.bat again.
 start "" "https://ollama.com/download/windows"
 pause
 exit /b 1
)
echo Downloading the local Qwen 2.5 3B model. This needs internet and several GB of disk space.
ollama pull qwen2.5:3b
if errorlevel 1 (
 echo Start the Ollama desktop application, then try again.
 pause
 exit /b 1
)
echo Local model is ready. Start Grant Office and open Office settings to check its connection.
pause
