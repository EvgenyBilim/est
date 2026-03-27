from uuid import UUID

from src.application.home.commands import (
    BlockCreateData,
    BlockSyncData,
    GalleryImageCreateData,
    GalleryImageSyncData,
    HomeCreateCommand,
    HomeSyncData,
    MetroStationCreateData,
    MetroStationSyncData,
    PlanCreateData,
    PlanSyncData,
)
from src.domain.home.aggregate import Home
from src.domain.home.entities import Plan
from src.domain.home.specifications import (
    AgreementsMatchCountrySpec,
    MetroStationInSameCitySpec,
    PaymentTypesMatchCountrySpec,
)
from src.infrastructure.components.repository import AcquireTxRepository
from src.infrastructure.repositories.locations import LocationsRepository


class HomeFactory:
    def __init__(
        self,
        locations_repo: AcquireTxRepository[LocationsRepository],
        agreements_spec: AgreementsMatchCountrySpec,
        metro_spec: MetroStationInSameCitySpec,
        payments_spec: PaymentTypesMatchCountrySpec,
    ) -> None:
        self._locations_repo = locations_repo
        self._specifications = [metro_spec, payments_spec, agreements_spec]

    async def create(self, command: HomeCreateCommand) -> Home:
        location_uuids = await self._get_location_path(command.location_uuid)

        home = Home.create(
            name=command.name,
            alias=command.alias,
            developer_uuid=command.developer_uuid,
            location_uuids=location_uuids,
            coordinates=command.coordinates,
            description=command.description,
            housing_class=command.housing_class,
            parking_types=command.parking_types,
            payment_type_uuids=command.payment_type_uuids,
            is_apartment=command.is_apartment,
            has_closed_territory=command.has_closed_territory,
            has_security=command.has_security,
            tags=command.tags,
            sort_order=command.sort_order,
        )

        self._populate_blocks(home, command.blocks)
        self._populate_gallery(home, command.gallery)
        self._populate_metro(home, command.metro_stations)

        await self.validate(home)
        home.mark_structure_changed()

        return home

    async def add_blocks(self, home: Home, blocks: list[BlockCreateData]) -> list[UUID]:
        new_uuids = []
        for block_data in blocks:
            block = home.add_block(
                name=block_data.name,
                address=block_data.address,
                floors=block_data.floors,
                wall_type=block_data.wall_type,
                delivery_date=block_data.delivery_date,
            )
            new_uuids.append(block.uuid)

            for plan_data in block_data.plans:
                self._add_plan(home, block.uuid, plan_data)

        await self.validate(home)
        home.mark_structure_changed()

        return new_uuids

    async def add_plans(self, home: Home, block_uuid: UUID, plans: list[PlanCreateData]) -> list[UUID]:
        new_uuids = []
        for plan_data in plans:
            plan = self._add_plan(home, block_uuid, plan_data)
            new_uuids.append(plan.uuid)

        await self.validate(home)
        home.mark_structure_changed()

        return new_uuids

    async def sync(self, home: Home, data: HomeSyncData) -> None:
        location_uuids = await self._get_location_path(data.location_uuid)

        home.update_attributes(
            name=data.name,
            alias=data.alias,
            developer_uuid=data.developer_uuid,
            location_uuids=location_uuids,
            coordinates=data.coordinates,
            description=data.description,
            housing_class=data.housing_class,
            parking_types=data.parking_types,
            payment_type_uuids=data.payment_type_uuids,
            is_apartment=data.is_apartment,
            has_closed_territory=data.has_closed_territory,
            has_security=data.has_security,
            tags=data.tags,
            sort_order=data.sort_order,
        )

        self._sync_blocks(home, data.blocks)
        self._sync_gallery(home, data.gallery)
        self._sync_metro(home, data.metro_stations)

        await self.validate(home)
        home.mark_structure_changed()

    async def validate(self, home: Home) -> None:
        for spec in self._specifications:
            await spec.check(home)

    # ==== Наполнение данными ====

    def _populate_blocks(self, home: Home, blocks: list[BlockCreateData]) -> None:
        for block_data in blocks:
            block = home.add_block(
                name=block_data.name,
                address=block_data.address,
                floors=block_data.floors,
                wall_type=block_data.wall_type,
                delivery_date=block_data.delivery_date,
            )
            for plan_data in block_data.plans:
                self._add_plan(home, block.uuid, plan_data)

    def _populate_gallery(self, home: Home, gallery: list[GalleryImageCreateData]) -> None:
        for image_data in gallery:
            home.add_gallery_image(
                image_type=image_data.image_type,
                image_path=image_data.image_path,
                sort_order=image_data.sort_order,
            )

    def _populate_metro(self, home: Home, stations: list[MetroStationCreateData]) -> None:
        for station_data in stations:
            home.add_metro_station(
                station_uuid=station_data.station_uuid,
                minutes_to_metro=station_data.minutes_to_metro,
                transport=station_data.transport,
            )

    def _add_plan(self, home: Home, block_uuid: UUID, data: PlanCreateData) -> Plan:
        plan = home.add_plan_to_block(
            block_uuid=block_uuid,
            rooms=data.rooms,
            agreement_uuid=data.agreement_uuid,
            square_total=data.square_total,
            square_kitchen=data.square_kitchen,
            trim=data.trim,
            bathroom_type=data.bathroom_type,
            roof_height=data.roof_height,
            price_base=data.price_base,
            price_discount=data.price_discount,
            floor=data.floor,
            img_path=data.img_path,
        )
        return plan

    # ==== Синхронизация ====

    def _sync_blocks(self, home: Home, blocks_data: list[BlockSyncData]) -> None:
        incoming_uuids = {b.uuid for b in blocks_data if b.uuid}
        home.remove_blocks_except(incoming_uuids)

        for block_data in blocks_data:
            if block_data.uuid:
                self._update_block(home, block_data)
            else:
                self._create_block(home, block_data)

    def _update_block(self, home: Home, data: BlockSyncData) -> None:
        home.update_block(
            block_uuid=data.uuid,
            name=data.name,
            address=data.address,
            floors=data.floors,
            wall_type=data.wall_type,
            delivery_date=data.delivery_date,
        )
        self._sync_plans(home, data.uuid, data.plans)

    def _create_block(self, home: Home, data: BlockSyncData) -> None:
        block = home.add_block(
            name=data.name,
            address=data.address,
            floors=data.floors,
            wall_type=data.wall_type,
            delivery_date=data.delivery_date,
        )
        for plan_data in data.plans:
            self._create_plan(home, block.uuid, plan_data)

    def _sync_plans(self, home: Home, block_uuid: UUID, plans_data: list[PlanSyncData]) -> None:
        incoming_uuids = {p.uuid for p in plans_data if p.uuid}
        home.remove_plans_from_block_except(block_uuid, incoming_uuids)

        for plan_data in plans_data:
            if plan_data.uuid:
                self._update_plan(home, block_uuid, plan_data)
            else:
                self._create_plan(home, block_uuid, plan_data)

    def _update_plan( self, home: Home, block_uuid: UUID, data: PlanSyncData) -> None:
        home.update_plan(
            block_uuid=block_uuid,
            plan_uuid=data.uuid,
            rooms=data.rooms,
            agreement_uuid=data.agreement_uuid,
            square_total=data.square_total,
            square_kitchen=data.square_kitchen,
            trim=data.trim,
            bathroom_type=data.bathroom_type,
            roof_height=data.roof_height,
            price_base=data.price_base,
            price_discount=data.price_discount,
            floor=data.floor,
            img_path=data.img_path,
        )

    def _create_plan(self, home: Home, block_uuid: UUID, data: PlanSyncData) -> None:
        home.add_plan_to_block(
            block_uuid=block_uuid,
            rooms=data.rooms,
            agreement_uuid=data.agreement_uuid,
            square_total=data.square_total,
            square_kitchen=data.square_kitchen,
            trim=data.trim,
            bathroom_type=data.bathroom_type,
            roof_height=data.roof_height,
            price_base=data.price_base,
            price_discount=data.price_discount,
            floor=data.floor,
            img_path=data.img_path,
        )

    def _sync_gallery(self, home: Home, gallery_data: list[GalleryImageSyncData]) -> None:
        incoming_uuids = {g.uuid for g in gallery_data if g.uuid}
        home.remove_gallery_except(incoming_uuids)

        for image_data in gallery_data:
            if image_data.uuid:
                home.update_gallery_image(
                    image_uuid=image_data.uuid,
                    image_type=image_data.image_type,
                    image_path=image_data.image_path,
                    sort_order=image_data.sort_order,
                )
            else:
                home.add_gallery_image(
                    image_type=image_data.image_type,
                    image_path=image_data.image_path,
                    sort_order=image_data.sort_order,
                )

    def _sync_metro(self, home: Home, metro_data: list[MetroStationSyncData]) -> None:
        incoming_uuids = {m.station_uuid for m in metro_data if m.station_uuid}
        home.remove_metro_except(incoming_uuids)

        for station_data in metro_data:
            if station_data.uuid:
                home.update_metro_station(
                    metro_uuid=station_data.uuid,
                    station_uuid=station_data.station_uuid,
                    minutes_to_metro=station_data.minutes_to_metro,
                    transport=station_data.transport,
                )
            else:
                home.add_metro_station(
                    station_uuid=station_data.station_uuid,
                    minutes_to_metro=station_data.minutes_to_metro,
                    transport=station_data.transport,
                )

    # ==== Вспомогательные методы ====

    async def _get_location_path(self, location_uuid: UUID) -> list[UUID]:
        async with self._locations_repo() as repo:
            locations = await repo.get_location_path(location_uuid=location_uuid)
            return [loc.uuid for loc in locations]
