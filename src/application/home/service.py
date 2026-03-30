from uuid import UUID

from src.application.home.commands import (
    AddBlocksCommand,
    AddPlansCommand,
    HomeCreateCommand,
    SyncHomeCommand,
)
from src.application.home.home_info_service import HomeInfoService
from src.application.home.queries import HomeSearchFilter, HomeTagFilter, PlanSearchFilter
from src.domain.home.factory import HomeFactory
from src.errors import NotFoundError
from src.http.schemas.homes import HomeNameResponse, HomePreviewResponse, HomeResponse, PlanResponse
from src.infra.components.repository import AcquireTxRepository
from src.infra.repositories.homes.command_repo import HomeCommandRepository
from src.infra.repositories.homes.query_repo import HomeQueryRepository


class HomesService:
    def __init__(
        self,
        home_factory: HomeFactory,
        home_command_repo: AcquireTxRepository[HomeCommandRepository],
        home_query_repo: AcquireTxRepository[HomeQueryRepository],
        home_info_service: HomeInfoService,
    ) -> None:
        self._home_factory = home_factory
        self._home_command_repo = home_command_repo
        self._home_query_repo = home_query_repo
        self._home_info_service = home_info_service

    async def create_homes(self, commands: list[HomeCreateCommand]) -> list[UUID]:
        """Создание домов со всей структурой"""

        created_uuids = []

        async with self._home_command_repo() as repo:
            for command in commands:
                home = await self._home_factory.create(command)
                await repo.save(home)
                # todo: потом тут появится запись в кэш. его и home_info вынести в event_handler
                await self._home_info_service.sync(home)
                created_uuids.append(home.uuid)

        return created_uuids

    async def add_blocks(self, command: AddBlocksCommand) -> list[UUID]:
        """Добавление корпусов к существующему дому"""

        async with self._home_command_repo() as repo:
            home = await repo.get_by_uuid(command.home_uuid)
            if not home:
                raise NotFoundError(f"Дом {command.home_uuid} не найден")

            new_block_uuids = await self._home_factory.add_blocks(home, command.blocks)

            await self._home_factory.validate(home)
            await repo.save(home)
            await self._home_info_service.sync(home)

        return new_block_uuids

    async def add_plans(self, command: AddPlansCommand) -> list[UUID]:
        """Добавление планировок к существующему корпусу"""

        async with self._home_command_repo() as repo:
            home = await repo.get_by_uuid(command.home_uuid)
            if not home:
                raise NotFoundError(f"Дом {command.home_uuid} не найден")

            new_plan_uuids = await self._home_factory.add_plans(home, command.block_uuid, command.plans)

            await self._home_factory.validate(home)
            await repo.save(home)
            await self._home_info_service.sync(home)

        return new_plan_uuids

    async def sync_home(self, command: SyncHomeCommand) -> None:
        """Полная синхронизация структуры дома"""
        # todo: мб тут стоит сделать возможность передавать выборочные поля и sync только их,
        #  а остальные не затирать, если они не переданы явно как пустые поля

        async with self._home_command_repo() as repo:
            home = await repo.get_by_uuid(command.home_uuid)
            if not home:
                raise NotFoundError(f"Дом {command.home_uuid} не найден")

            await self._home_factory.sync(home, command.data)
            await repo.save(home)
            await self._home_info_service.sync(home)

    async def get_by_uuid(self, home_uuid: UUID) -> HomeResponse | None:
        """Получение дома по UUID"""
        # todo: Получать из кэша. Если кэша нет, получать из бд и писать в кэш

        async with self._home_query_repo() as repo:
            return await repo.get_by_uuid(home_uuid)

    async def search_homes(self, filters: HomeSearchFilter) -> list[HomePreviewResponse]:
        """Поиск домов по параметрам"""

        async with self._home_query_repo() as repo:
            return await repo.search_homes(filters)

    async def get_by_tag(self, tag: HomeTagFilter) -> list[HomeNameResponse]:
        """Получение названий домов по тегу"""

        async with self._home_query_repo() as repo:
            return await repo.get_by_tag(tag)

    async def search_plans(self, home_uuid: UUID, filters: PlanSearchFilter) -> list[PlanResponse]:
        """Получение планировок дома по параметрам"""

        async with self._home_query_repo() as repo:
            return await repo.search_plans(home_uuid=home_uuid, filters=filters)
