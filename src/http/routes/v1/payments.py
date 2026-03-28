from fastapi import APIRouter, Depends

from src.application.payments import PaymentsService
from src.dependencies import payments_service_dependency
from src.http.schemas.payments import PaymentTypeCreateSchema

router = APIRouter(prefix="/payments")


@router.post("")
async def create_payments(
    payments: list[PaymentTypeCreateSchema],
    service: PaymentsService = Depends(payments_service_dependency),
):
    return await service.create(payments=payments)
