"""File-level utilities."""

import json
import logging
from collections.abc import Iterable
from operator import attrgetter
from pathlib import Path

from cattrs import structure

from src.mission.mission import Mission, map_name_from_mission_dir_path
from src.utils import pretty_iterable_of_str

_LOGGER = logging.getLogger(__name__)


def path_looks_like_mission_dir(path: Path) -> bool:
    """
    Verify mission directory candidate.

    Return True if `path` is a directory with name pattern `...{string}.{string}`.
    """
    if not path.is_dir():
        return False

    map_name = map_name_from_mission_dir_path(path)
    return map_name == path.stem[-len(map_name) :]


def mission_dirs_in_dir(path: Path) -> list[Path]:
    """
    Return candidate mission directories from a directory.

    Arguments:
        path: Directory to be searched.

    Returns:
        List of `Path`s.

    """
    dirs = [p for p in list(path.iterdir()) if path_looks_like_mission_dir(p)]
    log_msg = f"Found {len(dirs)} candidate missions in {path}."
    _LOGGER.info(log_msg)
    return dirs


def load_missions_data(path: Path, excludes: Iterable[str]) -> list[Mission]:
    """Load sorted `Missions` data from `path`."""
    json_files = [
        p
        for p in list(path.iterdir())
        if p.suffix == ".json" and p.stem not in excludes
    ]
    log_msg = (
        f"Found {len(json_files)} files in {path} "
        f"ignoring {pretty_iterable_of_str(excludes)}."
    )
    _LOGGER.info(log_msg)

    missions = []
    for fp in json_files:
        with Path.open(fp, "r", encoding="utf-8") as file:
            mission = structure(json.load(file), Mission)
            missions.append(mission)

    log_msg = f"Loaded data for {len(missions)} missions."
    _LOGGER.info(log_msg)
    return sorted(missions, key=attrgetter("map_name"))
