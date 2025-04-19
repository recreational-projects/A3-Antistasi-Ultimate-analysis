"""`Mission` class."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from attrs import Factory, define

from src.mission.mapinfo_hpp_parser import get_map_info_data
from src.mission.marker import Marker
from src.mission.mission_sqm_parser import get_marker_nodes
from src.utils import pretty_iterable_of_str

if TYPE_CHECKING:
    from pathlib import Path


_MAPINFO_FILENAME = "mapInfo.hpp"
_MISSION_FILENAME = "mission.sqm"
_LOGGER = logging.getLogger(__name__)


def map_name_from_mission_dir_path(path: Path) -> str:
    """
    Return map name from mission `path`.

    e.g. `Antistasi_Altis.Altis` -> "Altis".
    """
    return path.suffix.lstrip(".")


@define
class Mission:
    """Information about a mission."""

    map_name: str
    """Lower case. Derived from directory name. Assumed unique; used as primary key."""
    map_display_name: str | None
    """From static reference data. `None` if not available."""
    map_url: str | None
    """From static reference data. `None` if not available."""
    climate: str
    """From `mapinfo.hpp`."""
    towns: dict[str, int]
    """Towns defined in the mission. Derived from `populations` array in
    `mapinfo.hpp`."""
    disabled_towns: list[str]
    """Towns not used in the mission. Derived from `disabledTowns` array in
    `mapinfo.hpp`. NB: not necessarily relevant to the map!"""
    military_objective_markers: list[Marker] = Factory(list)
    """Relevant subset of markers from `mission.sqm`."""

    @classmethod
    def from_data(
        cls,
        *,
        map_dir: Path,
        map_index: dict[str, dict[str, str]],
    ) -> Mission:
        """Return instance from source data."""
        map_name = map_name_from_mission_dir_path(map_dir).lower()
        map_info = get_map_info_data(map_dir / _MAPINFO_FILENAME)
        populations_ = map_info["populations"]
        town_names_ = None if not populations_ else [p[0] for p in populations_]
        if town_names_:
            unique_town_names = set()
            duplicated = {
                t
                for t in town_names_
                # TODO: fix type issue
                if t in unique_town_names or unique_town_names.add(t)  # type: ignore[func-returns-value]
            }
            if len(unique_town_names) != len(town_names_):
                log_msg = (
                    f"'{map_name}': towns_count={len(town_names_)} but "
                    f"{len(unique_town_names)} unique.\n"
                    f"{pretty_iterable_of_str(duplicated)} duplicated."
                )
                _LOGGER.warning(log_msg)

        marker_nodes = get_marker_nodes(map_dir / _MISSION_FILENAME)

        map_display_name, map_url = None, None
        map_lookup = map_index.get(map_name)
        if not map_lookup:
            log_msg = f"'{map_name}': not in map index."
            _LOGGER.warning(log_msg)
        else:
            map_display_name = map_lookup.get("display_name")
            map_url = map_lookup.get("url")
        if not map_display_name:
            log_msg = f"'{map_name}': no `map_display_name` in index."
            _LOGGER.warning(log_msg)
        if not map_url:
            log_msg = f"'{map_name}' no `url` in index."
            _LOGGER.warning(log_msg)

        return cls(
            map_name=map_name,
            map_display_name=map_display_name,
            map_url=map_url,
            climate=map_info["climate"],
            towns={p[0]: p[1] for p in populations_},
            disabled_towns=map_info["disabled_towns"],
            military_objective_markers=[Marker.from_data(m) for m in marker_nodes],
        )

    def verify_vs_in_game_data(self, data: dict[str, dict[str, int]]) -> None:
        """Verify against in-game data."""
        in_game_lookup = data.get(self.map_name)
        if not in_game_lookup:
            log_msg = f"'{self.map_name}': no in-game data."
            _LOGGER.warning(log_msg)
        else:
            for field in in_game_lookup:
                field_value = getattr(self, field)
                reference_value = in_game_lookup.get(field)
                if field_value != reference_value:
                    log_msg = (
                        f"'{self.map_name}': '{field}': "
                        f"{field_value} != reference value: {reference_value}."
                    )
                    _LOGGER.warning(log_msg)
                else:
                    log_msg = f"'{self.map_name}': `{field}` matches in-game data."
                    _LOGGER.debug(log_msg)

    @property
    def towns_count(self) -> int | None:
        """Enumerate towns."""
        if not self.towns:
            return None
        return len(self.towns)

    @property
    def airports_count(self) -> int:
        """Enumerate airports from `self.markers`."""
        return len([m for m in self.military_objective_markers if m.is_airport])

    @property
    def waterports_count(self) -> int:
        """Enumerate sea/river ports from `self.markers`."""
        return len([m for m in self.military_objective_markers if m.is_waterport])

    @property
    def bases_count(self) -> int:
        """Enumerate bases from `self.markers`."""
        return len([m for m in self.military_objective_markers if m.is_base])

    @property
    def outposts_count(self) -> int:
        """Enumerate outposts from `self.markers`."""
        return len([m for m in self.military_objective_markers if m.is_outpost])

    @property
    def factories_count(self) -> int:
        """Enumerate factories from `self.markers`."""
        return len([m for m in self.military_objective_markers if m.is_factory])

    @property
    def resources_count(self) -> int:
        """Enumerate resources from `self.markers`."""
        return len([m for m in self.military_objective_markers if m.is_resource])

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
                2 * self.outposts_count,
                2 * self.resources_count,
                2 * self.factories_count,
                len(self.towns),
            )
        )

    def war_level_points_ratio(self, max_value: int) -> float | None:
        """Fraction of `max_value`."""
        if not self.war_level_points:
            return None

        ratio = self.war_level_points / max_value
        if ratio > 1:
            err_msg = f"War Level Points ratio {ratio} > 1."
            raise ValueError(err_msg)
        return ratio
