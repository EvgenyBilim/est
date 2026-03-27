from sqlalchemy import DECIMAL, Column, ForeignKey, Integer, String, text
from sqlalchemy.dialects.postgresql import UUID

from src.infrastructure.models.base import BaseEstModel


class Bank(BaseEstModel):
    __tablename__ = "banks"

    uuid = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    name = Column(String, nullable=False)
    logo = Column(String, nullable=True)
    description = Column(String, nullable=True)


class BankProgram(BaseEstModel):
    __tablename__ = "bank_programs"

    uuid = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    bank_uuid = Column(UUID(as_uuid=True), ForeignKey('banks.uuid', ondelete='CASCADE'))
    location_uuid = Column(UUID(as_uuid=True), ForeignKey('locations.uuid', ondelete='CASCADE'))
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    min_rate = Column(DECIMAL, nullable=False)
    contribution = Column(DECIMAL, nullable=False)
    terms = Column(Integer, nullable=False)


class BankProgramHome(BaseEstModel):
    __tablename__ = "bank_programs_homes"

    uuid = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    bank_program_uuid = Column(UUID(as_uuid=True), ForeignKey('bank_programs.uuid', ondelete='CASCADE'))
    home_uuid = Column(UUID(as_uuid=True), ForeignKey('homes.uuid', ondelete='CASCADE'))
