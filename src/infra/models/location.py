from sqlalchemy import Column, Enum, ForeignKey, String, text
from sqlalchemy.dialects.postgresql import UUID

from src.enums import LocationTypeEnum
from src.infra.models.base import BaseEstModel


class Location(BaseEstModel):
    __tablename__ = "locations"

    uuid = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    parent_uuid = Column(UUID(as_uuid=True), ForeignKey("locations.uuid"), index=True)
    name = Column(String, nullable=False)
    alias = Column(String, nullable=False)
    type = Column(Enum(LocationTypeEnum), nullable=False, index=True)
