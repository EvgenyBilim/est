from sqlalchemy import Column, String, Text, text
from sqlalchemy.dialects.postgresql import UUID

from src.infrastructure.models.base import BaseEstModel


class Developer(BaseEstModel):
    __tablename__ = "developers"

    uuid = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    name = Column(String, nullable=False)
    logo = Column(String, nullable=True)
    description = Column(Text, nullable=True)
