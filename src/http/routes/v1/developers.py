from fastapi import APIRouter, Depends

from src.application.developer.queries import DeveloperNameFilter
from src.application.developer.service import DevelopersService
from src.dependencies import developers_service_dependency
from src.http.schemas.developers import DeveloperCreateSchema, DeveloperNameResponse

router = APIRouter(prefix="/developers")


@router.get("/names", response_model=list[DeveloperNameResponse])
async def get_by_name(
    filters: DeveloperNameFilter = Depends(),
    service: DevelopersService = Depends(developers_service_dependency),
) -> list[DeveloperNameResponse]:
    return await service.get_by_name(filters=filters)


@router.post("")
async def create_developers(
    developers: list[DeveloperCreateSchema],
    service: DevelopersService = Depends(developers_service_dependency),
):
    return await service.create(developers=developers)
