from uuid import UUID

from pydantic import BaseModel


class FilterLocation(BaseModel):
    uuid: UUID
    name: str


class FilterPaymentType(BaseModel):
    uuid: UUID
    name: str


class FilterAgreementType(BaseModel):
    uuid: UUID
    name: str


class FilterMetroStation(BaseModel):
    uuid: UUID
    name: str
    line_color: str


class HomeFilterOptionsResponse(BaseModel):
    locations: list[FilterLocation]
    payment_types: list[FilterPaymentType]
    agreement_types: list[FilterAgreementType]
    metro_stations: list[FilterMetroStation]
