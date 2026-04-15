from uuid import UUID

from sqlalchemy import func, literal, or_, select

from src.application.home.queries import HomeSearchFilter, HomeTagFilter, PlanSearchFilter
from src.enums import GalleryImageTypeEnum
from src.http.schemas.homes import (
    BlockResponse,
    HomeDeliveryResponse,
    HomeDeveloperResponse,
    HomeFloorsResponse,
    HomeGalleryResponse,
    HomeNameResponse,
    HomePreviewResponse,
    HomeResponse,
    HomeRoofHeightResponse,
    LocationResponse,
    MetroStationResponse,
    PlanGroupResponse,
    PlanResponse,
    StatsByRoomsResponse,
)
from src.infra.models.contracts import AgreementType as AgreementTypeTable
from src.infra.models.developer import Developer as DeveloperTable
from src.infra.models.gallery import HomeGallery as HomeGalleryTable
from src.infra.models.home import (
    Block as BlockTable,
    Home as HomeTable,
    HomeInfo as HomeInfoTable,
    HomeLocation as HomeLocationTable,
    HomeMetroStation as HomeMetroStationTable,
    HomeTag as HomeTagTable,
    Plan as PlanTable,
    PlanGroup as PlanGroupTable,
)
from src.infra.repositories.base import BaseDBEntity


