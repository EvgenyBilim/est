from src.http.schemas.developers import DeveloperCreateSchema, DeveloperModel
from src.infra.components.repository import AcquireTxRepository
from src.infra.repositories.developers import DevelopersRepository


class DevelopersService:
    def __init__(self, developers_repo: AcquireTxRepository[DevelopersRepository]) -> None:
        self._developers_repo = developers_repo

    async def create(self, developers: list[DeveloperCreateSchema]) -> None:
        async with self._developers_repo() as repo:
            await repo.create(developers=[x.dict() for x in developers])

    async def get(self) -> list[DeveloperModel]:
        async with self._developers_repo() as repo:
            return await repo.get()
