from typing import cast
from uuid import UUID

from sqlalchemy import distinct, select
from sqlalchemy.ext.asyncio import AsyncConnection

from src.api.schemas.metro import (
    MetroLineModel,
    MetropolitanModel,
    MetroStationInfoModel,
    MetroStationModel,
)
from src.infrastructure.models.metro import MetroLine, Metropolitan, MetroStation
from src.infrastructure.repositories.base import BaseDBEntity


class CreateMetropolitans(BaseDBEntity):
    async def __call__(self, metropolitans: list[dict]) -> None:
        await self.batch_insert(Metropolitan, metropolitans)


class CreateLines(BaseDBEntity):
    async def __call__(self, metro_lines: list[dict]) -> None:
        await self.batch_insert(MetroLine, metro_lines)


class CreateStations(BaseDBEntity):
    async def __call__(self, metro_stations: list[dict]) -> None:
        await self.batch_insert(MetroStation, metro_stations)


class GetMetropolitans(BaseDBEntity):
    async def __call__(self) -> list[MetropolitanModel]:
        query = select(Metropolitan)
        rows = await self._connection.execute(query)
        return [MetropolitanModel(**row) for row in rows.mappings()]


class GetLines(BaseDBEntity):
    async def __call__(self) -> list[MetroLineModel]:
        query = select(MetroLine)
        rows = await self._connection.execute(query)
        return [MetroLineModel(**row) for row in rows.mappings()]


class GetStations(BaseDBEntity):
    async def __call__(self) -> list[MetroStationModel]:
        query = select(MetroStation)
        rows = await self._connection.execute(query)
        return [MetroStationModel(**row) for row in rows.mappings()]


class GetCityByStations(BaseDBEntity):
    async def __call__(self, station_uuids: list[UUID]) -> list[UUID]:
        if not station_uuids:
            return []

        query = (
            select(distinct(Metropolitan.location_uuid))
            .select_from(Metropolitan)
            .join(MetroLine, Metropolitan.uuid == MetroLine.metropolitan_uuid)
            .join(MetroStation, MetroLine.uuid == MetroStation.metro_line_uuid)
            .where(MetroStation.uuid.in_(station_uuids))
        )

        result = await self._connection.execute(query)
        return [cast(UUID, uuid) for uuid in result.scalars().all() if uuid is not None]


class GetStationsByCity(BaseDBEntity):
    async def __call__(self, city_uuid: UUID) -> list[MetroStationModel]:
        query = (
            select(MetroStation)
            .join(MetroLine, MetroStation.metro_line_uuid == MetroLine.uuid)
            .join(Metropolitan, MetroLine.metropolitan_uuid == Metropolitan.uuid)
            .where(Metropolitan.location_uuid == city_uuid)
        )
        rows = await self._connection.execute(query)
        return [MetroStationModel(**row) for row in rows.mappings()]


class GetStationsInfoByUUIDs(BaseDBEntity):
    async def __call__(self, station_uuids: list[UUID]) -> list[MetroStationInfoModel]:
        query = (
            select(
                MetroStation.uuid,
                MetroStation.name,
                MetroLine.color,
            )
            .join(MetroLine, MetroStation.metro_line_uuid == MetroLine.uuid)
            .where(MetroStation.uuid.in_(station_uuids))
        )
        rows = await self._connection.execute(query)
        return [MetroStationInfoModel(**row) for row in rows.mappings()]


class MetroRepository:
    def __init__(self, connection: AsyncConnection):
        self.create_metropolitans = CreateMetropolitans(connection=connection)
        self.create_lines = CreateLines(connection=connection)
        self.create_stations = CreateStations(connection=connection)
        self.get_metropolitans = GetMetropolitans(connection=connection)
        self.get_lines = GetLines(connection=connection)
        self.get_stations = GetStations(connection=connection)
        self.get_city_by_stations = GetCityByStations(connection=connection)
        self.get_stations_by_city = GetStationsByCity(connection=connection)
        self.get_stations_info_by_uuids = GetStationsInfoByUUIDs(connection=connection)
