"""Mission related."""

from pathlib import Path

from static_data.au_mission_overrides import DISABLED_TOWNS_IGNORED_PREFIXES


def path_looks_like_mission_dir(path: Path) -> bool:
    """
    Verify mission directory candidate.

    Return True if `path` is a directory with name pattern `...{string}.{string}`.
    """
    if not path.is_dir():
        return False

    map_name = map_name_from_mission_dir_path(path)
    return map_name == path.stem[-len(map_name) :].lower()


def mission_dirs_in_dir(path: Path) -> list[Path]:
    """
    Return candidate mission directories from a directory.

    Arguments:
        path: Directory to be searched.

    Returns:
        List of `Path`s.

    """
    return [p for p in (path.iterdir()) if path_looks_like_mission_dir(p)]


def map_name_from_mission_dir_path(path: Path) -> str:
    """
    Return map name from mission `path`.

    e.g. `Antistasi_Altis.Altis` -> "altis".
    """
    return path.suffix.lstrip(".").lower()


def normalise_town_name(name: str) -> str:
    """Normalise town name from map data, for comparison purposes."""
    return name.lower().replace(" ", "")


def normalise_mission_town_name(name: str) -> str:
    """Normalise town name from mission data, for comparison purposes."""
    for prefix in DISABLED_TOWNS_IGNORED_PREFIXES:
        name = name.removeprefix(prefix)

    return normalise_town_name(name)
