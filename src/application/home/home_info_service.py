from collections import defaultdict
from datetime import date
from decimal import Decimal
from uuid import UUID

from src.domain.home.aggregate import Home
from src.domain.home.entities import Plan
from src.domain.home.value_objects import (
    HomeInfo,
    LocationInfo,
    MetroStationInfo,
    PlansInfo,
    RoomStats,
)
from src.enums import RoomTypeEnum
from src.infra.components.repository import AcquireTxRepository
from src.infra.repositories.agreements import AgreementsRepository
from src.infra.repositories.home_info import HomeInfoRepository
from src.infra.repositories.locations import LocationsRepository
from src.infra.repositories.metro import MetroRepository
from src.infra.repositories.payments import PaymentsRepository


class HomeInfoService:
    def __init__(
        self,
        agreements_repo: AcquireTxRepository[AgreementsRepository],
        payments_repo: AcquireTxRepository[PaymentsRepository],
        locations_repo: AcquireTxRepository[LocationsRepository],
        metro_repo: AcquireTxRepository[MetroRepository],
        home_info_repo: AcquireTxRepository[HomeInfoRepository],
    ):
        self._agreements_repo = agreements_repo
        self._payments_repo = payments_repo
        self._locations_repo = locations_repo
        self._metro_repo = metro_repo
        self._home_info_repo = home_info_repo

    async def sync(self, home: Home):
        home_info = await self._calculate(home)

        async with self._home_info_repo() as repo:
            await repo.sync(home_info)

    async def _calculate(self, home: Home) -> HomeInfo:
        all_plans = [plan for block in home.blocks for plan in block.plans]

        delivery_from, delivery_to = self._calc_delivery_range(home)
        floors_min, floors_max = self._calc_floors_range(home)
        roof_height_min, roof_height_max = self._calc_roof_height_range(all_plans)

        wall_types = list({block.wall_type for block in home.blocks})
        trim_types = list({plan.trim for plan in all_plans})
        bathroom_types = list({plan.bathroom_type for plan in all_plans})

        agreement_types = await self._get_agreement_types(all_plans)
        payment_types = await self._get_payment_types(home.payment_type_uuids)
        locations = await self._get_locations(home.location_uuids)
        metro_stations = await self._get_metro_stations(home)

        plans_info = self._calc_plans_info(all_plans)

        return HomeInfo(
            uuid=home.uuid,
            delivery_from=delivery_from,
            delivery_to=delivery_to,
            floors_min=floors_min,
            floors_max=floors_max,
            roof_height_min=roof_height_min,
            roof_height_max=roof_height_max,
            wall_types=wall_types,
            trim_types=trim_types,
            bathroom_types=bathroom_types,
            agreement_types=agreement_types,
            payment_types=payment_types,
            locations=locations,
            metro_stations=metro_stations,
            plans_info=plans_info,
            blocks_count=len(home.blocks),
        )

    @staticmethod
    def _calc_delivery_range(home: Home) -> tuple[date | None, date | None]:
        if not home.blocks:
            return None, None

        dates = [block.delivery_date for block in home.blocks]
        return min(dates), max(dates)

    @staticmethod
    def _calc_floors_range(home: Home) -> tuple[int | None, int | None]:
        if not home.blocks:
            return None, None

        floors = [block.floors for block in home.blocks]
        return min(floors), max(floors)

    @staticmethod
    def _calc_roof_height_range(plans: list[Plan]) -> tuple[Decimal | None, Decimal | None]:
        if not plans:
            return None, None

        heights = [p.roof_height for p in plans if p.roof_height is not None]
        if not heights:
            return None, None

        return min(heights), max(heights)

    @staticmethod
    def _calc_plans_info(plans: list[Plan]) -> PlansInfo | None:
        if not plans:
            return None

        by_rooms: dict[RoomTypeEnum, list] = defaultdict(list)
        for plan in plans:
            by_rooms[plan.rooms].append(plan)

        rooms_stats = {}

        for room_type, room_plans in by_rooms.items():
            prices = [p.price_discount or p.price_base for p in room_plans]
            squares = [p.square_total for p in room_plans]

            rooms_stats[room_type] = RoomStats(
                count=len(room_plans),
                min_price=min(prices),
                max_price=max(prices),
                min_square=min(squares),
                max_square=max(squares),
            )

        all_prices = [p.price_discount or p.price_base for p in plans]
        all_squares = [p.square_total for p in plans]

        return PlansInfo(
            count=len(plans),
            min_price=min(all_prices),
            max_price=max(all_prices),
            min_square=min(all_squares),
            max_square=max(all_squares),
            rooms_stats=rooms_stats,
        )

    async def _get_agreement_types(self, plans: list) -> list:
        agreement_uuids = list({p.agreement_uuid for p in plans if p.agreement_uuid})
        if not agreement_uuids:
            return []

        async with self._agreements_repo() as repo:
            agreements = await repo.get_by_uuids(agreement_uuids)
            return [a.name.lower() for a in agreements]

    async def _get_payment_types(self, payment_type_uuids: list[UUID]) -> list:
        if not payment_type_uuids:
            return []

        async with self._payments_repo() as repo:
            payments = await repo.get_by_uuids(payment_type_uuids)
            return [p.name.lower() for p in payments]

    async def _get_locations(self, location_uuids: list[UUID]) -> LocationInfo | None:
        if not location_uuids:
            return None

        async with self._locations_repo() as repo:
            locations = await repo.get_by_uuids(location_uuids)

        if not locations:
            return None

        child_by_parent = {}
        root_location = None

        for location in locations:
            if location.parent_uuid is None:
                root_location = location
            else:
                child_by_parent[location.parent_uuid] = location

        if root_location is None:
            return None

        def build_chain(loc) -> LocationInfo:
            child_loc = child_by_parent.get(loc.uuid)
            return LocationInfo(
                uuid=loc.uuid,
                name=loc.name,
                alias=loc.alias,
                type=loc.type,
                child=build_chain(child_loc) if child_loc else None,
            )

        return build_chain(root_location)

    async def _get_metro_stations(self, home: Home) -> list[MetroStationInfo]:
        if not home.metro_stations:
            return []

        station_uuids = [m.station_uuid for m in home.metro_stations]

        async with self._metro_repo() as repo:
            stations = await repo.get_stations_info_by_uuids(station_uuids)

        home_metro_map = {m.station_uuid: m for m in home.metro_stations}

        return [
            MetroStationInfo(
                station_uuid=s.uuid,
                station_name=s.name,
                line_color=s.color,
                minutes_to_metro=home_metro_map[s.uuid].minutes_to_metro,
                transport=home_metro_map[s.uuid].transport,
            )
            for s in stations
            if s.uuid in home_metro_map
        ]