class HomeQueryRepository(BaseDBEntity):
    async def get_by_uuid(self, home_uuid: UUID) -> HomeResponse | None:
        home_row = await self._get_home_row(home_uuid)

        if not home_row:
            return None

        metro_stations = [MetroStationResponse(**station) for station in home_row.metro_stations]

        blocks = await self._get_blocks(home_uuid)
        plans = await self.search_plans(home_uuid=home_uuid, filters=PlanSearchFilter())
        gallery = await self._get_gallery(home_uuid)

        return HomeResponse(
            uuid=home_row.uuid,
            name=home_row.name,
            alias=home_row.alias,
            description=home_row.description,
            housing_class=home_row.housing_class,
            parking_types=home_row.parking_types,
            is_apartment=home_row.is_apartment,
            has_closed_territory=home_row.has_closed_territory,
            has_security=home_row.has_security,
            coordinates=home_row.coordinates,
            developer=HomeDeveloperResponse(
                uuid=home_row.developer_uuid,
                name=home_row.developer_name,
            ),
            payment_types=home_row.payment_types,
            agreement_types=home_row.agreement_types,
            wall_types=home_row.wall_types,
            trim_types=home_row.trim_types,
            blocks_count=home_row.blocks_count,
            delivery=HomeDeliveryResponse(
                min=home_row.delivery_from,
                max=home_row.delivery_to,
            ),
            floors=HomeFloorsResponse(
                min=home_row.floors_min,
                max=home_row.floors_max,
            ),
            roof_height=HomeRoofHeightResponse(
                min=home_row.roof_height_min,
                max=home_row.roof_height_max,
            ),
            stats_by_rooms=StatsByRoomsResponse.from_row(home_row.plans_info),
            locations=LocationResponse(**home_row.locations),
            metro_stations=metro_stations,
            blocks=blocks,
            plans=plans,
            gallery=gallery,
        )

    async def _get_home_row(self, home_uuid: UUID):
        developer_alias = DeveloperTable.__table__.alias()

        home_result = await self._connection.execute(
            select(HomeTable, HomeInfoTable, developer_alias.c.name.label("developer_name"))
            .join(HomeInfoTable, HomeTable.uuid == HomeInfoTable.uuid)
            .join(developer_alias, HomeTable.developer_uuid == developer_alias.c.uuid)
            .where(HomeTable.uuid == home_uuid)
        )
        return home_result.mappings().first()

    async def _get_blocks(self, home_uuid: UUID) -> list[BlockResponse]:
        blocks_result = await self._connection.execute(select(BlockTable).where(BlockTable.home_uuid == home_uuid))
        return [BlockResponse(**row) for row in blocks_result.mappings()]

    async def search_plans(self, home_uuid: UUID, filters: PlanSearchFilter) -> list[PlanResponse]:
        agreement_type_alias = AgreementTypeTable.__table__.alias()
        block_alias = BlockTable.__table__.alias()

        query = (
            select(
                PlanTable.block_uuid,
                PlanTable.rooms,
                PlanTable.square_total,
                PlanTable.square_kitchen,
                PlanTable.trim,
                PlanTable.bathroom_type,
                PlanTable.roof_height,
                PlanTable.price_base,
                PlanTable.price_discount,
                PlanTable.img_path,
                func.array_agg(func.distinct(PlanTable.floor)).label("floors"),
                block_alias.c.name.label("block_name"),
                block_alias.c.floors.label("floors_by_block"),
                block_alias.c.delivery_date.label("delivery_date"),
                block_alias.c.wall_type.label("wall_type"),
                agreement_type_alias.c.name.label("agreement"),
            )
            .join(block_alias, PlanTable.block_uuid == block_alias.c.uuid)
            .join(agreement_type_alias, PlanTable.agreement_uuid == agreement_type_alias.c.uuid)
            .where(block_alias.c.home_uuid == home_uuid)
            .group_by(
                PlanTable.block_uuid,
                PlanTable.rooms,
                PlanTable.square_total,
                PlanTable.square_kitchen,
                PlanTable.trim,
                PlanTable.bathroom_type,
                PlanTable.roof_height,
                PlanTable.price_base,
                PlanTable.price_discount,
                PlanTable.img_path,
                block_alias.c.name.label("block_name"),
                block_alias.c.floors.label("floors_by_block"),
                block_alias.c.delivery_date.label("delivery_date"),
                block_alias.c.wall_type.label("wall_type"),
                agreement_type_alias.c.name.label("agreement"),
            )
        )

        if filters.rooms:
            query = query.where(PlanTable.rooms.in_(filters.rooms))
        if filters.price_from is not None:
            query = query.where(PlanTable.price_base >= filters.price_from)
        if filters.price_to is not None:
            query = query.where(PlanTable.price_base <= filters.price_to)
        if filters.square_total_from is not None:
            query = query.where(PlanTable.square_total >= filters.square_total_from)
        if filters.square_total_to is not None:
            query = query.where(PlanTable.square_total <= filters.square_total_to)
        if filters.square_kitchen_from is not None:
            query = query.where(PlanTable.square_kitchen >= filters.square_kitchen_from)
        if filters.square_kitchen_to is not None:
            query = query.where(PlanTable.square_kitchen <= filters.square_kitchen_to)
        if filters.trim_type:
            query = query.where(PlanTable.trim.in_(filters.trim_type))
        if filters.bathroom_type:
            query = query.where(PlanTable.bathroom_type.in_(filters.bathroom_type))
        if filters.roof_height_min is not None:
            query = query.where(PlanTable.roof_height >= filters.roof_height_min)
        if filters.roof_height_max is not None:
            query = query.where(PlanTable.roof_height <= filters.roof_height_max)
        if filters.floor_min is not None:
            query = query.where(PlanTable.floor >= filters.floor_min)
        if filters.floor_max is not None:
            query = query.where(PlanTable.floor <= filters.floor_max)
        if filters.agreement_type:
            query = query.where(agreement_type_alias.c.name.in_(filters.agreement_type))
        if filters.delivery_from is not None:
            query = query.where(block_alias.c.delivery_date >= filters.delivery_from)
        if filters.delivery_to is not None:
            query = query.where(block_alias.c.delivery_date <= filters.delivery_to)
        if filters.wall_type:
            query = query.where(block_alias.c.wall_type.in_(filters.wall_type))

        query = query.limit(filters.limit).offset(filters.offset)

        plans_result = await self._connection.execute(query)
        return [PlanResponse(**x) for x in plans_result.mappings()]

    async def get_group_plan_by_uuid(self, group_uuid: UUID) -> PlanGroupResponse | None:
        agreement_type_alias = AgreementTypeTable.__table__.alias()
        block_alias = BlockTable.__table__.alias()
        home_alias = HomeTable.__table__.alias()
        home_info_alias = HomeInfoTable.__table__.alias()
        developer_alias = DeveloperTable.__table__.alias()

        query = (
            select(
                PlanGroupTable.group_uuid,
                home_alias.c.uuid.label("home_uuid"),
                home_alias.c.name.label("home_name"),
                home_alias.c.alias.label("home_alias"),
                home_alias.c.description.label("home_description"),
                home_alias.c.housing_class,
                home_alias.c.parking_types,
                home_alias.c.is_apartment,
                home_alias.c.has_closed_territory,
                home_alias.c.has_security,
                home_alias.c.coordinates,
                developer_alias.c.uuid.label("developer_uuid"),
                developer_alias.c.name.label("developer_name"),
                block_alias.c.name.label("block_name"),
                block_alias.c.delivery_date.label("delivery_date"),
                block_alias.c.wall_type.label("wall_type"),
                PlanTable.rooms,
                PlanTable.square_total,
                PlanTable.square_kitchen,
                PlanTable.trim,
                PlanTable.bathroom_type,
                PlanTable.roof_height,
                PlanTable.price_base,
                PlanTable.price_discount,
                PlanTable.img_path,
                func.array_agg(func.distinct(PlanTable.floor)).label("floors"),
                agreement_type_alias.c.name.label("agreement"),
                home_info_alias.c.payment_types,
                home_info_alias.c.locations,
                home_info_alias.c.metro_stations,
            )
            .join(PlanTable, PlanGroupTable.plan_uuid == PlanTable.uuid)
            .join(block_alias, PlanTable.block_uuid == block_alias.c.uuid)
            .join(home_alias, block_alias.c.home_uuid == home_alias.c.uuid)
            .join(home_info_alias, home_alias.c.uuid == home_info_alias.c.uuid)
            .join(developer_alias, home_alias.c.developer_uuid == developer_alias.c.uuid)
            .join(agreement_type_alias, PlanTable.agreement_uuid == agreement_type_alias.c.uuid)
            .where(PlanGroupTable.group_uuid == group_uuid)
            .group_by(
                PlanGroupTable.group_uuid,
                home_alias.c.uuid,
                home_alias.c.name,
                home_alias.c.alias,
                home_alias.c.description,
                home_alias.c.housing_class,
                home_alias.c.parking_types,
                home_alias.c.is_apartment,
                home_alias.c.has_closed_territory,
                home_alias.c.has_security,
                home_alias.c.coordinates,
                developer_alias.c.uuid,
                developer_alias.c.name,
                block_alias.c.name,
                block_alias.c.delivery_date,
                block_alias.c.wall_type,
                PlanTable.rooms,
                PlanTable.square_total,
                PlanTable.square_kitchen,
                PlanTable.trim,
                PlanTable.bathroom_type,
                PlanTable.roof_height,
                PlanTable.price_base,
                PlanTable.price_discount,
                PlanTable.img_path,
                agreement_type_alias.c.name,
                home_info_alias.c.payment_types,
                home_info_alias.c.locations,
                home_info_alias.c.metro_stations,
            )
        )

        result = await self._connection.execute(query)
        row = result.mappings().first()
        if not row:
            return None

        gallery = await self._get_gallery(row["home_uuid"])

        return PlanGroupResponse(
            group_uuid=row["group_uuid"],
            home_uuid=row["home_uuid"],
            home_name=row["home_name"],
            home_alias=row["home_alias"],
            home_description=row["home_description"],
            housing_class=row["housing_class"],
            parking_types=row["parking_types"],
            is_apartment=row["is_apartment"],
            has_closed_territory=row["has_closed_territory"],
            has_security=row["has_security"],
            coordinates=row["coordinates"],
            developer=HomeDeveloperResponse(
                uuid=row["developer_uuid"],
                name=row["developer_name"],
            ),
            block_name=row["block_name"],
            delivery_date=row["delivery_date"],
            wall_type=row["wall_type"],
            rooms=row["rooms"],
            square_total=row["square_total"],
            square_kitchen=row["square_kitchen"],
            trim=row["trim"],
            bathroom_type=row["bathroom_type"],
            roof_height=row["roof_height"],
            price_base=row["price_base"],
            price_discount=row["price_discount"],
            agreement=row["agreement"],
            img_path=row["img_path"],
            floors=row["floors"],
            payment_types=row["payment_types"],
            locations=LocationResponse(**row["locations"]) if row["locations"] else None,
            metro_stations=[MetroStationResponse(**s) for s in row["metro_stations"]]
            if row["metro_stations"]
            else None,
            gallery=gallery,
        )

    async def _get_gallery(self, home_uuid: UUID) -> HomeGalleryResponse:
        gallery = await self._connection.execute(
            select(
                HomeGalleryTable.image_type,
                HomeGalleryTable.image_path,
            )
            .where(HomeGalleryTable.home_uuid == home_uuid)
            .order_by(HomeGalleryTable.sort_order)
        )
        gallery_rows = gallery.fetchall()

        preview = [row.image_path for row in gallery_rows if row.image_type == GalleryImageTypeEnum.PREVIEW]
        full = [row.image_path for row in gallery_rows if row.image_type == GalleryImageTypeEnum.FULL]

        return HomeGalleryResponse(
            preview=preview,
            full=full,
        )

    async def search_homes(self, filters: HomeSearchFilter) -> list[HomePreviewResponse]:
        query = (
            select(
                HomeTable.uuid,
                HomeTable.name,
                HomeTable.alias,
                HomeTable.coordinates,
                HomeTable.developer_uuid,
                DeveloperTable.name.label("developer_name"),
                HomeInfoTable.delivery_from,
                HomeInfoTable.delivery_to,
                HomeInfoTable.plans_info,
                HomeInfoTable.metro_stations,
            )
            .join(HomeInfoTable, HomeTable.uuid == HomeInfoTable.uuid)
            .join(DeveloperTable, HomeTable.developer_uuid == DeveloperTable.uuid)
        )
        query = self._apply_filters(query, filters).limit(filters.limit).offset(filters.offset)
        result = await self._connection.execute(query)
        rows = result.mappings().all()

        home_uuids = [row.uuid for row in rows]
        gallery_by_home = await self._get_gallery_batch(home_uuids)

        return [
            HomePreviewResponse(
                uuid=row.uuid,
                name=row.name,
                alias=row.alias,
                coordinates=row.coordinates,
                developer=HomeDeveloperResponse(
                    uuid=row.developer_uuid,
                    name=row.developer_name,
                ),
                delivery=HomeDeliveryResponse(
                    min=row.delivery_from,
                    max=row.delivery_to,
                ),
                stats_by_rooms=StatsByRoomsResponse(**row.plans_info) if row.plans_info else None,
                metro_stations=[MetroStationResponse(**x) for x in row.metro_stations] if row.metro_stations else None,
                gallery=gallery_by_home.get(row.uuid),
            )
            for row in rows
        ]

    async def _get_gallery_batch(self, home_uuids: list[UUID]) -> dict[UUID, HomeGalleryResponse]:
        result = await self._connection.execute(
            select(
                HomeGalleryTable.home_uuid,
                HomeGalleryTable.image_type,
                HomeGalleryTable.image_path,
            )
            .where(HomeGalleryTable.home_uuid.in_(home_uuids))
            .order_by(HomeGalleryTable.sort_order)
        )

        gallery: dict = {}
        for row in result:
            bucket = gallery.setdefault(row.home_uuid, {"preview": [], "full": []})
            if row.image_type == GalleryImageTypeEnum.PREVIEW:
                bucket["preview"].append(row.image_path)
            else:
                bucket["full"].append(row.image_path)

        return {uuid: HomeGalleryResponse(**data) for uuid, data in gallery.items()}

    @staticmethod
    def _apply_filters(query, filters: HomeSearchFilter):
        # home_tags
        if filters.name is not None:
            query = (
                query.join(HomeTagTable, HomeTable.uuid == HomeTagTable.home_uuid)
                .where(HomeTagTable.tag.ilike(f"%{filters.name}%"))
                .distinct(HomeTable.uuid)
            )

        # homes
        if filters.developer is not None:
            query = query.where(HomeTable.developer_uuid.in_(filters.developer))
        if filters.housing_class is not None:
            query = query.where(HomeTable.housing_class.in_(filters.housing_class))
        if filters.parking_type is not None:
            query = query.where(HomeTable.parking_types.overlap(filters.parking_type))
        if filters.is_apartment is not None:
            query = query.where(HomeTable.is_apartment == filters.is_apartment)
        if filters.has_closed_territory is not None:
            query = query.where(HomeTable.has_closed_territory == filters.has_closed_territory)
        if filters.has_security is not None:
            query = query.where(HomeTable.has_security == filters.has_security)

        # home_info
        if filters.delivery_from is not None:
            query = query.where(HomeInfoTable.delivery_to >= filters.delivery_from)
        if filters.delivery_to is not None:
            query = query.where(HomeInfoTable.delivery_from <= filters.delivery_to)
        if filters.floors_min is not None:
            query = query.where(HomeInfoTable.floors_max >= filters.floors_min)
        if filters.floors_max is not None:
            query = query.where(HomeInfoTable.floors_min <= filters.floors_max)
        if filters.roof_height_min is not None:
            query = query.where(HomeInfoTable.roof_height_max >= filters.roof_height_min)
        if filters.roof_height_max is not None:
            query = query.where(HomeInfoTable.roof_height_min <= filters.roof_height_max)
        if filters.wall_type is not None:
            query = query.where(HomeInfoTable.wall_types.overlap(filters.wall_type))
        if filters.trim_type is not None:
            query = query.where(HomeInfoTable.trim_types.overlap(filters.trim_type))
        if filters.bathroom_type is not None:
            query = query.where(HomeInfoTable.bathroom_types.overlap(filters.bathroom_type))
        if filters.payment_type is not None:
            query = query.where(HomeInfoTable.payment_types.overlap(filters.payment_type))
        if filters.agreement_type is not None:
            query = query.where(HomeInfoTable.agreement_types.overlap(filters.agreement_type))

        # plans
        needs_plans_join = any(
            [
                filters.rooms,
                filters.price_from,
                filters.price_to,
                filters.square_total_from,
                filters.square_total_to,
                filters.square_kitchen_from,
                filters.square_kitchen_to,
            ]
        )
        if needs_plans_join:
            query = query.join(BlockTable, HomeTable.uuid == BlockTable.home_uuid).join(
                PlanTable, BlockTable.uuid == PlanTable.block_uuid
            )

            if filters.rooms:
                query = query.where(PlanTable.rooms.in_(filters.rooms))

            if filters.price_from is not None:
                query = query.where(PlanTable.price_base >= filters.price_from)
            if filters.price_to is not None:
                query = query.where(PlanTable.price_base <= filters.price_to)

            if filters.square_total_from is not None:
                query = query.where(PlanTable.square_total >= filters.square_total_from)
            if filters.square_total_to is not None:
                query = query.where(PlanTable.square_total <= filters.square_total_to)

            if filters.square_kitchen_from is not None:
                query = query.where(PlanTable.square_kitchen >= filters.square_kitchen_from)
            if filters.square_total_to is not None:
                query = query.where(PlanTable.square_kitchen <= filters.square_kitchen_to)

            query = query.distinct(HomeTable.uuid)

        # locations
        if filters.location:
            query = query.join(HomeLocationTable, HomeTable.uuid == HomeLocationTable.home_uuid).where(
                HomeLocationTable.location_uuid.in_(filters.location)
            )

        # metro_station
        if filters.metro:
            query = query.join(HomeMetroStationTable, HomeTable.uuid == HomeMetroStationTable.home_uuid).where(
                HomeMetroStationTable.station_uuid.in_(filters.metro)
            )

        return query

    async def get_by_tag(self, filters: HomeTagFilter) -> list[HomeNameResponse]:
        tag = filters.tag
        score = func.word_similarity(tag, HomeTagTable.tag).label("score")

        inner = (
            select(HomeTable.uuid, HomeTable.name, score)
            .select_from(HomeTagTable)
            .join(HomeTable, HomeTable.uuid == HomeTagTable.home_uuid)
        )

        if filters.location:
            inner = inner.join(HomeLocationTable, HomeLocationTable.home_uuid == HomeTable.uuid).where(
                HomeLocationTable.location_uuid.in_(filters.location)
            )

        inner = (
            inner.where(
                or_(
                    HomeTagTable.tag.ilike(f"{tag}%"),
                    literal(tag).op("<%")(HomeTagTable.tag),
                )
            )
            .distinct(HomeTable.uuid)
            .order_by(HomeTable.uuid, score.desc())
        )

        subq = inner.subquery()
        outer = select(subq.c.uuid, subq.c.name).order_by(subq.c.score.desc()).limit(filters.limit)

        result = await self._connection.execute(outer)
        return [HomeNameResponse(uuid=row.uuid, name=row.name) for row in result]
