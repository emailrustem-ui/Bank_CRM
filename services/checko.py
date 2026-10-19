import json
import random
import re
import threading
import time
from datetime import datetime
from pathlib import Path

from config import Config, SNAPSHOTS_DIR
from models import db, utcnow, Company, CompanyOkved, Contact
from services import card_extra

_DRIVER_LOCK = threading.Lock()
_LAST_FETCH = [0.0]

TIMEOUT_PAGE = 45
MIN_DELAY, MAX_DELAY = 1.5, 2.5

READY_MARKERS = (
    "Дата регистрации",
    "ОГРН",
    "Вид деятельности",
    "Действующая компания",
    "Юридический адрес",
)

ERROR_MARKERS = (
    "сейчас эта страница не работает",
    "не удается открыть страницу",
    "не удалось открыть страницу",
    "проверьте подключение к интернету",
    "не удается получить доступ к сайту",
    "err_",
    "this site can't be reached",
    "site can't be reached",
    "обратитесь к владельцу сайта",
)

MONTH_RX = re.compile(
    r"\b(январь|января|февраль|февраля|март|марта|апрель|апреля|май|мая|"
    r"июнь|июня|июль|июля|август|августа|сентябрь|сентября|октябрь|октября|"
    r"ноябрь|ноября|декабрь|декабря|года|год)\b",
    re.I,
)

JUNK_RX = re.compile(
    r"(человек|среднесписочн|регистрат|зарегистрирован|видов деятельности|"
    r"учредител|сведений|сообщений|контрактов|\bдел\b)",
    re.I,
)

EXCLUDE_DOMAIN_RX = re.compile(
    r"(checko\.ru|cloudflare|google|yandex|w3\.org|gov\.ru|arbitr\.ru|trudvsem\.ru|"
    r"fips\.ru|e-disclosure\.ru|fedresurs|rusprofile|sbis\.ru|kontur\.ru|list-org|"
    r"zachestnyibiznes|audit-it|vestnik-gosreg|nalog\.ru|consultant|garant\.ru)",
    re.I,
)

FIO_LINE_RX = re.compile(r"^[А-ЯЁ][а-яё]+ [А-ЯЁ][а-яё]+ [А-ЯЁ][а-яё]+$")

ORG_LINE_RX = re.compile(
    r"^(ООО|ОАО|АО|ПАО|ЗАКРЫТОЕ|ОБЩЕСТВО|АКЦИОНЕРНОЕ|ГОСУДАРСТВЕННОЕ|"
    r"МУНИЦИПАЛЬНОЕ|ФОНД|АССОЦИАЦИЯ|СОЮЗ|ТОВАРИЩЕСТВО|КОЛЛЕГИЯ|АДВОКАТ|АНО|НКО)",
    re.I,
)

PHONE_RX = re.compile(r"\+7(?:[\s().\-]*\d){10}")


class CheckoError(Exception):
    pass


def _log(log, message):
    if log:
        try:
            log(message)
        except Exception:
            pass


def _delay():
    time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))


# ============================================================
# БРАУЗЕР (скрытый режим по умолчанию)
# ============================================================

def _create_driver(kind, opts):
    from selenium import webdriver

    try:
        if kind == "edge":
            from selenium.webdriver.edge.service import Service as EdgeService
            from webdriver_manager.microsoft import EdgeChromiumDriverManager
            return webdriver.Edge(
                service=EdgeService(EdgeChromiumDriverManager().install()),
                options=opts,
            )
        from selenium.webdriver.chrome.service import Service as ChromeService
        from webdriver_manager.chrome import ChromeDriverManager
        return webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()),
            options=opts,
        )
    except Exception:
        if kind == "edge":
            return webdriver.Edge(options=opts)
        return webdriver.Chrome(options=opts)


def make_driver(log=None):
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.edge.options import Options as EdgeOptions

    attempts = [
        ("edge", EdgeOptions),
        ("chrome", ChromeOptions),
    ]

    for kind, opt_cls in attempts:
        try:
            opts = opt_cls()
            opts.add_argument("--disable-blink-features=AutomationControlled")
            opts.add_argument("--no-sandbox")
            opts.add_argument("--disable-dev-shm-usage")
            opts.add_argument("--disable-gpu")
            opts.add_argument("--lang=ru-RU")
            opts.add_argument("--disable-popup-blocking")
            opts.add_argument("--hide-scrollbars")
            opts.add_argument("--window-size=1920,1080")
            opts.add_experimental_option("excludeSwitches", ["enable-automation"])
            opts.add_experimental_option("useAutomationExtension", False)
            opts.add_argument(f"--user-data-dir={Config.CHECKO_PROFILE_DIR}")

            if Config.CHECKO_HEADLESS:
                opts.add_argument("--headless=new")

            driver = _create_driver(kind, opts)

            try:
                driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                    "source": (
                        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"
                        "window.chrome = window.chrome || { runtime: {} };"
                    )
                })
            except Exception:
                pass

            driver.set_page_load_timeout(TIMEOUT_PAGE)
            driver.implicitly_wait(0)

            _log(log, "[i] загрузчик готов")
            return driver

        except Exception:
            _log(log, "[!] попытка запуска загрузчика не удалась, пробую следующий…")

    raise CheckoError(
        "Не удалось запустить компонент загрузки данных. "
        "Проверьте, что в системе установлен Microsoft Edge или Google Chrome."
    )


