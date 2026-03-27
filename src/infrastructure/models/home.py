from sqlalchemy import (
    DECIMAL,
    Boolean,
    Column,
    Date,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    PrimaryKeyConstraint,
    String,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID

from src.enums import (
    BathroomTypeEnum,
    HousingClassEnum,
    ParkingTypeEnum,
    RoomTypeEnum,
    TransportTypeEnum,
    TrimTypeEnum,
    WallTypeEnum,
)
from src.infrastructure.models.base import BaseEstModel


class Home(BaseEstModel):
    __tablename__ = "homes"

    uuid = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    name = Column(String, nullable=False)
    alias = Column(String, nullable=False)
    developer_uuid = Column(UUID(as_uuid=True), ForeignKey("developers.uuid", ondelete="CASCADE"), index=True)
    description = Column(Text, nullable=True)
    housing_class = Column(Enum(HousingClassEnum), nullable=False, index=True)
    parking_types = Column(ARRAY(Enum(ParkingTypeEnum)), nullable=False)
    is_apartment = Column(Boolean, nullable=False, default=False)
    has_closed_territory = Column(Boolean, nullable=False, default=False)
    has_security = Column(Boolean, nullable=False, default=False)
    coordinates = Column(JSONB, nullable=True, server_default=text("'[]'::jsonb"))
    sort_order = Column(Integer, nullable=True, index=True)

    __table_args__ = (
        Index("ix_homes_parking_types", parking_types, postgresql_using="gin"),
    )


class HomeInfo(BaseEstModel):
    __tablename__ = "home_info"

    uuid = Column(UUID(as_uuid=True), ForeignKey("homes.uuid", ondelete="CASCADE"), primary_key=True)
    delivery_from = Column(Date, nullable=True, index=True)
    delivery_to = Column(Date, nullable=True, index=True)
    floors_min = Column(Integer, nullable=True, index=True)
    floors_max = Column(Integer, nullable=True, index=True)
    roof_height_min = Column(DECIMAL, nullable=True, index=True)
    roof_height_max = Column(DECIMAL, nullable=True, index=True)
    wall_types = Column(ARRAY(Enum(WallTypeEnum)), nullable=True)
    trim_types = Column(ARRAY(Enum(TrimTypeEnum)), nullable=True)
    bathroom_types = Column(ARRAY(Enum(BathroomTypeEnum)), nullable=True)
    agreement_types = Column(ARRAY(String), nullable=True)
    payment_types = Column(ARRAY(String), nullable=True)
    locations = Column(JSONB, nullable=True)
    metro_stations = Column(JSONB, nullable=True)
    plans_info = Column(JSONB, nullable=True)
    blocks_count = Column(Integer, nullable=False, default=0)

    __table_args__ = (
        Index("ix_homes_info_wall_types", wall_types, postgresql_using="gin"),
        Index("ix_homes_info_trim_types", trim_types, postgresql_using="gin"),
        Index("ix_homes_info_agreement_types", agreement_types, postgresql_using="gin"),
        Index("ix_homes_info_payment_types", payment_types, postgresql_using="gin"),
    )


class Block(BaseEstModel):
    __tablename__ = "blocks"

    uuid = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    name = Column(String, nullable=False)
    home_uuid = Column(UUID(as_uuid=True), ForeignKey("homes.uuid", ondelete="CASCADE"), index=True)
    address = Column(String, nullable=True)
    floors = Column(Integer, nullable=False)
    wall_type = Column(Enum(WallTypeEnum), nullable=False, index=True)
    delivery_date = Column(Date, nullable=False, index=True)


class Plan(BaseEstModel):
    __tablename__ = "plans"

    uuid = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    block_uuid = Column(UUID(as_uuid=True), ForeignKey("blocks.uuid", ondelete="CASCADE"), index=True)
    rooms = Column(Enum(RoomTypeEnum), nullable=False, index=True)
    agreement_uuid = Column(
        UUID(as_uuid=True), ForeignKey("agreement_types.uuid", ondelete="RESTRICT"), nullable=True
    )
    square_total = Column(Float, nullable=False, index=True)
    square_kitchen = Column(Float, nullable=False, index=True)
    trim = Column(Enum(TrimTypeEnum), nullable=False)
    bathroom_type = Column(Enum(BathroomTypeEnum), nullable=False)
    roof_height = Column(Float, nullable=False, index=True)
    price_base = Column(Integer, nullable=False, index=True)
    price_discount = Column(Integer, nullable=True, index=True)
    floor = Column(Integer, nullable=True, index=True)
    img_path = Column(String, nullable=True)


class HomeTag(BaseEstModel):
    __tablename__ = "home_tags"

    home_uuid = Column(UUID(as_uuid=True), ForeignKey("homes.uuid", ondelete="CASCADE"), nullable=False)
    tag = Column(Text, nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint("home_uuid", "tag", name="pk_home_tag"),
        Index("ix_home_tags_tag_trgm", "tag", postgresql_using="gin", postgresql_ops={"tag": "gin_trgm_ops"}),
        Index("ix_home_tags_home_uuid", "home_uuid"),
    )


class HomeLocation(BaseEstModel):
    __tablename__ = "home_locations"

    home_uuid = Column(UUID(as_uuid=True), ForeignKey("homes.uuid", ondelete="CASCADE"), index=True)
    location_uuid = Column(UUID(as_uuid=True), ForeignKey("locations.uuid", ondelete="RESTRICT"), index=True)

    __table_args__ = (
        PrimaryKeyConstraint("location_uuid", "home_uuid", name="pk_location_home"),
    )


class HomeMetroStation(BaseEstModel):
    __tablename__ = "home_metro_stations"

    uuid = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    home_uuid = Column(UUID(as_uuid=True), ForeignKey("homes.uuid", ondelete="CASCADE"), index=True)
    station_uuid = Column(UUID(as_uuid=True), ForeignKey("metro_stations.uuid", ondelete="CASCADE"), index=True)
    minutes_to_metro = Column(Integer, nullable=False)
    transport = Column(Enum(TransportTypeEnum), nullable=False)


class HomePaymentType(BaseEstModel):
    __tablename__ = "home_payment_types"

    home_uuid = Column(UUID(as_uuid=True), ForeignKey('homes.uuid', ondelete='CASCADE'), index=True)
    payment_type_uuid = Column(UUID(as_uuid=True), ForeignKey('payment_types.uuid', ondelete='CASCADE'), index=True)

    __table_args__ = (
        PrimaryKeyConstraint('payment_type_uuid', 'home_uuid', name='pk_payment_type_home'),
    )
