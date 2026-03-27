from src.api.schemas.agreements import AgreementTypeCreateSchema, AgreementTypeModel
from src.infrastructure.components.repository import AcquireTxRepository
from src.infrastructure.repositories.agreements import AgreementsRepository


class AgreementsService:
    def __init__(self, agreements_repo: AcquireTxRepository[AgreementsRepository]):
        self._agreements_repo = agreements_repo

    async def create(self, agreements: list[AgreementTypeCreateSchema]) -> None:
        async with self._agreements_repo() as repo:
            await repo.create(agreements=[x.dict() for x in agreements])

    async def get(self) -> list[AgreementTypeModel]:
        async with self._agreements_repo() as repo:
            return await repo.get()
