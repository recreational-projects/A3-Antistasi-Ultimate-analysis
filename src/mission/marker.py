"""`Marker` class."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Self

from attrs import define
from cattrs import structure

if TYPE_CHECKING:
    from src.types_ import DictNode


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
    def from_data(cls, data: DictNode) -> Self:
        """Construct instance from data."""
        return structure(data, cls)
