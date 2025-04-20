"""
Partial implementation of GeoJSON spec.

Derived from https://jcristharif.com/msgspec/examples/geojson.html.
"""

from typing import Any

import msgspec

Position = tuple[float, float]


class Point(msgspec.Struct, tag=True):
    """Point Geometry type."""

    coordinates: Position


class Feature(msgspec.Struct, tag=True):
    """Feature class."""

    geometry: Point
    properties: dict[str, Any]
    id: str | int | None = None
