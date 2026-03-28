import contextlib
from collections.abc import AsyncIterator
from typing import Any

import orjson
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from starlette.datastructures import State

from src.infrastructure.components.base import StateManager, get_from_state
from src.settings import SqlAlchemySettings


class AsyncPGEngineDeps:
    DEPS_ID = "AsyncPGEngine"

    def __init__(self, settings: SqlAlchemySettings) -> None:
        self._settings = settings
        self._engine: AsyncEngine | None = None
        self._exit_stack = contextlib.AsyncExitStack()

    async def _startup(self) -> AsyncEngine:
        self._engine = await self._create_engine(self._settings)
        return self._engine

    async def _shutdown(self) -> None:
        await self._exit_stack.aclose()

    @contextlib.asynccontextmanager
    async def _create_sqlalchemy_engine(self, *args: Any, **kwargs: Any) -> AsyncIterator[AsyncEngine]:
        engine = create_async_engine(*args, **kwargs)
        try:
            yield engine
        finally:
            await engine.dispose()

    async def _create_engine(self, settings) -> AsyncEngine:
        def orjson_serializer(obj: object) -> str:
            return orjson.dumps(obj, default=str, option=orjson.OPT_NON_STR_KEYS).decode()

        return await self._exit_stack.enter_async_context(
            self._create_sqlalchemy_engine(
                self._settings.postgres_dsn,
                pool_size=settings.pg_pool_size,
                pool_pre_ping=settings.pool_pre_ping,
                pool_timeout=settings.pool_timeout,
                pool_use_lifo=settings.pool_use_lifo,
                connect_args={"timeout": settings.pg_connection_timeout},
                max_overflow=0,
                json_serializer=orjson_serializer,
                json_deserializer=orjson.loads,
            )
        )

    async def __call__(self, state: State):
        payload = await self._startup()
        state_manager = get_from_state(StateManager.STATE_NAME, StateManager, state)
        await state_manager.register_shutdown_hook(self.DEPS_ID, self._shutdown)
        return payload