# ============================================================
# JS-ИЗВЛЕКАТЕЛИ
# ============================================================

JS_FIND_VALUE = r"""
const labels = arguments[0];
const norm = s => (s||'').replace(/\s+/g,' ').trim().toLowerCase();
const targets = labels.map(norm);

for (const dl of document.querySelectorAll('dl')) {
    const dts = dl.querySelectorAll('dt');
    const dds = dl.querySelectorAll('dd');
    for (let i = 0; i < dts.length; i++) {
        const k = norm(dts[i].innerText);
        if (targets.some(t => k === t || k.startsWith(t) || k.includes(t))) {
            if (dds[i]) return dds[i].innerText.replace(/\s+/g,' ').trim();
        }
    }
}

for (const tr of document.querySelectorAll('tr')) {
    const cells = Array.from(tr.querySelectorAll('td, th'))
        .map(c => c.innerText.replace(/\s+/g,' ').trim());
    if (cells.length < 2) continue;
    const k = norm(cells[0]);
    if (targets.some(t => k === t || k.startsWith(t) || k.includes(t))) {
        return cells.slice(1).filter(Boolean).join('| ');
    }
}

for (const el of document.querySelectorAll('div,span,p,h3,h4,dt,strong,b,a')) {
    const t = norm(el.innerText);
    if (!t || t.length > 80) continue;
    if (targets.some(x => t === x || t === x + ':')) {
        const sib = el.nextElementSibling;
        if (sib) {
            const v = sib.innerText.replace(/\s+/g,' ').trim();
            if (v) return v;
        }
    }
}

return '';
"""

JS_FULL_NAME = r"""
const h1 = document.querySelector('h1');
if (!h1) return '';
const h1t = h1.innerText.trim();
if (!h1t) return '';

let box = h1.parentElement;
for (let i = 0; i < 4 && box; i++) {
    if ((box.innerText || '').length > h1t.length + 3) break;
    box = box.parentElement;
}
if (!box) return '';

const lines = (box.innerText || '').split('\n').map(s => s.trim()).filter(Boolean);
const idx = lines.indexOf(h1t);
if (idx < 0) return '';

const SKIP = /^(действующая|ликвидирована|банкрот|реорганиз|инн|огрн|кпп)/i;
const ORG = /(обществ|акционерн|предприяти|учреждени|организаци|компани|фирм|товариществ|кооператив|фонд|ассоциац|союз|гуп|муп|нко)/i;

for (let j = idx + 1; j < Math.min(idx + 4, lines.length); j++) {
    const l = lines[j];
    if (SKIP.test(l)) continue;
    if (ORG.test(l)) return l;
}
for (let j = idx + 1; j < Math.min(idx + 3, lines.length); j++) {
    const l = lines[j];
    if (l && l !== h1t && !SKIP.test(l) && l.length > 5) return l;
}
return '';
"""

JS_OKVED_MAIN = r"""
const label = Array.from(document.querySelectorAll('div,span,h3,h4,b,strong,dt'))
    .find(el => {
        const t = (el.innerText || '').trim();
        return t.length < 40 && /^вид деятельности$/i.test(t);
    });
if (!label) return null;

let box = label.parentElement;
for (let i = 0; i < 5 && box; i++) {
    const lines = (box.innerText || '').split('\n').map(s => s.trim()).filter(Boolean);
    const idx = lines.findIndex(l => /^вид деятельности$/i.test(l));
    if (idx >= 0) {
        let title = '';
        for (let j = idx + 1; j < lines.length; j++) {
            const l = lines[j];
            if (/^\+/.test(l)) break;

            const mSolo = l.match(/^(\d{2}(?:\.\d{1,3}){0,3})$/);
            if (mSolo) return { code: mSolo[1], title: title };

            const mGlued = l.match(/^(.*[А-Яа-яA-Za-z].*?)\s*(\d{2}(?:\.\d{1,3}){0,3})$/);
            if (mGlued && mGlued[1].trim().length > 3) {
                return { code: mGlued[2], title: mGlued[1].trim() };
            }

            if (!title) title = l;
        }
    }
    box = box.parentElement;
}
return null;
"""

JS_EXPAND = r"""
let clicked = 0;
for (const el of document.querySelectorAll('summary,button,label,span,div,a')) {
    if (clicked >= 5) break;
    const t = (el.innerText || '').trim();
    if (t.length >= 60 || !/ещ[ёе]\s+\d+/i.test(t)) continue;

    const anchor = el.closest('a');
    if (anchor) {
        const href = anchor.getAttribute('href') || '';
        if (href && !href.startsWith('#') && !href.startsWith('javascript:')) continue;
    }

    try { el.click(); clicked++; } catch (e) {}
}
return clicked;
"""

