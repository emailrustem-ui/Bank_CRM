"""
Сбор всех дополнительных сведений карточки компании:
надёжность, суды, закупки, реестры, зарплаты, история,
а также активные ссылки каждого блока и url страницы-источника.
"""

import re

JS_SECTIONS = r"""
const SECTIONS = [
    ['status', /^(действующая компания|ликвидирована|реорганизация|в процессе банкротства)$/i],
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
                const body = lines.slice(start >= 0 ? start + 1 : 0).join('\n');

                const links = [];
                const seen = {};
                c.querySelectorAll('a[href^="http"]').forEach(a => {
                    const t = (a.innerText || '').trim();
                    const href = a.href;
                    if (!t || t.length > 80 || seen[href]) return;
                    if (/checko\.ru\/(search|company\/select)/i.test(href)) return;
                    seen[href] = 1;
                    links.push({ t: t.slice(0, 60), h: href });
                });

                return { body: body, links: links.slice(0, 10) };
            }
            c = c.parentElement;
        }
    }
    return null;
}

const sections = {};
const links = {};

for (const [key, rx] of SECTIONS) {
    const r = blockForHeading(rx);
    if (r && r.body) {
        sections[key] = r.body.slice(0, 1500);
        if (r.links && r.links.length) links[key] = r.links;
    }
}

return { sections: sections, links: links };
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


def extract_extra(driver, page_text, js_runner):
    raw = js_runner(driver, JS_SECTIONS)
    if not isinstance(raw, dict):
        raw = {}

    sections = raw.get("sections", {}) or {}
    section_links = raw.get("links", {}) or {}

    url = ""
    try:
        url = js_runner(driver, "return window.location.href;") or ""
    except Exception:
        pass

    return {
        "sections": sections,
        "links": section_links,
        "counts": parse_counts(page_text),
        "salary": parse_salary(sections.get("salary", "")),
        "url": str(url),
    }