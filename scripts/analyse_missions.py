"""Analyse each mission in a folder of AU source code and export `Mission`s as JSON."""

from __future__ import annotations

import logging

from rich.progress import track

from scripts.analyse_mission import analyse_mission
from scripts.constants import BASE_PATH, CONFIG
from src.mission.utils import mission_dirs_in_dir
from src.utils import configure_logging, pretty_iterable_of_str
from static_data import in_game_data
from static_data.map_index import MAP_INDEX

LOGGER = logging.getLogger(__name__)
AU_MAPS_DIRPATH = BASE_PATH / CONFIG["AU_SOURCE_DIR_RELATIVE"] / "A3A/addons/maps"
DATA_DIRPATH = BASE_PATH / CONFIG["INTERMEDIATE_DATA_DIR_RELATIVE"]


def analyse_missions() -> None:
    """Analyse all missions."""
    mission_dirs = sorted(mission_dirs_in_dir(AU_MAPS_DIRPATH))
    if not mission_dirs:
        err_msg = "No missions found."
        raise RuntimeError(err_msg)

    log_msg = f"Found {len(mission_dirs)} candidate missions in {AU_MAPS_DIRPATH}."
    LOGGER.info(log_msg)

    DATA_DIRPATH.mkdir(parents=True, exist_ok=True)
    analysed_map_names = set()
    for mission_dir in track(mission_dirs, description="Analysing missions..."):
        map_name = analyse_mission(mission_dir)
        analysed_map_names.add(map_name)

    log_msg = (
        f"Exported data for {len(analysed_map_names)} missions to '{DATA_DIRPATH}'."
    )
    LOGGER.info(log_msg)

    unused_map_index_names = MAP_INDEX.keys() - analysed_map_names
    if unused_map_index_names:
        log_msg = (
            f"{len(unused_map_index_names)} unused map index key(s): "
            f"{pretty_iterable_of_str(list(unused_map_index_names))}."
        )
        LOGGER.warning(log_msg)

    unused_in_game_map_names = (
        in_game_data.MILITARY_ZONES_COUNT.keys() - analysed_map_names
    )
    if unused_in_game_map_names:
        log_msg = (
            f"{len(unused_in_game_map_names)} unused in-game data key(s): "
            f"{pretty_iterable_of_str(list(unused_in_game_map_names))}."
        )
        LOGGER.warning(log_msg)


if __name__ == "__main__":
    configure_logging()
    analyse_missions()
