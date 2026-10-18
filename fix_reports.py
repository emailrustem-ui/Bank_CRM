"""
fix_reports.py - заменяет блок отчётов в app.py на чистую рабочую версию.
Запуск: .venv\Scripts\python.exe fix_reports.py
"""

import re
import shutil
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent
APP_PATH = BASE / "app.py"

if not APP_PATH.exists():
    print("[!] app.py не найден")
    exit(1)

# Бэкап
backup = APP_PATH.with_suffix(f".bak_reports_{datetime.now():%Y%m%d_%H%M%S}")
shutil.copy2(APP_PATH, backup)
print(f"[i] Бэкап: {backup.name}")

# Читаем файл
text = APP_PATH.read_text(encoding="utf-8")

# Новый блок отчётов
NEW_BLOCK = r'''
# ============================================================
# ОТЧЁТЫ И ВЫГРУЗКИ
# ============================================================

HEADER_FILL = PatternFill("solid", fgColor="0066CC")
HEADER_FONT = Font(bold=True, color="FFFFFF")


def _xlsx_response(headers, rows, filename):
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Отчет"
    for col, name in enumerate(headers, start=1):
        cell = sheet.cell(row=1, column=col, value=name)
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
    for row_idx, row in enumerate(rows, start=2):
        for col_idx, value in enumerate(row, start=1):
            sheet.cell(row=row_idx, column=col_idx, value=value)
    for col_idx in range(1, len(headers) + 1):
        sheet.column_dimensions[
            sheet.cell(row=1, column=col_idx).column_letter
        ].width = 22
    sheet.freeze_panes = "A2"
    buffer = io.BytesIO()
    workbook.save(buffer)
    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name=filename,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


def _deal_filters():
    return {
        "company": request.args.get("company", "").strip(),
        "status": request.args.get("status", "").strip(),
        "product_id": request.args.get("product_id", type=int),
        "date_from": request.args.get("date_from", "").strip(),
        "date_to": request.args.get("date_to", "").strip(),
    }


def _apply_deal_filters(query, filters):
    if filters.get("status"):
        query = query.filter(Deal.status == filters["status"])
    if filters.get("product_id"):
        query = query.filter(Deal.product_id == filters["product_id"])
    if filters.get("company"):
        like = f"%{filters['company']}%"
        query = query.join(Company, Deal.company_id == Company.id).filter(
            db.or_(
                Company.name.ilike(like),
                Company.short_name.ilike(like),
                Company.inn.ilike(like),
            )
        )
    if filters.get("date_from"):
        try:
            d = datetime.strptime(filters["date_from"], "%Y-%m-%d").date()
            query = query.filter(db.func.date(Deal.created_at) >= d.isoformat())
        except ValueError:
            pass
    if filters.get("date_to"):
        try:
            d = datetime.strptime(filters["date_to"], "%Y-%m-%d").date()
            query = query.filter(db.func.date(Deal.created_at) <= d.isoformat())
        except ValueError:
            pass
    return query


def _apply_company_filters(query, filters):
    if filters.get("company"):
        like = f"%{filters['company']}%"
        query = query.filter(
            db.or_(
                Company.name.ilike(like),
                Company.short_name.ilike(like),
                Company.inn.ilike(like),
            )
        )
    return query


@app.route("/reports")
@login_required
def reports_page():
    filters = _deal_filters()

    deals_query = Deal.query
    deals_query = _apply_deal_filters(deals_query, filters)
    deals = deals_query.order_by(Deal.created_at.desc()).all()

    companies_query = Company.query
    companies_query = _apply_company_filters(companies_query, filters)
    companies = companies_query.order_by(Company.name).all()

    total_deals = len(deals)
    total_amount = sum(d.amount or 0 for d in deals)
    active_amount = sum(
        d.amount or 0 for d in deals if d.status not in ("issued", "rejected")
    )

    funnel = []
    for key, label in DEAL_STATUSES.items():
        part = [d for d in deals if d.status == key]
        amount = sum(d.amount or 0 for d in part)
        conversion = round(len(part) * 100 / total_deals, 1) if total_deals else 0.0
        funnel.append({
            "key": key,
            "label": label,
            "count": len(part),
            "amount": amount,
            "conversion": conversion,
        })

    company_totals = {}
    for d in deals:
        name = d.company.display_name
        rec = company_totals.setdefault(name, {"amount": 0, "count": 0})
        rec["amount"] += d.amount or 0
        rec["count"] += 1
    top_companies = sorted(company_totals.items(), key=lambda x: x[1]["amount"], reverse=True)[:10]

    product_totals = {}
    for d in deals:
        name = d.product.name if d.product else "Без продукта"
        rec = product_totals.setdefault(name, {"amount": 0, "count": 0})
        rec["amount"] += d.amount or 0
        rec["count"] += 1
    top_products = sorted(product_totals.items(), key=lambda x: x[1]["amount"], reverse=True)[:10]

    return render_template(
        "reports.html",
        filters=filters,
        deals=deals,
        funnel=funnel,
        total_amount=total_amount,
        active_amount=active_amount,
        total_deals=total_deals,
        top_companies=top_companies,
        top_products=top_products,
        products_list=Product.query.filter_by(is_active=True).order_by(Product.name).all(),
        companies_count=len(companies),
        deal_statuses=DEAL_STATUSES,
    )


@app.route("/export/companies")
@login_required
def export_companies():
    filters = _deal_filters()
    query = _apply_company_filters(Company.query, filters)
    headers = [
        "ИНН", "Наименование", "Краткое наименование", "Статус работы",
        "Основной ОКВЭД", "Вид деятельности", "Руководитель",
        "Телефон", "E-mail", "Сайт",
        "Доступно продуктов", "С условиями", "Дата обновления",
    ]
    rows = []
    for company in query.order_by(Company.name).all():
        rows.append([
            company.inn, company.name, company.short_name, company.status_label,
            company.okved_main_code, company.okved_main_title, company.director,
            company.phone, company.email, company.site,
            company.allowed_products_count, company.conditional_products_count,
            company.checko_updated_at.strftime("%d.%m.%Y %H:%M") if company.checko_updated_at else "",
        ])
    return _xlsx_response(headers, rows, "companies.xlsx")


@app.route("/export/contacts")
@login_required
def export_contacts():
    filters = _deal_filters()
    company_query = _apply_company_filters(Company.query, filters)
    company_ids = [c.id for c in company_query.all()]
    headers = ["Компания", "ИНН", "ФИО", "Должность", "Телефон", "E-mail", "Основной"]
    rows = []
    for contact in (
        Contact.query.filter(Contact.company_id.in_(company_ids))
        .join(Company, Contact.company_id == Company.id)
        .order_by(Company.name)
        .all()
    ):
        rows.append([
            contact.company.display_name, contact.company.inn,
            contact.full_name, contact.position, contact.phone, contact.email,
            "да" if contact.is_primary else "",
        ])
    return _xlsx_response(headers, rows, "contacts.xlsx")


@app.route("/export/deals")
@login_required
def export_deals():
    filters = _deal_filters()
    query = _apply_deal_filters(Deal.query, filters)
    headers = [
        "Компания", "ИНН", "Продукт", "Сумма", "Срок",
        "Статус", "Аналитик", "Телефон аналитика", "Комментарий",
        "Создана", "Обновлена",
    ]
    rows = []
    for deal in query.order_by(Deal.updated_at.desc()).all():
        rows.append([
            deal.company.display_name, deal.company.inn,
            deal.product.name if deal.product else "",
            deal.amount or 0,
            deal.term_date.strftime("%d.%m.%Y") if deal.term_date else "",
            deal.status_label, deal.analyst_name, deal.analyst_phone, deal.comment,
            deal.created_at.strftime("%d.%m.%Y"),
            deal.updated_at.strftime("%d.%m.%Y %H:%M"),
        ])
    return _xlsx_response(headers, rows, "deals.xlsx")


@app.route("/export/tasks")
@login_required
def export_tasks():
    filters = _deal_filters()
    company_query = _apply_company_filters(Company.query, filters)
    company_ids = [c.id for c in company_query.all()]
    headers = ["Компания", "ИНН", "Задача", "Срок", "Статус"]
    rows = []
    for task in (
        Task.query.filter(Task.company_id.in_(company_ids))
        .join(Company, Task.company_id == Company.id)
        .order_by(Task.due_date)
        .all()
    ):
        rows.append([
            task.company.display_name, task.company.inn, task.title,
            task.due_date.strftime("%d.%m.%Y") if task.due_date else "",
            "Выполнена" if task.status == "done" else ("Просрочена" if task.is_overdue else "В работе"),
        ])
    return _xlsx_response(headers, rows, "tasks.xlsx")


@app.route("/export/products")
@login_required
def export_products():
    filters = _deal_filters()
    companies_query = _apply_company_filters(Company.query, filters)
    companies = companies_query.order_by(Company.name).all()
    products = Product.query.filter_by(is_active=True).order_by(Product.name).all()
    headers = ["Компания", "ИНН", "Основной ОКВЭД"] + [p.name for p in products]
    labels = {
        "allowed": "Доступно", "conditional": "С условиями",
        "forbidden": "Недоступно", "unknown": "Нет данных",
    }
    rows = []
    for company in companies:
        results = {c.product_id: c.result for c in company.checks}
        row = [company.display_name, company.inn, company.okved_main_code]
        row += [labels.get(results.get(p.id), "") for p in products]
        rows.append(row)
    return _xlsx_response(headers, rows, "products_matrix.xlsx")


@app.route("/export/deal_log")
@login_required
def export_deal_log():
    filters = _deal_filters()
    deals_query = _apply_deal_filters(Deal.query, filters)
    deal_ids = [d.id for d in deals_query.all()]
    headers = ["Дата", "Компания", "ИНН", "Продукт", "Старый статус", "Новый статус", "Кто изменил"]
    rows = []
    for log in (
        DealStatusLog.query.filter(DealStatusLog.deal_id.in_(deal_ids))
        .order_by(DealStatusLog.created_at.desc())
        .all()
    ):
        rows.append([
            log.created_at.strftime("%d.%m.%Y %H:%M"),
            log.company.display_name, log.company.inn,
            log.deal.product.name if log.deal and log.deal.product else "",
            DEAL_STATUSES.get(log.old_status, log.old_status or "—"),
            DEAL_STATUSES.get(log.new_status, log.new_status),
            log.user.full_name or (log.user.username if log.user else ""),
        ])
    return _xlsx_response(headers, rows, "deal_status_log.xlsx")


# ============================================================
# АВТООТКРЫТИЕ БРАУЗЕРА С CRM
# ============================================================
'''

