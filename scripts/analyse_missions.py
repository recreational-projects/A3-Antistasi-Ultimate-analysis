"""Analyse each mission in AU source code and export `Mission` as JSON."""

from __future__ import annotations

import logging

from rich.progress import track

from scripts.constants import PATHS
from src.mission.mission import analyse_single_mission
from src.mission.utils import map_name_from_mission_dir_path, mission_dirs_in_dir
from src.utils import configure_logging, pretty_iterable_of_str
from static_data import au_mission_overrides, in_game_data
from static_data.map_index import MAP_INDEX

LOGGER = logging.getLogger(__name__)


def analyse_missions() -> None:
    """Analyse all missions."""
    configure_logging()
    mission_dirs = sorted(
        d
        for d in mission_dirs_in_dir(PATHS["AU_MAPS_DIR"])
        if d.name not in au_mission_overrides.EXCLUDED_MISSIONS
    )
    if not mission_dirs:
        err_msg = "No missions found."
        raise RuntimeError(err_msg)

    log_msg = (
        f"Ignoring {pretty_iterable_of_str(au_mission_overrides.EXCLUDED_MISSIONS)}. "
        f"Found {len(mission_dirs)} candidate missions in {PATHS['AU_MAPS_DIR']}."
    )
    LOGGER.info(log_msg)

    PATHS["DATA_DIR"].mkdir(parents=True, exist_ok=True)
    analysed_map_names = set()
    for mission_dir in track(mission_dirs, description="Analysing missions..."):
        map_name = map_name_from_mission_dir_path(mission_dir)
        analyse_single_mission(
            au_map_dir=mission_dir,
            map_index=MAP_INDEX,
            grad_meh_map_dir=PATHS["GRAD_MEH_DIR"] / map_name,
            export_dir=PATHS["DATA_DIR"],
        )
        analysed_map_names.add(map_name)

    log_msg = (
        f"Exported data for {len(analysed_map_names)} missions "
        f"to '{PATHS['DATA_DIR']}'."
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
    analyse_missions()
