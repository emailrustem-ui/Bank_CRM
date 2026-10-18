# ============================================================
# start_all.ps1 - start EVERYTHING with one command (ASCII-only)
#   1) Outlook agent (minimized window)
#   2) CRM + auto-open browser
#
# Usage:  powershell -ExecutionPolicy Bypass -File .\start_all.ps1
# ============================================================

$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot

if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
    Write-Host "Virtual environment .venv not found." -ForegroundColor Red
    Write-Host "Run first:  powershell -ExecutionPolicy Bypass -File .\run.ps1" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# --- 1. Outlook agent in a separate minimized window ---
if (Test-Path ".\tools\outlook_agent.py") {
    Write-Host "Starting Outlook agent (minimized window)..." -ForegroundColor Cyan
    Start-Process powershell -ArgumentList @(
        "-NoExit",
        "-ExecutionPolicy", "Bypass",
        "-File", "$PSScriptRoot\run_agent.ps1"
    ) -WindowStyle Minimized
} else {
    Write-Host "tools\outlook_agent.py not found - agent skipped." -ForegroundColor Yellow
}

# --- 2. CRM (browser opens automatically) ---
Write-Host "Starting CRM..." -ForegroundColor Cyan
powershell -ExecutionPolicy Bypass -File "$PSScriptRoot\run.ps1"