import abc
from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from contextvars import ContextVar
from typing import TYPE_CHECKING, ClassVar, TypeVar

from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

if TYPE_CHECKING:
    pass

T = TypeVar("T", covariant=True)

_tx_connection_cv: ContextVar[dict[AsyncEngine, AsyncConnection]] = ContextVar("_tx_connection_cv")
_connection_cv: ContextVar[dict[AsyncEngine, AsyncConnection]] = ContextVar("_connection_cv")


class _SqlAlchemyAcquire[T](abc.ABC):
    CONNECTION_STORAGE: ClassVar[ContextVar[dict[AsyncEngine, AsyncConnection]]]

    def __init__(self, engine: AsyncEngine, repo_factory: Callable[[AsyncConnection], T]) -> None:
        self._engine = engine
        self._repo_factory = repo_factory

    @asynccontextmanager
    @abc.abstractmethod
    async def _get_connection(self) -> AsyncIterator[AsyncConnection]:
        raise NotImplementedError
        yield

    @asynccontextmanager
    async def __call__(self, to_context: bool = True) -> AsyncIterator[T]:
        if to_context and (connection := self.CONNECTION_STORAGE.get({}).get(self._engine, None)):
            yield self._repo_factory(connection)
        else:
            async with self._get_connection() as connection:
                if to_context:
                    token = self.CONNECTION_STORAGE.set(self.CONNECTION_STORAGE.get({}) | {self._engine: connection})
                try:
                    yield self._repo_factory(connection)
                finally:
                    if to_context:
                        self.CONNECTION_STORAGE.reset(token)


class AcquireRepository(_SqlAlchemyAcquire[T]):
    CONNECTION_STORAGE = _connection_cv

    @asynccontextmanager
    async def _get_connection(self) -> AsyncIterator[AsyncConnection]:
        async with self._engine.connect() as connection:
            yield connection


class AcquireTxRepository(_SqlAlchemyAcquire[T]):
    CONNECTION_STORAGE = _tx_connection_cv

    @asynccontextmanager
    async def _get_connection(self) -> AsyncIterator[AsyncConnection]:
        async with self._engine.begin() as connection:
            yield connection
