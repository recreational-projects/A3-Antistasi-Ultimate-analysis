"""`Position2D class."""

from __future__ import annotations

from typing import TYPE_CHECKING, Self

from attrs import define

if TYPE_CHECKING:
    from collections.abc import Sequence

    from src.geojson.feature import Point


@define
class Position2D:
    """2D coordinate."""

    x: float
    y: float

    @classmethod
    def from_a3_position(cls, data: Sequence[float]) -> Self:
        """Construct `Position2D` from Arma 3 position, which has xy and xzy forms."""
        return cls(x=data[0], y=data[-1])

    @classmethod
    def from_geojson_point(cls, point: Point) -> Self:
        """Construct `Position2D` from GeoJSON `Point`."""
        return cls(x=point.coordinates[0], y=point.coordinates[1])
