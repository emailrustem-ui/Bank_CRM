# ============================================================
# run.ps1 - Bank CRM startup script (ASCII-only, encoding-safe)
# Usage:  powershell -ExecutionPolicy Bypass -File .\run.ps1
# ============================================================

$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot

# --- 1. Locate Python ---
$python = $null

foreach ($cmd in @("python", "python3", "py")) {
    $found = Get-Command $cmd -ErrorAction SilentlyContinue
    if ($found) {
        $python = $found.Source
        break
    }
}

if (-not $python) {
    $candidates = @(
        "$env:LOCALAPPDATA\Python\pythoncore-3.14-64\python.exe",
        "$env:LOCALAPPDATA\Python\pythoncore-3.13-64\python.exe",
        "$env:LOCALAPPDATA\Python\pythoncore-3.12-64\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe"
    )
    foreach ($c in $candidates) {
        if (Test-Path $c) {
            $python = $c
            break
        }
    }
}

if (-not $python) {
    Write-Host ""
    Write-Host "Python not found." -ForegroundColor Red
    Write-Host "Install Python 3.11+ from https://www.python.org/downloads/ and retry." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Python found: $python" -ForegroundColor Cyan
& $python --version

# --- 2. Create virtual environment if missing ---
if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
    Write-Host ""
    Write-Host "Creating virtual environment .venv ..." -ForegroundColor Cyan
    & $python -m venv .venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to create .venv" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# --- 3. Upgrade pip and install dependencies ---
Write-Host ""
Write-Host "Upgrading pip..." -ForegroundColor Cyan
& .\.venv\Scripts\python.exe -m pip install --upgrade pip

Write-Host ""
Write-Host "Installing dependencies..." -ForegroundColor Cyan
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Dependency installation failed." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# --- 4. Run the app (browser opens automatically) ---
Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host " Starting CRM:  http://127.0.0.1:5000" -ForegroundColor Green
Write-Host " Login: manager   Password: manager" -ForegroundColor Green
Write-Host " Stop:  Ctrl+C" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""

& .\.venv\Scripts\python.exe app.py

Read-Host "Press Enter to exit"