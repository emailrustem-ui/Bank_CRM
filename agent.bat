@echo off
cd /d "%~dp0"
".venv\Scripts\python.exe" tools\outlook_agent.py --port 8765 --token crm-local-token
pause