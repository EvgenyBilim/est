from datetime import datetime

from pydantic import UUID4, BaseModel


# class HomesFilter(BaseModel):
#     names: list[str] | None = None
#     developers: list[UUID4] | None = None
#     locations: list[str] | None = None
#     wall_types: list[WallTypeEnum] | None = None
#     delivery_from: date | None = None
#     delivery_to: date | None = None
#     rooms: list[RoomTypeEnum] | None = None
#     square_from: int = Field(None, ge=0)
#     square_to: int = Field(None, ge=0)
#     kitchen_from: int = Field(None, ge=0)
#     kitchen_to: int = Field(None, ge=0)
#     trims: list[TrimTypeEnum] | None = None
#     roof_from: float = Field(None, ge=0)
#     roof_to: float = Field(None, ge=0)
#     price_from: int = Field(None, ge=0)
#     price_to: int = Field(None, ge=0)
#     floor_from: int = Field(None, ge=0)
#     floor_to: int = Field(None, ge=0)
#     agreements: list[UUID4] | None = None
#     payments: list[UUID4] | None = None
#     metro: list[UUID4] | None = None
