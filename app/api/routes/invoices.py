from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_invoice_service
from app.schemas import InvoiceGenerate, InvoiceRead
from app.services import InvoiceService

router = APIRouter(prefix="/invoices", tags=["invoices"])


@router.post("/generate", response_model=InvoiceRead, status_code=status.HTTP_201_CREATED)
def generate_invoice(data: InvoiceGenerate, service: InvoiceService = Depends(get_invoice_service)):
    return service.generate(data)


@router.get("/{invoice_id}", response_model=InvoiceRead)
def get_invoice(invoice_id: int, service: InvoiceService = Depends(get_invoice_service)):
    return service.get(invoice_id)