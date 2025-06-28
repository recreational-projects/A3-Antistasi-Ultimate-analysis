"""`Mission` class."""

from __future__ import annotations

import json
import logging
from logging import DEBUG, ERROR, INFO, WARNING
from operator import attrgetter
from pathlib import Path
from typing import TYPE_CHECKING

from attr import asdict
from attrs import Factory, define
from cattrs import ClassValidationError, structure

from src.geojson.load import load_towns_from_dir
from src.mission.mapinfo_hpp_parser import get_map_info_data
from src.mission.marker import Marker
from src.mission.mission_sqm_parser import get_marker_nodes
from src.mission.utils import (
    map_name_from_mission_dir_path,
    normalise_mission_town_name,
    normalise_town_name,
)
from src.utils import pretty_iterable_of_str

if TYPE_CHECKING:
    from collections.abc import Iterable

_MAPINFO_FILENAME = "mapInfo.hpp"
_MISSION_FILENAME = "mission.sqm"
_LOGGER = logging.getLogger(__name__)


def _log(level: int, message: str) -> None:
    """Wrap log messages."""
    _LOGGER.log(level, message)


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

    towns: dict[str, int | None]
    """Towns in the mission, with population if known.

    If the mission defines a `populations` array in `mapinfo.hpp`, it will be used to
    derive town names and population values, removing duplicates and any
    in `disabled_towns`.

    Otherwise, town names will be derived from grad-meh data if available, but this
    won't include population values, which will be set to `None`.
    """

    disabled_towns: list[str]
    """Towns defined in the mission as not used.

    Derived from `disabledTowns` array in `mapinfo.hpp`. NB: not necessarily relevant
    to the map!"""

    military_zone_markers: list[Marker] = Factory(list)
    """Relevant subset of markers from `mission.sqm`."""

    @classmethod
    def from_data(
        cls,
        *,
        mission_dir: Path,
        map_index: dict[str, dict[str, str]],
    ) -> Mission:
        """Return instance from source data."""
        map_name = map_name_from_mission_dir_path(mission_dir)
        map_info = get_map_info_data(mission_dir / _MAPINFO_FILENAME)
        populations_ = [
            # may include duplicates
            p
            for p in map_info["populations"]
            if p[0] not in map_info["disabled_towns"]
        ]
        if populations_:
            unique_town_names = set()
            duplicated = {
                p[0]
                for p in populations_
                # TODO: fix type issue
                if p[0] in unique_town_names or unique_town_names.add(p[0])  # type: ignore[func-returns-value]
            }
            if len(unique_town_names) != len(populations_):
                _log(
                    WARNING,
                    f"'{map_name}': towns_count={len(populations_)} but "
                    f"{len(unique_town_names)} unique.\n"
                    f"{pretty_iterable_of_str(duplicated)} duplicated.",
                )

        marker_nodes = get_marker_nodes(mission_dir / _MISSION_FILENAME)

        map_display_name, map_url = None, None
        if map_name not in map_index:
            _log(ERROR, f"'{map_name}': map index issue: key '{map_name}' not found.")
        else:
            map_lookup = map_index[map_name]
            map_display_name = map_lookup.get("display_name")
            map_url = map_lookup.get("url")

        if not map_display_name:
            _log(ERROR, f"'{map_name}': map index issue: no `map_display_name`.")
        if not map_url:
            _log(ERROR, f"'{map_name}': map index issue: no `url`.")

        return cls(
            map_name=map_name,
            map_display_name=map_display_name,
            map_url=map_url,
            climate=map_info["climate"],
            towns={p[0]: p[1] for p in sorted(populations_)},
            disabled_towns=map_info["disabled_towns"],
            military_zone_markers=[Marker.from_data(m) for m in marker_nodes],
        )

    def validate_towns_vs_grad_meh_data(self, gm_locations_dir: Path) -> None:
        """TO DO."""
        map_name = self.map_name
        towns_count = self.towns_count
        gm_towns = self._get_gm_towns(gm_locations_dir)

        if not self.towns and not gm_towns:
            _log(
                ERROR,
                f"'{map_name}': no towns defined in mission or in grad_meh data.",
            )
        elif not self.towns and gm_towns:
            self.towns = dict.fromkeys(gm_towns)
            _log(
                INFO,
                f"'{map_name}': no towns defined in mission; {towns_count} from map.",
            )
        elif self.towns and not gm_towns:
            _log(
                INFO,
                f"'{map_name}': {towns_count} towns defined in mission; "
                f"no grad-meh data.",
            )
        elif len(self.towns) != len(gm_towns):
            _log(
                WARNING,
                f"'{map_name}': {towns_count} towns defined in mission; "
                f"doesn't match {len(gm_towns)} in grad-meh data.",
            )
        else:
            _log(
                INFO,
                f"'{map_name}': {towns_count} towns defined in mission; "
                f"matches grad-meh data.",
            )

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
            _log(WARNING, f"'{self.map_name}': no grad-meh locations data.")
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
                _log(DEBUG, f"Didn't add disabled: '{k}' ('{v}').")
            else:
                gm_towns.add(v)
        return gm_towns

    @classmethod
    def missions_from_json(cls, path: Path, excludes: Iterable[str]) -> list[Mission]:
        """Load previously-exported `Missions` data from `path`."""
        json_files = [
            p
            for p in list(path.iterdir())
            if p.suffix == ".json" and p.stem not in excludes
        ]
        _log(
            INFO,
            f"Found {len(json_files)} files in {path} "
            f"ignoring {pretty_iterable_of_str(excludes)}.",
        )

        missions = []
        for fp in json_files:
            with Path.open(fp, "r", encoding="utf-8") as file:
                try:
                    mission = structure(json.load(file), Mission)
                except ClassValidationError as err:
                    err_msg = f"Error creating `Mission` from JSON: {fp}."
                    raise ValueError(err_msg) from err
                missions.append(mission)

        _log(INFO, f"Loaded data for {len(missions)} missions.")
        return sorted(missions, key=attrgetter("map_name"))

    @property
    def towns_count(self) -> int | None:
        """Enumerate towns."""
        if not self.towns:
            return None
        return len(self.towns)

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

    def verify_pois_vs_in_game_data(self, data: dict[str, dict[str, int]]) -> None:
        """Verify against in-game data."""
        map_name = self.map_name

        if map_name not in data:
            _log(
                ERROR,
                f"'{map_name}': military zone verification issue: "
                f"key '{map_name}' not found.",
            )

        in_game_lookup = data.get(self.map_name)
        if not in_game_lookup:
            _log(
                ERROR,
                f"'{self.map_name}': military zone verification issue: "
                "No data, so zone counts can't be verified.",
            )

        else:
            for field in in_game_lookup:
                field_value = getattr(self, field)
                reference_value = in_game_lookup.get(field)
                if field_value != reference_value:
                    _log(
                        ERROR,
                        f"'{self.map_name}': military zone verification issue: "
                        f"{field}': {field_value} != "
                        f"reference value: {reference_value}.",
                    )
                else:
                    _log(DEBUG, f"'{self.map_name}': `{field}` matches in-game data.")

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
            _log(INFO, f"'{self.map_name}': exported '{export_filename}'.")
