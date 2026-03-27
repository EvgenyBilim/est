from enum import StrEnum, IntEnum


class BaseIntEnum(IntEnum):
    @classmethod
    def values(cls) -> list[int]:
        return [item.value for item in cls]


class BaseStrEnum(StrEnum):
    @classmethod
    def values(cls) -> list[str]:
        return [item.value for item in cls]


class HousingClassEnum(BaseStrEnum):
    ECONOMIC = "economic"
    COMFORT = "comfort"
    BUSINESS = "business"
    PREMIUM = "premium"


class WallTypeEnum(BaseStrEnum):
    BRICK_MONOLITH = "brick_monolith"
    MONOLITH = "monolith"
    BRICK = "brick"
    PANEL = "panel"


class RoomTypeEnum(BaseIntEnum):
    STUDIO = 0
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    MORE = 6
    FREE = 7


class TrimTypeEnum(BaseStrEnum):
    NO_TRIM = "no_trim"
    PARTIAL = "partial"
    FULL = "full"


class BathroomTypeEnum(BaseStrEnum):
    UNIFIED = "unified"
    SEPARATED = "separated"
    TWO_AND_MORE = "two_and_more"


class LocationTypeEnum(BaseStrEnum):
    COUNTRY = "country"
    REGION = "region"
    CITY = "city"
    DISTRICT = "district"


class ParkingTypeEnum(BaseStrEnum):
    OPEN = "open"
    COVERED = "covered"
    UNDERGROUND = "underground"


class MetroTimeUnitTypeEnum(BaseStrEnum):
    MIN = "min"
    HOUR = "hour"


class TransportTypeEnum(BaseStrEnum):
    ON_FOOT = "on_foot"
    TRANSPORT = "transport"


class GalleryImageTypeEnum(BaseStrEnum):
    PREVIEW = "preview"
    FULL = "full"
