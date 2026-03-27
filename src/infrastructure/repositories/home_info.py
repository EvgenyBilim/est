from sqlalchemy import delete, insert
from sqlalchemy.ext.asyncio import AsyncConnection

from src.domain.home.value_objects import HomeInfo
from src.infrastructure.models.home import HomeInfo as HomeInfoTable
from src.infrastructure.repositories.base import BaseDBEntity


class Sync(BaseDBEntity):
    async def __call__(self, home_info: HomeInfo) -> None:
        await self._connection.execute(delete(HomeInfoTable).where(HomeInfoTable.uuid == home_info.uuid))

        home_info_data = {
            "uuid": home_info.uuid,
            "delivery_from": home_info.delivery_from,
            "delivery_to": home_info.delivery_to,
            "floors_min": home_info.floors_min,
            "floors_max": home_info.floors_max,
            "roof_height_min": home_info.roof_height_min,
            "roof_height_max": home_info.roof_height_max,
            "wall_types": home_info.wall_types,
            "trim_types": home_info.trim_types,
            "bathroom_types": home_info.bathroom_types,
            "agreement_types": home_info.agreement_types,
            "payment_types": home_info.payment_types,
            "locations": home_info.locations,
            "metro_stations": home_info.metro_stations,
            "plans_info": home_info.plans_info,
            "blocks_count": home_info.blocks_count,
        }
        await self._connection.execute(insert(HomeInfoTable).values(home_info_data))


class HomeInfoRepository:
    def __init__(self, connection: AsyncConnection):
        self.sync = Sync(connection=connection)
