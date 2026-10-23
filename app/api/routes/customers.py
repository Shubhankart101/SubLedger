from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_customer_service, get_ledger_service
from app.schemas import CustomerCreate, CustomerRead, LedgerEntryRead
from app.services import CustomerService, LedgerService

router = APIRouter(prefix="/customers", tags=["customers"])


@router.post("", response_model=CustomerRead, status_code=status.HTTP_201_CREATED)
def create_customer(data: CustomerCreate, service: CustomerService = Depends(get_customer_service)):
    return service.create(data)


@router.get("", response_model=list[CustomerRead])
def list_customers(service: CustomerService = Depends(get_customer_service)):
    return service.list()


@router.get("/{customer_id}", response_model=CustomerRead)
def get_customer(customer_id: int, service: CustomerService = Depends(get_customer_service)):
    return service.get(customer_id)


@router.get("/{customer_id}/ledger", response_model=list[LedgerEntryRead])
def get_customer_ledger(customer_id: int, service: LedgerService = Depends(get_ledger_service)):
    return service.list_for_customer(customer_id)