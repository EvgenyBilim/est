from dataclasses import dataclass
from typing import Annotated

from fastapi import Query


@dataclass
class DeveloperNameFilter:
    name: Annotated[str, Query(min_length=2)]
    limit: int = 10

    def __post_init__(self):
        self.name = self.name.strip()
