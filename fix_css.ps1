# ============================================================
# fix_css.ps1 - проверяет и восстанавливает static/style.css
# Usage: powershell -ExecutionPolicy Bypass -File .\fix_css.ps1
# ============================================================

$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot

$cssPath = ".\static\style.css"

if (-not (Test-Path $cssPath)) {
    Write-Host "style.css NOT FOUND at $cssPath" -ForegroundColor Red
    Write-Host "Creating empty file..." -ForegroundColor Yellow
    New-Item -ItemType File -Path $cssPath -Force | Out-Null
}

$size = (Get-Item $cssPath).Length
Write-Host "style.css size: $size bytes" -ForegroundColor Cyan

if ($size -lt 1000) {
    Write-Host "WARNING: file is too small (probably broken)" -ForegroundColor Red
} else {
    Write-Host "File size OK" -ForegroundColor Green
}

# Show first 200 chars
$content = [System.IO.File]::ReadAllText((Resolve-Path $cssPath), [System.Text.Encoding]::UTF8)
Write-Host "`nFirst 200 chars:" -ForegroundColor Cyan
Write-Host $content.Substring(0, [Math]::Min(200, $content.Length))
Write-Host "`n"

# Check if it contains expected CSS rules
$hasBody = $content -match "body\s*\{"
$hasBtn = $content -match "\.btn\s*\{"
$hasTabs = $content -match "\.tabs\s*\{"

