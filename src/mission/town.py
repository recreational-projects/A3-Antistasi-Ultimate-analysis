"""`Town` class."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Self

from attrs import define

from src.position_2d import Position2D
from src.utils import pretty_iterable_of_str

if TYPE_CHECKING:
    from src.geojson.feature import Feature
    from src.types_ import DictNode

LOGGER = logging.getLogger(__name__)


@define(kw_only=True)
class Town:
    """Information about a town used in the mission."""

    name: str
    position: Position2D | None
    population: int | None

    """If the mission defines a `populations` array in `mapinfo.hpp`, it will be used to
    derive town names and population values, removing duplicates and any
    in `disabled_town_names`.

    Otherwise, town names will be derived from grad-meh data if available, but this
    won't include population values, which will be set to `None`."""

    @classmethod
    def from_geojson(cls, feature: Feature) -> Self:
        """Construct instance from GeoJSON `Feature`."""
        return cls(
            name=feature.properties["name"],
            position=Position2D.from_geojson_point(feature.geometry),
            population=None,
        )

    @staticmethod
    def towns_from_map_info(map_info: DictNode, map_name: str) -> list[Town]:
        """Derive towns from data parsed from `mapinfo.hpp`."""
        towns = [
            Town(name=name, population=population, position=None)
            for (name, population) in map_info["populations"]
            if name not in map_info["disabled_town_names"]
        ]
        unique_town_names = {t.name for t in towns}
        if len(unique_town_names) != len(towns):
            duplicated_town_names = [t.name for t in towns]
            for t in unique_town_names:
                duplicated_town_names.remove(t)

            log_msg = (
                f"'{map_name}': {len(towns)} in mission but "
                f"{len(unique_town_names)} unique.\n"
                f"{pretty_iterable_of_str(duplicated_town_names)} duplicated."
            )
            LOGGER.warning(log_msg)

        return towns
