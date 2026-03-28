from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class MetroStationCreateSchema(BaseModel):
    name: str


class MetroLineCreateSchema(BaseModel):
    name: str
    color: str
    stations: list[MetroStationCreateSchema] = Field(default_factory=list)


class MetropolitanCreateSchema(BaseModel):
    name: str
    location_uuid: UUID
    lines: list[MetroLineCreateSchema] = Field(default_factory=list)


# Response-модели


class MetroStationModel(BaseModel):
    uuid: UUID
    name: str
    metro_line_uuid: UUID
    created_at: datetime
    updated_at: datetime | None


class MetroStationInfoModel(BaseModel):
    uuid: UUID
    name: str
    color: str


class MetroLineModel(BaseModel):
    uuid: UUID
    metropolitan_uuid: UUID
    name: str
    color: str
    created_at: datetime
    updated_at: datetime | None


class MetropolitanModel(BaseModel):
    uuid: UUID
    name: str
    location_uuid: UUID
    created_at: datetime
    updated_at: datetime | None
