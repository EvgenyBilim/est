from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from src.application.home_filters import HomeFiltersService
from src.dependencies import home_filters_service_dependency
from src.http.schemas.filters import HomeFilterOptionsResponse

router = APIRouter(prefix="/filters")


@router.get("/homes", response_model=HomeFilterOptionsResponse)
async def get_home_filter_options(
    location: UUID,
    service: HomeFiltersService = Depends(home_filters_service_dependency),
) -> HomeFilterOptionsResponse:
    result = await service(location_uuid=location)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Location {location} not found")
    return result
