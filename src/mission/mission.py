"""`Mission` class."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from attrs import Factory, define

from src.mission.file import map_name_from_mission_dir_path
from src.mission.mapinfo_hpp_parser import get_map_info_data
from src.mission.marker import Marker
from src.mission.mission_sqm_parser import get_marker_nodes
from src.static_data.map_index import MAP_INDEX

if TYPE_CHECKING:
    from pathlib import Path


_MAPINFO_FILENAME = "mapInfo.hpp"
_MISSION_FILENAME = "mission.sqm"
_LOGGER = logging.getLogger(__name__)


@define
class Mission:
    """Information about a mission."""

    map_name: str
    """Lower case. Derived from directory name. Assumed unique; used as primary key."""
    climate: str
    """From `mapinfo.hpp`."""
    towns: dict[str, int]
    """Towns in the mission. Derived from `populations` array in
    `mapinfo.hpp`."""
    disabled_towns: list[str]
    """Towns not used in the mission. Derived from `disabledTowns` array in
    `mapinfo.hpp`. NB: not necessarily relevant to the map!"""
    markers: list[Marker] = Factory(list)
    """Relevant subset of markers from `mission.sqm`."""

    @classmethod
    def from_dir(cls, map_dir: Path) -> Mission:
        """Attempt to return instance from a map directory."""
        map_name = map_name_from_mission_dir_path(map_dir)
        map_info = get_map_info_data(map_dir / _MAPINFO_FILENAME)
        populations = map_info["populations"]
        town_names = None if not populations else [p[0] for p in populations]
        if town_names:
            unique_town_names = set()
            duplicated = {
                t
                for t in town_names
                if t in unique_town_names or unique_town_names.add(t)
            }
            if len(unique_town_names) != len(town_names):
                log_msg = (
                    f"'{map_name}': towns_count={len(town_names)} but "
                    f"{len(unique_town_names)} unique.\n"
                    f"{list(duplicated)} duplicated."
                )
                _LOGGER.warning(log_msg)

        marker_nodes = get_marker_nodes(map_dir / _MISSION_FILENAME)

        return cls(
            map_name=map_name.lower(),
            climate=map_info["climate"],
            towns={p[0]: p[1] for p in map_info["populations"]},
            disabled_towns=map_info["disabled_towns"],
            markers=[Marker.from_data(m) for m in marker_nodes],
        )

    @property
    def display_name(self) -> str | None:
        """Return full name if it exists in lookup."""
        return MAP_INDEX.get(self.map_name, {}).get("display_name")

    @property
    def download_url(self) -> str | None:
        """Return URL if it exists in lookup."""
        return MAP_INDEX.get(self.map_name, {}).get("url")

    @property
    def towns_count(self) -> int | None:
        """Enumerate towns."""
        if not self.towns:
            return None
        return len(self.towns)

    @property
    def airports_count(self) -> int:
        """Enumerate airports."""
        return len([m for m in self.markers if m.is_airport])

    @property
    def waterports_count(self) -> int:
        """Enumerate sea/river ports."""
        return len([m for m in self.markers if m.is_waterport])

    @property
    def bases_count(self) -> int:
        """Enumerate bases."""
        return len([m for m in self.markers if m.is_base])

    @property
    def outposts_count(self) -> int:
        """Enumerate outposts."""
        return len([m for m in self.markers if m.is_outpost])

    @property
    def factories_count(self) -> int:
        """Enumerate factories."""
        return len([m for m in self.markers if m.is_factory])

    @property
    def resources_count(self) -> int:
        """Enumerate resources."""
        return len([m for m in self.markers if m.is_resource])

    @property
    def total_objectives_count(self) -> int:
        """Count total objectives (not towns)."""
        return sum(
            (
                self.airports_count,
                self.waterports_count,
                self.bases_count,
                self.outposts_count,
                self.factories_count,
                self.resources_count,
            )
        )

    @property
    def war_level_points(self) -> int | None:
        """Count total war level points."""
        if not self.towns:
            return None

        return sum(
            (
                8 * self.airports_count,
                6 * self.bases_count,
                4 * self.waterports_count,
                len(self.towns),
                2 * self.outposts_count,
                2 * self.resources_count,
                2 * self.factories_count,
            )
        )
