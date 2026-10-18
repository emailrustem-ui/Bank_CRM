"""
add_user.py — создание / обновление пользователя CRM.

Примеры запуска:
    .venv\Scripts\python.exe add_user.py Husainov "Хусаинов Рустем Рифович" МойПароль123
    .venv\Scripts\python.exe add_user.py manager "Клиентский менеджер" НовыйПароль

Без аргументов — интерактивный режим (спросит логин, ФИО и пароль).
"""

import getpass
import sys

from app import app, db
from models import User


def main():
    if len(sys.argv) >= 4:
        username = sys.argv[1].strip()
        full_name = sys.argv[2].strip()
        password = sys.argv[3]
    else:
        username = input("Логин: ").strip()
        full_name = input("ФИО (для писем и подписи): ").strip()
        password = getpass.getpass("Пароль: ")

    if not username or not password:
        print("Логин и пароль не могут быть пустыми.")
        sys.exit(1)

    with app.app_context():
        db.create_all()

        user = User.query.filter_by(username=username).first()

        if user:
            user.set_password(password)
            if full_name:
                user.full_name = full_name
            user.is_enabled = True
            print(f"Пользователь '{username}' обновлён (пароль заменён).")
        else:
            user = User(
                username=username,
                full_name=full_name or username,
                is_enabled=True,
            )
            user.set_password(password)
            db.session.add(user)
            print(f"Пользователь '{username}' создан.")

        db.session.commit()

    print("Теперь можно войти на http://127.0.0.1:5000")


if __name__ == "__main__":
    main()