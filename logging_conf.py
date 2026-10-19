"""Единая настройка логирования для CRM.

Логи пишутся в консоль и в data/crm.log (ротация 1 МБ x 5 файлов).
Использование: from logging_conf import log; log.error("...", exc_info=True)
"""
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_DIR = Path(__file__).resolve().parent / "data"


def setup_logging(level: int = logging.INFO) -> logging.Logger:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    root = logging.getLogger("crm")
    if root.handlers:  # повторный вызов (reloader/тесты) — не дублируем хендлеры
        return root
    root.setLevel(level)
    fmt = logging.Formatter("%(asctime)s %(levelname)-7s %(name)s: %(message)s")

    file_handler = RotatingFileHandler(
        LOG_DIR / "crm.log", maxBytes=1_000_000, backupCount=5, encoding="utf-8"
    )
    file_handler.setFormatter(fmt)
    root.addHandler(file_handler)

    console = logging.StreamHandler()
    console.setFormatter(fmt)
    root.addHandler(console)
    return root


log = setup_logging()
