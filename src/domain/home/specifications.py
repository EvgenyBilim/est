from abc import ABC, abstractmethod

from src.domain.home.aggregate import Home
from src.domain.home.errors import DomainError
from src.infra.components.repository import AcquireTxRepository
from src.infra.repositories.agreements import AgreementsRepository
from src.infra.repositories.metro import MetroRepository
from src.infra.repositories.payments import PaymentsRepository


class HomeSpecification(ABC):
    """Базовый класс для спецификаций агрегата Home"""

    @abstractmethod
    async def is_satisfied_by(self, home: Home) -> bool:
        """Проверка с результатом True/False"""

    @abstractmethod
    async def check(self, home: Home) -> None:
        """Проверка с выбросом исключения при нарушении"""


class AgreementsMatchCountrySpec(HomeSpecification):
    """Договоры должны соответствовать стране дома"""

    def __init__(self, agreements_repo: AcquireTxRepository[AgreementsRepository]):
        self._agreements_repo = agreements_repo

    async def is_satisfied_by(self, home: Home) -> bool:
        agreement_uuids = [plan.agreement_uuid for block in home.blocks for plan in block.plans if plan.agreement_uuid]

        if not agreement_uuids:
            return True

        async with self._agreements_repo() as repo:
            country_uuids = await repo.get_countries_by_agreement_types(agreement_uuids=agreement_uuids)

        if len(country_uuids) > 1:
            return False

        return country_uuids[0] in home.location_uuids

    async def check(self, home: Home) -> None:
        agreement_uuids = [plan.agreement_uuid for block in home.blocks for plan in block.plans if plan.agreement_uuid]

        if not agreement_uuids:
            return

        async with self._agreements_repo() as repo:
            country_uuids = await repo.get_countries_by_agreement_types(agreement_uuids=agreement_uuids)

        if len(country_uuids) > 1:
            raise DomainError("Все типы договоров в одном доме должны быть привязаны к одной стране")
        if country_uuids[0] not in home.location_uuids:
            raise DomainError("Тип договора должен относиться к той же стране, где расположен дом")


class MetroStationInSameCitySpec(HomeSpecification):
    """Станции метро должны быть в том же городе, что и дом"""

    def __init__(self, metro_repo: AcquireTxRepository[MetroRepository]):
        self._metro_repo = metro_repo

    async def is_satisfied_by(self, home: Home) -> bool:
        if not home.metro_stations:
            return True

        station_uuids = [s.station_uuid for s in home.metro_stations]

        async with self._metro_repo() as repo:
            city_uuids = await repo.get_city_by_stations(station_uuids)

        if not city_uuids or len(city_uuids) > 1:
            return False

        return city_uuids[0] in home.location_uuids

    async def check(self, home: Home) -> None:
        if not home.metro_stations:
            return

        station_uuids = [s.station_uuid for s in home.metro_stations]

        async with self._metro_repo() as repo:
            city_uuids = await repo.get_city_by_stations(station_uuids)

        if not city_uuids:
            raise DomainError("Станции метро не найдены")
        if len(city_uuids) > 1:
            raise DomainError("Станции метро должны находиться в одном городе")
        if city_uuids[0] not in home.location_uuids:
            raise DomainError("Станции метро должны находиться в том же городе, что и дом")


class PaymentTypesMatchCountrySpec(HomeSpecification):
    """Способы оплаты должны соответствовать стране дома"""

    def __init__(self, payments_repo: AcquireTxRepository[PaymentsRepository]):
        self._payments_repo = payments_repo

    async def is_satisfied_by(self, home: Home) -> bool:
        if not home.payment_type_uuids:
            return True

        async with self._payments_repo() as repo:
            country_uuids = await repo.get_countries_by_payment_types(payment_uuids=home.payment_type_uuids)

        if not country_uuids or len(country_uuids) > 1:
            return False
        if len(country_uuids) > 1:
            raise DomainError("Способы оплаты должны относиться к одной стране")

        return country_uuids[0] in home.location_uuids

    async def check(self, home: Home) -> None:
        if not home.payment_type_uuids:
            return

        async with self._payments_repo() as repo:
            country_uuids = await repo.get_countries_by_payment_types(payment_uuids=home.payment_type_uuids)

        if not country_uuids:
            raise DomainError("Способы оплаты не найдены")
        if len(country_uuids) > 1:
            raise DomainError("Способы оплаты должны относиться к одной стране")
        if country_uuids[0] not in home.location_uuids:
            raise DomainError("Способы оплаты должны относиться к той же стране, где расположен дом")
