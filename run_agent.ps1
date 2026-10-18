# ============================================================
# run_agent.ps1 - start CRM -> Outlook agent (ASCII-only)
# Usage:  powershell -ExecutionPolicy Bypass -File .\run_agent.ps1
# ============================================================

$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot

if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
    Write-Host "Virtual environment .venv not found." -ForegroundColor Red
    Write-Host "Run first:  powershell -ExecutionPolicy Bypass -File .\run.ps1" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

if (-not (Test-Path ".\tools\outlook_agent.py")) {
    Write-Host "File tools\outlook_agent.py not found." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Starting Outlook agent on port 8765..." -ForegroundColor Cyan
Write-Host "Keep this window open (you may minimize it)." -ForegroundColor Yellow
Write-Host ""

& .\.venv\Scripts\python.exe .\tools\outlook_agent.py --port 8765 --token crm-local-token

Read-Host "Press Enter to exit"