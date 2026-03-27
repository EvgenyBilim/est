from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4


@dataclass(frozen=True, kw_only=True)
class DomainEvent:
    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True, kw_only=True)
class HomeCreated(DomainEvent):
    home_uuid: UUID


@dataclass(frozen=True, kw_only=True)
class HomeStructureChanged(DomainEvent):
    home_uuid: UUID
