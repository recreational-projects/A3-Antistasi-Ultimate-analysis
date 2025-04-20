"""Analyse missions in source code and export intermediate data."""

import json
import logging
from pathlib import Path

from attrs import asdict
from rich.logging import RichHandler
from rich.progress import track

from src.geojson.load import load_towns_from_dir
from src.mission.file import mission_dirs_in_dir
from src.mission.mission import Mission
from src.utils import load_config, pretty_iterable_of_str
from static_data.au_mission_overrides import (
    DISABLED_TOWNS_IGNORED_PREFIXES,
    EXCLUDED_MISSIONS,
)
from static_data.in_game_data import IN_GAME_DATA
from static_data.map_index import MAP_INDEX

_BASE_PATH = Path(__file__).resolve().parent
_CONFIG_FILE = "config.toml"
_LOGGER = logging.getLogger(__name__)


def main() -> None:
    """Analyse all missions."""
    logging.basicConfig(
        level="INFO",
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler()],
    )
    config = load_config(_BASE_PATH / _CONFIG_FILE)
    missions_base_dir = _BASE_PATH / config["AU_SOURCE_DIR_RELATIVE"]
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

    gm_locations_base_dir = _BASE_PATH / config["GRAD_MEH_DATA_DIR_RELATIVE"]
    output_dir = _BASE_PATH / config["INTERMEDIATE_DATA_DIR_RELATIVE"]
    output_dir.mkdir(parents=True, exist_ok=True)

    map_names = set()
    for mission_dir in track(mission_dirs, description="Analysing missions..."):
        mission_map_name = analyse_mission(
            mission_dir=mission_dir,
            gm_locations_base_dir=gm_locations_base_dir,
            output_dir=output_dir,
        )
        map_names.add(mission_map_name)

    log_msg = f"Exported data for {len(map_names)} missions to '{output_dir}'."
    _LOGGER.info(log_msg)

    unused_map_index_names = MAP_INDEX.keys() - map_names
    if unused_map_index_names:
        log_msg = (
            f"{len(unused_map_index_names)} unused map index key(s): "
            f"{pretty_iterable_of_str(list(unused_map_index_names))}."
        )
        _LOGGER.warning(log_msg)

    unused_in_game_map_names = IN_GAME_DATA.keys() - map_names
    if unused_in_game_map_names:
        log_msg = (
            f"{len(unused_in_game_map_names)} unused in-game data key(s): "
            f"{pretty_iterable_of_str(list(unused_in_game_map_names))}'."
        )
        _LOGGER.warning(log_msg)


def analyse_mission(
    *,
    mission_dir: Path,
    gm_locations_base_dir: Path,
    output_dir: Path,
) -> str:
    """
    Analyse a mission.

    Returns:
        map_name
            To be used as key

    """
    mission = Mission.from_data(mission_dir=mission_dir, map_index=MAP_INDEX)
    mission.verify_vs_in_game_data(IN_GAME_DATA)

    if not mission.towns:
        log_msg = f"'{mission.map_name}': No towns defined in mission."
        _LOGGER.info(log_msg)

        gm_towns_path = (
            gm_locations_base_dir / mission.map_name / "geojson" / "locations"
        )
        gm_towns = None
        if not gm_towns_path.is_dir():
            log_msg = f"'{mission.map_name}': No grad-meh locations data."
            _LOGGER.warning(log_msg)
        else:
            gm_towns = load_towns_from_dir(gm_towns_path)

        if not gm_towns:
            log_msg = f"'{mission.map_name}': No towns available from grad-meh data."
            _LOGGER.warning(log_msg)
        else:
            log_msg = f"Checking {len(gm_towns)} towns from grad-meh data."
            _LOGGER.debug(log_msg)

            gm_towns_lookup = {
                t.properties["name"].lower().replace(" ", ""): t.properties["name"]
                for t in gm_towns
            }
            disabled_towns_lookup = {
                normalise_disabled_town_name(t): t for t in mission.disabled_towns
            }
            gm_towns_to_add = set()
            matched_keys = set()
            for k, v in gm_towns_lookup.items():
                if k in disabled_towns_lookup:
                    matched_keys.add(k)
                    log_msg = f"Didn't add disabled: '{k}' ('{v}')."
                    _LOGGER.debug(log_msg)
                else:
                    gm_towns_to_add.add(v)

            mission.towns = dict.fromkeys(gm_towns_to_add)
            log_msg = (
                f"'{mission.map_name}': "
                f"Added {len(gm_towns_to_add)} towns from grad-meh data."
            )
            _LOGGER.info(log_msg)

            unmatched_disabled = {
                k: v for k, v in disabled_towns_lookup.items() if k not in matched_keys
            }
            if unmatched_disabled:
                log_msg = (
                    f"'{mission.map_name}': Disabled towns defined in mission, but not "
                    f"found in grad-meh data: {unmatched_disabled}."
                )
                _LOGGER.warning(log_msg)

    export_filename = f"{mission.map_name}.json"
    with Path.open(output_dir / export_filename, "w", encoding="utf-8") as file:
        json.dump(
            asdict(mission),
            file,
            ensure_ascii=False,
            indent=4,
        )
        log_msg = f"'{mission.map_name}': Exported '{export_filename}'."
        _LOGGER.info(log_msg)
        return mission.map_name


def normalise_disabled_town_name(name: str) -> str:
    """
    "Normalise town name in mission data.

    Allows it to be compared with actual town names in map data.
    """
    for prefix in DISABLED_TOWNS_IGNORED_PREFIXES:
        name = name.removeprefix(prefix)
    return name.lower().replace(" ", "")


if __name__ == "__main__":
    main()
