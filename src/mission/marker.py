"""`Marker` class."""

from __future__ import annotations

from typing import TYPE_CHECKING, Self

from attrs import define

from src.position_2d import Position2D

if TYPE_CHECKING:
    from src.types_ import DictNode


RELEVANT_MARKER_PREFIXES = {
    # case-insensitive
    "airport",
    "factory",
    "milbase",
    "outpost",
    "resource",
    "seaport",
}


@define
class Marker:
    """Represents a map marker."""

    name: str
    position: Position2D

    @classmethod
    def from_mission_data(cls, data: DictNode) -> Self:
        """Construct `Marker` from data parsed from `mission.sqm`."""
        return cls(
            name=data["name"],
            position=Position2D.from_a3_position(data["position"]),
        )
