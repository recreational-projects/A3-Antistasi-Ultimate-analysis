"""`Town` class."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Self

from attrs import define

from src.geojson.load import load_towns_from_dir
from src.mission.position_2d import Position2D
from src.utils import pretty_iterable_of_str
from static_data import in_game_data
from static_data.au_mission_overrides import (
    DISABLED_TOWNS_IGNORED_PREFIXES,
    GM_TOWNS_TRANSLATIONS,
    MISSION_TOWNS_IGNORED_PREFIXES,
)

if TYPE_CHECKING:
    from collections.abc import Collection
    from pathlib import Path

    from src.geojson.feature import Feature
    from src.types_ import DictNode

LOGGER = logging.getLogger(__name__)


def towns_from_map_populations(
    *, populations: DictNode, logging_map_name: str
) -> list[Town]:
    """
    Derive `Town`s from data parsed from `mapinfo.hpp`.

    `Town`s include `population` but not `position`.
    """
    towns = [
        Town(name=name, position=None, population=population)
        for name, population in populations
    ]
    unique_town_names = {t.name for t in towns}
    if len(unique_town_names) != len(towns):
        duplicated_town_names = [t.name for t in towns]
        for t in unique_town_names:
            duplicated_town_names.remove(t)

        log_msg = (
            f"'{logging_map_name}': {len(towns)} towns defined in mission "
            f"but {len(unique_town_names)} unique. "
            f"{pretty_iterable_of_str(duplicated_town_names)} duplicated."
        )
        LOGGER.warning(log_msg)

    return towns


def _normalise_town_name(name: str) -> str:
    """Normalisation for all town names, for comparison purposes."""
    return name.lower().replace(" ", "")


def _normalise_mission_town_name(name: str) -> str:
    """Normalisation for town names from mission, for comparison purposes."""
    for prefix in MISSION_TOWNS_IGNORED_PREFIXES:
        name = name.removeprefix(prefix)

    return _normalise_town_name(name)


def _normalise_grad_meh_town_name(name: str) -> str:
    """Normalisation for town names from grad-meh data, for comparison purposes."""
    for old, new in GM_TOWNS_TRANSLATIONS.items():
        name = name.replace(old, new)

    return _normalise_town_name(name)


def _normalise_disabled_town_name(name: str) -> str:
    """Normalise disabled town name from mission data, for comparison purposes."""
    for prefix in DISABLED_TOWNS_IGNORED_PREFIXES:
        name = name.removeprefix(prefix)

    return _normalise_town_name(name)


def _towns_from_grad_meh(
    *,
    gm_locations_dir: Path,
    logging_map_name: str,
) -> list[Town]:
    """
    Derive `Town`s (all capital/city/village) from grad_meh data.

    `Town`s include `position` but not `population`.
    """
    if not gm_locations_dir.is_dir():
        log_msg = f"'{logging_map_name}': no grad-meh locations data."
        LOGGER.warning(log_msg)
        return []

    gm_towns_geojson = load_towns_from_dir(gm_locations_dir)
    gm_towns = [Town.from_geojson(t) for t in gm_towns_geojson]
    log_msg = f"'{logging_map_name}': loaded {len(gm_towns)} towns from locations data."
    LOGGER.info(log_msg)

    return gm_towns


def compile_towns(
    *,
    map_name: str,
    map_populations: DictNode,
    gm_locations_dir: Path,
    ignore_town_names: Collection[str],
) -> list[Town]:
    """Compile towns from all sources."""
    log_msg = f"{ignore_town_names=}"
    LOGGER.debug(log_msg)

    mission_defined_towns = towns_from_map_populations(
        populations=map_populations, logging_map_name=map_name
    )
    n_mission_defined_towns = len(mission_defined_towns)
    gm_towns = _towns_from_grad_meh(
        gm_locations_dir=gm_locations_dir,
        logging_map_name=map_name,
    )

    if mission_defined_towns:
        if not gm_towns:
            log_msg = (
                f"No map locations data."
                f"Using {n_mission_defined_towns} mission defined towns "
                f"without positions."
            )
            LOGGER.warning(log_msg)
            return mission_defined_towns

        gm_town_names_normalised = {
            _normalise_grad_meh_town_name(t.name) for t in gm_towns
        }
        log_msg = f"gm_town_names_normalised: {sorted(gm_town_names_normalised)}"
        LOGGER.debug(log_msg)

        mission_defined_town_names_normalised = {
            _normalise_mission_town_name(t.name) for t in mission_defined_towns
        }
        log_msg = (
            f"mission_defined_town_names_normalised: "
            f"{sorted(mission_defined_town_names_normalised)}"
        )
        LOGGER.debug(log_msg)

        relevant_gm_towns = [
            t
            for t in gm_towns
            if _normalise_grad_meh_town_name(t.name)
            in mission_defined_town_names_normalised
        ]
        log_msg = (
            f"Using {len(relevant_gm_towns)} matched grad-meh towns with positions."
        )
        LOGGER.info(log_msg)

        relevant_gm_town_names = sorted(t.name for t in relevant_gm_towns)
        log_msg = f"{relevant_gm_town_names}"
        LOGGER.debug(log_msg)

        return relevant_gm_towns

    n_reference_towns = in_game_data.TOWNS_COUNT.get(map_name)
    if n_reference_towns:
        log_msg = f"Using {n_reference_towns} anonymous towns from in-game count."
        LOGGER.warning(log_msg)
        return [
            Town(name=f"UNKNOWN_{i}", position=None, population=None)
            for i in range(n_reference_towns)
        ]

    log_msg = "No sources for towns."
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
