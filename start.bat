@echo off
chcp 65001 >nul
title Bank CRM
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo [1/3] Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 goto :err
    ".venv\Scripts\python.exe" -m pip install --upgrade pip
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
    if errorlevel 1 goto :err
) else (
    echo [1/3] Virtual environment found.
)

echo [2/3] Starting Outlook agent...
start "CRM Outlook Agent" /min cmd /c ""%~dp0agent.bat""
timeout /t 2 >nul

echo [3/3] Starting CRM...
start "" http://127.0.0.1:5000/
".venv\Scripts\python.exe" app.py
goto :eof

:err
echo.
echo Setup failed. Install Python 3.11+ and retry.
pause