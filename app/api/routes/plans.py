from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_plan_service
from app.schemas import PlanCreate, PlanRead
from app.services import PlanService

router = APIRouter(prefix="/plans", tags=["plans"])


@router.post("", response_model=PlanRead, status_code=status.HTTP_201_CREATED)
def create_plan(data: PlanCreate, service: PlanService = Depends(get_plan_service)):
    return service.create(data)


@router.get("", response_model=list[PlanRead])
def list_plans(service: PlanService = Depends(get_plan_service)):
    return service.list()


@router.put("/{plan_id}", response_model=PlanRead)
def update_plan(plan_id: int, data: PlanCreate, service: PlanService = Depends(get_plan_service)):
    return service.update(plan_id, data)


@router.post("/{plan_id}/deactivate", response_model=PlanRead)
def deactivate_plan(plan_id: int, service: PlanService = Depends(get_plan_service)):
    return service.deactivate(plan_id)