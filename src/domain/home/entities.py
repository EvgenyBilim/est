from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from uuid import UUID

from src.enums import (
    BathroomTypeEnum,
    GalleryImageTypeEnum,
    RoomTypeEnum,
    TransportTypeEnum,
    TrimTypeEnum,
    WallTypeEnum,
)


@dataclass
class Plan:
    uuid: UUID
    block_uuid: UUID
    rooms: RoomTypeEnum
    agreement_uuid: UUID | None
    square_total: Decimal
    square_kitchen: Decimal
    trim: TrimTypeEnum
    bathroom_type: BathroomTypeEnum
    roof_height: Decimal | None
    price_base: int
    price_discount: int | None
    floor: int | None
    img_path: str | None


@dataclass
class Block:
    uuid: UUID
    home_uuid: UUID
    name: str
    address: str | None
    floors: int
    wall_type: WallTypeEnum
    delivery_date: date

    plans: list[Plan] = field(default_factory=list)


@dataclass
class GalleryImage:
    uuid: UUID
    home_uuid: UUID
    image_type: GalleryImageTypeEnum
    image_path: str
    sort_order: int | None


@dataclass
class MetroStation:
    uuid: UUID  # убрать из бд и сделать составной fk по home_uuid + station_uuid
    home_uuid: UUID
    station_uuid: UUID
    minutes_to_metro: int
    transport: TransportTypeEnum
