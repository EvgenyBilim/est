from sqlalchemy.ext.asyncio import AsyncEngine

from src.application.agreements import AgreementsService
from src.application.developer.service import DevelopersService
from src.application.home.home_info_service import HomeInfoService
from src.application.home.service import HomesService
from src.application.locations import LocationsService
from src.application.metro import MetroService
from src.application.payments import PaymentsService
from src.application.seeder.service import DatabaseSeeder
from src.domain.home.factory import HomeFactory
from src.domain.home.specifications import (
    AgreementsMatchCountrySpec,
    MetroStationInSameCitySpec,
    PaymentTypesMatchCountrySpec,
)
from src.infra.components.asyncpg import AsyncPGEngineDeps
from src.infra.components.base import STATE, app_dep, get_from_state
from src.infra.components.repository import AcquireTxRepository
from src.infra.repositories.agreements import AgreementsRepository
from src.infra.repositories.developers import DevelopersRepository
from src.infra.repositories.home_info import HomeInfoRepository
from src.infra.repositories.homes.command_repo import HomeCommandRepository
from src.infra.repositories.homes.query_repo import HomeQueryRepository
from src.infra.repositories.locations import LocationsRepository
from src.infra.repositories.metro import MetroRepository
from src.infra.repositories.payments import PaymentsRepository
from src.settings import Settings


@app_dep(cache=True)
async def get_settings(state: STATE) -> Settings:
    return get_from_state("settings", Settings, state)


@app_dep(cache=True)
async def get_engine(state: STATE) -> AsyncEngine:
    settings = await get_settings(state)
    return await AsyncPGEngineDeps(settings=settings)(state)


@app_dep(cache=True)
async def locations_repository_dependency(state: STATE) -> AcquireTxRepository[LocationsRepository]:
    engine = await get_engine(state)
    return AcquireTxRepository(engine, LocationsRepository)


@app_dep(cache=True)
async def metro_repository_dependency(state: STATE) -> AcquireTxRepository[MetroRepository]:
    engine = await get_engine(state)
    return AcquireTxRepository(engine, MetroRepository)


@app_dep(cache=True)
async def agreements_repository_dependency(state: STATE) -> AcquireTxRepository[AgreementsRepository]:
    engine = await get_engine(state)
    return AcquireTxRepository(engine, AgreementsRepository)


@app_dep(cache=True)
async def payments_repository_dependency(state: STATE) -> AcquireTxRepository[PaymentsRepository]:
    engine = await get_engine(state)
    return AcquireTxRepository(engine, PaymentsRepository)


@app_dep(cache=True)
async def developers_repository_dependency(state: STATE) -> AcquireTxRepository[DevelopersRepository]:
    engine = await get_engine(state)
    return AcquireTxRepository(engine, DevelopersRepository)


@app_dep(cache=True)
async def home_command_repository_dependency(state: STATE) -> AcquireTxRepository[HomeCommandRepository]:
    engine = await get_engine(state)
    return AcquireTxRepository(engine, HomeCommandRepository)


@app_dep(cache=True)
async def home_query_repository_dependency(state: STATE) -> AcquireTxRepository[HomeQueryRepository]:
    engine = await get_engine(state)
    return AcquireTxRepository(engine, HomeQueryRepository)


@app_dep(cache=True)
async def home_info_repository_dependency(state: STATE) -> AcquireTxRepository[HomeInfoRepository]:
    engine = await get_engine(state)
    return AcquireTxRepository(engine, HomeInfoRepository)


@app_dep(cache=True)
async def locations_service_dependency(state: STATE) -> LocationsService:
    return LocationsService(locations_repo=await locations_repository_dependency(state))


@app_dep(cache=True)
async def metro_service_dependency(state: STATE) -> MetroService:
    return MetroService(
        metro_repo=await metro_repository_dependency(state),
    )


@app_dep(cache=True)
async def agreements_service_dependency(state: STATE) -> AgreementsService:
    return AgreementsService(
        agreements_repo=await agreements_repository_dependency(state),
    )


@app_dep(cache=True)
async def payments_service_dependency(state: STATE) -> PaymentsService:
    return PaymentsService(
        payments_repo=await payments_repository_dependency(state),
    )


@app_dep(cache=True)
async def developers_service_dependency(state: STATE) -> DevelopersService:
    return DevelopersService(
        developers_repo=await developers_repository_dependency(state),
    )


@app_dep(cache=True)
async def agreements_spec_dependency(state: STATE) -> AgreementsMatchCountrySpec:
    return AgreementsMatchCountrySpec(
        agreements_repo=await agreements_repository_dependency(state),
    )


@app_dep(cache=True)
async def metro_spec_dependency(state: STATE) -> MetroStationInSameCitySpec:
    return MetroStationInSameCitySpec(
        metro_repo=await metro_repository_dependency(state),
    )


@app_dep(cache=True)
async def payments_spec_dependency(state: STATE) -> PaymentTypesMatchCountrySpec:
    return PaymentTypesMatchCountrySpec(
        payments_repo=await payments_repository_dependency(state),
    )


@app_dep(cache=True)
async def home_info_service_dependency(state: STATE) -> HomeInfoService:
    return HomeInfoService(
        agreements_repo=await agreements_repository_dependency(state),
        payments_repo=await payments_repository_dependency(state),
        locations_repo=await locations_repository_dependency(state),
        metro_repo=await metro_repository_dependency(state),
        home_info_repo=await home_info_repository_dependency(state),
    )


@app_dep(cache=True)
async def home_factory_dependency(state: STATE) -> HomeFactory:
    return HomeFactory(
        locations_repo=await locations_repository_dependency(state),
        agreements_spec=await agreements_spec_dependency(state),
        metro_spec=await metro_spec_dependency(state),
        payments_spec=await payments_spec_dependency(state),
    )


@app_dep(cache=True)
async def homes_service_dependency(state: STATE) -> HomesService:
    return HomesService(
        home_factory=await home_factory_dependency(state),
        home_command_repo=await home_command_repository_dependency(state),
        home_query_repo=await home_query_repository_dependency(state),
        home_info_service=await home_info_service_dependency(state),
    )


@app_dep(cache=True)
async def database_seeder_service_dependency(state: STATE) -> DatabaseSeeder:
    return DatabaseSeeder(
        location_service=await locations_service_dependency(state),
        metro_service=await metro_service_dependency(state),
        developers_service=await developers_service_dependency(state),
        agreements_service=await agreements_service_dependency(state),
        payments_service=await payments_service_dependency(state),
        homes_service=await homes_service_dependency(state),
    )
