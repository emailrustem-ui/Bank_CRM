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

_DIGITS_RX = re.compile(r"\d")


def _looks_like_phone(part):
    """Похож ли фрагмент на полноценный номер (>=10 цифр)."""
    return len(_DIGITS_RX.findall(part)) >= 10


def _reassemble(parts):
    """Собрать «разрезанные» номера обратно.

    Например, '+7; 384; 277-62-22' — это один номер, где код страны,
    код региона и сам номер были ошибочно разделены точкой с запятой.
    Жадная склейка соседних частей: держим буфер, пока в нём не наберётся
    полноценный номер (10–11 цифр); лишние цифры = следующий номер.
    """
    result = []
    buf = ""
    for part in parts:
        candidate = f"{buf} {part}".strip() if buf else part
        digits = len(_DIGITS_RX.findall(candidate))
        if digits > 11 and buf:
            # Буфер уже был полноценным номером — часть относится к следующему
            result.append(buf)
            buf = part
        elif digits >= 10:
            result.append(candidate)
            buf = ""
        else:
            buf = candidate
    if buf:
        result.append(buf)
    return result


def split_phones(value):
    """Разбить строку на список отдельных номеров."""
    text = str(value or "").strip()
    if not text:
        return []
    raw_parts = [p.strip(" \t.;,-") for p in _SPLIT_RX.split(text)]
    parts = [p for p in raw_parts if p]
    if not parts:
        return []

    # Если хотя бы одна часть похожа на «обрывок» номера (мало цифр),
    # пробуем восстановить исходные номера склейкой соседних частей.
    if any(not _looks_like_phone(p) for p in parts):
        candidates = _reassemble(parts)
    else:
        candidates = parts

    result = []
    for cand in candidates:
        # Внутри части может быть несколько склеенных номеров
        matches = _PHONE_RX.findall(cand)
        sub = matches if len(matches) > 1 else [cand]
        for item in sub:
            item = item.strip()
            if item and item not in result:
                result.append(item)
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
