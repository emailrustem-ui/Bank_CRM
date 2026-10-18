"""
replace_reports.py - заменяет блок отчётов в app.py
Запуск: .venv\Scripts\python.exe replace_reports.py
"""

import shutil
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent
APP_PATH = BASE / "app.py"
BLOCK_PATH = BASE / "reports_block.py"

if not APP_PATH.exists():
    print(f"[!] app.py не найден: {APP_PATH}")
    exit(1)

if not BLOCK_PATH.exists():
    print(f"[!] reports_block.py не найден: {BLOCK_PATH}")
    exit(1)

# Читаем файлы
app_text = APP_PATH.read_text(encoding="utf-8")
block_text = BLOCK_PATH.read_text(encoding="utf-8")

# Находим маркеры
start_marker = '# ============================================================\n# ОТЧЁТЫ'
end_marker = '# ============================================================\n# АВТООТКРЫТИЕ БРАУЗЕРА'

i_start = app_text.find(start_marker)
if i_start < 0:
    print("[!] Стартовый маркер не найден. Ищем альтернативный...")
    start_marker = '@app.route("/reports")'
    i_start = app_text.find(start_marker)
    if i_start < 0:
        print("[!] Не удалось найти блок отчётов в app.py")
        exit(1)
    # Идём к началу строки
    i_start = app_text.rfind('\n', 0, i_start) + 1

i_end = app_text.find(end_marker)
if i_end < 0:
    print("[!] Конечный маркер не найден. Ищем альтернативный...")
    end_marker = 'def open_browser_delayed'
    i_end = app_text.find(end_marker)
    if i_end < 0:
        print("[!] Не удалось найти конец блока отчётов")
        exit(1)
    # Идём к началу строки
    i_end = app_text.rfind('\n', 0, i_end) + 1

# Бэкап
backup_path = APP_PATH.with_suffix(f".bak_{datetime.now():%Y%m%d_%H%M%S}")
shutil.copy2(APP_PATH, backup_path)
print(f"[i] Бэкап: {backup_path.name}")

# Замена
new_text = app_text[:i_start] + block_text.rstrip() + "\n\n\n" + app_text[i_end:]

# Запись
APP_PATH.write_text(new_text, encoding="utf-8", newline="\n")
print(f"[+] app.py обновлён ({APP_PATH.stat().st_size} байт)")
print()
print("=" * 60)
print("ГОТОВО. Далее:")
print("1. Перезапустите CRM: powershell -ExecutionPolicy Bypass -File .\\start_all.ps1")
print("2. Откройте раздел «Отчёты»")
print("=" * 60)