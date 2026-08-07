"""Load all `Mission`s from JSON and generate the Markdown doc."""

from __future__ import annotations

import tomllib
from operator import attrgetter
from pathlib import Path
from typing import TYPE_CHECKING

import attrs

from modules.mission.mission import Mission
from modules.utils import pretty_iterable_of_str
from scripts._common import (
    DATA_DIRPATH,
    DOC_DIRPATH,
    LOGGER,
    configure_logging,
    require_dir,
)
from scripts._docs_includes import COLUMNS, INTRO_MARKDOWN, OUTRO_MARKDOWN

if TYPE_CHECKING:
    from collections.abc import Sequence, Sized


def build_docs() -> None:
    """Generate the Markdown doc representing site content."""
    for path in DATA_DIRPATH, DOC_DIRPATH:
        require_dir(path)

    project_version_ = _project_version()
    log_msg = f"Project version {project_version_}"
    LOGGER.info(log_msg)

    missions = _missions_from_json(DATA_DIRPATH)
    max_war_level_points = max(
        m.war_level_points for m in missions if m.war_level_points
    )
    markdown_content = [
        INTRO_MARKDOWN,
        _markdown_total_missions(missions),
        _markdown_table(
            missions=sorted(missions, key=_sort_missions_by_points, reverse=True),
            columns=COLUMNS,
            max_war_level_points=max_war_level_points,
        ),
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

    missions = [Mission.from_json(fp) for fp in json_files]
    filtered_missions = [m for m in missions if not m.exclude]
    log_msg = f"Loaded data for {len(filtered_missions)} missions; "
    log_msg += f"{len(missions) - len(filtered_missions)} excluded."
    LOGGER.info(log_msg)

    required_fields = {
        field.name
        for field in attrs.fields(Mission)
        if field.name not in ["disabled_towns", "waterports", "exclude"]
    }
    for mission in filtered_missions:
        empty_fields = {f for f in required_fields if not getattr(mission, f)}
        if empty_fields:
            log_msg = f"{mission.map_name}: "
            log_msg += f"no {pretty_iterable_of_str(empty_fields)} value."
            LOGGER.error(log_msg)

    return sorted(filtered_missions, key=attrgetter("map_name"))


def _markdown_total_missions(missions: Sized) -> str:
    """Create Markdown total missions line."""
    return f"- {len(missions)} maps total including season variants\n"


def _markdown_table(
    *,
    missions: Sequence[Mission],
    columns: dict[str, dict[str, str | bool]],
    max_war_level_points: int,
) -> str:
    """Create Markdown table."""
    th_values = [
        str(properties.get("display_heading", col))
        for col, properties in columns.items()
    ]
    thead = f"\n| {' <br>| '.join(th_values)} |\n"
    # <br> prevents sort indicator disrupting right-aligned text
    tdivider = ""
    for col_details in columns.values():
        tdivider += "| ---"
        tdivider += ":" if col_details.get("text-align") == "right" else " "

    tdivider += "|\n"
    trs = [
        _markdown_table_row(
            mission=m, columns=columns, max_war_level_points=max_war_level_points
        )
        for m in missions
    ]
    return thead + tdivider + "".join(trs) + "\n"


def _markdown_table_row(
    *,
    mission: Mission,
    columns: dict[str, dict[str, str | bool]],
    max_war_level_points: int,
) -> str:
    """Create Markdown table row."""
    tr = ""
    for col in columns:
        td_value = ""
        if col == "map_name":
            td_value = str(mission.map_display_name)
            if mission.map_url:
                td_value = f"[{td_value}]({mission.map_url})"

        elif col == "war_level_points_ratio_dynamic":
            ratio = mission.war_level_points_ratio(max_war_level_points)
            if ratio:
                td_value = f"{ratio:.2f}"
        else:
            td_value = _markdown_handle_missing_value(getattr(mission, col))

        tr += f"| {td_value} "

    tr += "|\n"
    return tr


def _markdown_handle_missing_value(val: int | str | None) -> str:
    """
    Display '' instead of '0' if value is `None`.

    `None` is used to flag unknown/missing value, as opposed to calculated zero.
    """
    return "" if val is None else str(val)


def _markdown_project_version(v: str) -> str:
    """Create Markdown project version line."""
    return f"\n- Version {v}\n"


def _sort_missions_by_points(mission: Mission) -> int:
    """Sort order for `Mission`s table."""
    return 0 if mission.war_level_points is None else mission.war_level_points


if __name__ == "__main__":
    configure_logging()
    build_docs()
