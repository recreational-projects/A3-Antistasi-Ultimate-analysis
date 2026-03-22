"""Analyse a single mission in AU source code and export `Mission` as JSON."""

from __future__ import annotations

import argparse
from typing import TYPE_CHECKING

from scripts._common import (
    AU_MAPS_DIRPATH,
    DATA_DIRPATH,
    GRAD_MEH_DIRPATH,
    configure_logging,
    require_dir,
)
from src.map_render.map_render import export_map_render
from src.mission.mission import Mission
from static_data import in_game_data
from static_data.map_index import MAP_INDEX

if TYPE_CHECKING:
    from pathlib import Path


def analyse_mission(mission_dir: Path) -> str:
    """Analyse a single mission and export intermediate data."""
    for path in AU_MAPS_DIRPATH, GRAD_MEH_DIRPATH:
        require_dir(path)

    DATA_DIRPATH.mkdir(parents=True, exist_ok=True)
    mission_dir.resolve()
    require_dir(mission_dir)
    mission = Mission.from_data(mission_dir=mission_dir, map_index=MAP_INDEX)
    mission.validate_military_zones(in_game_data.MILITARY_ZONES_COUNT)
    mission.validate_and_correct_towns(
        GRAD_MEH_DIRPATH / mission.map_name / "geojson/locations"
    )
    mission.export_json(DATA_DIRPATH)
    export_map_render(
        mission=mission,
        grad_meh_dem_filepath=GRAD_MEH_DIRPATH / "dem.asc.gz",
        export_filepath=DATA_DIRPATH / f"{mission.map_name}_map.png",
    )
    return mission.map_name


if __name__ == "__main__":
    configure_logging()
    parser = argparse.ArgumentParser()
    parser.add_argument("map_name")
    args = parser.parse_args()
    analyse_mission(AU_MAPS_DIRPATH / f"Antistasi_{args.map_name}.{args.map_name}")
