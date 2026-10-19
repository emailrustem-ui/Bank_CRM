from datetime import datetime, timezone
from pathlib import Path

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash


def utcnow():
    """Текущее время в UTC без tzinfo (совместимо с колонками db.DateTime).

    Заменяет datetime.utcnow(), устаревший с Python 3.12.
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)


db = SQLAlchemy()


def validate_inn(inn: str) -> bool:
    """Проверка формата и контрольной суммы ИНН (10 цифр — юрлицо, 12 — ИП/физлицо)."""
    if not inn or not inn.isdigit():
        return False
    digits = [int(c) for c in inn]
    if len(digits) == 10:
        weights = [2, 4, 10, 3, 5, 9, 4, 6, 8]
        control = sum(w * d for w, d in zip(weights, digits[:9])) % 11 % 10
        return control == digits[9]
    if len(digits) == 12:
        w11 = [7, 2, 4, 10, 3, 5, 9, 4, 6, 8]
        c11 = sum(w * d for w, d in zip(w11, digits[:10])) % 11 % 10
        w12 = [3, 7, 2, 4, 10, 3, 5, 9, 4, 6, 8]
        c12 = sum(w * d for w, d in zip(w12, digits[:11])) % 11 % 10
        return c11 == digits[10] and c12 == digits[11]
    return False


COMPANY_STATUSES = {
    "new": "Новая компания",
    "qualified": "Отобрана по ОКВЭД",
    "proposal": "КП отправлено",
    "negotiation": "Переговоры",
    "won": "Сделка",
    "rejected": "Отказ",
}

ACTIVITY_TYPES = {
    "note": "Заметка",
    "call": "Звонок",
    "email": "Письмо",
    "meeting": "Встреча",
}

CHECK_RESULTS = {
    "allowed": "Доступно",
    "conditional": "С условиями",
    "forbidden": "Недоступно",
    "unknown": "Нет данных",
}

DEAL_STATUSES = {
    "anketa": "Анкета",
    "pre_verify": "Предварительная верификация",
    "docs": "Сбор документов",
    "verify": "Верификация",
    "decision": "Проект решения",
    "approved": "Одобрена",
    "issued": "Выдана",
    "rejected": "Отклонена",
}


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    full_name = db.Column(db.String(200), default="")
    password_hash = db.Column(db.String(256), nullable=False)
    is_enabled = db.Column(db.Boolean, default=True)
    # True для автоматически созданного аккаунта — потребовать смену пароля
    must_change_password = db.Column(db.Boolean, default=False)
    # "manager" | "admin" (админ может загружать справочники и удалять данные)
    role = db.Column(db.String(20), default="manager")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Company(db.Model):
    __tablename__ = "companies"

    id = db.Column(db.Integer, primary_key=True)
    inn = db.Column(db.String(12), unique=True, nullable=False, index=True)
    ogrn = db.Column(db.String(20), default="")

    name = db.Column(db.String(500), default="")
    short_name = db.Column(db.String(500), default="")

    reg_date = db.Column(db.String(80), default="")
    director = db.Column(db.String(300), default="")
    address = db.Column(db.Text, default="")

    phone = db.Column(db.String(300), default="")
    email = db.Column(db.String(300), default="")
    site = db.Column(db.String(300), default="")

    okved_main_code = db.Column(db.String(30), default="")
    okved_main_title = db.Column(db.Text, default="")

    founders = db.Column(db.Text, default="")
    employee_count = db.Column(db.String(100), default="")

    revenue = db.Column(db.String(200), default="")
    net_profit = db.Column(db.String(200), default="")
    assets = db.Column(db.String(200), default="")
    equity = db.Column(db.String(200), default="")
    fixed_assets = db.Column(db.String(200), default="")

    extra = db.Column(db.Text, default="")

    status = db.Column(db.String(40), default="new")
    source = db.Column(db.String(30), default="manual")

    checko_updated_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=utcnow)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)

    manager_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    okveds = db.relationship(
        "CompanyOkved", backref="company", lazy="select",
        cascade="all, delete-orphan"
    )
    contacts = db.relationship(
        "Contact", backref="company", lazy="select",
        cascade="all, delete-orphan"
    )
    checks = db.relationship(
        "OkvedCheck", backref="company", lazy="select",
        cascade="all, delete-orphan"
    )
    activities = db.relationship(
        "Activity", backref="company", lazy="select",
        cascade="all, delete-orphan"
    )
    tasks = db.relationship(
        "Task", backref="company", lazy="select",
        cascade="all, delete-orphan"
    )
    deals = db.relationship(
        "Deal", backref="company", lazy="select",
        cascade="all, delete-orphan"
    )

    @property
    def display_name(self):
        return self.short_name or self.name or f"Компания {self.inn}"

    @property
    def status_label(self):
        return COMPANY_STATUSES.get(self.status, self.status)

    @property
    def allowed_products_count(self):
        return sum(1 for c in self.checks if c.result == "allowed")

    @property
    def conditional_products_count(self):
        return sum(1 for c in self.checks if c.result == "conditional")


class CompanyOkved(db.Model):
    __tablename__ = "company_okveds"

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False)
    code = db.Column(db.String(30), nullable=False)
    title = db.Column(db.Text, default="")
    is_main = db.Column(db.Boolean, default=False)


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300), unique=True, nullable=False)
    description = db.Column(db.Text, default="")
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=utcnow)

    rules = db.relationship("OkvedRule", backref="product", lazy="select")


class ReferenceVersion(db.Model):
    __tablename__ = "reference_versions"

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(300))
    created_at = db.Column(db.DateTime, default=utcnow)
    product_count = db.Column(db.Integer, default=0)
    rule_count = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=False)


class OkvedRule(db.Model):
    __tablename__ = "okved_rules"

    id = db.Column(db.Integer, primary_key=True)
    version_id = db.Column(db.Integer, db.ForeignKey("reference_versions.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)

    code = db.Column(db.String(30), nullable=False, index=True)
    status_raw = db.Column(db.String(80), default="")
    status_norm = db.Column(db.String(20), default="unknown")
    condition = db.Column(db.Text, default="")
    scope = db.Column(db.String(20), default="any")

    __table_args__ = (
        db.UniqueConstraint("version_id", "product_id", "code", name="uq_rule_version_product_code"),
    )


class OkvedCheck(db.Model):
    __tablename__ = "okved_checks"

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    version_id = db.Column(db.Integer, db.ForeignKey("reference_versions.id"), nullable=True)

    result = db.Column(db.String(20), default="unknown")
    detail = db.Column(db.Text, default="")
    checked_at = db.Column(db.DateTime, default=utcnow)

    product = db.relationship("Product")
    version = db.relationship("ReferenceVersion")

    __table_args__ = (
        db.UniqueConstraint("company_id", "product_id", name="uq_check_company_product"),
    )


class Contact(db.Model):
    __tablename__ = "contacts"

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False)

    full_name = db.Column(db.String(300), default="")
    position = db.Column(db.String(200), default="")
    phone = db.Column(db.String(300), default="")
    email = db.Column(db.String(300), default="")
    is_primary = db.Column(db.Boolean, default=False)


class Activity(db.Model):
    __tablename__ = "activities"

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False)
    contact_id = db.Column(db.Integer, db.ForeignKey("contacts.id"), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    type = db.Column(db.String(30), default="note")
    subject = db.Column(db.String(500), default="")
    body = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=utcnow)

    user = db.relationship("User")
    contact = db.relationship("Contact")


class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    title = db.Column(db.String(500), nullable=False)
    due_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), default="open")
    created_at = db.Column(db.DateTime, default=utcnow)

    @property
    def is_overdue(self):
        from datetime import date
        return self.status == "open" and self.due_date is not None and self.due_date < date.today()


class Deal(db.Model):
    __tablename__ = "deals"

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=True)

    amount = db.Column(db.Float, default=0)
    term_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(40), default="anketa")

    analyst_name = db.Column(db.String(300), default="")
    analyst_phone = db.Column(db.String(100), default="")
    comment = db.Column(db.Text, default="")

    created_at = db.Column(db.DateTime, default=utcnow)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)

    product = db.relationship("Product")
    status_logs = db.relationship(
        "DealStatusLog", backref="deal", lazy="select",
        cascade="all, delete-orphan",
        order_by="DealStatusLog.created_at.desc()",
    )

    @property
    def status_label(self):
        return DEAL_STATUSES.get(self.status, self.status)

    @property
    def is_overdue_term(self):
        from datetime import date
        return (
            self.term_date is not None
            and self.term_date < date.today()
            and self.status not in ("issued", "rejected")
        )


class DealStatusLog(db.Model):
    __tablename__ = "deal_status_logs"

    id = db.Column(db.Integer, primary_key=True)
    deal_id = db.Column(db.Integer, db.ForeignKey("deals.id"), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False)

    old_status = db.Column(db.String(40), default="")
    new_status = db.Column(db.String(40), default="")
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=utcnow)

    company = db.relationship("Company")
    user = db.relationship("User")


class MailTemplate(db.Model):
    __tablename__ = "mail_templates"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    subject = db.Column(db.String(500), default="")
    body = db.Column(db.Text, default="")
    is_default = db.Column(db.Boolean, default=False)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)

    attachments = db.relationship(
        "TemplateAttachment", backref="template", lazy="select",
        cascade="all, delete-orphan",
    )


class TemplateAttachment(db.Model):
    """Файл-вложение, прикреплённый к шаблону письма."""

    __tablename__ = "template_attachments"

    id = db.Column(db.Integer, primary_key=True)
    template_id = db.Column(db.Integer, db.ForeignKey("mail_templates.id"), nullable=False)

    # сохранённое имя файла в data/attachments (используется для пути и удаления)
    filename = db.Column(db.String(300), default="")
    # исходное имя файла при загрузке (для отображения)
    original_name = db.Column(db.String(300), default="")
    # размер в байтах
    file_size = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=utcnow)

    @property
    def path(self):
        from config import Config
        return str(Path(Config.ATTACHMENTS_DIR) / self.filename)

    @property
    def file_path(self):
        return self.path

    @property
    def name(self):
        return self.original_name or self.filename


DEFAULT_TEMPLATE_SUBJECT = "Финансовые решения для {{ company_name }}"

DEFAULT_TEMPLATE_BODY = """{{ greeting }}

Меня зовут {{ manager }}, я клиентский менеджер банка.

Для компании {{ company_name }} (ИНН {{ inn }}) мы можем рассмотреть финансовые программы банка.
Буду рад предложить варианты финансирования, гарантийные инструменты и сопровождение вашего бизнеса.

Подскажите, пожалуйста, какие задачи сейчас наиболее актуальны для вашей компании?
Можем созвониться в удобное для вас время или встретиться лично.

С уважением,
{{ manager }}
Клиентский менеджер банка
"""