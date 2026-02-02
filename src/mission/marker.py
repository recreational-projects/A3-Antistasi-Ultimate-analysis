"""`Marker` class."""

from typing import ClassVar, Self

from attrs import define
from cattrs import structure

from src.types_ import Node


@define
class Marker:
    """Represents a map marker."""

    RELEVANT_PREFIXES: ClassVar = {
        # case-insensitive
        "airport",
        "factory",
        "milbase",
        "outpost",
        "resource",
        "seaport",
    }

    name: str

    @classmethod
    def from_data(cls, data: Node) -> Self:
        """Construct instance from data."""
        return structure(data, cls)
