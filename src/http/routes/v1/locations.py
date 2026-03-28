from fastapi import APIRouter, Depends

from src.application.locations import LocationsService
from src.dependencies import locations_service_dependency
from src.http.schemas.locations import LocationCreateSchema

router = APIRouter(prefix="/locations")


@router.post("")
async def create_locations(
    locations: list[LocationCreateSchema],
    service: LocationsService = Depends(locations_service_dependency),
):
    return await service.create(locations=locations)
