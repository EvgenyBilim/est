from uuid import UUID, uuid4

from src.api.schemas.metro import MetropolitanCreateSchema, MetroStationModel
from src.infrastructure.components.repository import AcquireTxRepository
from src.infrastructure.repositories.metro import MetroRepository


class CreateWithStructure:
    def __init__(self, metro_repo: AcquireTxRepository[MetroRepository]) -> None:
        self._metro_repo = metro_repo

    async def __call__(self, metros: list[MetropolitanCreateSchema]) -> None:
        metropolitans_data = []
        lines_data = []
        stations_data = []

        for metro in metros:
            metro_uuid = uuid4()

            metropolitans_data.append({
                "uuid": metro_uuid,
                "name": metro.name,
                "location_uuid": metro.location_uuid,
            })

            for line in metro.lines:
                line_uuid = uuid4()

                lines_data.append({
                    "uuid": line_uuid,
                    "metropolitan_uuid": metro_uuid,
                    "name": line.name,
                    "color": line.color,
                })

                for station in line.stations:
                    stations_data.append({
                        "uuid": uuid4(),
                        "metro_line_uuid": line_uuid,
                        "name": station.name,
                    })

        async with self._metro_repo() as repo:
            await repo.create_metropolitans(metropolitans_data)

            if lines_data:
                await repo.create_lines(lines_data)

            if stations_data:
                await repo.create_stations(stations_data)


class GetStationsByCity:
    def __init__(self, metro_repo: AcquireTxRepository[MetroRepository]) -> None:
        self._metro_repo = metro_repo

    async def __call__(self, city_uuid: UUID) -> list[MetroStationModel]:
        async with self._metro_repo() as repo:
            return await repo.get_stations_by_city(city_uuid=city_uuid)


class MetroService:
    def __init__(self, metro_repo: AcquireTxRepository[MetroRepository]) -> None:
        self.create_with_structure = CreateWithStructure(metro_repo=metro_repo)
        self.get_stations_by_city = GetStationsByCity(metro_repo=metro_repo)
