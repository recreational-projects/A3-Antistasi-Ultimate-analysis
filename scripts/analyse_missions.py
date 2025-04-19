"""Analyse missions in source code and export intermediate data."""

import json
import logging
from pathlib import Path

from attrs import asdict
from rich.logging import RichHandler
from rich.progress import track

from src.mission.file import mission_dirs_in_dir
from src.mission.mission import Mission
from src.utils import load_config, pretty_iterable_of_str
from static_data.au_mission_overrides import EXCLUDED_MISSIONS
from static_data.in_game_data import IN_GAME_DATA
from static_data.map_index import MAP_INDEX

_CONFIG_FILEPATH = "config.toml"
_LOGGER = logging.getLogger(__name__)


def main() -> None:
    """Parse all missions."""
    logging.basicConfig(
        level="INFO",
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler()],
    )
    base_filepath = Path(__file__).resolve().parent
    config = load_config(base_filepath / _CONFIG_FILEPATH)

    missions_base_dir = base_filepath / config["AU_SOURCE_DIR_RELATIVE"]
    mission_dirs = sorted(
        d
        for d in mission_dirs_in_dir(missions_base_dir)
        if d.name not in EXCLUDED_MISSIONS
    )
    log_msg = (
        f"Ignoring {pretty_iterable_of_str(EXCLUDED_MISSIONS)}. "
        f"Found {len(mission_dirs)} candidate missions in {missions_base_dir}."
    )
    _LOGGER.info(log_msg)

    output_dir_path = base_filepath / config["INTERMEDIATE_DATA_DIR_RELATIVE"]
    output_dir_path.mkdir(parents=True, exist_ok=True)

    map_names = set()
    mission_exports_count = 0

    for dir_ in track(mission_dirs, description="Analysing missions..."):
        mission = Mission.from_data(map_dir=dir_, map_index=MAP_INDEX)
        map_names.add(mission.map_name)

        mission.verify_vs_in_game_data(IN_GAME_DATA)
        export_filename = f"{dir_.name}.json"
        with Path.open(
            output_dir_path / export_filename, "w", encoding="utf-8"
        ) as file:
            json.dump(
                asdict(mission),
                file,
                ensure_ascii=False,
                indent=4,
            )
            mission_exports_count += 1
            log_msg = f"Exported '{export_filename}'."
            _LOGGER.info(log_msg)

    log_msg = (
        f"Exported data for {mission_exports_count} missions to '{output_dir_path}'."
    )
    _LOGGER.info(log_msg)

    unused_map_index_names = MAP_INDEX.keys() - map_names
    if unused_map_index_names:
        log_msg = (
            f"{len(unused_map_index_names)} unused map index key: "
            f"{pretty_iterable_of_str(list(unused_map_index_names))}."
        )
        _LOGGER.warning(log_msg)

    unused_in_game_map_names = IN_GAME_DATA.keys() - map_names
    if unused_in_game_map_names:
        log_msg = (
            f"{len(unused_in_game_map_names)} unused in-game data key: "
            f"{pretty_iterable_of_str(list(unused_in_game_map_names))}'."
        )
        _LOGGER.warning(log_msg)


if __name__ == "__main__":
    main()
