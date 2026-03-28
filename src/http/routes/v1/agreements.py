from fastapi import APIRouter, Depends

from src.application.agreements import AgreementsService
from src.dependencies import agreements_service_dependency
from src.http.schemas.agreements import AgreementTypeCreateSchema

router = APIRouter(prefix="/agreements")


@router.post("")
async def create_agreements(
    agreements: list[AgreementTypeCreateSchema],
    service: AgreementsService = Depends(agreements_service_dependency),
):
    return await service.create(agreements=agreements)
