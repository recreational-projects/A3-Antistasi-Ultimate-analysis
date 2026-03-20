"""`Mission` class."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Self

from attrs import Factory, asdict, define
from cattrs import ClassValidationError, structure

from src.mission.mapinfo_hpp_parser import parse_mapinfo_hpp_file
from src.mission.marker import Marker
from src.mission.mission_sqm_parser import get_military_zone_markers
from src.mission.town import Town, compile_towns
from static_data import in_game_data
from static_data.map_index import MAP_INDEX

if TYPE_CHECKING:
    from collections.abc import Mapping

LOGGER = logging.getLogger(__name__)


def analyse_mission(
    *, map_name: str, mission_dir: Path, grad_meh_map_dir: Path, export_dir: Path
) -> None:
    """Analyse a single mission and export intermediate data."""
    if map_name not in MAP_INDEX:
        log_msg = f"'{map_name}': map index issue: key '{map_name}' not found."
        LOGGER.error(log_msg)

    mission = Mission.from_source_data(
        map_name=map_name,
        mission_dir=mission_dir,
        grad_meh_map_dir=grad_meh_map_dir,
        reference_data=MAP_INDEX[map_name],
    )
    mission.validate_military_zones(in_game_data.MILITARY_ZONES_COUNT)
    mission.export(export_dir)


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

    towns: list[Town] = Factory(list)
    """Towns used in the mission."""

    disabled_town_names: list[str] = Factory(list)
    """Towns defined in the mission as not used.

    From mission's `mapinfo.hpp` `disabledTowns` array.
    NB: not necessarily relevant to the map!"""

    airports: list[Marker] = Factory(list)
    """From `mission.sqm`."""
    factories: list[Marker] = Factory(list)
    """From `mission.sqm`."""
    bases: list[Marker] = Factory(list)
    """From `mission.sqm`."""
    outposts: list[Marker] = Factory(list)
    """From `mission.sqm`."""
    waterports: list[Marker] = Factory(list)
    """From `mission.sqm`."""
    resources: list[Marker] = Factory(list)
    """From `mission.sqm`."""

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
    def from_source_data(
        cls,
        *,
        map_name: str,
        mission_dir: Path,
        grad_meh_map_dir: Path,
        reference_data: dict[str, str],
    ) -> Mission:
        """Return instance from AU mission data and reference data."""
        map_display_name = reference_data["display_name"]
        if not map_display_name:
            log_msg = f"'{map_name}': map index issue: no `map_display_name`."
            LOGGER.error(log_msg)

        map_url = reference_data["url"]
        if not map_url:
            log_msg = f"'{map_name}': map index issue: no `map_url`."
            LOGGER.error(log_msg)

        map_info = parse_mapinfo_hpp_file(mission_dir / "mapInfo.hpp")
        military_zone_markers = get_military_zone_markers(mission_dir / "mission.sqm")
        log_msg = f"'{map_name}': loaded AU source data."
        LOGGER.info(log_msg)

        towns = compile_towns(
            map_name=map_name,
            map_populations=map_info["populations"],
            gm_locations_dir=grad_meh_map_dir / "geojson/locations",
            ignore_town_names=map_info["disabled_town_names"],
        )
        return cls(
            map_name=map_name,
            map_display_name=map_display_name,
            map_url=map_url,
            climate=map_info["climate"],
            towns=towns,
            disabled_town_names=map_info["disabled_town_names"],
            airports=military_zone_markers["airport"],
            bases=military_zone_markers["milbase"],
            waterports=military_zone_markers["seaport"],
            outposts=military_zone_markers["outpost"],
            factories=military_zone_markers["factory"],
            resources=military_zone_markers["resource"],
        )

    def export(self, dir_: Path) -> None:
        """Export the mission as a JSON file in `dir_`."""
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

    def validate_military_zones(self, data: Mapping[str, dict[str, int]]) -> None:
        """Check against in-game data; log issues."""
        map_name_ = self.map_name
        if map_name_ not in data:
            log_msg = (
                f"'{map_name_}': military zone verification issue: "
                f"key '{map_name_}' not found."
            )
            LOGGER.error(log_msg)

        in_game_lookup = data.get(map_name_)
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
                        f"'{map_name_}': military zone verification issue: "
                        f"{field}': {field_value} != reference value: "
                        f"{reference_value}."
                    )
                    LOGGER.error(log_msg)
                else:
                    log_msg = f"'{map_name_}': `{field}` matches in-game data."
                    LOGGER.debug(log_msg)
