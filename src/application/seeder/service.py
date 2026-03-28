from src.api.schemas.locations import LocationCreateSchema
from src.application.agreements import AgreementsService
from src.application.developers import DevelopersService
from src.application.home.service import HomesService
from src.application.locations import LocationsService
from src.application.metro import MetroService
from src.application.payments import PaymentsService
from src.application.seeder.const import AGREEMENT_TYPES, PAYMENT_TYPES
from src.application.seeder.generators import (
    build_contracts_by_location,
    build_districts_hierarchy,
    generate_agreements,
    generate_create_home_commands,
    generate_developers,
    generate_districts,
    generate_metro,
    generate_payments,
)
from src.enums import LocationTypeEnum


class DatabaseSeeder:
    def __init__(
        self,
        location_service: LocationsService,
        metro_service: MetroService,
        developers_service: DevelopersService,
        agreements_service: AgreementsService,
        payments_service: PaymentsService,
        homes_service: HomesService,
    ):
        self._location_service = location_service
        self._metro_service = metro_service
        self._developers_service = developers_service
        self._agreements_service = agreements_service
        self._payments_service = payments_service
        self._homes_service = homes_service

    async def __call__(self, locations: list[LocationCreateSchema]):
        full_locations = generate_districts(locations=locations)
        await self._location_service.create(locations=full_locations)

        cities = await self._location_service.get_by_type(location_type=LocationTypeEnum.CITY)
        countries = await self._location_service.get_by_type(location_type=LocationTypeEnum.COUNTRY)

        await self._metro_service.create_with_structure(metros=generate_metro(cities=cities))
        await self._agreements_service.create(
            agreements=generate_agreements(countries=countries, agreements=AGREEMENT_TYPES)
        )
        await self._payments_service.create(payments=generate_payments(countries=countries, payments=PAYMENT_TYPES))
        await self._developers_service.create(developers=generate_developers(400))

        developer_uuids = [x.uuid for x in await self._developers_service.get()]

        locations_by_uuid = build_districts_hierarchy(locations=await self._location_service.get())
        agreements_by_country = build_contracts_by_location(
            contracts=await self._agreements_service.get(),  # type: ignore[arg-type]
        )
        payments_by_country = build_contracts_by_location(contracts=await self._payments_service.get())  # type: ignore[arg-type]
        metro_stations_by_city = {
            city.uuid: await self._metro_service.get_stations_by_city(city_uuid=city.uuid) for city in cities
        }

        create_home_commands = generate_create_home_commands(
            developers_uuids=developer_uuids,
            districts=locations_by_uuid,
            agreements=agreements_by_country,
            payments=payments_by_country,
            metro=metro_stations_by_city,
        )
        create_home_commands = create_home_commands[:1]  # todo: delete
        await self._homes_service.create_homes(commands=create_home_commands)
