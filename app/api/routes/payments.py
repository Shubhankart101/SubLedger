from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_payment_service
from app.schemas import InvoiceRead, PaymentAttemptRead, PaymentRecord
from app.services import PaymentService

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/record", status_code=status.HTTP_201_CREATED)
def record_payment(data: PaymentRecord, service: PaymentService = Depends(get_payment_service)):
    attempt, invoice = service.record(data)
    return {"payment_attempt": PaymentAttemptRead.model_validate(attempt), "invoice": InvoiceRead.model_validate(invoice)}