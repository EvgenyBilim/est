from src.api.schemas.payments import PaymentTypeCreateSchema, PaymentTypeModel
from src.infrastructure.components.repository import AcquireTxRepository
from src.infrastructure.repositories.payments import PaymentsRepository


class PaymentsService:
    def __init__(self, payments_repo: AcquireTxRepository[PaymentsRepository]):
        self._payments_repo = payments_repo

    async def create(self, payments: list[PaymentTypeCreateSchema]) -> None:
        async with self._payments_repo() as repo:
            await repo.create(payments=[x.dict() for x in payments])

    async def get(self) -> list[PaymentTypeModel]:
        async with self._payments_repo() as repo:
            return await repo.get()
