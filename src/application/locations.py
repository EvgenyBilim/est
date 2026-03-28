from typing import Any
from uuid import UUID, uuid4

from src.enums import LocationTypeEnum
from src.http.schemas.locations import LocationCreateSchema, LocationResponse
from src.infra.components.repository import AcquireTxRepository
from src.infra.repositories.locations import LocationsRepository


class Create:
    def __init__(self, locations_repo: AcquireTxRepository[LocationsRepository]):
        self._locations_repo = locations_repo

    async def __call__(self, locations: list[LocationCreateSchema]) -> None:
        flat_locations = self._flatten_locations(locations, parent_uuid=None)

        async with self._locations_repo() as repo:
            await repo.create(locations=flat_locations)

    def _flatten_locations(
        self, locations: list[LocationCreateSchema], parent_uuid: UUID | None
    ) -> list[dict[str, Any]]:
        result = []

        for location in locations:
            location_uuid = uuid4()

            result.append(
                {
                    "uuid": location_uuid,
                    "parent_uuid": parent_uuid,
                    "name": location.name,
                    "alias": location.alias,
                    "type": location.type,
                }
            )

            if location.locations:
                result.extend(self._flatten_locations(location.locations, parent_uuid=location_uuid))

        return result


class Get:
    def __init__(self, locations_repo: AcquireTxRepository[LocationsRepository]):
        self._locations_repo = locations_repo

    async def __call__(self) -> list[LocationResponse]:
        async with self._locations_repo() as repo:
            return await repo.get()


class GetByType:
    def __init__(self, locations_repo: AcquireTxRepository[LocationsRepository]):
        self._locations_repo = locations_repo

    async def __call__(self, location_type: LocationTypeEnum) -> list[LocationResponse]:
        async with self._locations_repo() as repo:
            return await repo.get_by_type(location_type=location_type)


class GetLocationPath:
    def __init__(self, locations_repo: AcquireTxRepository[LocationsRepository]):
        self._locations_repo = locations_repo

    async def __call__(self, location_uuid: UUID) -> list[LocationResponse]:
        async with self._locations_repo() as repo:
            return await repo.get_location_path(location_uuid=location_uuid)


class LocationsService:
    def __init__(self, locations_repo: AcquireTxRepository[LocationsRepository]):
        self.create = Create(locations_repo=locations_repo)
        self.get = Get(locations_repo=locations_repo)
        self.get_by_type = GetByType(locations_repo=locations_repo)
        self.get_location_path = GetLocationPath(locations_repo=locations_repo)
