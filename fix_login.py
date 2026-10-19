"""Разовая починка входа: пользователь 'manager' -> '1', пароль '1'.
Запуск: python fix_login.py   (сервер должен быть остановлен)"""
import os, sqlite3, sys
from werkzeug.security import generate_password_hash

DB = os.path.join(os.path.dirname(__file__), "data", "crm.db")
if not os.path.exists(DB):
    print("БД не найдена:", DB); sys.exit(1)

c = sqlite3.connect(DB)
users = dict(c.execute("SELECT username, id FROM users").fetchall())
print("Пользователи в БД:", list(users))

if "1" not in users:
    if "manager" in users:
        c.execute("UPDATE users SET username='1', is_enabled=1, must_change_password=0 WHERE username='manager'")
        print("Переименован 'manager' -> '1'")
    else:
        c.execute("INSERT INTO users (username, password_hash, full_name, is_enabled, must_change_password) VALUES (?,?,?,?,0)",
                  ("1", generate_password_hash("1"), "Клиентский менеджер", 1))
        print("Создан пользователь '1'")
else:
    c.execute("UPDATE users SET is_enabled=1, must_change_password=0 WHERE username='1'")

c.execute("UPDATE users SET password_hash=? WHERE username='1'", (generate_password_hash("1"),))
c.commit()
print("Готово. Теперь вход: логин 1, пароль 1")
print("Итог:", c.execute("SELECT id, username, is_enabled FROM users").fetchall())
c.close()
