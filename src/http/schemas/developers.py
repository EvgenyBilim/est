from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class DeveloperCreateSchema(BaseModel):
    name: str
    logo: str
    description: str


# Response-модели


class DeveloperModel(BaseModel):
    uuid: UUID
    name: str
    logo: str
    description: str
    created_at: datetime
    updated_at: datetime | None
