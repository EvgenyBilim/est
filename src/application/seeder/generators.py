import random
import re
import string
from datetime import date, timedelta
from decimal import Decimal
from uuid import UUID

from src.api.schemas.agreements import AgreementTypeCreateSchema, AgreementTypeModel
from src.api.schemas.developers import DeveloperCreateSchema
from src.api.schemas.locations import LocationCreateSchema, LocationResponse
from src.api.schemas.metro import (
    MetroLineCreateSchema,
    MetropolitanCreateSchema,
    MetroStationCreateSchema,
)
from src.api.schemas.payments import PaymentTypeCreateSchema, PaymentTypeModel
from src.application.home.commands import (
    BlockCreateData,
    GalleryImageCreateData,
    HomeCreateCommand,
    MetroStationCreateData,
    PlanCreateData,
)
from src.application.seeder.const import NAMES_ONE, NAMES_TWO, TRANSLIT_MAP
from src.enums import (
    BaseIntEnum,
    BaseStrEnum,
    BathroomTypeEnum,
    GalleryImageTypeEnum,
    HousingClassEnum,
    LocationTypeEnum,
    ParkingTypeEnum,
    RoomTypeEnum,
    TransportTypeEnum,
    TrimTypeEnum,
    WallTypeEnum,
)


def random_string(length: int = 20) -> str:
    return "".join(random.choices(string.ascii_lowercase, k=length))


def generate_districts(
    locations: list[LocationCreateSchema], min_districts: int = 1, max_districts: int = 20
) -> list[LocationCreateSchema]:
    result = []

    for country in locations:
        country_copy = country.model_copy(deep=True)

        if country_copy.locations:
            for city in country_copy.locations:
                districts_count = random.randint(min_districts, max_districts)

                city.locations = [
                    LocationCreateSchema(
                        name=(name := random_string()),
                        alias=name,
                        type=LocationTypeEnum.DISTRICT,
                    )
                    for _ in range(districts_count)
                ]

        result.append(country_copy)

    return result


def random_home_name(names_one: list[str], names_two: list[str]) -> str:
    return f"{random.choice(names_one)} {random.choice(names_two)}"


def name_to_alias(translit_map: dict[str, str], name: str) -> str:
    text = name.lower().strip()
    result = ""
    for char in text:
        if char == " ":
            result += "_"
        elif char in translit_map:
            result += translit_map[char]

    return result


def tags_by_names(strings: list[str]) -> list[str]:
    result = []
    for s in strings:
        result.extend(re.split(r"[ _]+", s.lower()))
    return result


def generate_metro(cities: list[LocationResponse]) -> list[MetropolitanCreateSchema]:
    return [
        MetropolitanCreateSchema(
            name=random_string(),
            location_uuid=city.uuid,
            lines=[
                MetroLineCreateSchema(
                    name=random_string(),
                    color=random_string(),
                    stations=[
                        MetroStationCreateSchema(
                            name=random_string(),
                        )
                        for _ in range(20)
                    ],
                )
                for _ in range(20)
            ],
        )
        for city in cities
    ]


def generate_agreements(countries: list[LocationResponse], agreements: list[str]) -> list[AgreementTypeCreateSchema]:
    return [
        AgreementTypeCreateSchema(name=agreement, location_uuid=country.uuid)
        for agreement in agreements
        for country in countries
    ]


def generate_payments(countries: list[LocationResponse], payments: list[str]) -> list[PaymentTypeCreateSchema]:
    return [
        PaymentTypeCreateSchema(name=payment, location_uuid=country.uuid)
        for payment in payments
        for country in countries
    ]


def generate_developers(count: int = 400) -> list[DeveloperCreateSchema]:
    return [
        DeveloperCreateSchema(name=random_string(), logo=random_string(), description=random_string())
        for _ in range(count)
    ]


def build_districts_hierarchy(locations: list[LocationResponse]) -> dict[UUID, dict[str, UUID]]:
    locations_by_uuid = {loc.uuid: loc for loc in locations}

    districts = {}

    for loc in locations:
        if loc.type == LocationTypeEnum.DISTRICT:
            city_uuid = loc.parent_uuid
            city = locations_by_uuid.get(city_uuid)
            country_uuid = city.parent_uuid if city else None

            districts[loc.uuid] = {
                "city_uuid": city_uuid,
                "country_uuid": country_uuid,
            }

    return districts


def build_contracts_by_location(contracts: list[AgreementTypeModel | PaymentTypeModel]) -> dict[UUID, list[UUID]]:
    result: dict[UUID, list[UUID]] = {}

    for contract in contracts:
        if contract.location_uuid not in result:
            result[contract.location_uuid] = []
        result[contract.location_uuid].append(contract.uuid)

    return result


def random_enum_value(enum: type[BaseStrEnum | BaseIntEnum]):
    return random.choice(enum.values())


def random_bool() -> bool:
    return random.choice([True, False])


def random_decimal_range(min_, max_):
    return Decimal(str(random.uniform(min_, max_)))


def random_date() -> date:
    start = date(2022, 1, 1)
    end = date(2028, 1, 1)
    return start + timedelta(days=random.randint(0, (end - start).days))


