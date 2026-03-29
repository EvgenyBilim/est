from uuid import UUID

from src.enums import LocationTypeEnum
from src.http.schemas.filters import (
    FilterAgreementType,
    FilterLocation,
    FilterMetroStation,
    FilterPaymentType,
    HomeFilterOptionsResponse,
)
from src.infra.components.repository import AcquireTxRepository
from src.infra.repositories.agreements import AgreementsRepository
from src.infra.repositories.locations import LocationsRepository
from src.infra.repositories.metro import MetroRepository
from src.infra.repositories.payments import PaymentsRepository


class HomeFiltersService:
    def __init__(
        self,
        locations_repo: AcquireTxRepository[LocationsRepository],
        payments_repo: AcquireTxRepository[PaymentsRepository],
        agreements_repo: AcquireTxRepository[AgreementsRepository],
        metro_repo: AcquireTxRepository[MetroRepository],
    ) -> None:
        self._locations_repo = locations_repo
        self._payments_repo = payments_repo
        self._agreements_repo = agreements_repo
        self._metro_repo = metro_repo

    async def __call__(self, location_uuid: UUID) -> HomeFilterOptionsResponse | None:
        async with self._locations_repo() as repo:
            locations = await repo.get_by_uuids(location_uuids=[location_uuid])
            if not locations:
                return None
            location = locations[0]
            children = await repo.get_children(location_uuid=location_uuid)
            location_path = await repo.get_location_path(location_uuid=location_uuid)

        location_uuids = [loc.uuid for loc in location_path]

        async with self._payments_repo() as repo:
            payment_types = await repo.get_by_locations(location_uuids=location_uuids)

        async with self._agreements_repo() as repo:
            agreement_types = await repo.get_by_locations(location_uuids=location_uuids)

        metro_stations: list[FilterMetroStation] = []
        if location.type == LocationTypeEnum.CITY:
            async with self._metro_repo() as repo:
                stations = await repo.get_stations_info_by_city(city_uuid=location_uuid)
                metro_stations = [FilterMetroStation(uuid=s.uuid, name=s.name, line_color=s.color) for s in stations]

        return HomeFilterOptionsResponse(
            locations=[FilterLocation(uuid=loc.uuid, name=loc.name) for loc in children],
            payment_types=[FilterPaymentType(uuid=pt.uuid, name=pt.name) for pt in payment_types],
            agreement_types=[FilterAgreementType(uuid=at.uuid, name=at.name) for at in agreement_types],
            metro_stations=metro_stations,
        )
