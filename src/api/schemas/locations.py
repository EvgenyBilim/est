from datetime import datetime
from uuid import UUID
from pydantic import BaseModel

from src.enums import LocationTypeEnum


class LocationCreateSchema(BaseModel):
    name: str
    alias: str
    type: LocationTypeEnum
    locations: list["LocationCreateSchema"] | None = None


# Response-модели

class LocationResponse(BaseModel):
    uuid: UUID
    parent_uuid: UUID | None
    name: str
    alias: str
    type: LocationTypeEnum
    created_at: datetime
    updated_at: datetime | None
