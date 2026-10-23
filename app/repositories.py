from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Customer, Invoice, LedgerEntry, PaymentAttempt, Plan, Subscription


class PlanRepository:
    def __init__(self, session: Session):
        self.session = session

    def get(self, plan_id: int) -> Plan | None:
        return self.session.get(Plan, plan_id)

    def get_by_name(self, name: str) -> Plan | None:
        return self.session.scalar(select(Plan).where(Plan.name == name))

    def list(self) -> list[Plan]:
        return list(self.session.scalars(select(Plan).order_by(Plan.id)))

    def add(self, plan: Plan) -> Plan:
        self.session.add(plan)
        self.session.flush()
        return plan


class CustomerRepository:
    def __init__(self, session: Session):
        self.session = session

    def get(self, customer_id: int) -> Customer | None:
        return self.session.get(Customer, customer_id)

    def get_by_email(self, email: str) -> Customer | None:
        return self.session.scalar(select(Customer).where(Customer.email == email))

    def list(self) -> list[Customer]:
        return list(self.session.scalars(select(Customer).order_by(Customer.id)))

    def add(self, customer: Customer) -> Customer:
        self.session.add(customer)
        self.session.flush()
        return customer


class SubscriptionRepository:
    def __init__(self, session: Session):
        self.session = session

    def get(self, subscription_id: int) -> Subscription | None:
        return self.session.get(Subscription, subscription_id)

    def get_active_for_customer_plan(self, customer_id: int, plan_id: int) -> Subscription | None:
        return self.session.scalar(
            select(Subscription).where(
                Subscription.customer_id == customer_id,
                Subscription.plan_id == plan_id,
                Subscription.status == "active",
            )
        )

    def list(self) -> list[Subscription]:
        return list(self.session.scalars(select(Subscription).order_by(Subscription.id)))

    def add(self, subscription: Subscription) -> Subscription:
        self.session.add(subscription)
        self.session.flush()
        return subscription


class InvoiceRepository:
    def __init__(self, session: Session):
        self.session = session

    def get(self, invoice_id: int) -> Invoice | None:
        return self.session.get(Invoice, invoice_id)

    def get_for_period(self, subscription_id: int, period_start: date, period_end: date) -> Invoice | None:
        return self.session.scalar(
            select(Invoice).where(
                Invoice.subscription_id == subscription_id,
                Invoice.period_start == period_start,
                Invoice.period_end == period_end,
            )
        )

    def add(self, invoice: Invoice) -> Invoice:
        self.session.add(invoice)
        self.session.flush()
        return invoice


class PaymentAttemptRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, attempt: PaymentAttempt) -> PaymentAttempt:
        self.session.add(attempt)
        self.session.flush()
        return attempt


class LedgerRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, entry: LedgerEntry) -> LedgerEntry:
        self.session.add(entry)
        self.session.flush()
        return entry

    def list_for_customer(self, customer_id: int) -> list[LedgerEntry]:
        return list(
            self.session.scalars(
                select(LedgerEntry)
                .where(LedgerEntry.customer_id == customer_id)
                .order_by(LedgerEntry.created_at, LedgerEntry.id)
            )
        )