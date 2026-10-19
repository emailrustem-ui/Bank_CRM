# -*- coding: utf-8 -*-
"""Одноразовая нормализация телефонов в существующей БД.

Приводит все поля phone (Company, Contact) к формату "номер1; номер2",
заменяя запятые, слеши, "|" и переносы на "; ".

Запуск:  python normalize_phones.py [--dry-run]
"""
import argparse

from app import app
from models import Company, Contact, db
from services.phones import normalize_phone_field


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="только показать изменения")
    args = parser.parse_args()

    with app.app_context():
        changed = 0
        for model, label in ((Company, "Компания"), (Contact, "Контакт")):
            for obj in model.query.all():
                old = obj.phone or ""
                new = normalize_phone_field(old)[:300]
                if new and new != old:
                    changed += 1
                    print(f"{label} #{obj.id}: {old!r} -> {new!r}")
                    if not args.dry_run:
                        obj.phone = new
        if not args.dry_run:
            db.session.commit()
        print(f"Итого изменено записей: {changed}{' (dry-run, не сохранено)' if args.dry_run else ''}")


if __name__ == "__main__":
    main()
