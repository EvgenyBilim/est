from uuid import UUID

from sqlalchemy import literal_column, nullslast, select
from sqlalchemy.ext.asyncio import AsyncConnection

from src.enums import LocationTypeEnum
from src.http.schemas.locations import CountrySearchAreasResponse, LocationResponse, SearchAreaItem
from src.infra.models.location import Location
from src.infra.repositories.base import BaseDBEntity


class LocationsRepositoryMixin(BaseDBEntity):
    @property
    def table(self):
        return Location


class Create(LocationsRepositoryMixin):
    async def __call__(self, locations: list[dict]) -> None:
        await self.batch_insert(self.table, locations)


class Get(LocationsRepositoryMixin):
    async def __call__(self) -> list[LocationResponse]:
        query = select(self.table)
        rows = await self._connection.execute(query)
        return [LocationResponse(**row) for row in rows.mappings()]


class GetByType(LocationsRepositoryMixin):
    async def __call__(self, location_type: LocationTypeEnum) -> list[LocationResponse]:
        query = select(self.table).where(self.table.type == location_type)
        rows = await self._connection.execute(query)
        return [LocationResponse(**row) for row in rows.mappings()]


class GetLocationPath(LocationsRepositoryMixin):
    async def __call__(self, location_uuid: UUID) -> list[LocationResponse]:
        base = (
            select(
                self.table.uuid,
                self.table.parent_uuid,
                self.table.name,
                self.table.alias,
                self.table.type,
                self.table.priority,
                self.table.created_at,
                self.table.updated_at,
                literal_column("0").label("depth"),
            )
            .where(self.table.uuid == location_uuid)
            .cte(name="parent_chain", recursive=True)
        )

        parent_chain = base.alias("pc")

        recursive = (
            select(
                self.table.uuid,
                self.table.parent_uuid,
                self.table.name,
                self.table.alias,
                self.table.type,
                self.table.priority,
                self.table.created_at,
                self.table.updated_at,
                (parent_chain.c.depth + 1).label("depth"),
            )
            .select_from(self.table)
            .join(parent_chain, self.table.uuid == parent_chain.c.parent_uuid)
            .where(parent_chain.c.parent_uuid.isnot(None))
        )

        cte = base.union_all(recursive)

        query = select(
            cte.c.uuid,
            cte.c.parent_uuid,
            cte.c.name,
            cte.c.alias,
            cte.c.type,
            cte.c.priority,
            cte.c.created_at,
            cte.c.updated_at,
        ).order_by(cte.c.depth)

        rows = await self._connection.execute(query)
        return [LocationResponse(**row) for row in rows.mappings()]


class GetByUUIDs(LocationsRepositoryMixin):
    async def __call__(self, location_uuids: list[UUID]) -> list[LocationResponse]:
        query = select(self.table).where(self.table.uuid.in_(location_uuids))
        rows = await self._connection.execute(query)
        return [LocationResponse(**row) for row in rows.mappings()]


class GetChildren(LocationsRepositoryMixin):
    async def __call__(self, location_uuid: UUID) -> list[LocationResponse]:
        query = (
            select(self.table)
            .where(self.table.parent_uuid == location_uuid)
            .order_by(nullslast(self.table.priority), self.table.name)
        )
        rows = await self._connection.execute(query)
        return [LocationResponse(**row) for row in rows.mappings()]


class GetSearchAreas(LocationsRepositoryMixin):
    async def __call__(self) -> list[CountrySearchAreasResponse]:
        base = (
            select(
                self.table.uuid,
                self.table.parent_uuid,
                self.table.name,
                self.table.type,
                self.table.priority,
                self.table.uuid.label("country_uuid"),
                self.table.name.label("country_name"),
                self.table.priority.label("country_priority"),
            )
            .where(self.table.type == LocationTypeEnum.COUNTRY)
            .cte(name="location_tree", recursive=True)
        )

        tree = base.alias("lt")

        recursive = (
            select(
                self.table.uuid,
                self.table.parent_uuid,
                self.table.name,
                self.table.type,
                self.table.priority,
                tree.c.country_uuid,
                tree.c.country_name,
                tree.c.country_priority,
            )
            .select_from(self.table)
            .join(tree, self.table.parent_uuid == tree.c.uuid)
        )

        cte = base.union_all(recursive)

        query = (
            select(
                cte.c.country_uuid,
                cte.c.country_name,
                cte.c.country_priority,
                cte.c.uuid.label("city_uuid"),
                cte.c.name.label("city_name"),
            )
            .where(cte.c.type.in_([LocationTypeEnum.CITY, LocationTypeEnum.REGION]))
            .order_by(
                nullslast(cte.c.country_priority),
                cte.c.country_name,
                nullslast(cte.c.priority),
                cte.c.name,
            )
        )

        rows = await self._connection.execute(query)

        countries: dict = {}
        for row in rows.mappings():
            country_uuid = row["country_uuid"]
            if country_uuid not in countries:
                countries[country_uuid] = CountrySearchAreasResponse(
                    uuid=country_uuid,
                    name=row["country_name"],
                    locations=[],
                )
            countries[country_uuid].locations.append(SearchAreaItem(uuid=row["city_uuid"], name=row["city_name"]))

        return list(countries.values())


class LocationsRepository:
    def __init__(self, connection: AsyncConnection):
        self.create = Create(connection=connection)
        self.get = Get(connection=connection)
        self.get_by_type = GetByType(connection=connection)
        self.get_location_path = GetLocationPath(connection=connection)
        self.get_by_uuids = GetByUUIDs(connection=connection)
        self.get_children = GetChildren(connection=connection)
        self.get_search_areas = GetSearchAreas(connection=connection)
