from fastapi import Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.repositories import (
    CustomerRepository,
    InvoiceRepository,
    LedgerRepository,
    PaymentAttemptRepository,
    PlanRepository,
    SubscriptionRepository,
)
from app.services import (
    CustomerService,
    InvoiceService,
    LedgerService,
    PaymentService,
    PlanService,
    SubscriptionService,
)


def get_plan_service(session: Session = Depends(get_db)) -> PlanService:
    return PlanService(session, PlanRepository(session))


def get_customer_service(session: Session = Depends(get_db)) -> CustomerService:
    return CustomerService(session, CustomerRepository(session))


def get_subscription_service(session: Session = Depends(get_db)) -> SubscriptionService:
    return SubscriptionService(
        session,
        SubscriptionRepository(session),
        CustomerRepository(session),
        PlanRepository(session),
    )


def get_ledger_service(session: Session = Depends(get_db)) -> LedgerService:
    return LedgerService(session, LedgerRepository(session), CustomerRepository(session))


def get_invoice_service(session: Session = Depends(get_db)) -> InvoiceService:
    return InvoiceService(
        session,
        SubscriptionRepository(session),
        PlanRepository(session),
        InvoiceRepository(session),
        get_ledger_service(session),
    )


def get_payment_service(session: Session = Depends(get_db)) -> PaymentService:
    return PaymentService(
        session,
        InvoiceRepository(session),
        PaymentAttemptRepository(session),
        get_ledger_service(session),
    )