if (-not $hasBody -or -not $hasBtn -or -not $hasTabs) {
    Write-Host "MISSING critical CSS rules (body/btn/tabs)" -ForegroundColor Red
    Write-Host "File is broken. Restoring..." -ForegroundColor Yellow
    
    # Backup broken file
    $backup = "$cssPath.broken_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    Copy-Item $cssPath $backup -Force
    Write-Host "Backup saved: $backup" -ForegroundColor Cyan
    
    # Write minimal working CSS
    $minimalCss = @'
:root {
    --navy: #0b2545;
    --blue: #1f6feb;
    --green: #1a7f4b;
    --orange: #b96a00;
    --red: #c62f38;
    --gray: #6b7785;
    --gray-light: #eef1f5;
    --border: #e3e8ef;
    --text: #1c2733;
    --bg: #f5f7fa;
    --radius: 12px;
    --shadow: 0 2px 10px rgba(16, 42, 77, .05);
}

* { box-sizing: border-box; }

body {
    margin: 0;
    font-family: "Segoe UI", system-ui, -apple-system, Arial, sans-serif;
    font-size: 14px;
    color: var(--text);
    background: var(--bg);
    line-height: 1.5;
}

h1 { font-size: 26px; margin: 0 0 6px; font-weight: 650; }
h2 { font-size: 21px; margin: 0 0 10px; }
h3 { font-size: 16px; margin: 0; font-weight: 600; }
h4 { font-size: 14px; margin: 0 0 10px; }
p { margin: 0 0 10px; }
a { color: var(--blue); text-decoration: none; }
a:hover { text-decoration: underline; }

.muted { color: var(--gray); }
.small { font-size: 12px; }
.text-danger { color: var(--red); }
.text-right { text-align: right; }
.mt-2 { margin-top: 8px; }
.mt-3 { margin-top: 12px; }
.mt-4 { margin-top: 20px; }
.mb-3 { margin-bottom: 12px; }
.flex-1 { flex: 1; }
.inline { display: inline-flex; }
.flex-gap { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }
.pre-wrap { white-space: pre-wrap; word-break: break-word; }
code { background: var(--gray-light); padding: 2px 5px; border-radius: 4px; font-size: 12px; }

.layout { display: flex; min-height: 100vh; }

.sidebar {
    width: 248px;
    flex-shrink: 0;
    background: var(--navy);
    color: #fff;
    display: flex;
    flex-direction: column;
    position: sticky;
    top: 0;
    height: 100vh;
}

.brand {
    display: flex;
    align-items: center;
    gap: 11px;
    padding: 24px 20px;
    border-bottom: 1px solid rgba(255,255,255,.09);
}

.brand-mark {
    width: 38px; height: 38px;
    background: var(--blue);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-weight: 700; font-size: 20px;
}

.brand-title { font-weight: 600; font-size: 15px; }
.brand-sub { font-size: 11px; color: #9fb3cd; margin-top: 2px; }

.nav { padding: 16px 12px; display: flex; flex-direction: column; gap: 4px; }

.nav-item {
    display: flex; align-items: center; gap: 11px;
    padding: 11px 13px;
    border-radius: 8px;
    color: #c7d5e8;
    font-size: 13.5px;
    transition: background .15s, color .15s;
}

.nav-item:hover { background: rgba(255,255,255,.07); color: #fff; text-decoration: none; }
.nav-icon { width: 18px; text-align: center; font-size: 15px; }

.sidebar-footer { margin-top: auto; padding: 16px; border-top: 1px solid rgba(255,255,255,.09); }

.user-box { display: flex; align-items: center; gap: 10px; }
.avatar {
    width: 34px; height: 34px; border-radius: 50%;
    background: var(--navy); display: flex; align-items: center; justify-content: center;
    font-weight: 600;
}
.user-name { font-size: 12.5px; }
.logout { font-size: 11.5px; color: #9fb3cd; }

.main { flex: 1; min-width: 0; }

.topbar {
    height: 62px;
    background: #fff;
    border-bottom: 1px solid var(--border);
    display: flex; align-items: center; justify-content: space-between;
    padding: 0 28px;
}

.topbar-title { font-weight: 600; font-size: 14px; color: var(--navy); }
.date-chip { font-size: 12px; color: var(--gray); }

.content { padding: 26px 28px 40px; max-width: 1560px; }

.page-head {
    display: flex; align-items: flex-start; justify-content: space-between;
    gap: 20px; margin-bottom: 22px; flex-wrap: wrap;
}

.head-meta { display: flex; align-items: center; gap: 10px; margin-top: 9px; flex-wrap: wrap; }
.head-actions { display: flex; gap: 8px; }

.card {
    background: #fff;
    border: 1px solid var(--border);
    border-radius: var(--radius);
    box-shadow: var(--shadow);
    overflow: hidden;
}

.card-head {
    display: flex; align-items: center; justify-content: space-between;
    gap: 12px; padding: 16px 20px;
    border-bottom: 1px solid var(--border);
}

.card-body { padding: 20px; }
.card-foot { padding: 12px 20px; border-top: 1px solid var(--border); background: #fafbfc; }

.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; align-items: start; }

@media (max-width: 1100px) {
    .grid-2 { grid-template-columns: 1fr; }
    .sidebar { width: 210px; }
}

@media (max-width: 760px) {
    .layout { flex-direction: column; }
    .sidebar { width: 100%; height: auto; position: relative; }
    .nav { flex-direction: row; flex-wrap: wrap; padding: 10px; }
    .sidebar-footer { display: none; }
    .content { padding: 18px 14px; }
    .topbar { padding: 0 14px; }
}

.stat-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 22px; }

@media (max-width: 1100px) { .stat-grid { grid-template-columns: repeat(2, 1fr); } }

.stat-card {
    background: #fff; border: 1px solid var(--border);
    border-radius: var(--radius); padding: 18px 20px; box-shadow: var(--shadow);
}

.stat-label { font-size: 12.5px; color: var(--gray); }
.stat-value { font-size: 32px; font-weight: 650; margin: 6px 0; letter-spacing: -.8px; }
.stat-note { font-size: 11.5px; color: var(--gray); }
.stat-link { font-size: 12px; }
.stat-green { border-top: 3px solid var(--green); }
.stat-orange { border-top: 3px solid var(--orange); }

.mini-badge {
    display: inline-block; font-size: 10.5px; font-weight: 500;
    background: #fdeced; color: var(--red);
    padding: 3px 7px; border-radius: 20px; margin-left: 8px; vertical-align: middle;
}

.btn {
    display: inline-flex; align-items: center; justify-content: center; gap: 6px;
    padding: 9px 16px;
    border: 1px solid transparent;
    border-radius: 8px;
    font-size: 13px; font-weight: 550;
    cursor: pointer;
    transition: background .15s, border-color .15s, transform .05s;
    white-space: nowrap;
    text-decoration: none;
    line-height: 1.4;
    font-family: inherit;
}

.btn:hover { text-decoration: none; }
.btn:active { transform: translateY(1px); }

.btn-primary { background: var(--blue); color: #fff; }
.btn-primary:hover { background: #1a60d0; }

.btn-outline { background: #fff; border-color: var(--border); color: var(--text); }
.btn-outline:hover { background: var(--gray-light); }

.btn-ghost { background: transparent; color: var(--gray); }
.btn-ghost:hover { background: var(--gray-light); color: var(--text); }

.btn-danger { background: #fdeced; color: var(--red); }
.btn-danger:hover { background: #f9d8db; }

.btn-sm { padding: 5px 10px; font-size: 12px; }
.btn-full { width: 100%; }

.check-btn {
    width: 24px; height: 24px; border: 1px solid var(--border);
    background: #fff; border-radius: 6px; cursor: pointer; color: var(--green);
}
.check-btn:hover { background: #e5f5ec; }

.link { font-size: 12.5px; }

.form-stack { display: flex; flex-direction: column; gap: 14px; }

label { display: flex; flex-direction: column; gap: 6px; font-size: 12.5px; color: var(--gray); font-weight: 500; }

input[type="text"], input[type="password"], input[type="email"],
input[type="date"], input[type="file"], select, textarea {
    width: 100%;
    padding: 9px 11px;
    border: 1px solid var(--border);
    border-radius: 8px;
    font-size: 13px;
    font-family: inherit;
    color: var(--text);
    background: #fff;
    outline: none;
    transition: border-color .15s, box-shadow .15s;
}

input:focus, select:focus, textarea:focus {
    border-color: var(--blue);
    box-shadow: 0 0 0 3px rgba(31,111,235,.12);
}

input:disabled { background: var(--gray-light); color: var(--gray); }

textarea { resize: vertical; line-height: 1.6; }

.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }

.checkbox-line { flex-direction: row; align-items: center; gap: 8px; font-size: 13px; }
.checkbox-line input { width: auto; }

.filter-bar { display: flex; gap: 10px; align-items: flex-end; flex-wrap: wrap; padding: 16px 20px; }
.filter-bar label { flex: 1; min-width: 160px; }
.filter-bar input, .filter-bar select { flex: 1; }
.filter-bar .btn { align-self: flex-end; }

.input-sm { width: 240px; padding: 6px 10px; font-size: 12px; }

.hint { font-size: 12px; color: var(--gray); }

.mail-body { font-family: "Segoe UI", Arial, sans-serif; font-size: 14px; }

.table-wrap { overflow-x: auto; }

.table { width: 100%; border-collapse: collapse; font-size: 13px; }

.table th {
    text-align: left; padding: 12px 18px;
    background: #fafbfc; color: var(--gray);
    font-size: 11.5px; font-weight: 600;
    text-transform: uppercase; letter-spacing: .3px;
    border-bottom: 1px solid var(--border);
    white-space: nowrap;
}

.table td { padding: 13px 18px; border-bottom: 1px solid var(--border); vertical-align: top; }
.table tr:last-child td { border-bottom: none; }
.table tbody tr:hover { background: #fafcff; }

.table-sm th, .table-sm td { padding: 10px 14px; font-size: 12.5px; }

.company-link { font-weight: 600; color: var(--navy); }
.company-link:hover { color: var(--blue); }

.email-link { font-weight: 550; }

.row-done td { color: var(--gray); }
.row-done td:first-child { text-decoration: line-through; }

.pagination {
    display: flex; align-items: center; justify-content: space-between;
    padding: 14px 20px; border-top: 1px solid var(--border);
}

.badge {
    display: inline-block; padding: 4px 9px;
    border-radius: 20px; font-size: 11.5px; font-weight: 550;
    white-space: nowrap;
}

.badge-blue { background: #e8f1ff; color: var(--blue); }
.badge-green { background: #e5f5ec; color: var(--green); }
.badge-orange { background: #fff3dd; color: var(--orange); }
.badge-red { background: #fdeced; color: var(--red); }
.badge-gray { background: var(--gray-light); color: var(--gray); }

.code-chip {
    display: inline-block;
    font-family: "Consolas", monospace;
    font-size: 12px;
    background: var(--gray-light);
    padding: 3px 7px;
    border-radius: 5px;
    color: var(--navy);
}

.tabs { display: flex; gap: 4px; border-bottom: 1px solid var(--border); margin-bottom: 20px; flex-wrap: wrap; }

.tab {
    padding: 12px 18px;
    background: transparent; border: none;
    border-bottom: 2px solid transparent;
    font-size: 13.5px; font-weight: 550; color: var(--gray);
    cursor: pointer;
    font-family: inherit;
}

.tab:hover { color: var(--text); background: #eef2f7; }
.tab.active { color: var(--blue); border-bottom-color: var(--blue); }

.pane { display: none; }
.pane.active { display: block; animation: fadeIn .18s ease; }

@keyframes fadeIn { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: none; } }

.list-row {
    display: flex; align-items: center; gap: 12px;
    padding: 13px 20px; border-bottom: 1px solid var(--border);
}
.list-row:last-child { border-bottom: none; }
.list-main { flex: 1; min-width: 0; }
.list-side { flex-shrink: 0; }

.timeline { padding: 6px 0; }
.timeline-item { display: flex; gap: 14px; padding: 10px 0 18px; position: relative; }
.timeline-dot {
    width: 9px; height: 9px; border-radius: 50%;
    background: var(--blue); margin-top: 6px; flex-shrink: 0;
    box-shadow: 0 0 0 4px #e8f1ff;
}
.timeline-title { font-weight: 600; margin: 4px 0; }
.timeline-body { font-size: 12.5px; color: var(--gray); white-space: pre-wrap; }

.detail-list { display: grid; grid-template-columns: 190px 1fr; gap: 12px 16px; margin: 0; }
.detail-list dt { color: var(--gray); font-size: 12.5px; }
.detail-list dd { margin: 0; font-size: 13px; font-weight: 500; }

@media (max-width: 600px) {
    .detail-list { grid-template-columns: 1fr; gap: 4px; }
    .detail-list dd { margin-bottom: 10px; }
}

.flashes { display: flex; flex-direction: column; gap: 10px; margin-bottom: 18px; }

.flash {
    padding: 12px 16px;
    border-radius: 9px;
    font-size: 13px;
    display: flex; align-items: flex-start; justify-content: space-between; gap: 12px;
    border: 1px solid transparent;
}

.flash-success { background: #e5f5ec; color: var(--green); border-color: #cbe9d8; }
.flash-danger { background: #fdeced; color: var(--red); border-color: #f5cfd2; }
.flash-warning { background: #fff3dd; color: var(--orange); border-color: #f5e2bd; }
.flash-info { background: #e8f1ff; color: var(--blue); border-color: #d3e3ff; }

.flash-close { background: none; border: none; font-size: 18px; cursor: pointer; color: inherit; line-height: 1; }

.info-strip {
    background: #e8f1ff;
    color: #355b8f;
    padding: 10px 16px;
    border-radius: 8px;
    font-size: 12.5px;
    margin-bottom: 18px;
}

.info-box {
    background: #f8fafc;
    border: 1px solid var(--border);
    border-radius: 9px;
    padding: 14px 16px;
    font-size: 13px;
}

.empty-inline { padding: 26px 20px; color: var(--gray); font-size: 13px; text-align: center; }
.empty-state { padding: 60px 20px; text-align: center; }

.auth-wrapper {
    min-height: 100vh; display: flex; align-items: center; justify-content: center;
    background: linear-gradient(135deg, #0b2545 0%, #13315c 60%, #1f6feb 140%);
    padding: 20px; flex-direction: column;
}

.auth-card {
    background: #fff; border-radius: 16px; padding: 38px;
    width: 100%; max-width: 400px; box-shadow: 0 20px 60px rgba(0,0,0,.25);
}

.auth-logo {
    width: 48px; height: 48px; border-radius: 12px;
    background: var(--blue); color: #fff;
    display: flex; align-items: center; justify-content: center;
    font-size: 24px; font-weight: 700; margin-bottom: 20px;
}

.auth-card h1 { font-size: 21px; }
.auth-hint { font-size: 12px; color: var(--gray); margin: 18px 0 0; text-align: center; }

.fetch-card { max-width: 640px; margin: 40px auto; }
.fetch-icon { font-size: 42px; margin-bottom: 12px; }

.progress { height: 8px; background: var(--gray-light); border-radius: 20px; overflow: hidden; margin: 22px 0; }
.progress-bar { height: 100%; background: var(--blue); transition: width .5s ease; border-radius: 20px; }

.fetch-log {
    background: #f8fafc; border: 1px solid var(--border);
    padding: 12px 14px; border-radius: 8px; min-height: 50px;
}

.flow-steps { display: flex; flex-direction: column; gap: 12px; }
.flow-step { display: flex; align-items: center; gap: 11px; font-size: 13px; }
.flow-step span {
    width: 24px; height: 24px; border-radius: 50%;
    background: #e8f1ff; color: var(--blue);
    display: flex; align-items: center; justify-content: center;
    font-size: 12px; font-weight: 600; flex-shrink: 0;
}

.var-list { margin: 10px 0 0; padding-left: 18px; font-size: 12.5px; }
.var-list li { margin-bottom: 7px; }

summary { cursor: pointer; }
details[open] summary { margin-bottom: 6px; }
'@

    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText((Resolve-Path $cssPath), $minimalCss, $utf8NoBom)
    Write-Host "RESTORED: minimal working CSS written" -ForegroundColor Green
} else {
    Write-Host "CSS file looks OK" -ForegroundColor Green
}

Write-Host "`nDone. Restart CRM and refresh browser with Ctrl+F5" -ForegroundColor Cyan