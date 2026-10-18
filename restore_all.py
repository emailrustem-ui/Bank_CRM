"""
restore_all.py - восстанавливает три ключевых файла CRM:
  static/style.css
  templates/base.html
  templates/company_detail.html

Запуск:  .venv\Scripts\python.exe restore_all.py
"""

import shutil
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent


def backup(path: Path):
    if path.exists():
        b = path.with_suffix(f"{path.suffix}.bak_{datetime.now():%Y%m%d_%H%M%S}")
        shutil.copy2(path, b)
        print(f"[i] бэкап: {b.name}")


def write(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print(f"[+] записан: {path} ({path.stat().st_size} байт)")


# ============================================================
# 1. static/style.css
# ============================================================
STYLE_CSS = r""":root {
    --navy: #0b2545;
    --navy-2: #13315c;
    --blue: #1f6feb;
    --blue-light: #e8f1ff;
    --green: #1a7f4b;
    --green-light: #e5f5ec;
    --orange: #b96a00;
    --orange-light: #fff3dd;
    --red: #c62f38;
    --red-light: #fdeced;
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

h1 { font-size: 26px; margin: 0 0 6px; font-weight: 650; letter-spacing: -.4px; }
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
    background: var(--navy-2); display: flex; align-items: center; justify-content: center;
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
    background: var(--red-light); color: var(--red);
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

.btn-danger { background: var(--red-light); color: var(--red); }
.btn-danger:hover { background: #f9d8db; }

.btn-sm { padding: 5px 10px; font-size: 12px; }
.btn-full { width: 100%; }

.check-btn {
    width: 24px; height: 24px; border: 1px solid var(--border);
    background: #fff; border-radius: 6px; cursor: pointer; color: var(--green);
}
.check-btn:hover { background: var(--green-light); }

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

.badge-blue { background: var(--blue-light); color: var(--blue); }
.badge-green { background: var(--green-light); color: var(--green); }
.badge-orange { background: var(--orange-light); color: var(--orange); }
.badge-red { background: var(--red-light); color: var(--red); }
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
    box-shadow: 0 0 0 4px var(--blue-light);
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

.flash-success { background: var(--green-light); color: var(--green); border-color: #cbe9d8; }
.flash-danger { background: var(--red-light); color: var(--red); border-color: #f5cfd2; }
.flash-warning { background: var(--orange-light); color: var(--orange); border-color: #f5e2bd; }
.flash-info { background: var(--blue-light); color: var(--blue); border-color: #d3e3ff; }

.flash-close { background: none; border: none; font-size: 18px; cursor: pointer; color: inherit; line-height: 1; }

.info-strip {
    background: var(--blue-light);
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
    background: var(--blue-light); color: var(--blue);
    display: flex; align-items: center; justify-content: center;
    font-size: 12px; font-weight: 600; flex-shrink: 0;
}

.var-list { margin: 10px 0 0; padding-left: 18px; font-size: 12.5px; }
.var-list li { margin-bottom: 7px; }

summary { cursor: pointer; }
details[open] summary { margin-bottom: 6px; }
"""


# ============================================================
# 2. templates/base.html
# ============================================================
BASE_HTML = r"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="csrf-token" content="{{ csrf_token() }}">
    <title>{% block title %}CRM банка{% endblock %}</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>

{% if current_user.is_authenticated %}
<div class="layout">

    <aside class="sidebar">
        <div class="brand">
            <div class="brand-mark">Б</div>
            <div>
                <div class="brand-title">CRM Менеджера</div>
                <div class="brand-sub">Корпоративный бизнес</div>
            </div>
        </div>

        <nav class="nav">
            <a href="{{ url_for('dashboard') }}" class="nav-item">
                <span class="nav-icon">▦</span> Дашборд
            </a>
            <a href="{{ url_for('companies') }}" class="nav-item">
                <span class="nav-icon">◈</span> Компании
            </a>
            <a href="{{ url_for('company_new') }}" class="nav-item">
                <span class="nav-icon">＋</span> Новая по ИНН
            </a>
            <a href="{{ url_for('deals_page') }}" class="nav-item">
                <span class="nav-icon">▣</span> Заявки
            </a>
            <a href="{{ url_for('products_page') }}" class="nav-item">
                <span class="nav-icon">▤</span> Продукты и ОКВЭД
            </a>
            <a href="{{ url_for('tasks_page') }}" class="nav-item">
                <span class="nav-icon">✓</span> Задачи
            </a>
            <a href="{{ url_for('reports_page') }}" class="nav-item">
                <span class="nav-icon">⇩</span> Отчёты
            </a>
            <a href="{{ url_for('templates_page') }}" class="nav-item">
                <span class="nav-icon">✉</span> Шаблоны писем
            </a>
        </nav>

        <div class="sidebar-footer">
            <div class="user-box">
                <div class="avatar">{{ current_user.full_name[:1] if current_user.full_name else 'М' }}</div>
                <div>
                    <div class="user-name">{{ current_user.full_name or current_user.username }}</div>
                    <a href="{{ url_for('logout') }}" class="logout">Выйти</a>
                </div>
            </div>
        </div>
    </aside>

    <main class="main">
        <header class="topbar">
            <div class="topbar-title">{% block page_title %}CRM{% endblock %}</div>
            <div class="topbar-right">
                <span class="date-chip">{{ now.strftime('%d.%m.%Y') }}</span>
            </div>
        </header>

        <div class="content">
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    <div class="flashes">
                        {% for category, message in messages %}
                            <div class="flash flash-{{ category }}">
                                {{ message }}
                                <button class="flash-close" onclick="this.parentElement.remove()">×</button>
                            </div>
                        {% endfor %}
                    </div>
                {% endif %}
            {% endwith %}

            {% block content %}{% endblock %}

            {% if error_page %}
                <div class="empty-state">
                    <h2>{{ error_page }}</h2>
                    <a class="btn btn-primary" href="{{ url_for('dashboard') }}">На главную</a>
                </div>
            {% endif %}
        </div>
    </main>
</div>

{% else %}
    <div class="auth-wrapper">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% for category, message in messages %}
                <div class="flash flash-{{ category }}">{{ message }}</div>
            {% endfor %}
        {% endwith %}
        {% block auth_content %}{% endblock %}
    </div>
{% endif %}