JS_SITES = r"""
const label = Array.from(document.querySelectorAll('div,span,h3,h4,b,strong'))
    .find(el => {
        const t = (el.innerText || '').trim();
        return t.length < 40 && /^веб-?сайты?$/i.test(t);
    });
if (!label) return [];

let box = label.parentElement;
for (let i = 0; i < 4 && box; i++) {
    if ((box.innerText || '').length > 15) break;
    box = box.parentElement;
}
if (!box) return [];

const out = [];
for (const a of box.querySelectorAll('a[href^="http"]')) {
    try {
        const u = new URL(a.href);
        const h = u.hostname.replace(/^www\./, '');
        if (h && !out.includes(h)) out.push(h);
    } catch (e) {}
}
return out;
"""

JS_FOUNDERS = r"""
const FIO_RX = /^[А-ЯЁ][а-яё]+ [А-ЯЁ][а-яё]+ [А-ЯЁ][а-яё]+$/;
const ORG_RX = /^(ООО|ОАО|АО|ПАО|ЗАКРЫТОЕ|ОБЩЕСТВО|АКЦИОНЕРНОЕ|ГОСУДАРСТВЕННОЕ|МУНИЦИПАЛЬНОЕ|ФОНД|АССОЦИАЦИЯ|СОЮЗ|ТОВАРИЩЕСТВО|КОЛЛЕГИЯ|АДВОКАТ|АНО|НКО)/i;

function founderName(line) {
    const c = line.replace(/^\d+[.)]\s*/, '').trim();
    if (!c) return '';
    if (FIO_RX.test(c)) return c;
    if (ORG_RX.test(c) && c.length > 10 && c.length < 300) return c;
    return '';
}

const heads = Array.from(document.querySelectorAll('*')).filter(el => {
    const t = (el.innerText || '').trim();
    return t && t.length < 40 && /^учредител/i.test(t);
});

let bestText = '';
let bestCount = 0;

for (const h of heads) {
    let c = h.parentElement;
    for (let i = 0; i < 6 && c; i++) {
        const txt = (c.innerText || '').trim();
        if (txt.length > 30 && txt.length < 2500) {
            const lines = txt.split('\n').map(s => s.trim()).filter(Boolean);
            let count = 0;
            for (const l of lines) {
                if (founderName(l)) count++;
            }
            if (count >= 1) {
                if (count > bestCount) {
                    bestCount = count;
                    bestText = txt;
                }
                break;
            }
        }
        c = c.parentElement;
    }
    if (bestCount >= 1) break;
}

if (!bestText || bestCount === 0) return '';

const lines = bestText.split('\n').map(s => s.trim()).filter(Boolean);
const entries = [];
let cur = null;

for (const l of lines) {
    if (/^экс-учредит/i.test(l)) break;

    const name = founderName(l);
    if (name) {
        if (cur) entries.push(cur);
        cur = { name: name, date: '', share: '', sum: '' };
        continue;
    }

    if (!cur) continue;

    if (/^с\s+\d{1,2}\s+\S+\s+\d{4}/.test(l)) { cur.date = l; continue; }
    if (/^\d+([.,]\d+)?\s*%$/.test(l)) { cur.share = l; continue; }
    if (/руб\.$/.test(l) && l.length < 40) { cur.sum = l; continue; }
}
if (cur) entries.push(cur);

return entries.map(e => {
    const parts = [];
    if (e.date) parts.push(e.date);
    if (e.share) parts.push('доля ' + e.share);
    if (e.sum) parts.push(e.sum);
    return parts.length ? e.name + ' (' + parts.join(', ') + ')' : e.name;
}).join('; ');
"""

JS_SSCHR = r"""
const labelRx = /^среднесписочная\s+численность/i;
const valueRx = /(\d[\d\s]*)\s*человек/i;
const candidates = [];
const all = document.querySelectorAll('div, section, aside, article, li, td');

for (const el of all) {
    const txt = el.innerText;
    if (!txt) continue;
    if (!/среднесписочная\s+численность/i.test(txt)) continue;
    const lines = txt.split('\n').map(s => s.trim()).filter(Boolean);
    const idx = lines.findIndex(l => labelRx.test(l));
    if (idx < 0) continue;
    for (let j = idx + 1; j < Math.min(idx + 4, lines.length); j++) {
        if (valueRx.test(lines[j])) {
            const cleaned = lines[j].replace(/\s*\+\d+.*$/, '').trim();
            candidates.push({ size: lines.length, value: cleaned });
            break;
        }
    }
}

if (!candidates.length) return '';
candidates.sort((a, b) => a.size - b.size);
return candidates[0].value;
"""

