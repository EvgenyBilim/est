from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from src.enums import (
    BathroomTypeEnum,
    LocationTypeEnum,
    RoomTypeEnum,
    TransportTypeEnum,
    TrimTypeEnum,
    WallTypeEnum,
)


@dataclass
class LocationInfo:
    uuid: UUID
    name: str
    alias: str
    type: LocationTypeEnum
    child: LocationInfo | None


@dataclass
class RoomStats:
    count: int
    min_price: int
    max_price: int
    min_square: Decimal
    max_square: Decimal


@dataclass
class PlansInfo:
    count: int
    min_price: int
    max_price: int
    min_square: Decimal
    max_square: Decimal
    rooms_stats: dict[RoomTypeEnum, RoomStats]


@dataclass
class MetroStationInfo:
    station_uuid: UUID
    station_name: str
    line_color: str
    minutes_to_metro: int
    transport: TransportTypeEnum


@dataclass
class HomeInfo:
    uuid: UUID
    delivery_from: date | None
    delivery_to: date | None
    floors_min: int | None
    floors_max: int | None
    roof_height_min: Decimal | None
    roof_height_max: Decimal | None
    wall_types: list[WallTypeEnum]
    trim_types: list[TrimTypeEnum]
    bathroom_types: list[BathroomTypeEnum]
    agreement_types: list[str]
    payment_types: list[str]
    locations: LocationInfo | None
    metro_stations: list[MetroStationInfo]
    plans_info: PlansInfo | None
    blocks_count: int | None
