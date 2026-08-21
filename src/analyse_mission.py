"""Analyse a single mission in AU source code and export `Mission` as JSON."""

from __future__ import annotations

import argparse
from typing import TYPE_CHECKING

from ._utils import (
    AU_MAPS_DIRPATH,
    DATA_DIRPATH,
    GRAD_MEH_DIRPATH,
    configure_logging,
    require_dir,
)
from .mission.mission import Mission
from .static_data import in_game_data
from .static_data.map_index import MAP_INDEX

if TYPE_CHECKING:
    from pathlib import Path


def main() -> None:
    """Script entry point."""
    configure_logging()
    parser = argparse.ArgumentParser()
    parser.add_argument("map_name")
    args = parser.parse_args()
    require_dir(AU_MAPS_DIRPATH)
    require_dir(GRAD_MEH_DIRPATH)
    DATA_DIRPATH.mkdir(parents=True, exist_ok=True)
    analyse_mission(
        mission_dir=AU_MAPS_DIRPATH / f"Antistasi_{args.map_name}.{args.map_name}",
        grad_meh_dir=GRAD_MEH_DIRPATH / args.map_name,
        export_dir=DATA_DIRPATH,
    )


def analyse_mission(
    *, mission_dir: Path, grad_meh_dir: Path, export_dir: Path
) -> str | None:
    """Analyse a single mission and export data."""
    require_dir(mission_dir)
    # NB: doesn't require `grad_meh_dir`.
    # Warnings are emitted by individual functions that use grad_meh data.
    mission = Mission.from_data(mission_dir=mission_dir, map_index=MAP_INDEX)
    if mission is None:
        return None

    mission.validate_military_zones(in_game_data.MILITARY_ZONES_COUNT)
    mission.validate_and_correct_towns(grad_meh_dir / "geojson/locations")
    mission.export_json(export_dir)
    return mission.map_name


if __name__ == "__main__":
    main()
