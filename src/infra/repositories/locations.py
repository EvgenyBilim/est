from uuid import UUID

from sqlalchemy import literal_column, select
from sqlalchemy.ext.asyncio import AsyncConnection

from src.enums import LocationTypeEnum
from src.http.schemas.locations import LocationResponse
from src.infra.models.location import Location
from src.infra.repositories.base import BaseDBEntity


class LocationsRepositoryMixin(BaseDBEntity):
    @property
    def table(self):
        return Location


class Create(LocationsRepositoryMixin):
    async def __call__(self, locations: list[dict]) -> None:
        await self.batch_insert(self.table, locations)


class Get(LocationsRepositoryMixin):
    async def __call__(self) -> list[LocationResponse]:
        query = select(self.table)
        rows = await self._connection.execute(query)
        return [LocationResponse(**row) for row in rows.mappings()]


class GetByType(LocationsRepositoryMixin):
    async def __call__(self, location_type: LocationTypeEnum) -> list[LocationResponse]:
        query = select(self.table).where(self.table.type == location_type)
        rows = await self._connection.execute(query)
        return [LocationResponse(**row) for row in rows.mappings()]


class GetLocationPath(LocationsRepositoryMixin):
    async def __call__(self, location_uuid: UUID) -> list[LocationResponse]:
        base = (
            select(
                self.table.uuid,
                self.table.parent_uuid,
                self.table.name,
                self.table.alias,
                self.table.type,
                self.table.created_at,
                self.table.updated_at,
                literal_column("0").label("depth"),
            )
            .where(self.table.uuid == location_uuid)
            .cte(name="parent_chain", recursive=True)
        )

        parent_chain = base.alias("pc")

        recursive = (
            select(
                self.table.uuid,
                self.table.parent_uuid,
                self.table.name,
                self.table.alias,
                self.table.type,
                self.table.created_at,
                self.table.updated_at,
                (parent_chain.c.depth + 1).label("depth"),
            )
            .select_from(self.table)
            .join(parent_chain, self.table.uuid == parent_chain.c.parent_uuid)
            .where(parent_chain.c.parent_uuid.isnot(None))
        )

        cte = base.union_all(recursive)

        query = select(
            cte.c.uuid,
            cte.c.parent_uuid,
            cte.c.name,
            cte.c.alias,
            cte.c.type,
            cte.c.created_at,
            cte.c.updated_at,
        ).order_by(cte.c.depth)

        rows = await self._connection.execute(query)
        return [LocationResponse(**row) for row in rows.mappings()]


class GetByUUIDs(LocationsRepositoryMixin):
    async def __call__(self, location_uuids: list[UUID]) -> list[LocationResponse]:
        query = select(self.table).where(self.table.uuid.in_(location_uuids))
        rows = await self._connection.execute(query)
        return [LocationResponse(**row) for row in rows.mappings()]


class LocationsRepository:
    def __init__(self, connection: AsyncConnection):
        self.create = Create(connection=connection)
        self.get = Get(connection=connection)
        self.get_by_type = GetByType(connection=connection)
        self.get_location_path = GetLocationPath(connection=connection)
        self.get_by_uuids = GetByUUIDs(connection=connection)
