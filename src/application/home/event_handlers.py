from typing import Protocol, TypeVar

from src.domain.home.events import HomeCreated, HomeStructureChanged

T = TypeVar("T")


class EventHandler(Protocol[T]):
    async def handle(self, event: T) -> None: ...


class HomeCreatedHandler(EventHandler[HomeCreated]):
    """Действия при добавлении дома"""

    def __init__(self):
        pass

    async def handle(self, event: HomeCreated) -> None:
        # Добавить дом в кэш, обновить индекс
        pass


class HomeStructureChangedHandler(EventHandler[HomeStructureChanged]):
    """Действия при изменении дома или его составных частей"""

    def __init__(self):
        pass

    async def handle(self, event: HomeStructureChanged) -> None:
        # Обновить кэш, обновить индекс
        pass
