from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from uuid import UUID

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

# Данные для синхронизации

@dataclass(frozen=True)
class PlanSyncData:
    rooms: RoomTypeEnum
    square_total: Decimal
    square_kitchen: Decimal
    trim: TrimTypeEnum
    bathroom_type: BathroomTypeEnum
    price_base: int
    roof_height: Decimal
    agreement_uuid: UUID | None = None
    price_discount: int | None = None
    floor: int | None = None
    img_path: str | None = None
    uuid: UUID | None = None  # None = создать новую


@dataclass(frozen=True)
class BlockSyncData:
    name: str
    address: str
    floors: int
    wall_type: WallTypeEnum
    delivery_date: date
    plans: list[PlanSyncData] = field(default_factory=list)
    uuid: UUID | None = None  # None = создать новый


@dataclass(frozen=True)
class MetroStationSyncData:
    station_uuid: UUID
    minutes_to_metro: int
    transport: TransportTypeEnum
    uuid: UUID | None = None  # None = создать новую


@dataclass(frozen=True)
class GalleryImageSyncData:
    image_type: GalleryImageTypeEnum
    image_path: str
    sort_order: int | None
    uuid: UUID | None = None  # None = создать новую


@dataclass(frozen=True)
class HomeSyncData:
    name: str
    alias: str
    developer_uuid: UUID
    location_uuid: UUID
    housing_class: HousingClassEnum
    parking_types: list[ParkingTypeEnum]
    is_apartment: bool = False
    has_closed_territory: bool = False
    has_security: bool = False
    sort_order: int | None = None
    description: str | None = None

    payment_type_uuids: list[UUID] = field(default_factory=list)
    coordinates: list[Decimal] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    blocks: list[BlockSyncData] = field(default_factory=list)
    gallery: list[GalleryImageSyncData] = field(default_factory=list)
    metro_stations: list[MetroStationSyncData] = field(default_factory=list)


# Данные для создания/добавления

@dataclass(frozen=True)
class MetroStationCreateData:
    station_uuid: UUID
    minutes_to_metro: int
    transport: TransportTypeEnum


@dataclass(frozen=True)
class GalleryImageCreateData:
    image_type: GalleryImageTypeEnum
    image_path: str
    sort_order: int | None


@dataclass(frozen=True)
class PlanCreateData:
    rooms: RoomTypeEnum
    square_total: Decimal
    square_kitchen: Decimal
    trim: TrimTypeEnum
    bathroom_type: BathroomTypeEnum
    price_base: int
    roof_height: Decimal
    agreement_uuid: UUID | None = None
    price_discount: int | None = None
    floor: int | None = None
    img_path: str | None = None


@dataclass(frozen=True)
class BlockCreateData:
    name: str
    address: str | None
    floors: int
    wall_type: WallTypeEnum
    delivery_date: date
    plans: list[PlanCreateData] = field(default_factory=list)


# Команды

@dataclass(frozen=True)
class HomeCreateCommand:
    name: str
    alias: str
    developer_uuid: UUID
    location_uuid: UUID
    housing_class: HousingClassEnum
    parking_types: list[ParkingTypeEnum]
    is_apartment: bool = False
    has_closed_territory: bool = False
    has_security: bool = False
    sort_order: int | None = None
    description: str | None = None

    payment_type_uuids: list[UUID] = field(default_factory=list)
    coordinates: list[Decimal] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    blocks: list[BlockCreateData] = field(default_factory=list)
    gallery: list[GalleryImageCreateData] = field(default_factory=list)
    metro_stations: list[MetroStationCreateData] = field(default_factory=list)


@dataclass(frozen=True)
class AddBlocksCommand:
    home_uuid: UUID
    blocks: list[BlockCreateData]


@dataclass(frozen=True)
class AddPlansCommand:
    home_uuid: UUID
    block_uuid: UUID
    plans: list[PlanCreateData]


@dataclass(frozen=True)
class SyncHomeCommand:
    home_uuid: UUID
    data: HomeSyncData
