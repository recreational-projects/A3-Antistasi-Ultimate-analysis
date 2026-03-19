"""`Town` class."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Self

from attrs import define

from src.geojson.load import load_towns_from_dir
from src.mission.position_2d import Position2D
from src.utils import pretty_iterable_of_str
from static_data import in_game_data
from static_data.au_mission_overrides import DISABLED_TOWNS_IGNORED_PREFIXES

if TYPE_CHECKING:
    from collections.abc import Collection
    from pathlib import Path

    from src.geojson.feature import Feature
    from src.types_ import DictNode

LOGGER = logging.getLogger(__name__)


def towns_from_map_info(*, map_info: DictNode, logging_map_name: str) -> list[Town]:
    """
    Derive `Town`s from data parsed from `mapinfo.hpp`.

    `Town`s include `population` but not `position`.
    """
    towns = [
        Town(name=name, position=None, population=population)
        for (name, population) in map_info["populations"]
        if name not in map_info["disabled_town_names"]
    ]
    unique_town_names = {t.name for t in towns}
    if len(unique_town_names) != len(towns):
        duplicated_town_names = [t.name for t in towns]
        for t in unique_town_names:
            duplicated_town_names.remove(t)

        log_msg = (
            f"'{logging_map_name}': {len(towns)} in mission but "
            f"{len(unique_town_names)} unique.\n"
            f"{pretty_iterable_of_str(duplicated_town_names)} duplicated."
        )
        LOGGER.warning(log_msg)

    return towns


def _normalise_town_name(name: str) -> str:
    """Normalise town name from map data, for comparison purposes."""
    return name.lower().replace(" ", "")


def _normalise_mission_town_name(name: str) -> str:
    """Normalise town name from mission data, for comparison purposes."""
    for prefix in DISABLED_TOWNS_IGNORED_PREFIXES:
        name = name.removeprefix(prefix)

    return _normalise_town_name(name)


def _towns_from_grad_meh(
    *,
    gm_locations_dir: Path,
    ignore_town_names: Collection[str],
    logging_map_name: str,
) -> list[Town]:
    """
    Derive `Town`s from grad_meh data, ignoring any defined as disabled in the mission.

    `Town`s include `position` but not `population`.
    """
    ignore_town_names = {_normalise_mission_town_name(t): t for t in ignore_town_names}
    gm_towns_lookup = {}

    if not gm_locations_dir.is_dir():
        log_msg = f"'{logging_map_name}': no grad-meh locations data."
        LOGGER.warning(log_msg)
    else:
        _gm_towns = load_towns_from_dir(gm_locations_dir)
        gm_towns_lookup = {
            _normalise_town_name(t.properties["name"]): t for t in _gm_towns
        }

    gm_towns = []
    matched_keys = set()
    for normalised_town_name, town in gm_towns_lookup.items():
        if normalised_town_name in ignore_town_names:
            matched_keys.add(normalised_town_name)
            log_msg = (
                f"Didn't add disabled town: "
                f"'{normalised_town_name}' ('{town.properties['name']}')."
            )
            LOGGER.debug(log_msg)
        else:
            gm_towns.append(Town.from_geojson(town))

    return gm_towns


def compile_towns(
    *,
    map_name: str,
    map_info: DictNode,
    gm_locations_dir: Path,
    ignore_town_names: Collection[str],
) -> list[Town]:
    """Check against map locations and in-game data."""
    mission_defined_towns = towns_from_map_info(
        map_info=map_info, logging_map_name=map_name
    )
    n_mission_defined_towns = len(mission_defined_towns)
    gm_towns = _towns_from_grad_meh(
        gm_locations_dir=gm_locations_dir,
        ignore_town_names=ignore_town_names,
        logging_map_name=map_name,
    )
    n_gm_towns = len(gm_towns)
    n_reference_towns = in_game_data.TOWNS_COUNT.get(map_name)
    log_msg = f"'{map_name}': "

    if mission_defined_towns:
        log_msg += f"used {n_mission_defined_towns} towns defined in mission; "
        if gm_towns:
            if n_mission_defined_towns == n_gm_towns:
                log_msg += "matches map locations data."
                LOGGER.info(log_msg)
            else:
                log_msg += f"doesn't match {n_gm_towns} in map locations data."
                LOGGER.warning(log_msg)

        else:
            log_msg += "no map locations data."
            LOGGER.info(log_msg)

        return mission_defined_towns

    if gm_towns:
        log_msg += (
            f"0 towns defined in mission; used {n_gm_towns} from map locations data."
        )
        LOGGER.info(log_msg)
        return gm_towns

    if n_reference_towns:
        anon_towns = [
            Town(name=f"UNKNOWN_{i}", position=None, population=None)
            for i in range(n_reference_towns)
        ]
        log_msg += (
            f"0 towns defined in mission or map locations data; "
            f"used {n_reference_towns} towns from in-game data."
        )
        LOGGER.warning(log_msg)
        return anon_towns

    log_msg += (
        "0 towns defined in mission, retrieved from map locations data or in-game data."
    )
    LOGGER.error(log_msg)
    return []


@define(kw_only=True)
class Town:
    """Information about a town used in the mission."""

    name: str
    position: Position2D | None
    population: int | None
    """Populated only if mission's `mapinfo.hpp` defines a `populations` array."""

    @classmethod
    def from_geojson(cls, feature: Feature) -> Self:
        """Construct instance from GeoJSON `Feature`."""
        return cls(
            name=feature.properties["name"],
            position=Position2D.from_geojson_point(feature.geometry),
            population=None,
        )
