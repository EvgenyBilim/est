import asyncio
from collections.abc import Awaitable, Callable
from functools import wraps
from typing import Annotated, AsyncIterator, TypeAlias, TypeVar, cast

from fastapi import Depends, FastAPI
from pydantic_settings import BaseSettings
from starlette.datastructures import State
from starlette.requests import Request

T = TypeVar("T")
DepType: TypeAlias = Callable[[State], Awaitable[T]]

DEPS_CACHE_STATE_NAME = "_deps_cache"


async def get_state(request: Request) -> State:
    return cast(State, request.app.state)


STATE: TypeAlias = Annotated[State, Depends(get_state)]


def get_from_state(name: str, dep_type: type[T], state: State) -> T:
    try:
        val = getattr(state, name)
    except AttributeError as exc:
        raise LookupError(f"Dependency not found in state: {state}") from exc

    if not isinstance(val, dep_type):
        raise TypeError

    return val


class AppDep:
    def __init__(self, cache: bool):
        self._cache = cache
        self._deps_events: dict[object, asyncio.Event] = {}

    def __call__(self, dependency: DepType[T]) -> DepType[T]:
        @wraps(dependency)
        async def wrapper(state: STATE) -> T:
            if not self._cache:
                return await dependency(state)

            deps_cache = get_from_state(DEPS_CACHE_STATE_NAME, dict, state)

            if dependency in deps_cache:
                return cast(T, deps_cache[dependency])

            if dependency in self._deps_events:
                await self._deps_events[dependency].wait()
                return cast(T, deps_cache[dependency])

            self._deps_events[dependency] = asyncio.Event()
            try:
                result = await dependency(state)
                deps_cache[dependency] = result
                return result
            finally:
                self._deps_events[dependency].set()
                del self._deps_events[dependency]

        return wrapper


app_dep = AppDep


class StateManager:
    STATE_NAME = "_state_manager"
    SETTINGS_DEP_NAME = "settings"

    def __init__(self, settings: BaseSettings) -> None:
        self._shutdown_hooks = {}
        self.started = False
        self.settings = settings
        self.state = {
            self.STATE_NAME: self,
            self.SETTINGS_DEP_NAME: self.settings,
            DEPS_CACHE_STATE_NAME: {},
        }

    async def startup(self) -> None:
        self.started = True

    async def shutdown(self) -> None:
        if self.started:
            for hook in reversed(self._shutdown_hooks.values()):
                await hook()

    async def register_shutdown_hook(self, hook_id: str, hook: Callable[[], Awaitable[object]]) -> None:
        self._shutdown_hooks[hook_id] = hook

    async def lifespan(self, app: FastAPI) -> AsyncIterator[dict[str, object]]:
        await self.startup()
        try:
            for key, value in self.state.items():
                setattr(app.state, key, value)
            yield self.state
        finally:
            await self.shutdown()


# class LifespanDeps(ABC):
#     DEPS_ID: str
#
#     @abstractmethod
#     async def _startup(self):
#         raise NotImplemented
#
#     @abstractmethod
#     async def _shutdown(self):
#         raise NotImplemented
#
#     async def __call__(self, state: State) -> T:
#         payload = await self._startup()
#         state_manager = get_from_state(StateManager.STATE_NAME, StateManager, state)
#         await state_manager.register_shutdown_hook(self.DEPS_ID, self._shutdown)
#         return payload
