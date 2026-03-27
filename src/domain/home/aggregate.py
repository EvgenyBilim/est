from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Self
from uuid import UUID, uuid4

from src.domain.home.entities import Block, GalleryImage, MetroStation, Plan
from src.domain.home.events import HomeCreated, HomeStructureChanged
from src.enums import (
    BathroomTypeEnum,
    GalleryImageTypeEnum,
    HousingClassEnum,
    ParkingTypeEnum,
    RoomTypeEnum,
    TransportTypeEnum,
    TrimTypeEnum,
    WallTypeEnum,
)


@dataclass
class Home:
    uuid: UUID
    name: str
    alias: str
    developer_uuid: UUID
    description: str | None
    housing_class: HousingClassEnum
    parking_types: list[ParkingTypeEnum]
    is_apartment: bool | None
    has_closed_territory: bool | None
    has_security: bool | None
    coordinates: list[Decimal] | None
    tags: list[str]
    sort_order: int | None

    location_uuids: list[UUID]
    payment_type_uuids: list[UUID]
    blocks: list[Block] = field(default_factory=list)
    gallery: list[GalleryImage] = field(default_factory=list)
    metro_stations: list[MetroStation] = field(default_factory=list)

    _events: list = field(default_factory=list, repr=False)

    @classmethod
    def create(
        cls,
        name: str,
        alias: str,
        developer_uuid: UUID,
        location_uuids: list[UUID],
        coordinates: list[Decimal] | None,
        description: str | None,
        housing_class: HousingClassEnum,
        parking_types: list[ParkingTypeEnum],
        payment_type_uuids: list[UUID],
        is_apartment: bool | None,
        has_closed_territory: bool | None,
        has_security: bool | None,
        tags: list[str] | None,
        sort_order: int | None,
    ) -> Self:
        home = cls(
            uuid=uuid4(),
            name=name,
            alias=alias,
            developer_uuid=developer_uuid,
            location_uuids=location_uuids,
            coordinates=coordinates,
            description=description,
            housing_class=housing_class,
            parking_types=parking_types,
            payment_type_uuids=payment_type_uuids,
            is_apartment=is_apartment,
            has_closed_territory=has_closed_territory,
            has_security=has_security,
            tags=tags,
            sort_order=sort_order,
        )
        home._events.append(HomeCreated(home_uuid=home.uuid))
        return home

    def update_attributes(
        self,
        name: str,
        alias: str,
        developer_uuid: UUID,
        location_uuids: list[UUID],
        coordinates: list[Decimal],
        description: str | None,
        housing_class: HousingClassEnum,
        parking_types: list[ParkingTypeEnum],
        payment_type_uuids: list[UUID],
        is_apartment: bool | None,
        has_closed_territory: bool | None,
        has_security: bool | None,
        tags: list[str] | None,
        sort_order: int | None,
    ) -> None:
        self.name = name
        self.alias = alias
        self.developer_uuid = developer_uuid
        self.location_uuids = location_uuids
        self.coordinates = coordinates
        self.description = description
        self.housing_class = housing_class
        self.parking_types = parking_types
        self.payment_type_uuids = payment_type_uuids
        self.is_apartment = is_apartment
        self.has_closed_territory = has_closed_territory
        self.has_security = has_security
        self.tags = tags
        self.sort_order = sort_order

    # ==== Операции с корпусами ====

    def add_block(self, name: str, address: str, floors: int, wall_type: WallTypeEnum, delivery_date: date) -> Block:
        block = Block(
            uuid=uuid4(),
            home_uuid=self.uuid,
            name=name,
            address=address,
            floors=floors,
            wall_type=wall_type,
            delivery_date=delivery_date,
        )
        self.blocks.append(block)
        return block

    def update_block(
        self,
        block_uuid: UUID,
        name: str,
        address: str | None,
        floors: int,
        wall_type: WallTypeEnum,
        delivery_date: date
    ) -> Block:
        block = self._get_block(block_uuid)
        block.name = name
        block.address = address
        block.floors = floors
        block.wall_type = wall_type
        block.delivery_date = delivery_date
        return block

    def remove_blocks_except(self, keep_uuids: set[UUID]) -> None:
        self.blocks = [b for b in self.blocks if b.uuid in keep_uuids]

    # ==== Операции с планировками ====

    def add_plan_to_block(
        self,
        block_uuid: UUID,
        rooms: RoomTypeEnum,
        agreement_uuid: UUID | None,
        square_total: Decimal,
        square_kitchen: Decimal,
        trim: TrimTypeEnum,
        bathroom_type: BathroomTypeEnum,
        roof_height: Decimal,
        price_base: int,
        price_discount: int | None,
        floor: int | None,
        img_path: str | None,
    ) -> Plan:
        block = self._get_block(block_uuid)

        new_plan = Plan(
            uuid=uuid4(),
            block_uuid=block_uuid,
            rooms=rooms,
            agreement_uuid=agreement_uuid,
            square_total=square_total,
            square_kitchen=square_kitchen,
            trim=trim,
            bathroom_type=bathroom_type,
            roof_height=roof_height,
            price_base=price_base,
            price_discount=price_discount,
            floor=floor,
            img_path=img_path,
        )
        block.plans.append(new_plan)
        return new_plan

    def update_plan(
        self,
        block_uuid: UUID,
        plan_uuid: UUID,
        rooms: RoomTypeEnum,
        square_total: Decimal,
        square_kitchen: Decimal,
        trim: TrimTypeEnum,
        bathroom_type: BathroomTypeEnum,
        price_base: int,
        agreement_uuid: UUID | None,
        roof_height: Decimal,
        price_discount: int | None,
        floor: int | None,
        img_path: str | None,
    ) -> Plan:
        block = self._get_block(block_uuid)

        plan = self._get_plan_in_block(block, plan_uuid)
        plan.rooms = rooms
        plan.agreement_uuid = agreement_uuid
        plan.square_total = square_total
        plan.square_kitchen = square_kitchen
        plan.trim = trim
        plan.bathroom_type = bathroom_type
        plan.roof_height = roof_height
        plan.price_base = price_base
        plan.price_discount = price_discount
        plan.floor = floor
        plan.img_path = img_path
        return plan

    def remove_plans_from_block_except(self, block_uuid: UUID, keep_uuids: set[UUID]) -> None:
        block = self._get_block(block_uuid)
        block.plans = [p for p in block.plans if p.uuid in keep_uuids]

    # ==== Операции с галереей ====

    def add_gallery_image(self, image_type: GalleryImageTypeEnum, image_path: str, sort_order: int | None) -> None:
        gallery_image = GalleryImage(
            uuid=uuid4(),
            home_uuid=self.uuid,
            image_type=image_type,
            image_path=image_path,
            sort_order=sort_order
        )
        self.gallery.append(gallery_image)

    def update_gallery_image(
        self,
        image_uuid: UUID,
        image_type: GalleryImageTypeEnum,
        image_path: str,
        sort_order: int | None,
    ) -> GalleryImage:
        image = self._get_gallery_image(image_uuid)
        image.image_type = image_type
        image.image_path = image_path
        image.sort_order = sort_order
        return image

    def remove_gallery_except(self, keep_uuids: set[UUID]) -> None:
        self.gallery = [g for g in self.gallery if g.uuid in keep_uuids]

    # ==== Операции с метро ====

    def add_metro_station(
        self,
        station_uuid: UUID,
        minutes_to_metro: int,
        transport: TransportTypeEnum,
    ) -> MetroStation:
        metro_station = MetroStation(
            uuid=uuid4(),
            home_uuid=self.uuid,
            station_uuid=station_uuid,
            minutes_to_metro=minutes_to_metro,
            transport=transport,
        )
        self.metro_stations.append(metro_station)
        return metro_station

    def update_metro_station(
        self,
        metro_uuid: UUID,
        station_uuid: UUID,
        minutes_to_metro: int,
        transport: TransportTypeEnum,
    ) -> MetroStation:
        station = self._get_metro_station(metro_uuid)
        station.station_uuid = station_uuid
        station.minutes_to_metro = minutes_to_metro
        station.transport = transport
        return station

    def remove_metro_except(self, keep_uuids: set[UUID]) -> None:
        self.metro_stations = [m for m in self.metro_stations if m.uuid in keep_uuids]

    # ==== Приватные методы ====

    def _get_block(self, block_uuid: UUID) -> Block:
        for block in self.blocks:
            if block.uuid == block_uuid:
                return block
        raise ValueError(f"Блок {block_uuid} не найден в доме {self.uuid}")

    def _get_plan_in_block(self, block: Block, plan_uuid: UUID) -> Plan:
        for plan in block.plans:
            if plan.uuid == plan_uuid:
                return plan
        raise ValueError(f"Планировка {plan_uuid} не найдена в корпусе {block.uuid}")

    def _get_gallery_image(self, image_uuid: UUID) -> GalleryImage:
        for image in self.gallery:
            if image.uuid == image_uuid:
                return image
        raise ValueError(f"Изображение {image_uuid} не найдено")

    def _get_metro_station(self, metro_uuid: UUID) -> MetroStation:
        for station in self.metro_stations:
            if station.uuid == metro_uuid:
                return station
        raise ValueError(f"Станция метро {metro_uuid} не найдена")

    # ==== События ====

    def mark_structure_changed(self) -> None:
        self._events.append(HomeStructureChanged(home_uuid=self.uuid))

    def collect_events(self) -> list:
        events = self._events.copy()
        self._events.clear()
        return events
