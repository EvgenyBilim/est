from fastapi import APIRouter, Depends

from src.application.seeder.const import SEED_LOCATIONS
from src.application.seeder.service import DatabaseSeeder
from src.dependencies import database_seeder_service_dependency
from src.http.schemas.locations import LocationCreateSchema

router = APIRouter(prefix="/seeder")


@router.post("")
async def seed(
    locations: list[LocationCreateSchema] | None = None,
    service: DatabaseSeeder = Depends(database_seeder_service_dependency),
) -> None:
    if not locations:
        locations = [LocationCreateSchema(**x) for x in SEED_LOCATIONS]
    return await service(locations=locations)