JS_FINANCES = r"""
const clean = s => (s||'')
    .replace(/[\u00a0\u202f]/g, ' ')
    .replace(/[ \t]+/g, ' ')
    .trim();

const lines = (document.body.innerText||'').split('\n').map(clean).filter(Boolean);

const out = {
    'revenue': '',
    'net_profit': '',
    'assets': '',
    'equity': '',
    'fixed_assets': ''
};

const rules = [
    [/^выручк/i, 'revenue'],
    [/^чист.{0,4}прибыл/i, 'net_profit'],
    [/^актив/i, 'assets'],
    [/^собственн.{0,4}капитал/i, 'equity'],
    [/^основн.{0,4}средств/i, 'fixed_assets']
];

for (const line of lines) {
    const vm = line.match(/([\d][\d\s.,]*)\s*(млн|млрд|тыс\.?)?\s*руб\./i);
    if (!vm) continue;

    const cm = line.match(/([+-]\s*\d+(?:[.,]\d+)?\s*%)/);
    let value = clean(vm[1] + (vm[2] ? ' ' + vm[2] : '') + ' руб.');
    if (cm) value += ' (' + cm[1].replace(/\s+/g, '') + ')';

    for (const [rx, key] of rules) {
        if (rx.test(line) && !out[key]) { out[key] = value; break; }
    }
}

return out;
"""

JS_CONTACTS = r"""
const phones = new Set(), emails = new Set(), sites = new Set();

document.querySelectorAll('a[href^="tel:"]').forEach(a => {
    const t = (a.innerText || '').trim() || a.getAttribute('href').replace('tel:', '');
    if (t) phones.add(t);
});

document.querySelectorAll('a[href^="mailto:"]').forEach(a => {
    const t = ((a.innerText || '').trim() || a.getAttribute('href').replace('mailto:', '')).split('?')[0];
    if (t) emails.add(t);
});

document.querySelectorAll('a[href^="http"]').forEach(a => {
    const href = a.href;
    if (/checko\.ru|cloudflare|google|yandex|w3\.org/i.test(href)) return;
    try {
        const u = new URL(href);
        sites.add(u.hostname.replace(/^www\./, ''));
    } catch (e) {}
});

return {
    phones: Array.from(phones),
    emails: Array.from(emails),
    sites: Array.from(sites)
};
"""

JS_OKVED = r"""
const codeLine = /^(\d{2}(?:\.\d{1,3}){0,3})[\s.)\-]+(.+)$/;
const BAD = /\b(январь|января|февраль|февраля|март|марта|апрель|апреля|май|мая|июнь|июня|июль|июля|август|августа|сентябрь|сентября|октябрь|октября|ноябрь|ноября|декабрь|декабря|года|год)\b/i;
const JUNK = /(человек|среднесписочн|регистрат|зарегистрирован|видов деятельности|учредител|сведений|сообщений|контрактов|дел\b)/i;
const out = { main: null, additional: [] };

function good(title) {
    return title && title.length >= 3 && !BAD.test(title) && !JUNK.test(title);
}

function parseLines(text, limit) {
    const res = [];
    if (!text) return res;
    for (const raw of text.split('\n')) {
        const t = raw.trim();
        if (!t || BAD.test(t) || JUNK.test(t) || /^—/.test(t)) continue;
        const m = t.match(codeLine);
        if (!m) continue;
        const title = m[2].trim();
        if (!good(title)) continue;
        res.push({ code: m[1], title: title });
        if (res.length >= limit) break;
    }
    return res;
}

const heads = Array.from(document.querySelectorAll('h1,h2,h3,h4,h5,div,span,strong,b,dt'));

function blockFor(rx) {
    for (const h of heads) {
        const t = (h.innerText || '').trim();
        if (!t || t.length > 100) continue;
        if (!rx.test(t)) continue;
        let p = h.parentElement;
        for (let i = 0; i < 5 && p; i++) {
            const txt = (p.innerText || '').trim();
            if (txt.length > 60 && txt.length < 25000) return txt;
            p = p.parentElement;
        }
    }
    return '';
}

const mainParsed = parseLines(
    blockFor(/^(основной\s+вид\s+деятельности|основной\s+оквэд)/i), 1
);
if (mainParsed.length) out.main = mainParsed[0];

out.additional = parseLines(
    blockFor(/^(дополнительные?\s+виды\s+деятельности|дополнительные?\s+оквэд)/i), 300
);

if (!out.main || out.additional.length === 0) {
    const seen = new Set(out.additional.map(x => x.code));
    for (const el of document.querySelectorAll('li,tr,div,p')) {
        const txt = (el.innerText || '').trim();
        if (txt.length < 12 || txt.length > 350) continue;
        if (BAD.test(txt) || JUNK.test(txt) || /^—/.test(txt)) continue;
        const m = txt.match(codeLine);
        if (!m) continue;
        const title = m[2].trim();
        if (!good(title)) continue;
        if (seen.has(m[1])) continue;
        seen.add(m[1]);
        if (!out.main) out.main = { code: m[1], title: title };
        else out.additional.push({ code: m[1], title: title });
        if (out.additional.length >= 300) break;
    }
}

return out;
"""


def _js(driver, script, arg=None):
    try:
        if arg is None:
            return driver.execute_script(script) or ""
        return driver.execute_script(script, arg) or ""
    except Exception:
        return ""


