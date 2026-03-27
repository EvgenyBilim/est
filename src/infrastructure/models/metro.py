from sqlalchemy import Column, ForeignKey, String, text
from sqlalchemy.dialects.postgresql import UUID

from src.infrastructure.models.base import BaseEstModel


class Metropolitan(BaseEstModel):
    __tablename__ = "metropolitans"

    uuid = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    name = Column(String, nullable=False)
    location_uuid = Column(UUID(as_uuid=True), ForeignKey('locations.uuid', ondelete='CASCADE'), index=True)


class MetroLine(BaseEstModel):
    __tablename__ = 'metro_lines'

    uuid = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    metropolitan_uuid = Column(UUID(as_uuid=True), ForeignKey('metropolitans.uuid', ondelete='CASCADE'), index=True)
    name = Column(String, nullable=False)
    color = Column(String, nullable=False)


class MetroStation(BaseEstModel):
    __tablename__ = "metro_stations"

    uuid = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    name = Column(String, nullable=False, index=True)
    metro_line_uuid = Column(UUID(as_uuid=True), ForeignKey('metro_lines.uuid', ondelete='CASCADE'), index=True)
