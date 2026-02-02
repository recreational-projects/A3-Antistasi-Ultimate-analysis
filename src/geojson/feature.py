"""
Partial implementation of GeoJSON spec.

Derived from https://jcristharif.com/msgspec/examples/geojson.html.
"""

import msgspec

from src.types_ import DictNode

Position = tuple[float, float]


class Point(msgspec.Struct, tag=True):
    """Point Geometry type."""

    coordinates: Position


class Feature(msgspec.Struct, tag=True):
    """Feature class."""

    geometry: Point
    properties: DictNode
    id: str | int | None = None
