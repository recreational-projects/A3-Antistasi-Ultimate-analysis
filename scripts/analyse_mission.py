"""Analyse a single mission in AU source code and export as JSON."""

from __future__ import annotations

import argparse
import logging

from scripts.constants import PATHS
from src.mission.mission import analyse_single_mission
from src.utils import configure_logging
from static_data.map_index import MAP_INDEX

LOGGER = logging.getLogger(__name__)


def analyse_mission(map_name: str) -> None:
    """Analyse a single mission."""
    configure_logging()
    PATHS["DATA_DIR"].mkdir(parents=True, exist_ok=True)

    log_msg = f"Analysing single mission '{map_name}'."
    LOGGER.info(log_msg)

    analyse_single_mission(
        au_map_dir=PATHS["AU_MAPS_DIR"] / f"Antistasi_{map_name}.{map_name}",
        map_index=MAP_INDEX,
        grad_meh_map_dir=PATHS["GRAD_MEH_DIR"] / map_name,
        export_dir=PATHS["DATA_DIR"],
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("map_name")
    args = parser.parse_args()
    analyse_mission(args.map_name)
