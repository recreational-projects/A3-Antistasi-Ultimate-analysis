"""Generate the Markdown doc representing site content."""

import logging
from collections.abc import Sequence
from pathlib import Path

from rich.logging import RichHandler

from scripts._docs_includes import INTRO_MARKDOWN, OUTRO_MARKDOWN
from src.mission.file import load_missions_data
from src.mission.mission import Mission
from src.utils import load_config, project_version
from static_data.au_mission_overrides import EXCLUDED_MISSIONS

_COLUMNS: dict[str, dict[str, str | bool]] = {
    "map_name": {
        "display_heading": "Map",
    },
    "climate": {},
    "airports_count": {
        "display_heading": "Airports",
        "text-align": "right",
    },
    "bases_count": {
        "display_heading": "Bases",
        "text-align": "right",
    },
    "waterports_count": {
        "display_heading": "Sea/<br>riverports",
        "text-align": "right",
    },
    "outposts_count": {
        "display_heading": "Outposts",
        "text-align": "right",
    },
    "factories_count": {
        "display_heading": "Factories",
        "text-align": "right",
    },
    "resources_count": {
        "display_heading": "Resources",
        "text-align": "right",
    },
    "total_objectives_count": {
        "display_heading": "Total<br>military<br>objectives[^1]",
        "text-align": "right",
    },
    "towns_count": {
        "display_heading": "Towns[^2]",
        "text-align": "right",
    },
    "war_level_points_ratio_dynamic": {
        "display_heading": "Total<br>War Level<br>points[^3]<br>ratio<br>",
        "text-align": "right",
    },
}
_CONFIG_FILEPATH = "config.toml"
_LOGGER = logging.getLogger(__name__)


def main() -> None:
    """Generate the Markdown doc representing site content."""
    logging.basicConfig(
        level="INFO",
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler()],
    )
    base_filepath = Path(__file__).resolve().parent
    config = load_config(base_filepath / _CONFIG_FILEPATH)

    au_missions = load_missions_data(
        base_filepath / config["INTERMEDIATE_DATA_DIR_RELATIVE"],
        excludes=EXCLUDED_MISSIONS,
    )
    max_war_level_points = max(
        mission.war_level_points for mission in au_missions if mission.war_level_points
    )

    markdown = (
        INTRO_MARKDOWN
        + markdown_total_missions(au_missions)
        + markdown_table(
            missions=sorted(au_missions, key=sort_missions_by_name),
            columns=_COLUMNS,
            max_war_level_points=max_war_level_points,
        )
        + OUTRO_MARKDOWN
        + markdown_version()
    )
    log_msg = "Generated Markdown."
    _LOGGER.info(log_msg)

    doc_file_path = base_filepath / config["MARKDOWN_OUTPUT_FILE_RELATIVE"]
    with Path.open(doc_file_path, "w", encoding="utf-8") as fp:
        fp.write(markdown)

    log_msg = f"Markdown saved to {doc_file_path}."
    _LOGGER.info(log_msg)


def sort_missions_by_name(mission: Mission) -> str:
    """Sort order for `Mission`s table."""
    if mission.map_display_name is None:
        return mission.map_name.casefold()
    return mission.map_display_name.casefold()


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

    tbody = ""
    for mission in missions:
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

            tbody += f"| {td_value} "
        tbody += "|\n"

    return thead + tdivider + tbody


def markdown_handle_missing_value(val: int | str | None) -> str:
    """
    Display `` instead of `0` if value is `None`.

    `None` is used to flag unknown/missing value, as opposed to calculated zero.
    """
    return "" if val is None else str(val)


def markdown_total_missions(missions: Sequence[Mission]) -> str:
    """Create Markdown total missions line."""
    return (
        f"- {len(missions)} maps total including season variants, excluding Stratis\n"
    )


def markdown_version() -> str:
    """
    Create Markdown project version line.

    Version from `pyproject.toml`.
    """
    version = project_version()
    return f"\n- Version {version}\n"


if __name__ == "__main__":
    main()
