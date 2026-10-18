import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

REFERENCES_DIR = DATA_DIR / "references"
SNAPSHOTS_DIR = DATA_DIR / "snapshots"
CHROME_PROFILE_DIR = DATA_DIR / "chrome_profile"
ATTACHMENTS_DIR = DATA_DIR / "attachments"


class Config:
    SECRET_KEY = os.getenv("CRM_SECRET_KEY", "change-this-secret-key-in-production")

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
    OUTLOOK_AGENT_TOKEN = os.getenv("OUTLOOK_AGENT_TOKEN", "crm-local-token")

    # --- Вложения писем: Path-объект (используется с оператором /) ---
    ATTACHMENTS_DIR = ATTACHMENTS_DIR

    # --- Автооткрытие браузера с CRM ---
    AUTO_OPEN_BROWSER = os.getenv("CRM_OPEN_BROWSER", "1") == "1"
    APP_URL = os.getenv("CRM_URL", "http://127.0.0.1:5000/")

    COMPANIES_PER_PAGE = 25
    MAX_CONTENT_LENGTH = 20 * 1024 * 1024