# ============================================================
# patch_svedeniya.ps1 - replace "extra" pane in company_detail.html
# with include of company_svedeniya.html
# Usage: powershell -ExecutionPolicy Bypass -File .\patch_svedeniya.ps1
# ============================================================

$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot

$path  = ".\templates\company_detail.html"
$block = ".\templates\company_svedeniya.html"

if (-not (Test-Path $path))  { Write-Host "company_detail.html not found" -ForegroundColor Red; exit 1 }
if (-not (Test-Path $block)) { Write-Host "company_svedeniya.html not found" -ForegroundColor Red; exit 1 }

$text = [System.IO.File]::ReadAllText((Resolve-Path $path), [System.Text.Encoding]::UTF8)

$startKey = 'data-pane="extra"'
$endKey   = 'data-pane="okved"'

$i0 = $text.IndexOf($startKey)
if ($i0 -lt 0) { Write-Host "Start marker not found: $startKey" -ForegroundColor Red; exit 1 }

$i1 = $text.IndexOf($endKey, $i0)
if ($i1 -lt 0) { Write-Host "End marker not found: $endKey" -ForegroundColor Red; exit 1 }

$iStart = $text.LastIndexOf("<div", $i0)
$iEnd   = $text.LastIndexOf("<div", $i1)

if ($iStart -lt 0 -or $iEnd -lt 0 -or $iEnd -le $iStart) {
    Write-Host "Cannot locate pane boundaries" -ForegroundColor Red
    exit 1
}

Copy-Item $path "$path.bak" -Force
Write-Host "Backup saved: company_detail.html.bak" -ForegroundColor Cyan

$includeLine = '{% include "company_svedeniya.html" %}'
$result = $text.Substring(0, $iStart) + $includeLine + "`r`n`r`n" + $text.Substring($iEnd)

$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText((Resolve-Path $path), $result, $utf8NoBom)

Write-Host "OK: company_detail.html patched (extra pane -> include)." -ForegroundColor Green