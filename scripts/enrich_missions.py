"""Load each `Mission` from JSON, enrich, and re-export."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from rich.progress import track

from scripts.constants import BASE_PATH, CONFIG
from src.mission.mission import Mission
from src.mission.mission_enrich import (
    validate_and_correct_towns,
    validate_military_zones,
)
from src.mission.utils import mission_dirs_in_dir
from src.utils import configure_logging
from static_data import in_game_data

if TYPE_CHECKING:
    from pathlib import Path

LOGGER = logging.getLogger(__name__)
DATA_DIRPATH = BASE_PATH / CONFIG["INTERMEDIATE_DATA_DIR_RELATIVE"]
GM_LOCATIONS_BASE_DIRPATH = BASE_PATH / CONFIG["GRAD_MEH_DATA_DIR_RELATIVE"]


def _process_mission(mission_dir: Path) -> str:
    """Analyse a single mission and export intermediate data."""
    mission = Mission.from_json(mission_dir)
    log_msg = f"'{mission_dir.name}': loaded mission."
    LOGGER.info(log_msg)

    validate_military_zones(mission=mission, data=in_game_data.MILITARY_ZONES_COUNT)
    validate_and_correct_towns(
        mission=mission,
        gm_locations_dir=GM_LOCATIONS_BASE_DIRPATH
        / mission.map_name
        / "geojson"
        / "locations",
    )
    mission.export(mission_dir)
    return mission.map_name


def main() -> None:
    """Enrich all missions."""
    configure_logging()
    mission_data_dirs = sorted(d for d in mission_dirs_in_dir(DATA_DIRPATH))
    if not mission_data_dirs:
        msg = "No missions found."
        raise RuntimeError(msg)

    log_msg = f"Found {len(mission_data_dirs)} missions in {DATA_DIRPATH}."
    LOGGER.info(log_msg)

    processed_map_names = set()
    for mission_dir in track(mission_data_dirs, description="Analysing missions..."):
        map_name = _process_mission(mission_dir)
        processed_map_names.add(map_name)

    log_msg = (
        f"Exported data for {len(processed_map_names)} missions to '{DATA_DIRPATH}'."
    )
    LOGGER.info(log_msg)


if __name__ == "__main__":
    main()
