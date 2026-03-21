"""Analyse a single mission in AU source code and export `Mission` as JSON."""

from __future__ import annotations

import argparse
import logging
from typing import TYPE_CHECKING

from scripts.constants import BASE_PATH, CONFIG
from src.mission.mission import Mission
from src.utils import configure_logging
from static_data import in_game_data
from static_data.map_index import MAP_INDEX

if TYPE_CHECKING:
    from pathlib import Path

LOGGER = logging.getLogger(__name__)
AU_MAPS_DIRPATH = BASE_PATH / CONFIG["AU_SOURCE_DIR_RELATIVE"] / "A3A/addons/maps"
GRAD_MEH_DIRPATH = BASE_PATH / CONFIG["GRAD_MEH_DATA_DIR_RELATIVE"]
DATA_DIRPATH = BASE_PATH / CONFIG["INTERMEDIATE_DATA_DIR_RELATIVE"]


def analyse_mission(mission_dir: Path) -> str:
    """Analyse a single mission and export intermediate data."""
    dir_ = mission_dir.resolve()
    if not dir_.is_dir():
        err_msg = f"No such directory: {dir_}"
        raise RuntimeError(err_msg)

    mission = Mission.from_data(mission_dir=dir_, map_index=MAP_INDEX)
    log_msg = f"'{mission.map_name}': loaded mission."
    LOGGER.info(log_msg)

    mission.validate_military_zones(in_game_data.MILITARY_ZONES_COUNT)
    mission.validate_and_correct_towns(
        GRAD_MEH_DIRPATH / mission.map_name / "geojson/locations"
    )
    mission.export(DATA_DIRPATH)
    return mission.map_name


if __name__ == "__main__":
    configure_logging()
    parser = argparse.ArgumentParser()
    parser.add_argument("map_name")
    args = parser.parse_args()
    analyse_mission(AU_MAPS_DIRPATH / f"Antistasi_{args.map_name}.{args.map_name}")