def generate_create_home_commands(developers_uuids, districts, agreements, payments, metro):
    return [
        HomeCreateCommand(
            name=(home_name := random_home_name(NAMES_ONE, NAMES_TWO)),
            alias=(alias := name_to_alias(TRANSLIT_MAP, home_name)),
            developer_uuid=random.choice(developers_uuids),
            location_uuid=district_uuid,
            housing_class=random_enum_value(HousingClassEnum),
            is_apartment=random_bool(),
            has_closed_territory=random_bool(),
            has_security=random_bool(),
            sort_order=1,
            description=random_string(length=random.randint(200, 400)),
            coordinates=[Decimal("30.00"), Decimal("60.00")],
            tags=tags_by_names([home_name, alias]),
            blocks=[
                BlockCreateData(
                    name="block",
                    address="address",
                    floors=20,
                    wall_type=random_enum_value(WallTypeEnum),
                    delivery_date=random_date(),
                    plans=[
                        PlanCreateData(
                            rooms=random_enum_value(RoomTypeEnum),
                            agreement_uuid=agreements[districts[district_uuid]["country_uuid"]][random.randint(0, 2)],
                            square_total=random_decimal_range(26.0, 250.0),
                            square_kitchen=random_decimal_range(8.0, 25.0),
                            trim=random_enum_value(TrimTypeEnum),
                            bathroom_type=random_enum_value(BathroomTypeEnum),
                            roof_height=random_decimal_range(2.6, 3.2),
                            price_base=random.randint(4_900_000, 120_000_000),
                            price_discount=random.randint(4_900_000, 120_000_000),
                            floor=random.randint(1, 20),
                            img_path="url",
                        )
                        for _ in range(random.randint(20, 200))
                    ],
                    # plans=[
                    #     PlanCreateData(
                    #         rooms=RoomTypeEnum.ONE,
                    #         agreement_uuid=agreements[districts[district_uuid]["country_uuid"]][0],
                    #         square_total=Decimal("32.1"),
                    #         square_kitchen=Decimal("8.2"),
                    #         trim=TrimTypeEnum.NO_TRIM,
                    #         bathroom_type=BathroomTypeEnum.UNIFIED,
                    #         roof_height=Decimal("2.8"),
                    #         price_base=8_200_000,
                    #         price_discount=7_900_000,
                    #         floor=10,
                    #         img_path="url",
                    #     ),
                    #     PlanCreateData(
                    #         rooms=RoomTypeEnum.ONE,
                    #         agreement_uuid=agreements[districts[district_uuid]["country_uuid"]][0],
                    #         square_total=Decimal("32.1"),
                    #         square_kitchen=Decimal("8.2"),
                    #         trim=TrimTypeEnum.NO_TRIM,
                    #         bathroom_type=BathroomTypeEnum.UNIFIED,
                    #         roof_height=Decimal("2.8"),
                    #         price_base=8_200_000,
                    #         price_discount=7_900_000,
                    #         floor=12,
                    #         img_path="url",
                    #     ),
                    #     PlanCreateData(
                    #         rooms=random_enum_value(RoomTypeEnum),
                    #         agreement_uuid=agreements[districts[district_uuid]["country_uuid"]][random.randint(0, 2)],
                    #         square_total=Decimal("34.5"),
                    #         square_kitchen=Decimal("12.1"),
                    #         trim=random_enum_value(TrimTypeEnum),
                    #         bathroom_type=random_enum_value(BathroomTypeEnum),
                    #         roof_height=Decimal("2.8"),
                    #         price_base=8_400_000,
                    #         price_discount=8_300_000,
                    #         floor=14,
                    #         img_path="url",
                    #     )
                    # ],
                )
                for _ in range(random.randint(1, 10))
                # for _ in range(2)
            ],
            gallery=[
                GalleryImageCreateData(
                    image_type=GalleryImageTypeEnum.PREVIEW,
                    image_path="path1",
                    sort_order=1,
                ),
                GalleryImageCreateData(
                    image_type=GalleryImageTypeEnum.PREVIEW,
                    image_path="path2",
                    sort_order=2,
                ),
                GalleryImageCreateData(
                    image_type=GalleryImageTypeEnum.FULL,
                    image_path="path3",
                    sort_order=1,
                ),
                GalleryImageCreateData(
                    image_type=GalleryImageTypeEnum.FULL,
                    image_path="path4",
                    sort_order=2,
                ),
            ],
            metro_stations=[
                MetroStationCreateData(
                    station_uuid=station.uuid,
                    minutes_to_metro=random.randint(5, 60),
                    transport=TransportTypeEnum.ON_FOOT,
                )
                for station in random.sample(metro[districts[district_uuid]["city_uuid"]], random.randint(1, 4))
            ],
            payment_type_uuids=random.sample(payments[districts[district_uuid]["country_uuid"]], random.randint(1, 3)),
            parking_types=[random_enum_value(ParkingTypeEnum)],
        )
        for _ in range(25)
        for district_uuid, locations in districts.items()
    ]
