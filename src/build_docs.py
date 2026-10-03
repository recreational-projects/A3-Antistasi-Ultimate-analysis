"""Load all `Mission`s from JSON and generate the Markdown doc."""

from __future__ import annotations

import tomllib
from operator import attrgetter
from pathlib import Path
from typing import TYPE_CHECKING

import attrs

from ._data_table import markdown_table
from ._docs_includes import INTRO_MARKDOWN, OUTRO_MARKDOWN
from ._utils import (
    DATA_DIRPATH,
    DOC_DIRPATH,
    LOGGER,
    configure_logging,
    require_dir,
)
from .mission.mission import Mission
from .mission.utils import pretty_iterable_of_str
from .static_data.map_index import MAP_INDEX

if TYPE_CHECKING:
    from collections.abc import Sized


def main() -> None:
    """
    Script entry point.

    Generate the Markdown doc representing site content.
    """
    configure_logging()
    require_dir(DATA_DIRPATH)
    DOC_DIRPATH.mkdir(parents=True, exist_ok=True)
    project_version_ = _project_version()
    log_msg = f"Project version {project_version_}"
    LOGGER.info(log_msg)

    missions = _missions_from_json(DATA_DIRPATH)
    markdown_content = [
        INTRO_MARKDOWN,
        _markdown_total_missions(missions),
        markdown_table(missions),
        OUTRO_MARKDOWN,
        _markdown_project_version(project_version_),
    ]
    LOGGER.info("Generated Markdown.")

    doc_filepath = DOC_DIRPATH / "index.md"
    with Path.open(doc_filepath, "w", encoding="utf-8") as fp:
        fp.write("".join(markdown_content))

    log_msg = f"Markdown saved to {doc_filepath}."
    LOGGER.info(log_msg)


def _project_version() -> str:
    """Get project version from `pyproject.toml`."""
    filepath = Path(__file__).resolve().parent / "../pyproject.toml"
    with filepath.open("rb") as fp:
        version = tomllib.load(fp).get("project", {}).get("version")
        return str(version)


def _missions_from_json(path: Path) -> list[Mission]:
    """Load previously-exported `Missions` from `path`."""
    json_files = [p for p in list(path.iterdir()) if p.suffix == ".json"]
    log_msg = f"Found {len(json_files)} files in {path}."
    LOGGER.info(log_msg)

    missions = []
    for fp in json_files:
        map_name = fp.stem
        if MAP_INDEX[map_name].get("exclude"):
            log_msg = f"Excluded `{map_name}`."
            LOGGER.info(log_msg)
            continue

        missions.append(Mission.from_json(fp))

    log_msg = f"Loaded data for {len(missions)} missions."
    LOGGER.info(log_msg)

    required_fields = {
        field.name
        for field in attrs.fields(Mission)
        if field.name not in ["disabled_towns", "waterports", "exclude"]
    }
    for mission in missions:
        empty_fields = {f for f in required_fields if not getattr(mission, f)}
        if empty_fields:
            log_msg = f"{mission.map_name}: "
            log_msg += f"no {pretty_iterable_of_str(empty_fields)} value."
            LOGGER.error(log_msg)

    return sorted(missions, key=attrgetter("map_name"))


def _markdown_total_missions(missions: Sized) -> str:
    """Create Markdown total missions line."""
    return f"- {len(missions)} maps total including season variants\n"


def _markdown_project_version(v: str) -> str:
    """Create Markdown project version line."""
    return f"\n- Version {v}\n"


if __name__ == "__main__":
    main()
