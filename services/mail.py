import re
from datetime import date
from urllib.parse import quote

import requests

from config import Config


def _clean_name(value):
    if not value:
        return ""
    text = str(value)
    for char in ("'", "’", "`", "ʼ"):
        text = text.replace(char, "")
    text = re.sub(r"^(г-?н\.?|господин|госпожа)\s+", "", text.strip(), flags=re.I)
    return re.sub(r"\s+", " ", text).strip()


def detect_gender_by_patronymic(patronymic):
    value = (patronymic or "").strip().lower()
    if not value:
        return "unknown"

    if value.endswith(("вна", "овна", "евна", "ична", "йновна")):
        return "female"

    if value.endswith(("вич", "ович", "евич", "ич", "ыч")):
        return "male"

    return "unknown"


def parse_fio(full_name):
    text = _clean_name(full_name)
    if not text:
        return "", "", "", "unknown"

    parts = text.split()

    if any(p.upper().strip('."') in {"ООО", "ОАО", "ПАО", "АО", "ЗАО", "ИП", "НКО"} for p in parts):
        return "", "", "", "unknown"

    if len(parts) >= 3:
        last_name, first_name, patronymic = parts[0], parts[1], parts[2]
    elif len(parts) == 2:
        last_name = ""
        first_name, patronymic = parts[0], parts[1]
    else:
        last_name = ""
        first_name = parts[0]
        patronymic = ""

    gender = detect_gender_by_patronymic(patronymic)

    if gender == "unknown" and first_name:
        lower = first_name.lower()
        if lower.endswith(("а", "я")):
            gender = "female"
        elif lower:
            gender = "male"

    return last_name, first_name, patronymic, gender


def build_greeting(full_name):
    last_name, first_name, patronymic, gender = parse_fio(full_name)

    if not first_name:
        return "Уважаемые коллеги!"

    name_part = f"{first_name} {patronymic}".strip()

    if gender == "female":
        return f"Уважаемая {name_part}!"
    if gender == "male":
        return f"Уважаемый {name_part}!"

    return f"Уважаемый(ая) {name_part}!"


def build_context(company, contact=None, product=None, user=None):
    full_name = contact.full_name if contact else (company.director or "")

    last_name, first_name, patronymic, gender = parse_fio(full_name)

    return {
        "greeting": build_greeting(full_name),
        "full_name": _clean_name(full_name),
        "first_name": first_name,
        "last_name": last_name,
        "patronymic": patronymic,
        "position": (contact.position if contact else "") or "",
        "company_name": company.display_name,
        "company_full_name": company.name or "",
        "inn": company.inn or "",
        "ogrn": company.ogrn or "",
        "director": _clean_name(company.director),
        "phone": (contact.phone if contact and contact.phone else company.phone) or "",
        "email": (contact.email if contact else company.email) or "",
        "product": product.name if product else "",
        "manager": (user.full_name if user and user.full_name else "Клиентский менеджер"),
        "date": date.today().strftime("%d.%m.%Y"),
    }


def render_template_text(text, context):
    if not text:
        return ""

    def replace(match):
        key = match.group(1).lower()
        return str(context.get(key, match.group(0)))

    return re.sub(r"\{\{\s*([a-zA-Z_]+)\s*\}\}", replace, text)


def prepare_email(company, contact, template, product=None, user=None):
    context = build_context(company, contact, product, user)
    subject = render_template_text(template.subject or "", context)
    body = render_template_text(template.body or "", context)
    return subject, body


def mailto_link(to, subject, body):
    return (
        f"mailto:{quote(to, safe=';@,._-')}"
        f"?subject={quote(subject, safe='')}"
        f"&body={quote(body, safe='')}"
    )


def try_open_outlook(to, subject, body, attachments=None):
    """
    Пробует создать письмо через локальный агент outlook_agent.py.
    Возвращает (успех, сообщение). В сообщение попадает точная причина сбоя.
    """
    payload = {
        "to": to,
        "subject": subject,
        "body": body,
        "attachments": attachments or [],
        "send": False,
    }

    url = Config.OUTLOOK_AGENT_URL.rstrip("/") + "/outlook"

    try:
        response = requests.post(
            url,
            json=payload,
            headers={"X-CRM-Token": Config.OUTLOOK_AGENT_TOKEN},
            timeout=10,
        )
    except requests.exceptions.ConnectionError:
        return False, (
            "Локальный Outlook-агент не запущен. "
            "Запустите tools/outlook_agent.py на этом компьютере "
            "или используйте кнопку «Открыть в почтовом клиенте»."
        )
    except Exception as exc:
        return False, f"Не удалось связаться с Outlook-агентом: {exc}"

    try:
        data = response.json()
    except Exception:
        data = {}

    if response.status_code == 200 and data.get("ok"):
        return True, "Письмо открыто в Outlook."

    detail = data.get("error") or f"код ответа {response.status_code}"

    return False, (
        f"Outlook-агент: {detail}. "
        f"Проверьте, что установлен и запущен классический Outlook "
        f"(«новый Outlook» COM не поддерживает), либо нажмите "
        f"«Открыть в почтовом клиенте»."
    )