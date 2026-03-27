from uuid import UUID

from sqlalchemy import distinct, select
from sqlalchemy.ext.asyncio import AsyncConnection

from src.api.schemas.payments import PaymentTypeModel
from src.infrastructure.models.contracts import PaymentType
from src.infrastructure.repositories.base import BaseDBEntity


class Create(BaseDBEntity):
    async def __call__(self, payments: list[dict]) -> None:
        await self.batch_insert(PaymentType, payments)


class Get(BaseDBEntity):
    async def __call__(self) -> list[PaymentTypeModel]:
        query = select(PaymentType)
        rows = await self._connection.execute(query)
        return [PaymentTypeModel(**row) for row in rows.mappings()]


class GetByCountry(BaseDBEntity):
    async def __call__(self, location_uuid: UUID) -> list[PaymentTypeModel]:
        query = select(PaymentType).where(PaymentType.location_uuid == location_uuid)
        rows = await self._connection.execute(query)
        return [PaymentTypeModel(**row) for row in rows.mappings()]


class GetByUUIDs(BaseDBEntity):
    async def __call__(self, payment_uuids: list[UUID]) -> list[PaymentTypeModel]:
        query = select(PaymentType).where(PaymentType.uuid.in_(payment_uuids))
        rows = await self._connection.execute(query)
        return [PaymentTypeModel(**row) for row in rows.mappings()]


class GetCountriesByPaymentTypes(BaseDBEntity):
    async def __call__(self, payment_uuids: list[UUID]) -> list[UUID]:
        if not payment_uuids:
            return []

        query = (
            select(distinct(PaymentType.location_uuid))
            .where(PaymentType.uuid.in_(payment_uuids))
        )

        result = await self._connection.execute(query)
        return list(result.scalars().all())


class PaymentsRepository:
    def __init__(self, connection: AsyncConnection):
        self.create = Create(connection=connection)
        self.get = Get(connection=connection)
        self.get_by_country = GetByCountry(connection=connection)
        self.get_by_uuids = GetByUUIDs(connection=connection)
        self.get_countries_by_payment_types = GetCountriesByPaymentTypes(connection=connection)
