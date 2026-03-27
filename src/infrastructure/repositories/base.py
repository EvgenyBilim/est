from abc import ABC, abstractmethod

from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncConnection


class BaseDBEntity(ABC):
    def __init__(self, connection: AsyncConnection):
        self._connection = connection

    async def batch_insert(self, table, data: list[dict], batch_size: int = 1000) -> None:
        for i in range(0, len(data), batch_size):
            batch = data[i : i + batch_size]
            query = insert(table).values(batch)
            await self._connection.execute(query)
