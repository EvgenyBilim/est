from fastapi import APIRouter, Depends

from src.application.locations import LocationsService
from src.dependencies import locations_service_dependency
from src.http.schemas.locations import CountrySearchAreasResponse, LocationCreateSchema

router = APIRouter(prefix="/locations")


@router.post("")
async def create_locations(
    locations: list[LocationCreateSchema],
    service: LocationsService = Depends(locations_service_dependency),
):
    return await service.create(locations=locations)


@router.get("/search-areas", response_model=list[CountrySearchAreasResponse])
async def get_search_areas(
    service: LocationsService = Depends(locations_service_dependency),
):
    return await service.get_search_areas()
