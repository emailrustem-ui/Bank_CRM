import logging
import os
import secrets
from pathlib import Path

try:  # необязательная зависимость: .env подхватывается, если установлен
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent / ".env")
except ImportError:
    pass

log = logging.getLogger("crm.config")

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

REFERENCES_DIR = DATA_DIR / "references"
SNAPSHOTS_DIR = DATA_DIR / "snapshots"
CHROME_PROFILE_DIR = DATA_DIR / "chrome_profile"
ATTACHMENTS_DIR = DATA_DIR / "attachments"


def _load_secret_key() -> str:
    """SECRET_KEY обязателен. В dev допускается временный ключ (с предупреждением),
    в production приложение не стартует без заданного секрета."""
    key = os.getenv("CRM_SECRET_KEY", "").strip()
    if key:
        return key
    if os.getenv("FLASK_ENV", "").lower() == "production" or os.getenv("CRM_FORCE_SECRET") == "1":
        raise RuntimeError(
            "Переменная CRM_SECRET_KEY не задана. Сгенерируйте ключ: "
            "python -c \"import secrets; print(secrets.token_hex(32))\" и поместите в .env"
        )
    log.warning(
        "CRM_SECRET_KEY не задан — используется временный ключ. "
        "Сессии сбрасываются при каждом запуске. Для постоянной работы добавьте ключ в .env "
        "(файл .env в git не попадает)."
    )
    return secrets.token_hex(32)


class Config:
    SECRET_KEY = _load_secret_key()

    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DATA_DIR / 'crm.db'}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # --- Загрузчик данных компаний ---
    # 1 = скрытый режим (без окна браузера), 0 = видимое окно (для отладки)
    CHECKO_HEADLESS = os.getenv("CHECKO_HEADLESS", "1") == "1"
    CHECKO_PROFILE_DIR = str(CHROME_PROFILE_DIR)
    CHECKO_MIN_DELAY = 15
    CHECKO_CACHE_DAYS = 30

    # --- Outlook ---
    OUTLOOK_AGENT_URL = os.getenv("OUTLOOK_AGENT_URL", "http://127.0.0.1:8765")
    # Токен агента обязателен (совпадает с OUTLOOK_AGENT_TOKEN у tools/outlook_agent.py)
    OUTLOOK_AGENT_TOKEN = os.getenv("OUTLOOK_AGENT_TOKEN", "").strip()

    # --- Загрузка файлов: белый список расширений ---
    ALLOWED_UPLOAD_EXTENSIONS = {"xlsx", "xlsm", "csv"}
    ALLOWED_ATTACHMENT_EXTENSIONS = {
        "pdf", "doc", "docx", "xls", "xlsx", "xlsm", "ppt", "pptx",
        "png", "jpg", "jpeg", "txt", "zip",
    }

    # --- Вложения писем: Path-объект (используется с оператором /) ---
    ATTACHMENTS_DIR = ATTACHMENTS_DIR

    # --- Автооткрытие браузера с CRM ---
    AUTO_OPEN_BROWSER = os.getenv("CRM_OPEN_BROWSER", "1") == "1"
    APP_URL = os.getenv("CRM_URL", "http://127.0.0.1:5000/")

    COMPANIES_PER_PAGE = 25
    MAX_CONTENT_LENGTH = 20 * 1024 * 1024