<script src="{{ url_for('static', filename='app.js') }}"></script>
{% block scripts %}{% endblock %}
</body>
</html>
"""


# ============================================================
# 3. templates/company_detail.html
# ============================================================
COMPANY_DETAIL_HTML = r"""{% extends "base.html" %}

{% block title %}{{ company.display_name }}{% endblock %}
{% block page_title %}Карточка компании{% endblock %}

{% block content %}
<div class="page-head">
    <div>
        <h1>{{ company.display_name }}</h1>
        <div class="head-meta">
            <span class="code-chip">ИНН {{ company.inn }}</span>
            {% if company.ogrn %}<span class="muted small">ОГРН {{ company.ogrn }}</span>{% endif %}
            <span class="badge badge-blue">{{ company.status_label }}</span>
        </div>
    </div>

    <div class="head-actions">
        <form method="post" action="{{ url_for('company_refresh', company_id=company.id) }}" class="inline">
            <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
            <button class="btn btn-outline" type="submit">↻ Обновить данные</button>
        </form>

        <form method="post" action="{{ url_for('company_delete', company_id=company.id) }}" class="inline">
            <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
            <button class="btn btn-danger"
                    data-confirm="Удалить компанию {{ company.display_name }} вместе с контактами, задачами, заявками и историей?">
                ✕ Удалить
            </button>
        </form>
    </div>
</div>

{% if company.checko_updated_at %}
    <div class="info-strip">
        Данные обновлены: {{ company.checko_updated_at.strftime('%d.%m.%Y %H:%M') }}
    </div>
{% endif %}

<div class="tabs">
    <button class="tab active" data-tab="card">Карточка</button>
    <button class="tab" data-tab="extra">Сведения</button>
    <button class="tab" data-tab="okved">ОКВЭД и продукты</button>
    <button class="tab" data-tab="deals">Заявки</button>
    <button class="tab" data-tab="contacts">Контакты</button>
    <button class="tab" data-tab="history">История</button>
    <button class="tab" data-tab="tasks">Задачи</button>
</div>

