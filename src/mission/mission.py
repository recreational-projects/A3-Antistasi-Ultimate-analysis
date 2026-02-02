"""`Mission` class."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Self

from attrs import Factory, asdict, define
from cattrs import ClassValidationError, structure

from scripts.constants import BASE_PATH, CONFIG
from src.geojson.load import load_towns_from_dir
from src.mission.mapinfo_hpp_parser import parse_mapinfo_hpp_file
from src.mission.marker import Marker
from src.mission.mission_sqm_parser import get_military_zone_marker_nodes
from src.mission.utils import (
    map_name_from_mission_dir_path,
    normalise_mission_town_name,
    normalise_town_name,
)
from src.utils import pretty_iterable_of_str
from static_data import in_game_data
from static_data.map_index import MAP_INDEX

if TYPE_CHECKING:
    from src.types_ import DictNode

LOGGER = logging.getLogger(__name__)
PATHS = {
    "GRAD_MEH_DIR": (BASE_PATH / CONFIG["GRAD_MEH_DATA_DIR_RELATIVE"]).resolve(),
    "DATA_DIR": (BASE_PATH / CONFIG["INTERMEDIATE_DATA_DIR_RELATIVE"]).resolve(),
}


def analyse_mission(mission_dir: Path) -> str:
    """Analyse a single mission and export intermediate data."""
    mission = Mission.from_data(mission_dir=mission_dir, map_index=MAP_INDEX)
    log_msg = f"'{mission_dir.name}': loaded mission."
    LOGGER.info(log_msg)

    mission.validate_military_zones(in_game_data.MILITARY_ZONES_COUNT)
    grad_meh_map_dirpath = PATHS["GRAD_MEH_DIR"] / mission.map_name
    if not grad_meh_map_dirpath.is_dir():
        grad_meh_map_dirpath = PATHS["GRAD_MEH_DIR"] / mission.map_name.capitalize()

    if not grad_meh_map_dirpath.is_dir():
        log_msg = (
            f"'{mission.map_name}': "
            f"no grad-meh data. Skipping locations validation/correction."
        )
        LOGGER.warning(log_msg)

    else:
        mission.validate_and_correct_towns(grad_meh_map_dirpath / "geojson/locations")

    mission.export(PATHS["DATA_DIR"])
    return mission.map_name


def _towns_from_map_info(map_info: DictNode, map_name: str) -> dict[str, int | None]:
    towns = [
        (name, population)
        for (name, population) in map_info["populations"]
        if name not in map_info["disabled_towns"]
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

    airports: list[Marker] = Factory(list)
    factories: list[Marker] = Factory(list)
    bases: list[Marker] = Factory(list)
    outposts: list[Marker] = Factory(list)
    waterports: list[Marker] = Factory(list)
    resources: list[Marker] = Factory(list)

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
    def from_data(
        cls,
        *,
        mission_dir: Path,
        map_index: dict[str, dict[str, str]],
    ) -> Mission:
        """Return instance from source data."""
        map_name = map_name_from_mission_dir_path(mission_dir)
        map_info = parse_mapinfo_hpp_file(mission_dir / "mapInfo.hpp")
        towns = _towns_from_map_info(map_info, map_name)
        marker_nodes = get_military_zone_marker_nodes(mission_dir / "mission.sqm")

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

        military_zone_markers: dict[str, list[Marker]] = {}
        for prefix in Marker.RELEVANT_PREFIXES:
            military_zone_markers[prefix] = []

        for marker_node in marker_nodes:
            marker = Marker.from_data(marker_node)
            for prefix, list_ in military_zone_markers.items():
                if marker.name.lower().startswith(prefix):
                    list_.append(marker)

        return cls(
            map_name=map_name,
            map_display_name=map_display_name,
            map_url=map_url,
            climate=map_info["climate"],
            towns=towns,
            disabled_towns=map_info["disabled_towns"],
            airports=military_zone_markers["airport"],
            bases=military_zone_markers["milbase"],
            waterports=military_zone_markers["seaport"],
            outposts=military_zone_markers["outpost"],
            factories=military_zone_markers["factory"],
            resources=military_zone_markers["resource"],
        )

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

    @classmethod
    def from_json(cls, file_path: Path) -> Self:
        """Load previously-exported `Mission` data from `path`."""
        with Path.open(file_path, "r", encoding="utf-8") as file:
            try:
                mission = structure(json.load(file), cls)
            except ClassValidationError as err:
                err_msg = f"Error creating `Mission` from JSON: {file_path}."
                raise ValueError(err_msg) from err

        return mission

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
