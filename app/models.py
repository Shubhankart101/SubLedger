from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, Index, Integer, Numeric, String, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Plan(Base):
    __tablename__ = "plans"
    __table_args__ = (CheckConstraint("price > 0", name="ck_plan_price_positive"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    billing_cycle: Mapped[str] = mapped_column(String(20))
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    status: Mapped[str] = mapped_column(String(20), default="active", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    subscriptions: Mapped[list["Subscription"]] = relationship(back_populates="plan")


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(160))
    company: Mapped[str | None] = mapped_column(String(160), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    subscriptions: Mapped[list["Subscription"]] = relationship(back_populates="customer")
    ledger_entries: Mapped[list["LedgerEntry"]] = relationship(back_populates="customer")


class Subscription(Base):
    __tablename__ = "subscriptions"
    __table_args__ = (
        Index(
            "uq_active_subscription_customer_plan",
            "customer_id",
            "plan_id",
            unique=True,
            sqlite_where=text("status = 'active'"),
            postgresql_where=text("status = 'active'"),
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), index=True)
    plan_id: Mapped[int] = mapped_column(ForeignKey("plans.id"), index=True)
    status: Mapped[str] = mapped_column(String(20), default="active", index=True)
    start_date: Mapped[date] = mapped_column(Date, default=date.today)
    next_billing_date: Mapped[date] = mapped_column(Date, default=date.today)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    customer: Mapped[Customer] = relationship(back_populates="subscriptions")
    plan: Mapped[Plan] = relationship(back_populates="subscriptions")
    invoices: Mapped[list["Invoice"]] = relationship(back_populates="subscription")


class Invoice(Base):
    __tablename__ = "invoices"
    __table_args__ = (
        CheckConstraint("amount_due > 0", name="ck_invoice_amount_due_positive"),
        CheckConstraint("amount_paid >= 0 AND amount_paid <= amount_due", name="ck_invoice_amount_paid_range"),
        UniqueConstraint("subscription_id", "period_start", "period_end", name="uq_invoice_subscription_period"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    subscription_id: Mapped[int] = mapped_column(ForeignKey("subscriptions.id"), index=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), index=True)
    amount_due: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    amount_paid: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))
    currency: Mapped[str] = mapped_column(String(3))
    status: Mapped[str] = mapped_column(String(20), default="issued", index=True)
    period_start: Mapped[date] = mapped_column(Date)
    period_end: Mapped[date] = mapped_column(Date)
    due_date: Mapped[date] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    subscription: Mapped[Subscription] = relationship(back_populates="invoices")
    payment_attempts: Mapped[list["PaymentAttempt"]] = relationship(back_populates="invoice")
    ledger_entries: Mapped[list["LedgerEntry"]] = relationship(back_populates="invoice")


class PaymentAttempt(Base):
    __tablename__ = "payment_attempts"
    __table_args__ = (CheckConstraint("amount > 0", name="ck_payment_amount_positive"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    invoice_id: Mapped[int] = mapped_column(ForeignKey("invoices.id"), index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    currency: Mapped[str] = mapped_column(String(3))
    status: Mapped[str] = mapped_column(String(20), index=True)
    provider_reference: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    failure_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    invoice: Mapped[Invoice] = relationship(back_populates="payment_attempts")


class LedgerEntry(Base):
    __tablename__ = "ledger_entries"
    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_ledger_amount_positive"),
        UniqueConstraint("entry_type", "reference_id", name="uq_ledger_type_reference"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), index=True)
    invoice_id: Mapped[int | None] = mapped_column(ForeignKey("invoices.id"), nullable=True, index=True)
    entry_type: Mapped[str] = mapped_column(String(40), index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    currency: Mapped[str] = mapped_column(String(3))
    reference_id: Mapped[str] = mapped_column(String(160), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    customer: Mapped[Customer] = relationship(back_populates="ledger_entries")
    invoice: Mapped[Invoice | None] = relationship(back_populates="ledger_entries")