<!-- ================= КАРТОЧКА ================= -->
<div class="pane active" data-pane="card">
    <div class="grid-2">
        <div class="card">
            <div class="card-head"><h3>Реквизиты</h3></div>
            <div class="card-body">
                <form method="post" action="{{ url_for('company_edit', company_id=company.id) }}" class="form-stack">
                    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">

                    <label>Полное наименование
                        <input type="text" name="name" value="{{ company.name }}">
                    </label>

                    <label>Краткое наименование
                        <input type="text" name="short_name" value="{{ company.short_name }}">
                    </label>

                    <div class="form-row">
                        <label>ОГРН
                            <input type="text" name="ogrn" value="{{ company.ogrn }}">
                        </label>
                        <label>Дата регистрации
                            <input type="text" name="reg_date" value="{{ company.reg_date }}">
                        </label>
                    </div>

                    <label>Руководитель
                        <input type="text" name="director" value="{{ company.director }}">
                    </label>

                    <label>Юридический адрес
                        <textarea name="address" rows="2">{{ company.address }}</textarea>
                    </label>

                    <div class="form-row">
                        <label>Телефон
                            <input type="text" name="phone" value="{{ company.phone }}">
                        </label>
                        <label>E-mail
                            <input type="text" name="email" value="{{ company.email }}">
                        </label>
                    </div>

                    <label>Сайт
                        <input type="text" name="site" value="{{ company.site }}">
                    </label>

                    <div class="form-row">
                        <label>Основной ОКВЭД
                            <input type="text" name="okved_main_code" value="{{ company.okved_main_code }}"
                                   placeholder="46.12.1">
                        </label>
                        <label>Статус в работе
                            <select name="status">
                                {% for key, label in company_statuses.items() %}
                                    <option value="{{ key }}" {% if company.status == key %}selected{% endif %}>{{ label }}</option>
                                {% endfor %}
                            </select>
                        </label>
                    </div>

                    <button type="submit" class="btn btn-primary">Сохранить карточку</button>
                </form>
            </div>
        </div>

        <div class="card">
            <div class="card-head"><h3>Финансы и дополнительные сведения</h3></div>
            <div class="card-body">
                <dl class="detail-list">
                    <dt>Выручка</dt><dd>{{ company.revenue or '—' }}</dd>
                    <dt>Чистая прибыль</dt><dd>{{ company.net_profit or '—' }}</dd>
                    <dt>Активы</dt><dd>{{ company.assets or '—' }}</dd>
                    <dt>Собственный капитал</dt><dd>{{ company.equity or '—' }}</dd>
                    <dt>Основные средства</dt><dd>{{ company.fixed_assets or '—' }}</dd>
                    <dt>Среднесписочная численность</dt><dd>{{ company.employee_count or '—' }}</dd>
                </dl>

                {% if company.founders %}
                    <details class="mt-4">
                        <summary>Учредители</summary>
                        <div class="pre-wrap mt-2">{{ company.founders }}</div>
                    </details>
                {% endif %}

                {% if company.okved_main_title %}
                    <div class="info-box mt-4">
                        <div class="small muted">Основной вид деятельности</div>
                        <div>{{ company.okved_main_code }} — {{ company.okved_main_title }}</div>
                    </div>
                {% endif %}
            </div>
        </div>
    </div>
</div>

<!-- ================= СВЕДЕНИЯ ================= -->
{% include "company_svedeniya.html" %}

