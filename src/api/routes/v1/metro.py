from fastapi import APIRouter, Depends

from src.api.schemas.metro import MetropolitanCreateSchema
from src.application.metro import MetroService
from src.dependencies import metro_service_dependency

router = APIRouter(prefix="/metro")


@router.post("/metro_with_structure")
async def create_metro_with_structure(
    metros: list[MetropolitanCreateSchema],
    service: MetroService = Depends(metro_service_dependency),
):
    return await service.create_with_structure(metros=metros)
