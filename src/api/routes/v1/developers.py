from fastapi import APIRouter, Depends

from src.api.schemas.developers import DeveloperCreateSchema
from src.application.developers import DevelopersService
from src.dependencies import developers_service_dependency

router = APIRouter(prefix="/developers")


@router.post("")
async def create_developers(
    developers: list[DeveloperCreateSchema],
    service: DevelopersService = Depends(developers_service_dependency),
):
    return await service.create(developers=developers)