<!-- ================= ОКВЭД ================= -->
<div class="pane" data-pane="okved">
    <div class="grid-2">
        <div class="card">
            <div class="card-head"><h3>ОКВЭД компании</h3></div>

            <div class="table-wrap">
                <table class="table table-sm">
                    <thead>
                        <tr><th>Код</th><th>Вид</th><th></th></tr>
                    </thead>
                    <tbody>
                        {% for item in company.okveds %}
                            <tr>
                                <td>
                                    <span class="code-chip">{{ item.code }}</span>
                                    {% if item.title %}<div class="muted small">{{ item.title[:90] }}</div>{% endif %}
                                </td>
                                <td>
                                    {% if item.is_main %}
                                        <span class="badge badge-blue">основной</span>
                                    {% else %}
                                        <span class="muted small">дополнительный</span>
                                    {% endif %}
                                </td>
                                <td class="text-right">
                                    <form method="post"
                                          action="{{ url_for('okved_delete', company_id=company.id, okved_id=item.id) }}"
                                          class="inline">
                                        <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
                                        <button class="btn btn-sm btn-danger"
                                                data-confirm="Удалить ОКВЭД {{ item.code }} и перепроверить продукты?">✕</button>
                                    </form>
                                </td>
                            </tr>
                        {% else %}
                            <tr><td colspan="3" class="muted">ОКВЭД не загружены.</td></tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>

            <div class="card-body">
                <form method="post" action="{{ url_for('okved_add', company_id=company.id) }}" class="form-stack">
                    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">

                    <div class="form-row">
                        <label>Код ОКВЭД
                            <input type="text" name="code" placeholder="46.12.1" required>
                        </label>
                        <label>Наименование вида
                            <input type="text" name="title">
                        </label>
                    </div>

                    <label class="checkbox-line">
                        <input type="checkbox" name="is_main"> Это основной ОКВЭД
                    </label>

                    <button class="btn btn-outline btn-sm" type="submit">＋ Добавить ОКВЭД</button>
                </form>
            </div>
        </div>

        <div class="card">
            <div class="card-head">
                <h3>Доступность продуктов</h3>
                <form method="post" action="{{ url_for('company_check', company_id=company.id) }}" class="inline">
                    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
                    <button class="btn btn-sm btn-primary">Проверить</button>
                </form>
            </div>

            {% if not active_version %}
                <div class="card-body">
                    <div class="flash flash-warning">
                        Справочник ОКВЭД не загружен.
                        <a href="{{ url_for('products_page') }}">Загрузите файл в разделе «Продукты и ОКВЭД»</a>.
                    </div>
                </div>
            {% endif %}

            <div class="table-wrap">
                <table class="table table-sm">
                    <thead>
                        <tr><th>Продукт</th><th>Результат</th><th>Условия</th></tr>
                    </thead>
                    <tbody>
                        {% for check in checks %}
                            <tr>
                                <td>
                                    <a href="{{ url_for('product_detail', product_id=check.product_id) }}">
                                        {{ check.product.name }}
                                    </a>
                                </td>
                                <td>
                                    {% if check.result == 'allowed' %}
                                        <span class="badge badge-green">Доступно</span>
                                    {% elif check.result == 'conditional' %}
                                        <span class="badge badge-orange">С условиями</span>
                                    {% elif check.result == 'forbidden' %}
                                        <span class="badge badge-red">Недоступно</span>
                                    {% else %}
                                        <span class="badge badge-gray">Нет данных</span>
                                    {% endif %}
                                </td>
                                <td>
                                    {% if check.detail %}
                                        <details>
                                            <summary class="link small">Показать</summary>
                                            <div class="pre-wrap small mt-2">{{ check.detail }}</div>
                                        </details>
                                    {% endif %}
                                </td>
                            </tr>
                        {% else %}
                            <tr><td colspan="3" class="muted">Проверка ещё не выполнялась.</td></tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>

            {% if active_version %}
                <div class="card-foot small muted">
                    Версия справочника: {{ active_version.filename }}
                    · {{ active_version.created_at.strftime('%d.%m.%Y %H:%M') }}
                </div>
            {% endif %}
        </div>
    </div>
</div>

<!-- ================= ЗАЯВКИ ================= -->
<div class="pane" data-pane="deals">
    <div class="card">
        <div class="card-head">
            <h3>Заявки компании</h3>
            <a href="{{ url_for('deals_page', new=1, company_id=company.id) }}" class="btn btn-sm btn-primary">
                ＋ Новая заявка
            </a>
        </div>

        <div class="table-wrap">
            <table class="table table-sm">
                <thead>
                    <tr>
                        <th>Продукт</th>
                        <th>Сумма</th>
                        <th>Срок</th>
                        <th>Статус</th>
                        <th>Аналитик</th>
                        <th></th>
                    </tr>
                </thead>
                <tbody>
                    {% for deal in company.deals %}
                        <tr>
                            <td>{{ deal.product.name if deal.product else '—' }}</td>
                            <td>{{ deal.amount | money }}</td>
                            <td class="{% if deal.is_overdue_term %}text-danger{% endif %}">
                                {{ deal.term_date.strftime('%d.%m.%Y') if deal.term_date else '—' }}
                            </td>
                            <td><span class="badge badge-blue">{{ deal.status_label }}</span></td>
                            <td>
                                {{ deal.analyst_name or '—' }}
                                {% if deal.analyst_phone %}<div class="muted small">{{ deal.analyst_phone }}</div>{% endif %}
                            </td>
                            <td class="text-right">
                                <a href="{{ url_for('deals_page', edit=deal.id) }}" class="btn btn-sm btn-ghost">Изменить</a>
                            </td>
                        </tr>
                    {% else %}
                        <tr><td colspan="6" class="muted">Заявок по компании пока нет.</td></tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>

