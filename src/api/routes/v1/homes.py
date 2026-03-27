from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from src.api.schemas.homes import HomeCreateSchema, HomeResponse, HomePreviewResponse, HomeNameResponse
from src.application.home.queries import HomeSearchFilter, HomeTagFilter, validate_filters
from src.application.home.service import HomesService
from src.dependencies import homes_service_dependency

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
async def search(
    filters: HomeSearchFilter = Depends(validate_filters),
    service: HomesService = Depends(homes_service_dependency),
) -> list[HomePreviewResponse]:
    return await service.search(filters=filters)
