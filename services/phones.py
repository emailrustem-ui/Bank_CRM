# -*- coding: utf-8 -*-
"""Единая нормализация телефонных номеров.

Правило: несколько телефонов хранятся в одной строке через разделитель "; ".
Любые другие разделители (",", "/", "|", "или", переводы строк, переносы)
приводятся к каноническому виду.
"""
import re

PHONE_SEPARATOR = "; "

# Любые «мягкие» разделители между номерами
_SPLIT_RX = re.compile(
    r"(?:;|,|\B/\B|\s/\s*|\||\u0438\u043b\u0438|\r?\n)+",  # ; , / | или, перенос строки
    flags=re.I,
)

# Один телефонный номер: необязательный +7/8 и 10–11 цифр с возможными
# скобками, пробелами, дефисами и точками внутри.
_PHONE_RX = re.compile(r"(?:\+7|8)?[\s(]*7?[\s().\-]*\d[\d\s().\-]{8,18}\d")


def split_phones(value):
    """Разбить строку на список отдельных номеров."""
    text = str(value or "").strip()
    if not text:
        return []
    parts = [p.strip(" \t.;,-") for p in _SPLIT_RX.split(text)]
    result = []
    for part in parts:
        if not part:
            continue
        # Если часть содержит несколько склеенных номеров — разбиваем по паттерну
        matches = _PHONE_RX.findall(part)
        candidates = matches if len(matches) > 1 else [part]
        for cand in candidates:
            cand = cand.strip()
            if cand and cand not in result:
                result.append(cand)
    return result


def join_phones(phones):
    """Собрать список номеров в строку через '; ' (без дублей)."""
    seen = []
    for phone in phones or []:
        phone = str(phone or "").strip()
        if phone and phone not in seen:
            seen.append(phone)
    return PHONE_SEPARATOR.join(seen)


def normalize_phone_field(value):
    """Нормализовать произвольную строку телефонов к формату 'т1; т2; ...'."""
    return join_phones(split_phones(value))


def first_phone(value):
    """Первый номер из строки (для ссылки tel:)."""
    phones = split_phones(value)
    return phones[0] if phones else ""


def tel_href(value):
    """Ссылка tel: из первого номера — только цифры и '+'. Остальное вырезаем,
    чтобы лишние ';' не портили набор номера."""
    raw = first_phone(value)
    cleaned = re.sub(r"[^\d+]", "", raw)
    if not cleaned:
        return ""
    if cleaned.startswith("8"):
        cleaned = "+7" + cleaned[1:]
    elif not cleaned.startswith("+"):
        cleaned = "+7" + cleaned
    return f"tel:{cleaned}"
