from fastapi import APIRouter, Depends

from src.api.schemas.agreements import AgreementTypeCreateSchema
from src.application.agreements import AgreementsService
from src.dependencies import agreements_service_dependency

router = APIRouter(prefix="/agreements")


@router.post("")
async def create_agreements(
    agreements: list[AgreementTypeCreateSchema],
    service: AgreementsService = Depends(agreements_service_dependency),
):
    return await service.create(agreements=agreements)
