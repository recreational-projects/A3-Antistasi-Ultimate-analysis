"""`MapInformation` class."""

from __future__ import annotations

from typing import TYPE_CHECKING

from attrs import Factory, define

from src.marker import Marker
from src.parse.mapinfo_hpp_parser import get_map_info_data
from src.parse.mission_sqm_parser import get_marker_nodes
from src.utils import map_name_from_path

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path

    from src.parse.mission_sqm_parser import JSONNode

_MAPINFO_FILENAME = "mapInfo.hpp"
_MISSION_FILENAME = "mission.sqm"


@define
class MapInformation:
    """Information about a map."""

    map_name: str
    climate: str | None = None
    towns_count: int | None = None
    """Explicit `None` if no towns found."""
    markers: list[Marker] = Factory(list)
    """Relevant subset of markers from `mission.sqm`."""

    @classmethod
    def from_data(
        cls,
        map_name: str,
        climate_: str | None,
        populations_: Sequence[tuple[str, int]],
        markers_: Sequence[JSONNode],
    ) -> MapInformation:
        """Construct instance from parsed data, ignoring anything not needed."""
        towns_count_ = None if not populations_ else len(populations_)
        return cls(
            map_name=map_name,
            climate=climate_,
            towns_count=towns_count_,
            markers=[Marker.from_data(m) for m in markers_],
        )

    @classmethod
    def from_files(cls, map_dir: Path) -> MapInformation:
        """Attempt to return instance from a map directory."""
        map_name = map_name_from_path(map_dir)
        marker_nodes = get_marker_nodes(map_dir / _MISSION_FILENAME)
        map_info = get_map_info_data(map_dir / _MAPINFO_FILENAME)

        return MapInformation.from_data(
            map_name=map_name,
            climate_=map_info["climate"],
            populations_=map_info["populations"],
            markers_=marker_nodes,
        )

    @property
    def airports_count(self) -> int:
        """Enumerate airports."""
        return len([m for m in self.markers if m.is_airport])

    @property
    def bases_count(self) -> int:
        """Enumerate bases."""
        return len([m for m in self.markers if m.is_base])

    @property
    def factories_count(self) -> int:
        """Enumerate factories."""
        return len([m for m in self.markers if m.is_factory])

    @property
    def outposts_count(self) -> int:
        """Enumerate outposts."""
        return len([m for m in self.markers if m.is_outpost])

    @property
    def resources_count(self) -> int:
        """Enumerate resources."""
        return len([m for m in self.markers if m.is_resource])

    @property
    def waterports_count(self) -> int:
        """Enumerate sea/river ports."""
        return len([m for m in self.markers if m.is_waterport])

    @property
    def objectives_count(self) -> int:
        """Enumerate objectives."""
        return sum(
            (
                self.airports_count,
                self.bases_count,
                self.factories_count,
                self.outposts_count,
                self.resources_count,
                self.waterports_count,
            )
        )
