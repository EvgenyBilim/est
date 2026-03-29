from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncConnection

from src.http.schemas.developers import DeveloperNameResponse, DeveloperResponse
from src.infra.models.developer import Developer
from src.infra.repositories.base import BaseDBEntity


class Create(BaseDBEntity):
    async def __call__(self, developers: list[dict]) -> None:
        await self.batch_insert(Developer, developers)


class Get(BaseDBEntity):
    async def __call__(self) -> list[DeveloperResponse]:
        query = select(Developer)
        rows = await self._connection.execute(query)
        return [DeveloperResponse(**row) for row in rows.mappings()]


class GetByName(BaseDBEntity):
    async def __call__(self, name: str, limit: int) -> list[DeveloperNameResponse]:
        query = (
            select(Developer.uuid, Developer.name)
            .where(Developer.name.ilike(f"%{name}%"))
            .order_by(Developer.name)
            .limit(limit)
        )
        rows = await self._connection.execute(query)
        return [DeveloperNameResponse(uuid=row.uuid, name=row.name) for row in rows]


class DevelopersRepository:
    def __init__(self, connection: AsyncConnection):
        self.create = Create(connection=connection)
        self.get = Get(connection=connection)
        self.get_by_name = GetByName(connection=connection)