<!-- ================= КОНТАКТЫ ================= -->
<div class="pane" data-pane="contacts">
    <div class="card">
        <div class="card-head"><h3>Контактные лица</h3></div>

        <div class="table-wrap">
            <table class="table">
                <thead>
                    <tr>
                        <th>ФИО</th>
                        <th>Должность</th>
                        <th>Телефон</th>
                        <th>E-mail</th>
                        <th></th>
                    </tr>
                </thead>
                <tbody>
                    {% for contact in company.contacts %}
                        <tr>
                            <td>
                                {{ contact.full_name or '—' }}
                                {% if contact.is_primary %}<span class="badge badge-blue">основной</span>{% endif %}
                            </td>
                            <td>{{ contact.position or '—' }}</td>
                            <td>{{ contact.phone or '—' }}</td>
                            <td>
                                {% if contact.email %}
                                    <a href="{{ url_for('email_open', company_id=company.id, contact_id=contact.id, auto=1) }}"
                                       class="email-link"
                                       title="Открыть письмо в Outlook с обращением по ФИО">
                                        ✉ {{ contact.email }}
                                    </a>
                                    <div class="muted small">
                                        Обращение: {{ contact.full_name }}
                                    </div>
                                {% else %}
                                    <span class="muted">не указан</span>
                                {% endif %}
                            </td>
                            <td class="text-right">
                                <button class="btn btn-sm btn-ghost"
                                        data-edit-contact
                                        data-id="{{ contact.id }}"
                                        data-full-name="{{ contact.full_name }}"
                                        data-position="{{ contact.position }}"
                                        data-phone="{{ contact.phone }}"
                                        data-email="{{ contact.email }}"
                                        data-primary="{{ 1 if contact.is_primary else 0 }}">
                                    Изменить
                                </button>

                                <form method="post"
                                      action="{{ url_for('contact_delete', company_id=company.id, contact_id=contact.id) }}"
                                      class="inline">
                                    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
                                    <button class="btn btn-sm btn-danger" data-confirm="Удалить контакт?">✕</button>
                                </form>
                            </td>
                        </tr>
                    {% else %}
                        <tr><td colspan="5" class="muted">Контактов пока нет.</td></tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>

        <div class="card-body">
            <h4 class="mb-3" id="contactFormTitle">Новый контакт</h4>

            <form method="post" action="{{ url_for('contact_save', company_id=company.id) }}" class="form-stack" id="contactForm">
                <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
                <input type="hidden" name="contact_id" id="contact_id" value="">

                <div class="form-row">
                    <label>ФИО (Фамилия Имя Отчество)
                        <input type="text" name="full_name" id="contact_full_name"
                               placeholder="Иванов Иван Сергеевич" required>
                    </label>
                    <label>Должность
                        <input type="text" name="position" id="contact_position">
                    </label>
                </div>

                <div class="form-row">
                    <label>Телефон
                        <input type="text" name="phone" id="contact_phone">
                    </label>
                    <label>E-mail
                        <input type="email" name="email" id="contact_email">
                    </label>
                </div>

                <label class="checkbox-line">
                    <input type="checkbox" name="is_primary" id="contact_primary"> Основной контакт
                </label>

                <div class="flex-gap">
                    <button class="btn btn-primary" type="submit">Сохранить контакт</button>
                    <button class="btn btn-ghost" type="button" id="resetContactForm">Очистить</button>
                </div>
            </form>
        </div>
    </div>
</div>