def find_value(driver, *labels):
    return _js(driver, JS_FIND_VALUE, list(labels))


# ============================================================
# ОЧИСТКА ЗНАЧЕНИЙ
# ============================================================

def _clean_ogrn(value):
    match = re.search(r"\b(\d{13}|\d{15})\b", str(value or ""))
    return match.group(1) if match else ""


def _clean_okved_title(title):
    title = (title or "").strip()
    if MONTH_RX.search(title) or JUNK_RX.search(title):
        return ""
    return title


def _parse_main_okved_raw(raw):
    if not raw:
        return None

    chunk = re.split(r"\+\s*ещ[ёе]", str(raw), flags=re.I)[0]
    codes = re.findall(r"\d{2}(?:\.\d{1,3}){0,3}", chunk)
    if not codes:
        return None

    code = codes[-1]
    pos = chunk.rfind(code)
    title = chunk[:pos].strip(" \n\t.-:")

    if MONTH_RX.search(title) or JUNK_RX.search(title):
        title = ""

    return {"code": code, "title": title}


def _clean_sites(values):
    result = []
    for item in values or []:
        item = str(item).strip().lower()
        if not item or EXCLUDE_DOMAIN_RX.search(item):
            continue
        if item not in result:
            result.append(item)
        if len(result) >= 3:
            break
    return result


def _clean_director(value):
    text = str(value or "").strip()
    if not text:
        return ""
    text = re.split(r"\s+ИНН\b", text, flags=re.I)[0]
    text = re.sub(r"\s+с\s+\d{1,2}\s.*$", "", text, flags=re.I)
    return text.strip()


def _clean_address(value):
    text = str(value or "").strip()
    text = re.sub(r"\s*\d+\s+юридических\s.*$", "", text, flags=re.I)
    text = re.sub(r"\s*показать\s+на\s+карте.*$", "", text, flags=re.I)
    return text.strip()


def _split_list(value, limit=10):
    parts = re.split(r"[;,\s]+", str(value or ""))
    result = []
    for part in parts:
        part = part.strip()
        if part and part not in result:
            result.append(part)
    return result[:limit]


def _join_phones(phones):
    """Канонический вид строки телефонов: номера через '; '."""
    from services.phones import join_phones

    return join_phones(phones)


def _is_error_page(text):
    lower = str(text or "").lower()
    return any(marker in lower for marker in ERROR_MARKERS)


def _is_founder_line(line):
    clean = re.sub(r"^\d+[.)]\s*", "", line).strip()
    if FIO_LINE_RX.match(clean):
        return clean
    if ORG_LINE_RX.match(clean) and 10 < len(clean) < 300:
        return clean
    return ""


def _parse_founders_from_text(page_text):
    lines = [ln.strip() for ln in str(page_text or "").split("\n")]
    founders = []
    inside = False

    for line in lines:
        if re.match(r"^учредител", line, re.I):
            inside = True
            continue
        if inside:
            if re.match(r"^(экс-учредит|среднесписочн|единый реестр|арбитражн|федресурс|связи|держатель)", line, re.I):
                break
            name = _is_founder_line(line)
            if name and name not in founders:
                founders.append(name)

    return "; ".join(founders[:10])


def _parse_phones_from_text(page_text):
    lines = [ln.strip() for ln in str(page_text or "").split("\n")]
    phones = []
    inside = False

    for line in lines:
        if re.match(r"^телефоны?$", line, re.I):
            inside = True
            continue
        if inside:
            if not line or re.match(
                r"^(электронная|веб-|сайт|социальн|адрес|показать|нашли ошибку|ещ[ёе])",
                line, re.I,
            ):
                break
            for match in PHONE_RX.finditer(line):
                phone = match.group(0).strip()
                if phone not in phones:
                    phones.append(phone)

    if not phones:
        for match in PHONE_RX.finditer(str(page_text or "")):
            phone = match.group(0).strip()
            if phone not in phones:
                phones.append(phone)

    return phones[:6]


# ============================================================
# ГОТОВНОСТЬ СТРАНИЦЫ, ПОИСК КАРТОЧКИ, ВОССТАНОВЛЕНИЕ
# ============================================================

def _page_text(driver):
    try:
        return driver.execute_script("return document.body.innerText||'';") or ""
    except Exception:
        return ""


def _page_ready(text):
    return any(marker in text for marker in READY_MARKERS)


def _wait_ready(driver, seconds=30):
    from selenium.webdriver.support.ui import WebDriverWait

    try:
        WebDriverWait(driver, seconds).until(
            lambda d: _page_ready(_page_text(d))
        )
        return True
    except Exception:
        return False


def _company_links(driver):
    """Ссылки на карточки компаний, без служебных страниц каталога."""
    from selenium.webdriver.common.by import By

    try:
        links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/company/']")
    except Exception:
        return []

    candidates = []
    for link in links:
        href = link.get_attribute("href") or ""
        if not href:
            continue
        if "/company/select" in href:
            continue
        if href.rstrip("/").endswith("/company"):
            continue
        if href not in candidates:
            candidates.append(href)

    return candidates


