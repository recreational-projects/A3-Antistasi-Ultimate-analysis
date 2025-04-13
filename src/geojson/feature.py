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


Geometry = Point  # TODO


class Feature(msgspec.Struct, tag=True):
    """Feature class."""

    geometry: Geometry | None = None
    properties: dict[str, Any] | None = None  # additional dict type params
    id: str | int | None = None
