"""Generate the Markdown doc representing site content."""

import logging
from collections.abc import Sequence
from pathlib import Path

from rich.logging import RichHandler

from scripts import docs_includes
from scripts.constants import BASE_PATH, CONFIG
from src.mission.mission import Mission
from src.utils import project_version
from static_data import au_mission_overrides

LOGGER = logging.getLogger(__name__)
DATA_DIRPATH = BASE_PATH / CONFIG["INTERMEDIATE_DATA_DIR_RELATIVE"]
DOC_FILEPATH = BASE_PATH / CONFIG["MARKDOWN_OUTPUT_FILE_RELATIVE"]
PROJECT_VERSION = project_version()


def sort_missions_by_points(mission: Mission) -> int:
    """Sort order for `Mission`s table."""
    return 0 if mission.war_level_points is None else mission.war_level_points


def markdown_total_missions(missions: Sequence[Mission]) -> str:
    """Create Markdown total missions line."""
    return (
        f"- {len(missions)} maps total including season variants, excluding Stratis\n"
    )


def markdown_handle_missing_value(val: int | str | None) -> str:
    """
    Display `` instead of `0` if value is `None`.

    `None` is used to flag unknown/missing value, as opposed to calculated zero.
    """
    return "" if val is None else str(val)


def markdown_table_row(
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
            td_value = markdown_handle_missing_value(getattr(mission, col))

        tr += f"| {td_value} "

    tr += "|\n"
    return tr


def markdown_table(
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
        markdown_table_row(
            mission=m,
            columns=columns,
            max_war_level_points=max_war_level_points,
        )
        for m in missions
    ]
    return thead + tdivider + "".join(trs) + "\n"


def markdown_version() -> str:
    """Create Markdown project version line."""
    return f"\n- Version {PROJECT_VERSION}\n"


def main() -> None:
    """Generate the Markdown doc representing site content."""
    logging.basicConfig(
        level="INFO",
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler()],
    )
    log_msg = f"{PROJECT_VERSION = }"
    LOGGER.info(log_msg)

    missions = Mission.missions_from_json(
        DATA_DIRPATH, excludes=au_mission_overrides.EXCLUDED_MISSIONS
    )
    max_war_level_points = max(
        m.war_level_points for m in missions if m.war_level_points
    )
    markdown_content = [
        docs_includes.INTRO_MARKDOWN,
        markdown_total_missions(missions),
        markdown_table(
            missions=sorted(missions, key=sort_missions_by_points, reverse=True),
            columns=docs_includes.COLUMNS,
            max_war_level_points=max_war_level_points,
        ),
        docs_includes.OUTRO_MARKDOWN,
        markdown_version(),
    ]
    LOGGER.info("Generated Markdown.")

    with Path.open(DOC_FILEPATH, "w", encoding="utf-8") as fp:
        fp.write("".join(markdown_content))

    log_msg = f"Markdown saved to {DOC_FILEPATH}."
    LOGGER.info(log_msg)


if __name__ == "__main__":
    main()
