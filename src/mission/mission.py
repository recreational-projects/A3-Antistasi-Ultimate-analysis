"""`Mission` class."""

from __future__ import annotations

import json
import logging
from operator import attrgetter
from pathlib import Path
from typing import TYPE_CHECKING

from attrs import Factory, asdict, define
from cattrs import ClassValidationError, structure

from src.geojson.load import load_towns_from_dir
from src.mission.mapinfo_hpp_parser import parse_mapinfo_hpp_file
from src.mission.marker import Marker
from src.mission.mission_sqm_parser import get_marker_nodes
from src.mission.utils import (
    map_name_from_mission_dir_path,
    normalise_mission_town_name,
    normalise_town_name,
)
from src.utils import pretty_iterable_of_str
from static_data import in_game_data

if TYPE_CHECKING:
    from collections.abc import Iterable

    from src.types_ import Node

LOGGER = logging.getLogger(__name__)
_MAPINFO_FILENAME = "mapInfo.hpp"
_MISSION_FILENAME = "mission.sqm"


def _populations_from_map_info(map_info: Node) -> list[tuple[str, int | None]]:
    # List of tuple instead of dict, as may include duplicate town names
    return [
        (p[0], p[1])
        for p in map_info["populations"]
        if p[0] not in map_info["disabled_towns"]
    ]