def _ensure_company_card(driver, inn, log):
    if _wait_ready(driver, 30):
        return True

    _log(log, "[i] на странице поиска карточка не готова, ищу ссылку…")

    digits = re.sub(r"\D", "", inn)
    candidates = _company_links(driver)

    href = ""
    for h in candidates:
        if digits and digits in re.sub(r"\D", "", h):
            href = h
            break

    if not href:
        for h in candidates:
            if re.search(r"/company/[a-z0-9\-]*\d{6,}", h, re.I):
                href = h
                break

    if href:
        _log(log, "[i] открываю карточку компании…")
        try:
            driver.get(href)
            if _wait_ready(driver, 20):
                return True
        except Exception:
            pass

    _log(log, "[i] повторяю запрос к источнику…")
    try:
        driver.get(f"https://checko.ru/search?query={digits}")
        if _wait_ready(driver, 20):
            return True
    except Exception:
        return False

    # Последняя попытка: первая подходящая ссылка из результатов
    for h in _company_links(driver):
        try:
            driver.get(h)
            if _wait_ready(driver, 15):
                return True
        except Exception:
            continue

    return False


def _recover_page(driver, inn, log, reason):
    _log(log, f"[i] {reason} — повторяю запрос…")
    try:
        driver.get(f"https://checko.ru/search?query={re.sub(r'\D', '', inn)}")
    except Exception:
        return False
    time.sleep(1.5)
    if not _wait_ready(driver, 25):
        return False
    return not _is_error_page(_page_text(driver))


