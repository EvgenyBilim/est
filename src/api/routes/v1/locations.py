from fastapi import APIRouter, Depends

from src.api.schemas.locations import LocationCreateSchema
from src.application.locations import LocationsService
from src.dependencies import locations_service_dependency

router = APIRouter(prefix="/locations")


@router.post("")
async def create_locations(
    locations: list[LocationCreateSchema],
    service: LocationsService = Depends(locations_service_dependency),
):
    return await service.create(locations=locations)
