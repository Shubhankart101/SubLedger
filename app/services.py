import calendar
from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.errors import ConflictError, NotFoundError, RuleViolationError
from app.models import Customer, Invoice, LedgerEntry, PaymentAttempt, Plan, Subscription
from app.repositories import (
    CustomerRepository,
    InvoiceRepository,
    LedgerRepository,
    PaymentAttemptRepository,
    PlanRepository,
    SubscriptionRepository,
)
from app.schemas import CustomerCreate, InvoiceGenerate, PaymentRecord, PlanCreate, SubscriptionCreate


def add_billing_cycle(start: date, billing_cycle: str) -> date:
    if billing_cycle == "yearly":
        year = start.year + 1
        return start.replace(year=year, day=min(start.day, calendar.monthrange(year, start.month)[1]))
    month = start.month % 12 + 1
    year = start.year + (start.month // 12)
    return start.replace(year=year, month=month, day=min(start.day, calendar.monthrange(year, month)[1]))


class PlanService:
    def __init__(self, session: Session, plans: PlanRepository):
        self.session = session
        self.plans = plans

    def create(self, data: PlanCreate) -> Plan:
        if self.plans.get_by_name(data.name):
            raise ConflictError("A plan with this name already exists")
        plan = self.plans.add(Plan(**data.model_dump()))
        self.session.commit()
        return plan

    def list(self) -> list[Plan]:
        return self.plans.list()

    def update(self, plan_id: int, data: PlanCreate) -> Plan:
        plan = self.plans.get(plan_id)
        if not plan:
            raise NotFoundError("Plan not found")
        duplicate = self.plans.get_by_name(data.name)
        if duplicate and duplicate.id != plan_id:
            raise ConflictError("A plan with this name already exists")
        for field, value in data.model_dump().items():
            setattr(plan, field, value)
        self.session.commit()
        return plan

    def deactivate(self, plan_id: int) -> Plan:
        plan = self.plans.get(plan_id)
        if not plan:
            raise NotFoundError("Plan not found")
        plan.status = "inactive"
        self.session.commit()
        return plan


class CustomerService:
    def __init__(self, session: Session, customers: CustomerRepository):
        self.session = session
        self.customers = customers

    def create(self, data: CustomerCreate) -> Customer:
        email = str(data.email).lower()
        if self.customers.get_by_email(email):
            raise ConflictError("A customer with this email already exists")
        customer = self.customers.add(Customer(**data.model_dump(exclude={"email"}), email=email))
        self.session.commit()
        return customer

    def list(self) -> list[Customer]:
        return self.customers.list()

    def get(self, customer_id: int) -> Customer:
        customer = self.customers.get(customer_id)
        if not customer:
            raise NotFoundError("Customer not found")
        return customer


class SubscriptionService:
    def __init__(
        self,
        session: Session,
        subscriptions: SubscriptionRepository,
        customers: CustomerRepository,
        plans: PlanRepository,
    ):
        self.session = session
        self.subscriptions = subscriptions
        self.customers = customers
        self.plans = plans

    def create(self, data: SubscriptionCreate) -> Subscription:
        if not self.customers.get(data.customer_id):
            raise NotFoundError("Customer not found")
        plan = self.plans.get(data.plan_id)
        if not plan:
            raise NotFoundError("Plan not found")
        if plan.status != "active":
            raise RuleViolationError("An inactive plan cannot be subscribed to")
        if self.subscriptions.get_active_for_customer_plan(data.customer_id, data.plan_id):
            raise ConflictError("Customer already has an active subscription to this plan")
        subscription = self.subscriptions.add(
            Subscription(customer_id=data.customer_id, plan_id=data.plan_id)
        )
        self.session.commit()
        return subscription

    def list(self) -> list[Subscription]:
        return self.subscriptions.list()

    def cancel(self, subscription_id: int) -> Subscription:
        subscription = self.subscriptions.get(subscription_id)
        if not subscription:
            raise NotFoundError("Subscription not found")
        if subscription.status != "active":
            raise ConflictError("Subscription is not active")
        subscription.status = "canceled"
        self.session.commit()
        return subscription


class LedgerService:
    def __init__(self, session: Session, ledger: LedgerRepository, customers: CustomerRepository):
        self.session = session
        self.ledger = ledger
        self.customers = customers

    def record(
        self,
        customer_id: int,
        invoice_id: int | None,
        entry_type: str,
        amount: Decimal,
        currency: str,
        reference_id: str,
    ) -> LedgerEntry:
        return self.ledger.add(
            LedgerEntry(
                customer_id=customer_id,
                invoice_id=invoice_id,
                entry_type=entry_type,
                amount=amount,
                currency=currency,
                reference_id=reference_id,
            )
        )

    def list_for_customer(self, customer_id: int) -> list[LedgerEntry]:
        if not self.customers.get(customer_id):
            raise NotFoundError("Customer not found")
        return self.ledger.list_for_customer(customer_id)


class InvoiceService:
    def __init__(
        self,
        session: Session,
        subscriptions: SubscriptionRepository,
        plans: PlanRepository,
        invoices: InvoiceRepository,
        ledger: LedgerService,
    ):
        self.session = session
        self.subscriptions = subscriptions
        self.plans = plans
        self.invoices = invoices
        self.ledger = ledger

    def generate(self, data: InvoiceGenerate) -> Invoice:
        subscription = self.subscriptions.get(data.subscription_id)
        if not subscription:
            raise NotFoundError("Subscription not found")
        if subscription.status != "active":
            raise RuleViolationError("Invoices can only be generated for active subscriptions")
        plan = self.plans.get(subscription.plan_id)
        if not plan:
            raise NotFoundError("Subscription plan not found")
        period_start = data.period_start or subscription.next_billing_date
        period_end = data.period_end or add_billing_cycle(period_start, plan.billing_cycle)
        if self.invoices.get_for_period(subscription.id, period_start, period_end):
            raise ConflictError("An invoice already exists for this subscription period")
        invoice = self.invoices.add(
            Invoice(
                subscription_id=subscription.id,
                customer_id=subscription.customer_id,
                amount_due=plan.price,
                amount_paid=Decimal("0.00"),
                currency=plan.currency,
                status="issued",
                period_start=period_start,
                period_end=period_end,
                due_date=period_start + timedelta(days=14),
            )
        )
        self.ledger.record(
            customer_id=subscription.customer_id,
            invoice_id=invoice.id,
            entry_type="invoice_created",
            amount=invoice.amount_due,
            currency=invoice.currency,
            reference_id=f"invoice:{invoice.id}",
        )
        if period_start >= subscription.next_billing_date:
            subscription.next_billing_date = period_end
        self.session.commit()
        return invoice

    def get(self, invoice_id: int) -> Invoice:
        invoice = InvoiceRepository(self.session).get(invoice_id)
        if not invoice:
            raise NotFoundError("Invoice not found")
        return invoice


class PaymentService:
    def __init__(
        self,
        session: Session,
        invoices: InvoiceRepository,
        attempts: PaymentAttemptRepository,
        ledger: LedgerService,
    ):
        self.session = session
        self.invoices = invoices
        self.attempts = attempts
        self.ledger = ledger

    def record(self, data: PaymentRecord) -> tuple[PaymentAttempt, Invoice]:
        invoice = self.invoices.get(data.invoice_id)
        if not invoice:
            raise NotFoundError("Invoice not found")
        if data.currency != invoice.currency:
            raise RuleViolationError("Payment currency must match invoice currency")
        if invoice.status == "paid":
            raise ConflictError("Invoice is already paid")
        if data.status == "success" and data.amount > invoice.amount_due - invoice.amount_paid:
            raise RuleViolationError("Payment exceeds the remaining unpaid amount")
        attempt = self.attempts.add(
            PaymentAttempt(
                invoice_id=invoice.id,
                amount=data.amount,
                currency=data.currency,
                status=data.status,
                provider_reference=data.provider_reference,
                failure_reason=data.failure_reason if data.status == "failed" else None,
            )
        )
        entry_type = "payment_success" if data.status == "success" else "payment_failure"
        if data.status == "success":
            invoice.amount_paid += data.amount
            invoice.status = "paid" if invoice.amount_paid == invoice.amount_due else "partially_paid"
        self.ledger.record(
            customer_id=invoice.customer_id,
            invoice_id=invoice.id,
            entry_type=entry_type,
            amount=data.amount,
            currency=data.currency,
            reference_id=data.provider_reference,
        )
        self.session.commit()
        return attempt, invoice