<!-- ================= ИСТОРИЯ ================= -->
<div class="pane" data-pane="history">
    <div class="grid-2">
        <div class="card">
            <div class="card-head"><h3>Добавить запись</h3></div>
            <div class="card-body">
                <form method="post" action="{{ url_for('activity_add', company_id=company.id) }}" class="form-stack">
                    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">

                    <div class="form-row">
                        <label>Тип
                            <select name="type">
                                {% for key, label in activity_types.items() %}
                                    <option value="{{ key }}">{{ label }}</option>
                                {% endfor %}
                            </select>
                        </label>
                        <label>Тема
                            <input type="text" name="subject" placeholder="Например: первичный звонок">
                        </label>
                    </div>

                    <label>Текст
                        <textarea name="body" rows="6" required placeholder="О чём договорились, какие шаги дальше…"></textarea>
                    </label>

                    <button class="btn btn-primary" type="submit">Добавить в историю</button>
                </form>
            </div>
        </div>

        <div class="card">
            <div class="card-head"><h3>История взаимодействий</h3></div>
            <div class="card-body">
                {% if activities %}
                    <div class="timeline">
                        {% for item in activities %}
                            <div class="timeline-item">
                                <div class="timeline-dot"></div>
                                <div>
                                    <div class="small muted">
                                        {{ item.created_at.strftime('%d.%m.%Y %H:%M') }}
                                        · {{ activity_types.get(item.type, item.type) }}
                                    </div>
                                    <div class="timeline-title">{{ item.subject or 'Заметка' }}</div>
                                    <div class="pre-wrap small">{{ item.body }}</div>
                                </div>
                            </div>
                        {% endfor %}
                    </div>
                {% else %}
                    <div class="empty-inline">История пуста.</div>
                {% endif %}
            </div>
        </div>
    </div>
</div>

<!-- ================= ЗАДАЧИ ================= -->
<div class="pane" data-pane="tasks">
    <div class="card">
        <div class="card-head"><h3>Задачи по компании</h3></div>

        <div class="card-body">
            <form method="post" action="{{ url_for('task_add', company_id=company.id) }}" class="filter-bar">
                <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
                <input type="text" name="title" placeholder="Например: отправить КП по поручительству" required>
                <input type="date" name="due_date">
                <button class="btn btn-primary" type="submit">＋ Создать задачу</button>
            </form>
        </div>

        <div class="table-wrap">
            <table class="table">
                <thead>
                    <tr><th>Задача</th><th>Срок</th><th>Статус</th><th></th></tr>
                </thead>
                <tbody>
                    {% for task in tasks %}
                        <tr class="{% if task.status == 'done' %}row-done{% endif %}">
                            <td>{{ task.title }}</td>
                            <td class="{% if task.is_overdue %}text-danger{% endif %}">
                                {{ task.due_date.strftime('%d.%m.%Y') if task.due_date else '—' }}
                            </td>
                            <td>
                                {% if task.status == 'done' %}
                                    <span class="badge badge-green">Выполнена</span>
                                {% elif task.is_overdue %}
                                    <span class="badge badge-red">Просрочена</span>
                                {% else %}
                                    <span class="badge badge-orange">В работе</span>
                                {% endif %}
                            </td>
                            <td class="text-right">
                                <form method="post" action="{{ url_for('task_toggle', task_id=task.id) }}" class="inline">
                                    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
                                    <button class="btn btn-sm btn-outline">
                                        {{ 'Вернуть' if task.status == 'done' else 'Выполнить' }}
                                    </button>
                                </form>

                                <form method="post" action="{{ url_for('task_delete', task_id=task.id) }}" class="inline">
                                    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
                                    <button class="btn btn-sm btn-danger" data-confirm="Удалить задачу?">✕</button>
                                </form>
                            </td>
                        </tr>
                    {% else %}
                        <tr><td colspan="4" class="muted">Задач нет.</td></tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>
{% endblock %}
"""


# ============================================================
# ЗАПУСК
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("Восстановление ключевых файлов CRM")
    print("=" * 60)

    files = {
        BASE / "static" / "style.css": STYLE_CSS,
        BASE / "templates" / "base.html": BASE_HTML,
        BASE / "templates" / "company_detail.html": COMPANY_DETAIL_HTML,
    }

    for path, content in files.items():
        backup(path)
        write(path, content)

    print()
    print("=" * 60)
    print("ГОТОВО. Далее:")
    print("1. Перезапустите CRM: powershell -ExecutionPolicy Bypass -File .\\start_all.ps1")
    print("2. В браузере нажмите Ctrl+F5 (жёсткая перезагрузка)")
    print("3. Проверьте: http://127.0.0.1:5000/static/style.css — должен показать отформатированный CSS")
    print("=" * 60)