"""Load data from GeoJSON files."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from arma3_offline_map_lib.grad_meh.geojson import (
    geojson_gz_files_in_dir,
    load_features_from_file,
)

from src.static_data import in_game_data
from src.static_data.au_mission_overrides import DISABLED_TOWNS_IGNORED_PREFIXES

if TYPE_CHECKING:
    from pathlib import Path

    from arma3_offline_map_lib.grad_meh.geojson import Feature

    from .mission import Mission


LOGGER = logging.getLogger(__name__)


def validate_and_correct_towns(*, mission: Mission, gm_locations_dir: Path) -> None:
    """Check against map locations and in-game data."""
    map_name = mission.map_name
    gm_towns = _get_gm_towns(mission=mission, gm_locations_dir=gm_locations_dir)
    in_game_towns_count = in_game_data.TOWNS_COUNT.get(map_name)

    if mission.towns and gm_towns:
        if mission.towns_count == len(gm_towns):
            log_msg = (
                f"'{map_name}': used {mission.towns_count} towns defined in mission; "
                f"matches map locations data."
            )
            LOGGER.info(log_msg)
        else:
            log_msg = (
                f"'{map_name}': used {mission.towns_count} towns defined in mission; "
                f"doesn't match {len(gm_towns)} in map locations data."
            )
            LOGGER.warning(log_msg)

    elif mission.towns:
        log_msg = (
            f"'{map_name}': {mission.towns_count} towns defined in mission; "
            f"no map locations data."
        )
        LOGGER.info(log_msg)
    elif gm_towns:
        mission.towns = dict.fromkeys(gm_towns)
        log_msg = (
            f"'{map_name}': 0 towns defined in mission; used {mission.towns_count} "
            f"from map locations data."
        )
        LOGGER.info(log_msg)
    elif in_game_towns_count:
        mission.towns = {f"UNKNOWN_{i}": 0 for i in range(in_game_towns_count)}
        log_msg = (
            f"'{map_name}': 0 towns defined in mission or map locations data; "
            f"used {mission.towns_count} towns from in-game data."
        )
        LOGGER.warning(log_msg)
    else:
        log_msg = (
            f"'{map_name}': 0 towns defined in mission, retrieved from map "
            f"locations data or in-game data."
        )
        LOGGER.error(log_msg)


def _get_gm_towns(*, mission: Mission, gm_locations_dir: Path) -> set[str]:
    """
    Return town names from grad_meh data.

    Discards any defined as disabled in mission.
    """
    disabled_towns_lookup = {
        _normalise_mission_town_name(t): t for t in mission.disabled_towns
    }
    gm_towns_lookup = {}

    if not gm_locations_dir.is_dir():
        log_msg = f"'{mission.map_name}': no grad-meh locations data."
        LOGGER.warning(log_msg)
    else:
        _gm_towns = _load_towns_from_dir(gm_locations_dir)
        gm_towns_lookup = {
            _normalise_town_name(t.properties["name"]): t.properties["name"]
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


def _load_towns_from_dir(path: Path) -> list[Feature]:
    """
    Load town locations (subset of GeoJSON features) from files in a directory.

    Directory must exist.

    Returns:
         `dict`. Keys are `FILENAME_STEM` for each relevant
         `path/{FILENAME_STEM}.geojson.gz`.

    """
    towns: list[Feature] = []

    filepaths = [
        fp
        for fp in geojson_gz_files_in_dir(path)
        if fp.stem.removesuffix(".geojson")
        in ("namecitycapital", "namecity", "namevillage")
    ]
    for fp in filepaths:
        locations = load_features_from_file(fp)
        towns.extend(locations)

    return towns


def _normalise_mission_town_name(name: str) -> str:
    """Normalise town name from mission data, for comparison purposes."""
    for prefix in DISABLED_TOWNS_IGNORED_PREFIXES:
        name = name.removeprefix(prefix)

    return _normalise_town_name(name)


def _normalise_town_name(name: str) -> str:
    """Normalise town name from map data, for comparison purposes."""
    return name.lower().replace(" ", "")
