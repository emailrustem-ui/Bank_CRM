"""
migrate_db.py — одноразовая проверка/достройка схемы SQLite.
Запуск:  .venv\Scripts\python.exe migrate_db.py
"""

from sqlalchemy import text as sa_text

from app import app, db


def _columns(table):
    rows = db.session.execute(sa_text(f"PRAGMA table_info({table})")).fetchall()
    return {row[1] for row in rows}


def _ensure(table, additions):
    existing = _columns(table)
    if not existing:
        print(f"[i] таблица {table} отсутствует — будет создана при старте CRM")
        return
    added = []
    for name, ddl in additions.items():
        if name not in existing:
            db.session.execute(sa_text(f"ALTER TABLE {table} ADD COLUMN {ddl}"))
            added.append(name)
    if added:
        db.session.commit()
        print(f"[+] {table}: добавлены колонки {', '.join(added)}")
    else:
        print(f"[=] {table}: схема актуальна")


with app.app_context():
    db.create_all()
    print("[i] недостающие таблицы созданы")

    _ensure("companies", {
        "extra": "extra TEXT DEFAULT ''",
    })

    _ensure("template_attachments", {
        "filename": "filename VARCHAR(300) DEFAULT ''",
        "original_name": "original_name VARCHAR(300) DEFAULT ''",
        "file_size": "file_size INTEGER DEFAULT 0",
    })

    _ensure("deals", {
        "analyst_name": "analyst_name VARCHAR(300) DEFAULT ''",
        "analyst_phone": "analyst_phone VARCHAR(100) DEFAULT ''",
        "comment": "comment TEXT DEFAULT ''",
    })

print("Миграция завершена.")