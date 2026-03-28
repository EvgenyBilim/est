from collections import defaultdict
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert

from src.domain.home.aggregate import Home
from src.domain.home.entities import Block, GalleryImage, MetroStation, Plan
from src.infrastructure.models.home import (
    Block as BlockTable,
    Home as HomeTable,
    HomeLocation as HomeLocationTable,
    HomeMetroStation as HomeMetroStationTable,
    HomePaymentType as HomePaymentTypeTable,
    HomeTag as HomeTagTable,
    Plan as PlanTable,
)
from src.infrastructure.models.gallery import HomeGallery as HomeGalleryTable
from src.infrastructure.repositories.base import BaseDBEntity


class HomeCommandRepository(BaseDBEntity):
    async def save(self, home: Home) -> None:
        await self._upsert_home(home)
        await self._sync_tags(home)
        await self._sync_blocks(home)
        await self._sync_gallery(home)
        await self._sync_locations(home)
        await self._sync_metro_stations(home)
        await self._sync_payment_types(home)

    async def delete(self, home_uuid: UUID) -> None:
        await self._connection.execute(delete(HomeTable).where(HomeTable.uuid == home_uuid))

    async def _upsert_home(self, home: Home) -> None:
        query = (
            insert(HomeTable)
            .values(
                uuid=home.uuid,
                name=home.name,
                alias=home.alias,
                developer_uuid=home.developer_uuid,
                description=home.description,
                housing_class=home.housing_class,
                parking_types=home.parking_types,
                is_apartment=home.is_apartment,
                has_closed_territory=home.has_closed_territory,
                has_security=home.has_security,
                coordinates=home.coordinates,
                sort_order=home.sort_order,
            )
            .on_conflict_do_update(
                index_elements=["uuid"],
                set_={
                    "name": home.name,
                    "alias": home.alias,
                    "developer_uuid": home.developer_uuid,
                    "description": home.description,
                    "housing_class": home.housing_class,
                    "parking_types": home.parking_types,
                    "is_apartment": home.is_apartment,
                    "has_closed_territory": home.has_closed_territory,
                    "has_security": home.has_security,
                    "coordinates": home.coordinates,
                    "sort_order": home.sort_order,
                },
            )
        )
        await self._connection.execute(query)

    # todo: проверить
    async def _sync_tags(self, home: Home) -> None:
        await self._connection.execute(delete(HomeTagTable).where(HomeTagTable.home_uuid == home.uuid))

        if not home.tags:
            return

        tags_data = [{"home_uuid": home.uuid, "tag": tag} for tag in home.tags]
        await self._connection.execute(insert(HomeTagTable).values(tags_data))

    async def _sync_blocks(self, home: Home) -> None:
        current_block_uuids = [b.uuid for b in home.blocks]

        delete_query = delete(BlockTable).where(BlockTable.home_uuid == home.uuid)
        if current_block_uuids:
            delete_query = delete_query.where(BlockTable.uuid.not_in(current_block_uuids))
        await self._connection.execute(delete_query)

        if not home.blocks:
            return

        blocks_data = [
            {
                "uuid": block.uuid,
                "name": block.name,
                "home_uuid": block.home_uuid,
                "address": block.address,
                "floors": block.floors,
                "wall_type": block.wall_type,
                "delivery_date": block.delivery_date,
            }
            for block in home.blocks
        ]
        await self._batch_upsert(
            BlockTable,
            blocks_data,
            index_elements=["uuid"],
            update_fields=["name", "home_uuid", "address", "floors", "wall_type", "delivery_date"],
        )

        await self._sync_plans(home.blocks)

    async def _sync_plans(self, blocks: list[Block]) -> None:
        all_plan_uuids = []
        all_plans_data = []
        block_uuids = [b.uuid for b in blocks]

        for block in blocks:
            for plan in block.plans:
                all_plan_uuids.append(plan.uuid)
                all_plans_data.append(
                    {
                        "uuid": plan.uuid,
                        "block_uuid": plan.block_uuid,
                        "rooms": plan.rooms,
                        "agreement_uuid": plan.agreement_uuid,
                        "square_total": plan.square_total,
                        "square_kitchen": plan.square_kitchen,
                        "trim": plan.trim,
                        "bathroom_type": plan.bathroom_type,
                        "roof_height": plan.roof_height,
                        "price_base": plan.price_base,
                        "price_discount": plan.price_discount,
                        "floor": plan.floor,
                        "img_path": plan.img_path,
                    }
                )

        delete_query = delete(PlanTable).where(PlanTable.block_uuid.in_(block_uuids))
        if all_plan_uuids:
            delete_query = delete_query.where(PlanTable.uuid.not_in(all_plan_uuids))
        await self._connection.execute(delete_query)

        if not all_plans_data:
            return

        await self._batch_upsert(
            PlanTable,
            all_plans_data,
            index_elements=["uuid"],
            update_fields=[
                "block_uuid",
                "rooms",
                "agreement_uuid",
                "square_total",
                "square_kitchen",
                "trim",
                "bathroom_type",
                "roof_height",
                "price_base",
                "price_discount",
                "floor",
                "img_path",
            ],
        )

    async def _sync_gallery(self, home: Home) -> None:
        current_image_uuids = [i.uuid for i in home.gallery]

        delete_query = delete(HomeGalleryTable).where(HomeGalleryTable.home_uuid == home.uuid)
        if current_image_uuids:
            delete_query = delete_query.where(HomeGalleryTable.uuid.not_in(current_image_uuids))
        await self._connection.execute(delete_query)

        if not home.gallery:
            return

        gallery_data = [
            {
                "uuid": image.uuid,
                "home_uuid": image.home_uuid,
                "image_type": image.image_type,
                "image_path": image.image_path,
                "sort_order": image.sort_order,
            }
            for image in home.gallery
        ]
        await self._batch_upsert(
            HomeGalleryTable,
            gallery_data,
            index_elements=["uuid"],
            update_fields=["home_uuid", "image_type", "image_path", "sort_order"],
        )

    async def _sync_locations(self, home: Home) -> None:
        if not home.location_uuids:
            return

        # Тут важно удалить все старые локации и добавить новые целиком, т.к. у них каскадная связь
        await self._connection.execute(delete(HomeLocationTable).where(HomeLocationTable.home_uuid == home.uuid))

        locations_data = [{"home_uuid": home.uuid, "location_uuid": loc_uuid} for loc_uuid in home.location_uuids]
        await self._connection.execute(insert(HomeLocationTable).values(locations_data))

    async def _sync_metro_stations(self, home: Home) -> None:
        current_metro_uuids = [m.uuid for m in home.metro_stations]

        delete_query = delete(HomeMetroStationTable).where(HomeMetroStationTable.home_uuid == home.uuid)
        if current_metro_uuids:
            delete_query = delete_query.where(HomeMetroStationTable.uuid.not_in(current_metro_uuids))
        await self._connection.execute(delete_query)

        if not home.metro_stations:
            return

        metro_data = [
            {
                "uuid": station.uuid,
                "home_uuid": station.home_uuid,
                "station_uuid": station.station_uuid,
                "minutes_to_metro": station.minutes_to_metro,
                "transport": station.transport,
            }
            for station in home.metro_stations
        ]
        await self._batch_upsert(
            HomeMetroStationTable,
            metro_data,
            index_elements=["uuid"],
            update_fields=["home_uuid", "station_uuid", "minutes_to_metro", "transport"],
        )

    async def _sync_payment_types(self, home: Home) -> None:
        await self._connection.execute(delete(HomePaymentTypeTable).where(HomePaymentTypeTable.home_uuid == home.uuid))

        if not home.payment_type_uuids:
            return

        payment_data = [{"home_uuid": home.uuid, "payment_type_uuid": pt_uuid} for pt_uuid in home.payment_type_uuids]
        await self._connection.execute(insert(HomePaymentTypeTable).values(payment_data))

    async def _batch_upsert(
        self,
        table,
        data: list[dict],
        index_elements: list[str],
        update_fields: list[str],
        batch_size: int = 1000,
    ) -> None:
        for i in range(0, len(data), batch_size):
            batch = data[i : i + batch_size]
            stmt = insert(table).values(batch)
            stmt = stmt.on_conflict_do_update(
                index_elements=index_elements,
                set_={field: stmt.excluded[field] for field in update_fields},
            )
            await self._connection.execute(stmt)

    async def get_by_uuid(self, home_uuid: UUID) -> Home | None:
        # 1. Дом
        home_result = await self._connection.execute(select(HomeTable).where(HomeTable.uuid == home_uuid))
        home_row = home_result.mappings().first()
        if not home_row:
            return None

        # 2. Корпуса
        blocks_result = await self._connection.execute(select(BlockTable).where(BlockTable.home_uuid == home_uuid))
        blocks_rows = blocks_result.mappings().all()
        block_uuids = [b["uuid"] for b in blocks_rows]

        # 3. Планировки из всех корпусов
        plans_by_block: dict[UUID, list[Plan]] = defaultdict(list)
        if block_uuids:
            plans_result = await self._connection.execute(
                select(PlanTable).where(PlanTable.block_uuid.in_(block_uuids))
            )
            for p in plans_result.mappings().all():
                plans_by_block[p["block_uuid"]].append(
                    Plan(
                        uuid=p["uuid"],
                        block_uuid=p["block_uuid"],
                        rooms=p["rooms"],
                        agreement_uuid=p["agreement_uuid"],
                        square_total=p["square_total"],
                        square_kitchen=p["square_kitchen"],
                        trim=p["trim"],
                        bathroom_type=p["bathroom_type"],
                        roof_height=p["roof_height"],
                        price_base=p["price_base"],
                        price_discount=p["price_discount"],
                        floor=p["floor"],
                        img_path=p["img_path"],
                    )
                )

        # 4. Корпуса с планировками
        blocks = [
            Block(
                uuid=b["uuid"],
                home_uuid=b["home_uuid"],
                name=b["name"],
                address=b["address"],
                floors=b["floors"],
                wall_type=b["wall_type"],
                delivery_date=b["delivery_date"],
                plans=plans_by_block.get(b["uuid"], []),
            )
            for b in blocks_rows
        ]

        # 5. Галерея
        gallery_result = await self._connection.execute(
            select(HomeGalleryTable).where(HomeGalleryTable.home_uuid == home_uuid)
        )
        gallery = [
            GalleryImage(
                uuid=g["uuid"],
                home_uuid=g["home_uuid"],
                image_type=g["image_type"],
                image_path=g["image_path"],
                sort_order=g["sort_order"],
            )
            for g in gallery_result.mappings().all()
        ]

        # 6. Станции метро
        metro_result = await self._connection.execute(
            select(HomeMetroStationTable).where(HomeMetroStationTable.home_uuid == home_uuid)
        )
        metro_stations = [
            MetroStation(
                uuid=m["uuid"],
                home_uuid=m["home_uuid"],
                station_uuid=m["station_uuid"],
                minutes_to_metro=m["minutes_to_metro"],
                transport=m["transport"],
            )
            for m in metro_result.mappings().all()
        ]

        # 7. Локации
        locations_result = await self._connection.execute(
            select(HomeLocationTable.location_uuid).where(HomeLocationTable.home_uuid == home_uuid)
        )
        location_uuids = [loc["location_uuid"] for loc in locations_result.mappings().all()]

        # 8. Типы оплаты
        payment_result = await self._connection.execute(
            select(HomePaymentTypeTable.payment_type_uuid).where(HomePaymentTypeTable.home_uuid == home_uuid)
        )
        payment_type_uuids = [pt["payment_type_uuid"] for pt in payment_result.mappings().all()]

        # 9. Теги
        tags_result = await self._connection.execute(
            select(HomeTagTable.tag).where(HomeTagTable.home_uuid == home_uuid)
        )
        tags = [row["tag"] for row in tags_result.mappings().all()]

        return Home(
            uuid=home_row["uuid"],
            name=home_row["name"],
            alias=home_row["alias"],
            developer_uuid=home_row["developer_uuid"],
            description=home_row["description"],
            housing_class=home_row["housing_class"],
            parking_types=home_row["parking_types"],
            is_apartment=home_row["is_apartment"],
            has_closed_territory=home_row["has_closed_territory"],
            has_security=home_row["has_security"],
            coordinates=home_row["coordinates"],
            tags=tags,
            sort_order=home_row["sort_order"],
            location_uuids=location_uuids,
            payment_type_uuids=payment_type_uuids,
            blocks=blocks,
            gallery=gallery,
            metro_stations=metro_stations,
        )
