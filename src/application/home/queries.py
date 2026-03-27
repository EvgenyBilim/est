from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, Query

from src.enums import (
    BathroomTypeEnum,
    HousingClassEnum,
    ParkingTypeEnum,
    RoomTypeEnum,
    TrimTypeEnum,
    WallTypeEnum,
)


@dataclass
class HomeSearchFilter:
    # homes
    name: str | None = None
    developer: Annotated[list[UUID] | None, Query()] = None
    housing_class: Annotated[list[HousingClassEnum] | None, Query()] = None
    parking_type: Annotated[list[ParkingTypeEnum] | None, Query()] = None
    is_apartment: bool | None = None
    has_closed_territory: bool | None = None
    has_security: bool | None = None

    # home_info
    delivery_from: date | None = None
    delivery_to: date | None = None
    wall_type: Annotated[list[WallTypeEnum] | None, Query()] = None
    trim_type: Annotated[list[TrimTypeEnum] | None, Query()] = None
    bathroom_type: Annotated[list[BathroomTypeEnum] | None, Query()] = None
    roof_height_min: Decimal | None = None
    roof_height_max: Decimal | None = None
    floors_min: int | None = None
    floors_max: int | None = None
    payment_type: Annotated[list[str] | None, Query()] = None
    agreement_type: Annotated[list[str] | None, Query()] = None

    # plans
    rooms: Annotated[list[RoomTypeEnum] | None, Query()] = None
    price_from: int | None = None
    price_to: int | None = None
    square_total_from: Decimal | None = None
    square_total_to: Decimal | None = None
    square_kitchen_from: Decimal | None = None
    square_kitchen_to: Decimal | None = None

    # relations
    location: Annotated[list[UUID] | None, Query()] = None
    metro: Annotated[list[UUID] | None, Query()] = None

    # pagination
    limit: int = field(default=20)
    offset: int = field(default=0)

    def __post_init__(self):
        if self.payment_type:
            self.payment_type = [v.lower() for v in self.payment_type]
        if self.agreement_type:
            self.agreement_type = [v.lower() for v in self.agreement_type]


@dataclass
class HomeTagFilter:
    tag: Annotated[str, Query(min_length=2)]
    location: Annotated[list[UUID] | None, Query()] = None
    limit: int = 10

    def __post_init__(self):
        self.tag = self.tag.lower().strip()


def validate_filters(filters: HomeSearchFilter = Depends()) -> HomeSearchFilter:
    ranges = [
        ("delivery_from", "delivery_to"),
        ("roof_height_min", "roof_height_max"),
        ("floors_min", "floors_max"),
        ("price_from", "price_to"),
        ("square_total_from", "square_total_to"),
        ("square_kitchen_from", "square_kitchen_to"),
    ]
    for from_field, to_field in ranges:
        from_val = getattr(filters, from_field)
        to_val = getattr(filters, to_field)
        if from_val is not None and to_val is not None and from_val > to_val:
            raise HTTPException(
                status_code=422,
                detail=f"{from_field} cannot be greater than {to_field}",
            )
    return filters
