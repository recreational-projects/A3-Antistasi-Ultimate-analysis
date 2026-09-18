"""`Mission` class."""

from __future__ import annotations

import json
import logging
from collections.abc import Mapping
from pathlib import Path
from typing import TYPE_CHECKING, Self

from arma3_offline_map_lib.mission.mission_sqm import Marker, MissionSqm
from attrs import Factory, asdict, define
from cattrs import ClassValidationError, structure

from .mapinfo_hpp_parser import MapInfoHppData
from .utils import map_name_from_mission_dir_path, pretty_iterable_of_str

if TYPE_CHECKING:
    from .types_ import MappingNode

LOGGER = logging.getLogger(__name__)

_ATTRIBUTES_TO_MARKER_PREFIXES = {
    # Case-insensitive. Values are used to filter markers of interest.
    "airports": "airport",
    "factories": "factory",
    "bases": "milbase",
    "outposts": "outpost",
    "resources": "resource",
    "waterports": "seaport",
    "redfor_support_corridor": "csat_carrier",
    "_nato_carrier": "nato_carrier",  # not attribute
    "_respawn_west": "respawn_west",  # not attribute
}


@define(kw_only=True)
class Mission:
    """Information about a mission."""

    map_name: str
    """
    Derived from directory name and normalised to lower case.

    Assumed unique; used as primary key."""

    map_display_name: str | None
    """
    Full name of map, generally as it appears in Steam app/workshop titles/text.

    From static reference data. `None` if not available."""

    map_url: str | None
    """
    URL at which the map can be downloaded.

    From static reference data. `None` if not available."""

    climate: str
    """From `mapinfo.hpp`."""

    towns: Mapping[str, int | None] = Factory(Mapping)
    """Towns in the mission, with population if known.

    If the mission defines a `populations` array in `mapinfo.hpp`, it will be used to
    derive town names and population values, removing duplicates and any
    in `disabled_towns`.

    Otherwise, town names will be derived from grad-meh data if available, but this
    won't include population values, which will be set to `None`.
    """

    disabled_towns: list[str] = Factory(list)
    """Towns defined in the mission as not used.

    Derived from `disabledTowns` array in `mapinfo.hpp`. NB: not necessarily relevant
    to the map!"""

    airports: list[Marker] = Factory(list)
    """Airport markers from `mission.sqm`."""
    factories: list[Marker] = Factory(list)
    """Factory markers from `mission.sqm."""
    bases: list[Marker] = Factory(list)
    """Base markers from `mission.sqm."""
    outposts: list[Marker] = Factory(list)
    """Outpost markers from `mission.sqm."""
    resources: list[Marker] = Factory(list)
    """Resource markers from `mission.sqm`."""
    waterports: list[Marker] = Factory(list)
    """Waterport (sea/river port) markers from `mission.sqm`."""
    blufor_support_corridor: Marker
    """BLUFOR support corridor marker from `mission.sqm`."""
    redfor_support_corridor: Marker
    """REDFOR support corridor marker from `mission.sqm`."""

    @property
    def airports_count(self) -> int:
        """Enumerate airports."""
        return len(self.airports)

    @property
    def waterports_count(self) -> int:
        """Enumerate sea/river ports."""
        return len(self.waterports)

    @property
    def bases_count(self) -> int:
        """Enumerate bases."""
        return len(self.bases)

    @property
    def outposts_count(self) -> int:
        """Enumerate outposts."""
        return len(self.outposts)

    @property
    def factories_count(self) -> int:
        """Enumerate factories."""
        return len(self.factories)

    @property
    def resources_count(self) -> int:
        """Enumerate resources."""
        return len(self.resources)

    @property
    def total_military_zones_count(self) -> int:
        """Count total military zones (not towns)."""
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
    def towns_count(self) -> int | None:
        """Enumerate towns."""
        if not self.towns:
            return None

        return len(self.towns)

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
                len(self.towns),  # as self.towns_count may be None
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

    @classmethod
    def from_data(cls, *, mission_dir: Path, map_index: MappingNode) -> Mission | None:
        """Return instance from AU mission data and reference map index."""
        map_name = map_name_from_mission_dir_path(mission_dir)
        if map_name not in map_index:
            log_msg = f"'{map_name}': map index issue: key '{map_name}' not found."
            LOGGER.error(log_msg)
            return None

        map_lookup = map_index[map_name]
        map_display_name = map_lookup.get("display_name")
        map_url = map_lookup.get("url")
        if not map_display_name:
            log_msg = f"'{map_name}': map index issue: no `map_display_name`."
            LOGGER.error(log_msg)

        if not map_url:
            log_msg = f"'{map_name}': map index issue: no `map_url`."
            LOGGER.error(log_msg)

        parsed_map_info = MapInfoHppData.from_file(mission_dir / "mapInfo.hpp")
        mission_sqm = MissionSqm.from_file(mission_dir / "mission.sqm")
        log_msg = f"'{map_name}': parsed AU source data."
        LOGGER.info(log_msg)

        towns = _towns_from_map_info(parsed_map_info, map_name)
        markers = _markers_by_prefix(mission_sqm.markers)
        if markers["nato_carrier"]:
            blufor_support_corridor_marker = markers["nato_carrier"][0]
        elif markers["respawn_west"]:  # handles 'abramia' special case
            blufor_support_corridor_marker = markers["respawn_west"][0]
            log_msg = f"'{map_name}': BLUFOR support corridor marker is 'respawn_west'."
            LOGGER.warning(log_msg)
        else:
            err_msg = f"'{map_name}': BLUFOR support corridor marker not found."
            raise ValueError(err_msg)

        return cls(
            map_name=map_name,
            map_display_name=map_display_name,
            map_url=map_url,
            climate=parsed_map_info.climate,
            towns=towns,
            disabled_towns=parsed_map_info.disabled_town_names,
            airports=markers[_ATTRIBUTES_TO_MARKER_PREFIXES["airports"]],
            bases=markers[_ATTRIBUTES_TO_MARKER_PREFIXES["bases"]],
            waterports=markers[_ATTRIBUTES_TO_MARKER_PREFIXES["waterports"]],
            outposts=markers[_ATTRIBUTES_TO_MARKER_PREFIXES["outposts"]],
            factories=markers[_ATTRIBUTES_TO_MARKER_PREFIXES["factories"]],
            resources=markers[_ATTRIBUTES_TO_MARKER_PREFIXES["resources"]],
            blufor_support_corridor=blufor_support_corridor_marker,
            redfor_support_corridor=markers[
                _ATTRIBUTES_TO_MARKER_PREFIXES["redfor_support_corridor"]
            ][0],
        )

    def export_json(self, dir_: Path) -> None:
        """Export the mission as a JSON file."""
        export_filename = f"{self.map_name}.json"
        with Path.open(dir_ / export_filename, "w", encoding="utf-8") as file:
            try:
                json.dump(
                    asdict(self),
                    file,
                    ensure_ascii=False,
                    indent=4,
                )
                log_msg = f"'{self.map_name}': exported '{export_filename}'."
                LOGGER.info(log_msg)
            except Exception as err:
                err_msg = f"Error exporting '{self.map_name}': {err}"
                LOGGER.exception(err_msg)

    @classmethod
    def from_json(cls, file_path: Path) -> Self:
        """Load `Mission` from previously-exported JSON file."""
        with Path.open(file_path, "r", encoding="utf-8") as file:
            try:
                mission = cls._from_json_data(json.load(file))
            except ClassValidationError as err:
                err_msg = f"Error creating `Mission` from JSON: {file_path}."
                raise ValueError(err_msg) from err

        return mission

    @classmethod
    def _from_json_data(cls, data: MappingNode) -> Self:
        return structure(data, cls)

    def validate_military_zones(self, data: dict[str, dict[str, int]]) -> None:
        """Check against in-game data; log issues."""
        in_game_lookup = data.get(self.map_name)
        if not in_game_lookup:
            log_msg = (
                f"'{self.map_name}': "
                "no data in `src.static_data.in_game_data`, "
                "so military zone counts can't be verified."
            )
            LOGGER.warning(log_msg)

        else:
            for field in in_game_lookup:
                field_value = getattr(self, field)
                reference_value = in_game_lookup.get(field)
                if field_value != reference_value:
                    log_msg = (
                        f"'{self.map_name}': military zone verification issue: "
                        f"{field}': {field_value} != reference value: "
                        f"{reference_value}."
                    )
                    LOGGER.error(log_msg)
                else:
                    log_msg = f"'{self.map_name}': `{field}` matches in-game data."
                    LOGGER.debug(log_msg)


def _towns_from_map_info(
    map_info: MapInfoHppData, map_name: str
) -> Mapping[str, int | None]:
    towns = [
        p for p in map_info.populations if p[0] not in map_info.disabled_town_names
    ]
    unique_towns = dict(towns)

    if len(unique_towns) != len(towns):
        duplicated_town_names = [p[0] for p in towns]
        for t in unique_towns:
            duplicated_town_names.remove(t)

        log_msg = (
            f"'{map_name}': {len(towns)} in mission but "
            f"{len(unique_towns)} unique.\n"
            f"{pretty_iterable_of_str(duplicated_town_names)} duplicated."
        )
        LOGGER.warning(log_msg)

    return unique_towns


def _markers_by_prefix(marker_list: list[Marker]) -> dict[str, list[Marker]]:
    """Derive `dict` of relevant markers, keyed by prefix."""
    marker_dict: dict[str, list[Marker]] = {
        prefix: [] for prefix in _ATTRIBUTES_TO_MARKER_PREFIXES.values()
    }
    for marker in marker_list:
        for prefix, markers in marker_dict.items():
            if marker.name and marker.name.lower().startswith(prefix):
                markers.append(marker)

    return marker_dict
