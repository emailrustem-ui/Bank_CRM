import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Добавляем timezone в импорты
content = content.replace(
    "from datetime import date, datetime, timedelta",
    "from datetime import date, datetime, timedelta, timezone"
)

# 2. Заменяем устаревший utcnow() на современный аналог
content = content.replace("datetime.utcnow()", "datetime.now(timezone.utc)")

# 3. Добавляем недостающий эндпоинт /jobs/, который вызывает ошибку 404
old_func = """def _job_get(job_id):
    with JOBS_LOCK:
        job = JOBS.get(job_id)
        return dict(job) if job else None"""

new_func = """def _job_get(job_id):
    with JOBS_LOCK:
        job = JOBS.get(job_id)
        return dict(job) if job else None

@app.route("/jobs/<job_id>")
@login_required
def job_status(job_id):
    job = _job_get(job_id)
    if not job:
        return jsonify({"error": "Задача не найдена"}), 404
    return jsonify(job)"""

content = content.replace(old_func, new_func)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Файл app.py успешно исправлен! Ошибки 404 и предупреждения datetime удалены.")
