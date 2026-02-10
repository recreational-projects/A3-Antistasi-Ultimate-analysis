"""`Marker` and supporting classes."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Self

from attrs import define

if TYPE_CHECKING:
    from collections.abc import Sequence

    from src.types_ import DictNode


@define
class Position2D:
    """2D coordinate for `Marker`."""

    x: float
    y: float

    @classmethod
    def from_sequence(
        cls,
        data: Sequence[float],
    ) -> Self:
        """Construct instance from data."""
        return cls(
            x=data[0],
            y=data[2],
        )


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
    position: Position2D

    @classmethod
    def from_data(cls, data: DictNode) -> Self:
        """Construct instance from data."""
        return cls(
            name=data["name"],
            position=Position2D.from_sequence(data["position"]),
        )