@define
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

    towns: dict[str, int | None] = Factory(dict)
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

    military_zone_markers: list[Marker] = Factory(list)
    """Relevant subset of markers from `mission.sqm`."""

    @property
    def airports_count(self) -> int:
        """Enumerate airports from `self.markers`."""
        return len([m for m in self.military_zone_markers if m.is_airport])

    @property
    def waterports_count(self) -> int:
        """Enumerate sea/river ports from `self.markers`."""
        return len([m for m in self.military_zone_markers if m.is_waterport])

    @property
    def bases_count(self) -> int:
        """Enumerate bases from `self.markers`."""
        return len([m for m in self.military_zone_markers if m.is_base])

    @property
    def outposts_count(self) -> int:
        """Enumerate outposts from `self.markers`."""
        return len([m for m in self.military_zone_markers if m.is_outpost])

    @property
    def factories_count(self) -> int:
        """Enumerate factories from `self.markers`."""
        return len([m for m in self.military_zone_markers if m.is_factory])

    @property
    def resources_count(self) -> int:
        """Enumerate resources from `self.markers`."""
        return len([m for m in self.military_zone_markers if m.is_resource])

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

    @classmethod
    def from_data(
        cls,
        *,
        mission_dir: Path,
        map_index: dict[str, dict[str, str]],
    ) -> Mission:
        """Return instance from source data."""
        map_name = map_name_from_mission_dir_path(mission_dir)
        map_info = parse_mapinfo_hpp_file(mission_dir / _MAPINFO_FILENAME)
        populations_ = _populations_from_map_info(map_info)  # may contain duplicates
        towns = dict(populations_)  # unique

        if len(towns) != len(populations_):
            duplicated_town_names = [p[0] for p in populations_]
            for t in towns:
                duplicated_town_names.remove(t)

            log_msg = (
                f"'{map_name}': {len(populations_)} in mission but "
                f"{len(towns)} unique.\n"
                f"{pretty_iterable_of_str(duplicated_town_names)} duplicated."
            )
            LOGGER.warning(log_msg)

        marker_nodes = get_marker_nodes(mission_dir / _MISSION_FILENAME)

        map_display_name, map_url = None, None
        if map_name not in map_index:
            log_msg = f"'{map_name}': map index issue: key '{map_name}' not found."
            LOGGER.error(log_msg)
        else:
            map_lookup = map_index[map_name]
            map_display_name = map_lookup.get("display_name")
            map_url = map_lookup.get("url")

        if not map_display_name:
            log_msg = f"'{map_name}': map index issue: no `map_display_name`."
            LOGGER.error(log_msg)
        if not map_url:
            log_msg = f"'{map_name}': map index issue: no `map_url`."
            LOGGER.error(log_msg)

        return cls(
            map_name=map_name,
            map_display_name=map_display_name,
            map_url=map_url,
            climate=map_info["climate"],
            towns=towns,
            disabled_towns=map_info["disabled_towns"],
            military_zone_markers=[Marker.from_data(m) for m in marker_nodes],
        )

    @classmethod
    def missions_from_json(cls, path: Path, excludes: Iterable[str]) -> list[Mission]:
        """Load previously-exported `Missions` data from `path`."""
        json_files = [
            p
            for p in list(path.iterdir())
            if p.suffix == ".json" and p.stem not in excludes
        ]
        log_msg = (
            f"Found {len(json_files)} files in {path} "
            f"ignoring {pretty_iterable_of_str(excludes)}."
        )
        LOGGER.info(log_msg)

        missions = []
        for fp in json_files:
            with Path.open(fp, "r", encoding="utf-8") as file:
                try:
                    mission = structure(json.load(file), Mission)
                except ClassValidationError as err:
                    err_msg = f"Error creating `Mission` from JSON: {fp}."
                    raise ValueError(err_msg) from err
                missions.append(mission)

        log_msg = f"Loaded data for {len(missions)} missions."
        LOGGER.info(log_msg)
        return sorted(missions, key=attrgetter("map_name"))

    def _get_gm_towns(self, gm_locations_dir: Path) -> set[str]:
        """
        Return town names from grad_meh data.

        Discards any defined as disabled in mission.
        """
        disabled_towns_lookup = {
            normalise_mission_town_name(t): t for t in self.disabled_towns
        }
        gm_towns_lookup = {}

        if not gm_locations_dir.is_dir():
            log_msg = f"'{self.map_name}': no grad-meh locations data."
            LOGGER.warning(log_msg)
        else:
            _gm_towns = load_towns_from_dir(gm_locations_dir)
            gm_towns_lookup = {
                normalise_town_name(t.properties["name"]): t.properties["name"]
                for t in _gm_towns
            }

        gm_towns = set()
        matched_keys = set()
        for k, v in gm_towns_lookup.items():
            if k in disabled_towns_lookup:
                matched_keys.add(k)
                log_msg = f"Didn't add disabled: '{k}' ('{v}')."
                LOGGER.debug(log_msg)
            else:
                gm_towns.add(v)
        return gm_towns

    def validate_and_correct_towns(self, gm_locations_dir: Path) -> None:
        """Check against map locations and in-game data."""
        map_name = self.map_name
        gm_towns = self._get_gm_towns(gm_locations_dir)
        in_game_towns_count = in_game_data.TOWNS_COUNT.get(map_name)

        if self.towns and gm_towns:
            if self.towns_count == len(gm_towns):
                log_msg = (
                    f"'{map_name}': used {self.towns_count} towns defined in mission; "
                    f"matches map locations data."
                )
                LOGGER.info(log_msg)
            else:
                log_msg = (
                    f"'{map_name}': used {self.towns_count} towns defined in mission; "
                    f"doesn't match {len(gm_towns)} in map locations data."
                )
                LOGGER.warning(log_msg)
        elif self.towns:
            log_msg = (
                f"'{map_name}': {self.towns_count} towns defined in mission; "
                f"no map locations data."
            )
            LOGGER.info(log_msg)
        elif gm_towns:
            self.towns = dict.fromkeys(gm_towns)
            log_msg = (
                f"'{map_name}': 0 towns defined in mission; used {self.towns_count} "
                f"from map locations data."
            )
            LOGGER.info(log_msg)
        elif in_game_towns_count:
            self.towns = {f"UNKNOWN_{i}": 0 for i in range(in_game_towns_count)}
            log_msg = (
                f"'{map_name}': 0 towns defined in mission or map locations data; "
                f"used {self.towns_count} towns from in-game data."
            )
            LOGGER.warning(log_msg)
        else:
            log_msg = (
                f"'{map_name}': 0 towns defined in mission, retrieved from map "
                f"locations data or in-game data."
            )
            LOGGER.error(log_msg)

    def validate_military_zones(self, data: dict[str, dict[str, int]]) -> None:
        """Check against in-game data; log issues."""
        map_name = self.map_name

        if map_name not in data:
            log_msg = (
                f"'{map_name}': military zone verification issue: "
                f"key '{map_name}' not found."
            )
            LOGGER.error(log_msg)

        in_game_lookup = data.get(self.map_name)
        if not in_game_lookup:
            log_msg = (
                f"'{self.map_name}': military zone verification issue: no data, "
                "so zone counts can't be verified."
            )
            LOGGER.error(log_msg)

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

    def export(self, dir_: Path) -> None:
        """Export the mission as a JSON file."""
        export_filename = f"{self.map_name}.json"
        with Path.open(dir_ / export_filename, "w", encoding="utf-8") as file:
            json.dump(
                asdict(self),
                file,
                ensure_ascii=False,
                indent=4,
            )
            log_msg = f"'{self.map_name}': exported '{export_filename}'."
            LOGGER.info(log_msg)
