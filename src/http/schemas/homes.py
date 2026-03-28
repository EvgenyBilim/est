from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any, Self
from uuid import UUID

from pydantic import BaseModel, Field

from src.application.home.commands import (
    BlockCreateData,
    GalleryImageCreateData,
    HomeCreateCommand,
    MetroStationCreateData,
    PlanCreateData,
)
from src.enums import (
    BathroomTypeEnum,
    GalleryImageTypeEnum,
    HousingClassEnum,
    LocationTypeEnum,
    ParkingTypeEnum,
    RoomTypeEnum,
    TransportTypeEnum,
    TrimTypeEnum,
    WallTypeEnum,
)


class HomeMetroStationCreateSchema(BaseModel):
    station_uuid: UUID
    minutes_to_metro: int
    transport: TransportTypeEnum

    def to_command(self) -> MetroStationCreateData:
        return MetroStationCreateData(
            station_uuid=self.station_uuid,
            minutes_to_metro=self.minutes_to_metro,
            transport=self.transport,
        )


class GalleryImageCreateSchema(BaseModel):
    image_type: GalleryImageTypeEnum
    image_path: str
    sort_order: int | None = Field(default=None, gt=0)

    def to_command(self) -> GalleryImageCreateData:
        return GalleryImageCreateData(
            image_type=self.image_type,
            image_path=self.image_path,
            sort_order=self.sort_order,
        )


class PlanCreateSchema(BaseModel):
    rooms: RoomTypeEnum
    agreement_uuid: UUID | None = None
    square_total: Decimal = Field(gt=0)
    square_kitchen: Decimal = Field(gt=0)
    trim: TrimTypeEnum
    bathroom_type: BathroomTypeEnum
    roof_height: Decimal = Field(gt=0)
    price_base: int = Field(gt=0)
    price_discount: int | None = Field(default=None, ge=0)
    floor: int | None = Field(default=None, ge=1)
    img_path: str | None = None

    def to_command(self) -> PlanCreateData:
        return PlanCreateData(
            rooms=self.rooms,
            agreement_uuid=self.agreement_uuid,
            square_total=self.square_total,
            square_kitchen=self.square_kitchen,
            trim=self.trim,
            bathroom_type=self.bathroom_type,
            roof_height=self.roof_height,
            price_base=self.price_base,
            price_discount=self.price_discount,
            floor=self.floor,
            img_path=self.img_path,
        )


class BlockCreateSchema(BaseModel):
    name: str
    address: str | None = None
    floors: int = Field(gt=1)
    wall_type: WallTypeEnum
    delivery_date: date
    plans: list[PlanCreateSchema] = Field(default_factory=list)

    def to_command(self) -> BlockCreateData:
        return BlockCreateData(
            name=self.name,
            address=self.address,
            floors=self.floors,
            wall_type=self.wall_type,
            delivery_date=self.delivery_date,
            plans=[p.to_command() for p in self.plans],
        )


class HomeCreateSchema(BaseModel):
    name: str
    alias: str
    developer_uuid: UUID
    location_uuid: UUID
    coordinates: list[Decimal] = Field(min_length=2, max_length=2)
    description: str | None = Field(default=None, max_length=5000)
    housing_class: HousingClassEnum
    parking_types: list[ParkingTypeEnum]
    is_apartment: bool = False
    has_closed_territory: bool = False
    has_security: bool = False
    tags: list[str] = Field(default_factory=list)
    sort_order: int | None = Field(default=None, ge=0)
    blocks: list[BlockCreateSchema] = Field(default_factory=list)
    gallery: list[GalleryImageCreateSchema] = Field(default_factory=list)
    metro_stations: list[HomeMetroStationCreateSchema] = Field(default_factory=list)
    payment_type_uuids: list[UUID] = Field(default_factory=list)

    def to_command(self) -> HomeCreateCommand:
        return HomeCreateCommand(
            name=self.name,
            alias=self.alias,
            developer_uuid=self.developer_uuid,
            location_uuid=self.location_uuid,
            coordinates=self.coordinates,
            description=self.description,
            housing_class=self.housing_class,
            parking_types=self.parking_types,
            is_apartment=self.is_apartment,
            has_closed_territory=self.has_closed_territory,
            has_security=self.has_security,
            tags=self.tags,
            sort_order=self.sort_order,
            blocks=[b.to_command() for b in self.blocks],
            gallery=[g.to_command() for g in self.gallery],
            metro_stations=[m.to_command() for m in self.metro_stations],
            payment_type_uuids=self.payment_type_uuids,
        )


