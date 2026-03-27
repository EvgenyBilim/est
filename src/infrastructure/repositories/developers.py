from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncConnection

from src.api.schemas.developers import DeveloperModel
from src.infrastructure.models.developer import Developer
from src.infrastructure.repositories.base import BaseDBEntity


class Create(BaseDBEntity):
    async def __call__(self, developers: list[dict]) -> None:
        await self.batch_insert(Developer, developers)


class Get(BaseDBEntity):
    async def __call__(self) -> list[DeveloperModel]:
        query = select(Developer)
        rows = await self._connection.execute(query)
        return [DeveloperModel(**row) for row in rows.mappings()]


class DevelopersRepository:
    def __init__(self, connection: AsyncConnection):
        self.create = Create(connection=connection)
        self.get = Get(connection=connection)
