"""Analyse missions in source code and export intermediate data."""

import logging
from logging import INFO, WARNING
from pathlib import Path

from rich.logging import RichHandler
from rich.progress import track

from src.mission.mission import Mission
from src.mission.utils import mission_dirs_in_dir
from src.utils import load_config, pretty_iterable_of_str
from static_data.au_mission_overrides import (
    EXCLUDED_MISSIONS,
)
from static_data.in_game_data import IN_GAME_DATA
from static_data.map_index import MAP_INDEX

_CONFIG_FILENAME = "config.toml"
_LOGGER = logging.getLogger(__name__)


def main() -> None:
    """Analyse all missions."""
    logging.basicConfig(
        level="INFO",
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler()],
    )
    mission_dirs = sorted(
        d
        for d in mission_dirs_in_dir(MISSIONS_BASE_DIRPATH)
        if d.name not in EXCLUDED_MISSIONS
    )
    log(
        INFO,
        f"Ignoring {pretty_iterable_of_str(EXCLUDED_MISSIONS)}. "
        f"Found {len(mission_dirs)} candidate missions in {MISSIONS_BASE_DIRPATH}.",
    )

    OUTPUT_DIRPATH.mkdir(parents=True, exist_ok=True)

    analysed_map_names = set()
    for mission_dir in track(mission_dirs, description="Analysing missions..."):
        map_name = process_mission(mission_dir)
        analysed_map_names.add(map_name)

    log(
        INFO,
        f"Exported data for {len(analysed_map_names)} missions to '{OUTPUT_DIRPATH}'.",
    )
    unused_map_index_names = MAP_INDEX.keys() - analysed_map_names
    if unused_map_index_names:
        log(
            WARNING,
            f"{len(unused_map_index_names)} unused map index key(s): "
            f"{pretty_iterable_of_str(list(unused_map_index_names))}.",
        )

    unused_in_game_map_names = IN_GAME_DATA.keys() - analysed_map_names
    if unused_in_game_map_names:
        log(
            WARNING,
            f"{len(unused_in_game_map_names)} unused in-game data key(s): "
            f"{pretty_iterable_of_str(list(unused_in_game_map_names))}.",
        )


def log(level: int, message: str) -> None:
    """Wrap log messages."""
    _LOGGER.log(level, message)


def process_mission(mission_dir: Path) -> str:
    """Analyse a single mission and export intermediate data."""
    mission = Mission.from_data(mission_dir=mission_dir, map_index=MAP_INDEX)
    log(INFO, f"'{mission_dir.name}': loaded mission.")

    mission.verify_pois_vs_in_game_data(IN_GAME_DATA)
    mission.validate_towns_vs_grad_meh_data(
        GM_LOCATIONS_BASE_DIRPATH / mission.map_name / "geojson" / "locations"
    )
    mission.export(OUTPUT_DIRPATH)
    return mission.map_name


if __name__ == "__main__":
    _BASE_PATH = Path(__file__).resolve().parent
    _CONFIG = load_config(_BASE_PATH / _CONFIG_FILENAME)
    MISSIONS_BASE_DIRPATH = _BASE_PATH / _CONFIG["AU_SOURCE_DIR_RELATIVE"]
    GM_LOCATIONS_BASE_DIRPATH = _BASE_PATH / _CONFIG["GRAD_MEH_DATA_DIR_RELATIVE"]
    OUTPUT_DIRPATH = _BASE_PATH / _CONFIG["INTERMEDIATE_DATA_DIR_RELATIVE"]
    main()
