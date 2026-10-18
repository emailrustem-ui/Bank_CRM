"""
Сбор дополнительных сведений карточки компании:
паспорт (реквизиты блоками), надёжность, суды, закупки, реестры, зарплаты.
"""

import re

JS_SECTIONS = r"""
const SECTIONS = [
    ['opf', /^организационно-правовая форма$/i],
    ['management', /^управляющая организация$/i],
    ['registrar', /^держатель реестра акционеров$/i],
    ['sanctions', /^санкции$/i],
    ['bankruptcy', /^ефрсб/i],
    ['accounts', /^блокировка банковских счетов$/i],
    ['taxes', /^налоги и сборы( за \d{4} год)?$/i],
    ['tax_regime', /^специальный налоговый режим$/i],
    ['arbitration', /^арбитражные дела$/i],
    ['fssp', /^фссп$/i],
    ['licenses', /^лицензии$/i],
    ['trademarks', /^товарные знаки$/i],
    ['fedresurs', /^федресурс$/i],
    ['leasing', /^лизинг$/i],
    ['pledges', /^залоги$/i],
    ['checks', /^проверки и кнм$/i],
    ['goszakupki', /^госзакупки$/i],
    ['msp', /^единый реестр субъектов малого и среднего предпринимательства$/i],
    ['salary', /^среднемесячная зарплата$/i],
    ['vacancies', /^вакансии$/i],
    ['history', /^история изменений$/i],
    ['reliability', /^оценка надежности$/i]
];

const MENU_RX = /(подписка pro|базы данных|правовые основания|расширенный поиск|мой бизнес|войти)/i;

function blockForHeading(rx) {
    const heads = Array.from(document.querySelectorAll('*')).filter(el => {
        const t = (el.innerText || '').trim();
        return t && t.length < 70 && rx.test(t);
    });

    for (const h of heads) {
        let c = h.parentElement;
        for (let i = 0; i < 5 && c; i++) {
            const txt = (c.innerText || '').trim();
            if (txt.length > 25 && txt.length < 2000 && !MENU_RX.test(txt)) {
                const lines = txt.split('\n').map(s => s.trim()).filter(Boolean);
                const start = lines.findIndex(l => rx.test(l));
                return lines.slice(start >= 0 ? start + 1 : 0).join('\n');
            }
            c = c.parentElement;
        }
    }
    return '';
}

const out = {};
for (const [key, rx] of SECTIONS) {
    const text = blockForHeading(rx);
    if (text) out[key] = text.slice(0, 1200);
}
return out;
"""

COUNT_KEYS = (
    "Виды деятельности",
    "Учредители",
    "Связи",
    "Лицензии",
    "Товарные знаки",
    "Федресурс",
    "Лизинг",
    "Залоги",
    "Госзакупки",
    "Проверки и КНМ",
    "Арбитражные дела",
    "ФССП",
    "Сотрудники",
    "Вакансии",
    "История изменений",
)

SALARY_ROW_RX = re.compile(r"^(\d{4})\s*г\.?\s+(.+?)\s+(.+?руб\.)$", re.I)

FACT_LABELS = (
    ("reg_date", re.compile(r"^Дата регистрации$", re.I)),
    ("okved", re.compile(r"^Вид деятельности$", re.I)),
    ("address", re.compile(r"^Юридический адрес$", re.I)),
    ("opf", re.compile(r"^Организационно-правовая форма$", re.I)),
    ("capital", re.compile(r"^Уставный капитал$", re.I)),
    ("tax_regime", re.compile(r"^Специальный налоговый режим$", re.I)),
    ("msp", re.compile(r"^Единый реестр субъектов малого и среднего предпринимательства$", re.I)),
)


def parse_counts(page_text):
    lines = [ln.strip() for ln in str(page_text or "").split("\n") if ln.strip()]
    counts = {}
    for i, line in enumerate(lines[:-1]):
        if line in COUNT_KEYS:
            raw = lines[i + 1].replace(" ", "").replace("\u00a0", "")
            if raw.isdigit():
                counts[line] = int(raw)
    return counts


def parse_salary(section_text):
    rows = []
    for line in str(section_text or "").split("\n"):
        line = line.strip()
        match = SALARY_ROW_RX.match(line)
        if match:
            rows.append({
                "year": match.group(1),
                "headcount": match.group(2).strip(),
                "salary": match.group(3).strip(),
            })
    return rows


def parse_facts(page_text):
    """Структурированный паспорт компании из верхней части карточки."""
    text = str(page_text or "")
    lines = [ln.strip() for ln in text.split("\n")]
    facts = {}

    for key, rx in (
        ("ogrn", re.compile(r"ОГРН\s+(\d{13}|\d{15})")),
        ("inn", re.compile(r"ИНН\s+(\d{10}|\d{12})")),
        ("kpp", re.compile(r"КПП\s+(\d{9})")),
    ):
        match = re.search(rx, text)
        if match:
            facts[key] = match.group(1)

    def _after(label_rx, count=1):
        for i, line in enumerate(lines):
            if label_rx.match(line):
                values = []
                for j in range(i + 1, min(i + 1 + count, len(lines))):
                    if lines[j]:
                        values.append(lines[j])
                return " ".join(values)
        return ""

    for key, label_rx in FACT_LABELS:
        count = 2 if key == "okved" else 1
        value = _after(label_rx, count)
        if value:
            facts[key] = value

    return facts


def extract_extra(driver, page_text, js_runner):
    sections = js_runner(driver, JS_SECTIONS)
    if not isinstance(sections, dict):
        sections = {}

    return {
        "sections": sections,
        "counts": parse_counts(page_text),
        "salary": parse_salary(sections.get("salary", "")),
        "facts": parse_facts(page_text),
    }