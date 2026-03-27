from sqlalchemy import Column, Enum, ForeignKey, Integer, Text, text
from sqlalchemy.dialects.postgresql import UUID

from src.enums import GalleryImageTypeEnum
from src.infrastructure.models.base import BaseEstModel


class HomeGallery(BaseEstModel):
    __tablename__ = "home_gallery"

    uuid = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    home_uuid = Column(UUID(as_uuid=True), ForeignKey('homes.uuid', ondelete='CASCADE'), index=True)
    image_type = Column(Enum(GalleryImageTypeEnum), index=True)
    image_path = Column(Text, nullable=False)
    sort_order = Column(Integer, nullable=True, index=True)