# Response-модели


class MetroStationResponse(BaseModel):
    station_uuid: UUID
    station_name: str
    line_color: str
    minutes_to_metro: int
    transport: TransportTypeEnum


class LocationResponse(BaseModel):
    uuid: UUID
    name: str
    alias: str
    type: LocationTypeEnum
    child: LocationResponse | None


class RoomsStats(BaseModel):
    count: int
    min_price: int
    max_price: int
    min_square: Decimal
    max_square: Decimal


class StatsByRoomsResponse(BaseModel):
    count: int
    min_price: int
    max_price: int
    min_square: Decimal
    max_square: Decimal
    rooms_stats: dict[RoomTypeEnum, RoomsStats]

    @classmethod
    def from_row(cls, row: dict[str, Any]) -> Self:
        rooms_stats = row["rooms_stats"]

        return cls(
            count=row["count"],
            min_price=row["min_price"],
            max_price=row["max_price"],
            min_square=row["min_square"],
            max_square=row["max_square"],
            rooms_stats={
                room_type: RoomsStats(
                    count=stats["count"],
                    min_price=stats["min_price"],
                    max_price=stats["max_price"],
                    min_square=stats["min_square"],
                    max_square=stats["max_square"],
                )
                for room_type, stats in rooms_stats.items()
            },
        )


class HomeRoofHeightResponse(BaseModel):
    min: Decimal | None
    max: Decimal | None


class HomeFloorsResponse(BaseModel):
    min: int | None
    max: int | None


class HomeDeliveryResponse(BaseModel):
    min: date | None
    max: date | None


class HomeDeveloperResponse(BaseModel):
    uuid: UUID
    name: str


class HomeGalleryResponse(BaseModel):
    preview: list[str] | None
    full: list[str] | None


class BlockResponse(BaseModel):
    uuid: UUID
    name: str
    address: str | None
    floors: int
    wall_type: WallTypeEnum
    delivery_date: date


class PlanResponse(BaseModel):
    # todo: тут что-то нужно придумать, чтобы переходить по uuid на страницу планировки
    block_uuid: UUID
    rooms: RoomTypeEnum
    square_total: Decimal
    square_kitchen: Decimal
    trim: TrimTypeEnum
    bathroom_type: BathroomTypeEnum
    roof_height: Decimal
    price_base: int
    price_discount: int | None
    floors: list[int] | None
    floors_by_block: int
    block_name: str
    agreement: str | None
    img_path: str | None


class HomeResponse(BaseModel):
    uuid: UUID
    name: str
    alias: str
    description: str | None
    housing_class: HousingClassEnum
    parking_types: list[ParkingTypeEnum]
    is_apartment: bool
    has_closed_territory: bool
    has_security: bool
    coordinates: list[Decimal]

    developer: HomeDeveloperResponse

    payment_types: list[str] | None
    agreement_types: list[str] | None
    wall_types: list[WallTypeEnum] | None
    trim_types: list[TrimTypeEnum] | None
    blocks_count: int
    delivery: HomeDeliveryResponse
    floors: HomeFloorsResponse
    roof_height: HomeRoofHeightResponse
    stats_by_rooms: StatsByRoomsResponse | None
    locations: LocationResponse | None
    metro_stations: list[MetroStationResponse] | None

    blocks: list[BlockResponse]
    plans: list[PlanResponse]
    gallery: HomeGalleryResponse | None


class HomePreviewResponse(BaseModel):
    uuid: UUID
    name: str
    alias: str
    coordinates: list[Decimal]

    developer: HomeDeveloperResponse
    delivery: HomeDeliveryResponse
    stats_by_rooms: StatsByRoomsResponse | None
    metro_stations: list[MetroStationResponse] | None
    gallery: HomeGalleryResponse | None


class HomeNameResponse(BaseModel):
    uuid: UUID
    name: str
