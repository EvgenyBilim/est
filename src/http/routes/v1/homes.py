from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from src.application.home.queries import (
    HomeSearchFilter,
    HomeTagFilter,
    PlanSearchFilter,
    validate_home_filters,
)
from src.application.home.service import HomesService
from src.dependencies import homes_service_dependency
from src.http.schemas.homes import (
    HomeCreateSchema,
    HomeNameResponse,
    HomePreviewResponse,
    HomeResponse,
    PlanGroupResponse,
    PlanResponse,
)

router = APIRouter(prefix="/homes")


@router.post("", response_model=list[UUID])
async def bulk_create(
    homes: list[HomeCreateSchema],
    service: HomesService = Depends(homes_service_dependency),
) -> list[UUID]:
    commands = [home.to_command() for home in homes]
    return await service.create_homes(commands=commands)


@router.get("/names", response_model=list[HomeNameResponse])
async def get_by_tag(
    tag: HomeTagFilter = Depends(),
    service: HomesService = Depends(homes_service_dependency),
) -> list[HomeNameResponse]:
    return await service.get_by_tag(tag=tag)


@router.get("/plans/{group_uuid}", response_model=PlanGroupResponse)
async def get_group_plan(
    group_uuid: UUID,
    service: HomesService = Depends(homes_service_dependency),
) -> PlanGroupResponse:
    plan_group = await service.get_group_plan_by_uuid(group_uuid=group_uuid)
    if not plan_group:
        raise HTTPException(status_code=404, detail=f"Plan group {group_uuid} not found")
    return plan_group


@router.get("/{home_uuid}/plans", response_model=list[PlanResponse])
async def search_plans(
    home_uuid: UUID,
    filters: PlanSearchFilter = Depends(),
    service: HomesService = Depends(homes_service_dependency),
) -> list[PlanResponse]:
    return await service.search_plans(home_uuid=home_uuid, filters=filters)


@router.get("/{home_uuid}", response_model=HomeResponse)
async def get_by_uuid(
    home_uuid: UUID,
    service: HomesService = Depends(homes_service_dependency),
) -> HomeResponse:
    home = await service.get_by_uuid(home_uuid=home_uuid)
    if not home:
        raise HTTPException(status_code=404, detail=f"Home {home_uuid} not found")
    return home


@router.get("", response_model=list[HomePreviewResponse])
async def search_homes(
    filters: HomeSearchFilter = Depends(validate_home_filters),
    service: HomesService = Depends(homes_service_dependency),
) -> list[HomePreviewResponse]:
    return await service.search_homes(filters=filters)
