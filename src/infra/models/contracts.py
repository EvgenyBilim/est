from sqlalchemy import Column, ForeignKey, String, text
from sqlalchemy.dialects.postgresql import UUID

from src.infra.models.base import BaseEstModel


class AgreementType(BaseEstModel):
    __tablename__ = "agreement_types"

    uuid = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    name = Column(String(255), nullable=False, index=True)
    location_uuid = Column(UUID(as_uuid=True), ForeignKey("locations.uuid", ondelete="CASCADE"), index=True)


class PaymentType(BaseEstModel):
    __tablename__ = "payment_types"

    uuid = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    name = Column(String(255), nullable=False, index=True)
    location_uuid = Column(UUID(as_uuid=True), ForeignKey("locations.uuid", ondelete="CASCADE"), index=True)
