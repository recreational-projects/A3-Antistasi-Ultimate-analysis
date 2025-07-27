"""`Marker` and supporting classes."""

from typing import ClassVar, Self

from attrs import define

from src.types_ import DictNode


@define
class Position:
    """3D coordinate for `Marker`."""

    x: float
    y: float
    z: float

    @classmethod
    def from_data(
        cls,
        data: list[float],
    ) -> Self:
        """Construct instance from data."""
        return cls(
            x=data[0],
            y=data[2],
            z=data[1],
        )


@define
class Marker:
    """
    Represents a map marker.

    Implemented as a class for future-proofing.
    """

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
    position: Position

    @classmethod
    def from_data(cls, data: DictNode) -> Self:
        """Construct instance from data."""
        return cls(
            name=data["name"],
            position=Position.from_data(data["position"]),
        )
