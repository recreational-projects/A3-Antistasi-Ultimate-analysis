"""
Generate the Markdown doc representing site content.

Load all JSON files in `DATA_RELATIVE_DIR`; export Markdown
to `OUTPUT_RELATIVE_DIR`.
"""

import logging
from collections.abc import Sequence
from pathlib import Path

from rich.logging import RichHandler

from scripts._docs_includes import INTRO_MARKDOWN, KNOWN_ISSUES_MARKDOWN
from src.mission.file import load_missions_data
from src.mission.mission import Mission
from src.static_data.au_mission_overrides import EXCLUDED_MISSIONS
from src.static_data.in_game_data import IN_GAME_DATA
from src.static_data.map_index import MAP_INDEX
from src.utils import load_config, pretty_iterable_of_str

_COLUMNS: dict[str, dict[str, str | bool]] = {
    "display_name": {
        "display_heading": "map",
        "link_cell_content": True,
    },
    "climate": {},
    "airports_count": {
        "display_heading": "airports",
        "text-align": "right",
    },
    "waterports_count": {
        "display_heading": "sea/<br>riverports",
        "text-align": "right",
    },
    "bases_count": {
        "display_heading": "bases",
        "text-align": "right",
    },
    "outposts_count": {
        "display_heading": "outposts",
        "text-align": "right",
    },
    "factories_count": {
        "display_heading": "factories",
        "text-align": "right",
    },
    "resources_count": {
        "display_heading": "resources",
        "text-align": "right",
    },
    "total_objectives_count": {
        "display_heading": "total<br>military<br>objectives",
        "text-align": "right",
    },
    "towns_count": {
        "display_heading": "towns<br>",
        "text-align": "right",
    },
    "war_level_points": {
        "display_heading": "total<br>war level<br>points<br>",
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
        base_filepath / config["DATA_RELATIVE_DIR"], excludes=EXCLUDED_MISSIONS
    )
    mission_map_names = {m.map_name for m in au_missions}
    unused_map_index_names = MAP_INDEX.keys() - mission_map_names
    if unused_map_index_names:
        log_msg = (
            f"Unexpected {len(unused_map_index_names)} reference data:"
            f"{pretty_iterable_of_str(list(unused_map_index_names))}'."
        )
        _LOGGER.warning(log_msg)

    unused_in_game_map_names = IN_GAME_DATA.keys() - mission_map_names
    if unused_in_game_map_names:
        log_msg = (
            f"Unexpected {len(unused_in_game_map_names)} reference data:"
            f"{pretty_iterable_of_str(list(unused_in_game_map_names))}'."
        )
        _LOGGER.warning(log_msg)

    for mission in au_missions:
        map_name = mission.map_name

        if map_name not in MAP_INDEX:
            log_msg = f"'{map_name}': not in map index."
            _LOGGER.warning(log_msg)
        else:
            verify_vs_map_index(map_name=map_name, data=MAP_INDEX[map_name])

        if map_name not in IN_GAME_DATA:
            log_msg = f"'{map_name}': no in-game data."
            _LOGGER.warning(log_msg)
        else:
            verify_vs_in_game_data(au_mission=mission, data=IN_GAME_DATA[map_name])

    markdown = (
        INTRO_MARKDOWN
        + markdown_total_missions(au_missions)
        + markdown_table(
            missions=sorted(au_missions, key=sort_missions_by_name), columns=_COLUMNS
        )
        + KNOWN_ISSUES_MARKDOWN
    )
    log_msg = "Generated Markdown."
    _LOGGER.info(log_msg)

    doc_file_path = base_filepath / config["OUTPUT_RELATIVE_FILE"]
    with Path.open(doc_file_path, "w", encoding="utf-8") as fp:
        fp.write(markdown)

    log_msg = f"Markdown saved to {doc_file_path}."
    _LOGGER.info(log_msg)


def verify_vs_map_index(*, map_name: str, data: dict[str, str]) -> None:
    """Verify generated data against reference data."""
    if not data.get("display_name"):
        log_msg = f"'{map_name}': no `display_name` in index."
        _LOGGER.warning(log_msg)

    if not data.get("url"):
        log_msg = f"'{map_name}' no `url` in index."
        _LOGGER.warning(log_msg)


def verify_vs_in_game_data(*, au_mission: Mission, data: dict[str, int]) -> None:
    """Verify generated data against in-game reference data."""
    for field in data:
        field_value = getattr(au_mission, field)
        reference_value = data.get(field)
        if field_value != reference_value:
            log_msg = (
                f"'{au_mission.map_name}': '{field}' verification failure: "
                f"{field_value} != {reference_value}."
            )
            _LOGGER.warning(log_msg)
        else:
            log_msg = f"'{au_mission.map_name}': `{field}` matches in-game data."
            _LOGGER.info(log_msg)


def sort_missions_by_name(mission: Mission) -> str:
    """Sort order for `Mission`s table."""
    if mission.display_name is None:
        return mission.map_name.casefold()
    return mission.display_name.casefold()


def markdown_table(
    *, missions: Sequence[Mission], columns: dict[str, dict[str, str | bool]]
) -> str:
    """Create Markdown table."""
    th_values = [
        str(properties.get("display_heading", col)).capitalize()
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
        for col, details in columns.items():
            td_value = markdown_handle_missing_value(getattr(mission, col))
            if details.get("link_cell_content") and mission.download_url:
                td_value = f"[{td_value}]({mission.download_url})"

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


if __name__ == "__main__":
    main()