# Находим маркеры
start_marker = "# ============================================================\n# ОТЧЁТЫ"
end_marker = "# ============================================================\n# АВТООТКРЫТИЕ БРАУЗЕРА"

i_start = text.find(start_marker)
if i_start < 0:
    # Альтернативный поиск
    i_start = text.find('@app.route("/reports")')
    if i_start < 0:
        print("[!] Не найден блок отчётов")
        exit(1)
    # Идём к началу строки с комментарием перед ним
    i_start = text.rfind('#', 0, i_start)
    if i_start < 0:
        i_start = text.rfind('\n', 0, i_start) + 1
else:
    i_start = text.rfind('\n', 0, i_start) + 1

i_end = text.find(end_marker)
if i_end < 0:
    print("[!] Не найден конец блока отчётов")
    exit(1)
i_end = text.rfind('\n', 0, i_end) + 1

# Замена
new_text = text[:i_start] + NEW_BLOCK.strip() + "\n\n" + text[i_end:]

# Запись
APP_PATH.write_text(new_text, encoding="utf-8", newline="\n")
print(f"[+] app.py обновлён ({APP_PATH.stat().st_size} байт)")
print()
print("=" * 60)
print("ГОТОВО. Перезапустите CRM и обновите страницу отчётов.")
print("=" * 60)