from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class PlanCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=500)
    price: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    billing_cycle: Literal["monthly", "yearly"]
    currency: str = Field(default="USD", min_length=3, max_length=3)

    @field_validator("currency")
    @classmethod
    def normalize_currency(cls, value: str) -> str:
        return value.upper()


class PlanUpdate(PlanCreate):
    pass


class PlanRead(ORMModel):
    id: int
    name: str
    description: str | None
    price: Decimal
    billing_cycle: str
    currency: str
    status: str
    created_at: datetime


class CustomerCreate(BaseModel):
    email: EmailStr
    name: str = Field(min_length=1, max_length=160)
    company: str | None = Field(default=None, max_length=160)
    phone: str | None = Field(default=None, max_length=40)


class CustomerRead(ORMModel):
    id: int
    email: str
    name: str
    company: str | None
    phone: str | None
    created_at: datetime


class SubscriptionCreate(BaseModel):
    customer_id: int = Field(gt=0)
    plan_id: int = Field(gt=0)


class SubscriptionRead(ORMModel):
    id: int
    customer_id: int
    plan_id: int
    status: str
    start_date: date
    next_billing_date: date
    created_at: datetime


class InvoiceGenerate(BaseModel):
    subscription_id: int = Field(gt=0)
    period_start: date | None = None
    period_end: date | None = None

    @model_validator(mode="after")
    def validate_period(self):
        if (self.period_start is None) != (self.period_end is None):
            raise ValueError("period_start and period_end must be provided together")
        if self.period_start is not None and self.period_end <= self.period_start:
            raise ValueError("period_end must be after period_start")
        return self


class InvoiceRead(ORMModel):
    id: int
    subscription_id: int
    customer_id: int
    amount_due: Decimal
    amount_paid: Decimal
    currency: str
    status: str
    period_start: date
    period_end: date
    due_date: date
    created_at: datetime


class PaymentRecord(BaseModel):
    invoice_id: int = Field(gt=0)
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    currency: str = Field(min_length=3, max_length=3)
    status: Literal["success", "failed"]
    provider_reference: str = Field(min_length=1, max_length=160)
    failure_reason: str | None = Field(default=None, max_length=500)

    @field_validator("currency")
    @classmethod
    def normalize_currency(cls, value: str) -> str:
        return value.upper()


class PaymentAttemptRead(ORMModel):
    id: int
    invoice_id: int
    amount: Decimal
    currency: str
    status: str
    provider_reference: str
    failure_reason: str | None
    created_at: datetime


class LedgerEntryRead(ORMModel):
    id: int
    customer_id: int
    invoice_id: int | None
    entry_type: str
    amount: Decimal
    currency: str
    reference_id: str
    created_at: datetime