def _save_snapshot(inn, url, data=None, page_text="", error=""):
    try:
        SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)
        payload = {
            "inn": inn,
            "fetched_at": utcnow().isoformat(),
            "url": url,
            "error": error,
            "data": data,
            "text_preview": page_text[:30000],
        }
        Path(SNAPSHOTS_DIR / f"{inn}.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except Exception:
        pass


# ============================================================
# СБОР ДАННЫХ ПО ОДНОЙ КОМПАНИИ
# ============================================================

def scrape_company(inn, log=None):
    inn = re.sub(r"\D", "", str(inn or ""))
    if len(inn) not in (10, 12):
        raise CheckoError("ИНН должен содержать 10 или 12 цифр.")

    search_url = f"https://checko.ru/search?query={inn}"

    with _DRIVER_LOCK:
        elapsed = time.time() - _LAST_FETCH[0]
        if elapsed < Config.CHECKO_MIN_DELAY:
            wait_sec = Config.CHECKO_MIN_DELAY - elapsed
            _log(log, f"[i] пауза между запросами {int(wait_sec)} с.…")
            time.sleep(wait_sec)

        _LAST_FETCH[0] = time.time()

        driver = None
        try:
            _log(log, "[i] подготавливаю загрузчик…")
            driver = make_driver(log)

            _log(log, "[i] запрашиваю данные источника…")
            driver.get(search_url)
            time.sleep(1.2)

            if _is_error_page(_page_text(driver)):
                if not _recover_page(driver, inn, log, "страница источника сброшена"):
                    page_text = _page_text(driver)
                    _save_snapshot(inn, driver.current_url, page_text=page_text, error="browser error")
                    raise CheckoError(
                        "Источник данных сбросил соединение. "
                        "Повторите попытку через минуту."
                    )

            if not _ensure_company_card(driver, inn, log):
                page_text = _page_text(driver)
                _save_snapshot(inn, driver.current_url, page_text=page_text, error="not ready")
                raise CheckoError(
                    "Источник данных не вернул карточку компании. "
                    "Повторите попытку через минуту."
                )

            _delay()

            page_text = _page_text(driver)
            lower = page_text.lower()
            title = (driver.title or "").lower()

            if _is_error_page(page_text):
                if not _recover_page(driver, inn, log, "страница источника сброшена"):
                    _save_snapshot(inn, driver.current_url, page_text=_page_text(driver), error="browser error")
                    raise CheckoError(
                        "Источник данных сбросил соединение. "
                        "Повторите попытку через минуту."
                    )
                page_text = _page_text(driver)
                lower = page_text.lower()
                title = (driver.title or "").lower()

            if any(marker in lower for marker in (
                "подтвердите, что вы не робот",
                "проверьте, что вы не робот",
                "captcha",
                "access denied",
                "доступ ограничен",
            )):
                _save_snapshot(inn, driver.current_url, page_text=page_text, error="captcha")
                raise CheckoError(
                    "Источник данных временно запросил проверку защиты от роботов. "
                    "Повторите попытку через несколько минут."
                )

            # "Не найдена" — только если карточки реально нет на странице
            if not _page_ready(page_text) and (
                "404" in title
                or "не найдена" in title
                or "ничего не найдено" in lower
                or "не найдено" in lower
            ):
                _save_snapshot(inn, driver.current_url, page_text=page_text, error="not found")
                raise CheckoError(f"Компания с ИНН {inn} не найдена в источнике данных.")

            if len(page_text.strip()) < 200:
                _save_snapshot(inn, driver.current_url, page_text=page_text, error="empty page")
                raise CheckoError(
                    "Источник данных вернул пустую страницу. "
                    "Повторите попытку через минуту."
                )

            _log(log, "[i] карточка получена, раскрываю скрытые блоки…")
            _js(driver, JS_EXPAND)
            time.sleep(0.8)

            page_text = _page_text(driver)
            if _is_error_page(page_text) or not _page_ready(page_text):
                if not _recover_page(driver, inn, log, "после раскрытия блоков страница повреждена"):
                    _save_snapshot(inn, driver.current_url, page_text=_page_text(driver), error="browser error")
                    raise CheckoError(
                        "Источник данных сбросил соединение. "
                        "Повторите попытку через минуту."
                    )
                page_text = _page_text(driver)

            _log(log, "[i] извлекаю реквизиты…")

            short_name = ""
            try:
                from selenium.webdriver.common.by import By
                short_name = driver.find_element(By.TAG_NAME, "h1").text.strip()
            except Exception:
                pass

            full_name = _js(driver, JS_FULL_NAME) or short_name

            if _is_error_page(short_name) or _is_error_page(full_name):
                if not _recover_page(driver, inn, log, "вместо карточки получена страница ошибки"):
                    _save_snapshot(inn, driver.current_url, page_text=_page_text(driver), error="browser error")
                    raise CheckoError(
                        "Источник данных сбросил соединение. "
                        "Повторите попытку через минуту."
                    )
                try:
                    short_name = driver.find_element(By.TAG_NAME, "h1").text.strip()
                except Exception:
                    short_name = ""
                full_name = _js(driver, JS_FULL_NAME) or short_name
                page_text = _page_text(driver)

            data = {
                "inn": inn,
                "name": full_name or short_name or f"Компания {inn}",
                "short_name": short_name,
                "ogrn": _clean_ogrn(find_value(driver, "огрн")),
                "reg_date": find_value(driver, "дата регистрации", "дата создания"),
                "director": _clean_director(find_value(
                    driver, "руководитель", "директор", "генеральный директор"
                )),
                "address": _clean_address(find_value(driver, "юридический адрес", "адрес")),
                "phone": "",
                "email": "",
                "site": "",
                "founders": "",
                "employee_count": "",
                "finances": {},
                "okved_main": None,
                "okved_additional": [],
                "extra": {},
            }

            _delay()
            _log(log, "[i] извлекаю ОКВЭД…")

            main_item = _js(driver, JS_OKVED_MAIN)
            if isinstance(main_item, dict) and main_item.get("code"):
                data["okved_main"] = {
                    "code": main_item["code"],
                    "title": _clean_okved_title(main_item.get("title", "")),
                }

            if not data["okved_main"]:
                raw_main = find_value(driver, "вид деятельности", "основной вид деятельности")
                parsed = _parse_main_okved_raw(raw_main)
                if parsed:
                    data["okved_main"] = parsed

            okved = _js(driver, JS_OKVED)
            if isinstance(okved, dict):
                if not data["okved_main"] and okved.get("main"):
                    item = okved["main"]
                    data["okved_main"] = {
                        "code": item.get("code", ""),
                        "title": _clean_okved_title(item.get("title", "")),
                    }

                additional = []
                seen = {data["okved_main"]["code"]} if data["okved_main"] else set()
                for item in okved.get("additional") or []:
                    code = item.get("code")
                    if not code or code in seen:
                        continue
                    if JUNK_RX.search(item.get("title", "")):
                        continue
                    seen.add(code)
                    additional.append({
                        "code": code,
                        "title": _clean_okved_title(item.get("title", "")),
                    })
                data["okved_additional"] = additional

            if data["okved_main"] and not data["okved_main"].get("code"):
                data["okved_main"] = None
            if data["okved_main"] and JUNK_RX.search(data["okved_main"].get("title", "")):
                data["okved_main"]["title"] = ""

            _delay()
            _log(log, "[i] извлекаю учредителей и численность…")
            data["founders"] = _js(driver, JS_FOUNDERS)

            if not data["founders"]:
                data["founders"] = _parse_founders_from_text(page_text)

            sschr = _js(driver, JS_SSCHR)
            if not sschr:
                sschr = find_value(
                    driver, "среднесписочная численность", "численность работников"
                )
            data["employee_count"] = sschr

            _log(log, "[i] извлекаю финансы…")
            finances = _js(driver, JS_FINANCES)
            if isinstance(finances, dict):
                data["finances"] = finances
                found = sum(1 for v in finances.values() if v)
                _log(log, f"[i] финансы найдено: {found}/5")

            _log(log, "[i] извлекаю контакты…")
            contacts = _js(driver, JS_CONTACTS)
            if not isinstance(contacts, dict):
                contacts = {"phones": [], "emails": [], "sites": []}

            emails_list = _split_list(";".join(contacts.get("emails", [])), 10)
            if not emails_list:
                found = re.findall(
                    r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", page_text
                )
                found = [
                    e for e in found
                    if not any(s in e.lower() for s in ("checko", "example", "sentry"))
                ]
                emails_list = _split_list(";".join(found), 10)

            phones_list = _split_list(";".join(contacts.get("phones", [])), 6)
            if not phones_list:
                phones_list = _parse_phones_from_text(page_text)

            data["email"] = "; ".join(emails_list)
            data["phone"] = _join_phones(phones_list)

            block_sites = _js(driver, JS_SITES)
            cleaned_sites = _clean_sites(block_sites)
            if not cleaned_sites:
                label_sites = find_value(driver, "веб-сайты", "сайт", "веб-сайт")
                if label_sites:
                    cleaned_sites = _clean_sites(re.split(r"[,\s]+", label_sites))
            if not cleaned_sites:
                cleaned_sites = _clean_sites(contacts.get("sites", []))
            data["site"] = ", ".join(cleaned_sites)

            _log(log, "[i] собираю дополнительные сведения карточки…")
            try:
                data["extra"] = card_extra.extract_extra(driver, page_text, _js)
            except Exception as exc:
                _log(log, f"[!] доп. сведения: {exc}")
                data["extra"] = {}

            _save_snapshot(inn, driver.current_url, data=data, page_text=page_text)

            _log(log, "[i] данные получены.")
            return data

        except CheckoError:
            raise
        except Exception as exc:
            try:
                url = driver.current_url if driver else ""
                _save_snapshot(inn, url, page_text=_page_text(driver) if driver else "",
                               error=str(exc))
            except Exception:
                pass
            raise CheckoError(f"Не удалось получить данные: {exc}") from exc
        finally:
            if driver:
                try:
                    driver.quit()
                except Exception:
                    pass


# ============================================================
# ЗАПИСЬ ДАННЫХ В КАРТОЧКУ КОМПАНИИ
# ============================================================

def apply_scraped_data(company, data):
    string_fields = {
        "ogrn": ("ogrn", 20),
        "reg_date": ("reg_date", 80),
        "director": ("director", 300),
        "address": ("address", 100000),
        "phone": ("phone", 300),
        "site": ("site", 300),
        "founders": ("founders", 100000),
        "employee_count": ("employee_count", 100),
    }

    for key, (field, limit) in string_fields.items():
        value = data.get(key)
        if value:
            setattr(company, field, str(value).strip()[:limit])

    name_value = str(data.get("name") or "").strip()
    short_value = str(data.get("short_name") or "").strip()

    if name_value and not _is_error_page(name_value):
        company.name = name_value[:500]
    if short_value and not _is_error_page(short_value):
        company.short_name = short_value[:500]

    emails_list = _split_list(data.get("email", ""), 10)
    phones_list = _split_list(data.get("phone", ""), 6)

    if emails_list:
        company.email = "; ".join(emails_list)
    if phones_list:
        company.phone = _join_phones(phones_list)

    finance_map = {
        "revenue": "revenue",
        "net_profit": "net_profit",
        "assets": "assets",
        "equity": "equity",
        "fixed_assets": "fixed_assets",
    }
    finances = data.get("finances") or {}
    for key, field in finance_map.items():
        if finances.get(key):
            setattr(company, field, str(finances[key])[:200])

    try:
        company.extra = json.dumps(data.get("extra") or {}, ensure_ascii=False)
    except Exception:
        company.extra = ""

    CompanyOkved.query.filter_by(company_id=company.id).delete()
    db.session.flush()

    seen = set()

    main = data.get("okved_main")
    if main and main.get("code"):
        code = main["code"]
        company.okved_main_code = code
        company.okved_main_title = main.get("title", "")
        db.session.add(CompanyOkved(
            company_id=company.id,
            code=code,
            title=main.get("title", ""),
            is_main=True,
        ))
        seen.add(code)

    for item in data.get("okved_additional") or []:
        code = item.get("code")
        if not code or code in seen:
            continue
        seen.add(code)
        db.session.add(CompanyOkved(
            company_id=company.id,
            code=code,
            title=item.get("title", ""),
            is_main=False,
        ))

    company.source = "auto"
    company.checko_updated_at = utcnow()

    director = (data.get("director") or "").strip()
    phones_joined = _join_phones(phones_list)

    if emails_list or phones_list:
        first_email = emails_list[0] if emails_list else ""

        existing = None
        if first_email:
            existing = Contact.query.filter(
                Contact.company_id == company.id,
                db.func.lower(Contact.email) == first_email.lower()
            ).first()

        if not existing:
            existing = Contact.query.filter(
                Contact.company_id == company.id,
                Contact.is_primary == True,
            ).first()

        if existing:
            if emails_list:
                existing.email = "; ".join(emails_list)
            if phones_joined:
                existing.phone = phones_joined
            if director and not existing.full_name:
                existing.full_name = director
        else:
            db.session.add(Contact(
                company_id=company.id,
                full_name=director or company.display_name,
                position="Руководитель",
                email="; ".join(emails_list),
                phone=phones_joined,
                is_primary=True,
            ))

    db.session.flush()
    return company