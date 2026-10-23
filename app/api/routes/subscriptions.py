from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_subscription_service
from app.schemas import SubscriptionCreate, SubscriptionRead
from app.services import SubscriptionService

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


@router.post("", response_model=SubscriptionRead, status_code=status.HTTP_201_CREATED)
def create_subscription(data: SubscriptionCreate, service: SubscriptionService = Depends(get_subscription_service)):
    return service.create(data)


@router.get("", response_model=list[SubscriptionRead])
def list_subscriptions(service: SubscriptionService = Depends(get_subscription_service)):
    return service.list()


@router.patch("/{subscription_id}/cancel", response_model=SubscriptionRead)
def cancel_subscription(subscription_id: int, service: SubscriptionService = Depends(get_subscription_service)):
    return service.cancel(subscription_id)