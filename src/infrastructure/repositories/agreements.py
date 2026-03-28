from typing import cast
from uuid import UUID

from sqlalchemy import distinct, select
from sqlalchemy.ext.asyncio import AsyncConnection

from src.api.schemas.agreements import AgreementTypeModel
from src.infrastructure.models.contracts import AgreementType
from src.infrastructure.repositories.base import BaseDBEntity


class Create(BaseDBEntity):
    async def __call__(self, agreements: list[dict]) -> None:
        await self.batch_insert(AgreementType, agreements)


class Get(BaseDBEntity):
    async def __call__(self) -> list[AgreementTypeModel]:
        query = select(AgreementType)
        rows = await self._connection.execute(query)
        return [AgreementTypeModel(**row) for row in rows.mappings()]


class GetByCountry(BaseDBEntity):
    async def __call__(self, location_uuid: UUID) -> list[AgreementTypeModel]:
        query = select(AgreementType).where(AgreementType.location_uuid == location_uuid)
        rows = await self._connection.execute(query)
        return [AgreementTypeModel(**row) for row in rows.mappings()]


class GetCountriesByAgreementTypes(BaseDBEntity):
    async def __call__(self, agreement_uuids: list[UUID]) -> list[UUID]:
        if not agreement_uuids:
            return []

        query = select(distinct(AgreementType.location_uuid)).where(AgreementType.uuid.in_(agreement_uuids))

        result = await self._connection.execute(query)
        return [cast(UUID, uuid) for uuid in result.scalars().all() if uuid is not None]


class GetByUUIDs(BaseDBEntity):
    async def __call__(self, agreement_uuids: list[UUID]) -> list[AgreementTypeModel]:
        if not agreement_uuids:
            return []
        query = select(AgreementType).where(AgreementType.uuid.in_(agreement_uuids))
        rows = await self._connection.execute(query)
        return [AgreementTypeModel(**row) for row in rows.mappings()]


class AgreementsRepository:
    def __init__(self, connection: AsyncConnection):
        self.create = Create(connection=connection)
        self.get = Get(connection=connection)
        self.get_by_country = GetByCountry(connection=connection)
        self.get_countries_by_agreement_types = GetCountriesByAgreementTypes(connection=connection)
        self.get_by_uuids = GetByUUIDs(connection=connection)
