"""Load all `Mission`s from JSON and generate the Markdown doc."""

from __future__ import annotations

import logging
from operator import attrgetter
from pathlib import Path
from typing import TYPE_CHECKING

import attrs

from scripts import docs_includes
from scripts.constants import BASE_PATH, CONFIG
from src.mission.mission import Mission
from src.utils import configure_logging, pretty_iterable_of_str, project_version
from static_data import au_mission_overrides

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence, Sized

LOGGER = logging.getLogger(__name__)
DATA_DIRPATH = BASE_PATH / CONFIG["INTERMEDIATE_DATA_DIR_RELATIVE"]
DOC_FILEPATH = BASE_PATH / CONFIG["MARKDOWN_OUTPUT_FILE_RELATIVE"]
PROJECT_VERSION = project_version()


def _missions_from_json(path: Path, excludes: Iterable[str]) -> list[Mission]:
    """Load previously-exported `Missions` from `path`."""
    json_files = [
        p
        for p in list(path.iterdir())
        if p.suffix == ".json" and p.stem not in excludes
    ]
    _excludes_str = pretty_iterable_of_str(excludes)
    log_msg = f"Found {len(json_files)} files in {path} ignoring {excludes}."
    LOGGER.info(log_msg)

    missions = [Mission.from_json(fp) for fp in json_files]
    log_msg = f"Loaded data for {len(missions)} missions."
    LOGGER.info(log_msg)

    required_fields = {
        field.name
        for field in attrs.fields(Mission)
        if field.name not in ["disabled_town_names", "waterports"]
    }
    for mission in missions:
        empty_fields = {f for f in required_fields if not getattr(mission, f)}
        if empty_fields:
            log_msg = (
                f"{mission.map_display_name}: "
                f"no {pretty_iterable_of_str(empty_fields)} value."
            )
            LOGGER.error(log_msg)

    return sorted(missions, key=attrgetter("map_name"))


def _sort_missions_by_points(mission: Mission) -> int:
    """Sort order for `Mission`s table."""
    return 0 if mission.war_level_points is None else mission.war_level_points


def _markdown_total_missions(missions: Sized) -> str:
    """Create Markdown total missions line."""
    return (
        f"- {len(missions)} maps total including season variants, excluding Stratis\n"
    )


def _markdown_handle_missing_value(val: int | str | None) -> str:
    """
    Display '' instead of '0' if value is `None`.

    `None` is used to flag unknown/missing value, as opposed to calculated zero.
    """
    return "" if val is None else str(val)


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


def _markdown_version() -> str:
    """Create Markdown project version line."""
    return f"\n- Version {PROJECT_VERSION}\n"


def build_docs() -> None:
    """Generate the Markdown doc representing site content."""
    configure_logging()
    log_msg = f"Project version {PROJECT_VERSION}"
    LOGGER.info(log_msg)

    missions = _missions_from_json(
        DATA_DIRPATH, excludes=au_mission_overrides.EXCLUDED_MISSIONS
    )
    max_war_level_points = max(
        m.war_level_points for m in missions if m.war_level_points
    )
    markdown_content = [
        docs_includes.INTRO_MARKDOWN,
        _markdown_total_missions(missions),
        _markdown_table(
            missions=sorted(missions, key=_sort_missions_by_points, reverse=True),
            columns=docs_includes.COLUMNS,
            max_war_level_points=max_war_level_points,
        ),
        docs_includes.OUTRO_MARKDOWN,
        _markdown_version(),
    ]
    LOGGER.info("Generated Markdown.")

    with Path.open(DOC_FILEPATH, "w", encoding="utf-8") as fp:
        fp.write("".join(markdown_content))

    log_msg = f"Markdown saved to {DOC_FILEPATH}."
    LOGGER.info(log_msg)


if __name__ == "__main__":
    build_docs()
