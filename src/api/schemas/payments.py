from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class PaymentTypeCreateSchema(BaseModel):
    name: str
    location_uuid: UUID


# Response-модели

class PaymentTypeModel(BaseModel):
    uuid: UUID
    name: str
    location_uuid: UUID
    created_at: datetime
    updated_at: datetime | None
