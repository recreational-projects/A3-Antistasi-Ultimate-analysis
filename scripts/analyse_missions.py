"""Analyse each mission in AU source code and export `Mission` as JSON."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from rich.progress import track

from scripts.constants import BASE_PATH, CONFIG
from src.mission.mission import Mission
from src.mission.utils import mission_dirs_in_dir
from src.utils import configure_logging, pretty_iterable_of_str
from static_data import au_mission_overrides, in_game_data
from static_data.map_index import MAP_INDEX

if TYPE_CHECKING:
    from pathlib import Path

LOGGER = logging.getLogger(__name__)
PATHS = {
    "AU_MAPS_DIR": (
        BASE_PATH / CONFIG["AU_SOURCE_DIR_RELATIVE"] / "A3A/addons/maps"
    ).resolve(),
    "GRAD_MEH_DIR": (BASE_PATH / CONFIG["GRAD_MEH_DATA_DIR_RELATIVE"]).resolve(),
    "DATA_DIR": (BASE_PATH / CONFIG["INTERMEDIATE_DATA_DIR_RELATIVE"]).resolve(),
}


def _analyse_mission(mission_dir: Path) -> str:
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


def analyse_missions() -> None:
    """Analyse all missions."""
    configure_logging()
    for name, path in PATHS.items():
        if not path.is_dir():
            err_msg = f"{name}: {path} not found"
            raise RuntimeError(err_msg)

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
        map_name = _analyse_mission(mission_dir)
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
