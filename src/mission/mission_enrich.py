"""Analyse missions in source code and export intermediate data."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from src.geojson.load import load_towns_from_dir
from src.mission.utils import normalise_mission_town_name, normalise_town_name
from static_data import in_game_data

if TYPE_CHECKING:
    from pathlib import Path

    from src.mission.mission import Mission

LOGGER = logging.getLogger(__name__)


def _get_gm_towns(*, mission: Mission, gm_locations_dir: Path) -> set[str]:
    """
    Return town names from grad_meh data.

    Discards any defined as disabled in mission.
    """
    disabled_towns_lookup = {
        normalise_mission_town_name(t): t for t in mission.disabled_towns
    }
    gm_towns_lookup = {}

    if not gm_locations_dir.is_dir():
        log_msg = f"'{mission.map_name}': no grad-meh locations data."
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


def validate_and_correct_towns(mission: Mission, gm_locations_dir: Path) -> None:
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


def validate_military_zones(mission: Mission, data: dict[str, dict[str, int]]) -> None:
    """Check against in-game data; log issues."""
    map_name = mission.map_name

    if map_name not in data:
        log_msg = (
            f"'{map_name}': military zone verification issue: "
            f"key '{map_name}' not found."
        )
        LOGGER.error(log_msg)

    in_game_lookup = data.get(mission.map_name)
    if not in_game_lookup:
        log_msg = (
            f"'{mission.map_name}': military zone verification issue: no data, "
            "so zone counts can't be verified."
        )
        LOGGER.error(log_msg)

    else:
        for field in in_game_lookup:
            field_value = getattr(mission, field)
            reference_value = in_game_lookup.get(field)
            if field_value != reference_value:
                log_msg = (
                    f"'{mission.map_name}': military zone verification issue: "
                    f"{field}': {field_value} != reference value: "
                    f"{reference_value}."
                )
                LOGGER.error(log_msg)
            else:
                log_msg = f"'{mission.map_name}': `{field}` matches in-game data."
                LOGGER.debug(log_msg)
