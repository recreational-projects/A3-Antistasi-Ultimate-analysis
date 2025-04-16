"""
Generate the Markdown doc representing site content.

Load all JSON files in `DATA_RELATIVE_DIR`; export Markdown
to `OUTPUT_RELATIVE_DIR`.
"""

import json
import logging
from collections.abc import Iterable, Sequence
from pathlib import Path

from cattrs import structure
from rich.logging import RichHandler

from scripts._docs_includes import INTRO_MARKDOWN, KNOWN_ISSUES_MARKDOWN
from src.mission.mission import Mission
from src.static_data.in_game_data import IN_GAME_DATA
from src.utils import load_config

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
    data_dir_path = base_filepath / config["DATA_RELATIVE_DIR"]
    doc_file_path = base_filepath / config["OUTPUT_RELATIVE_FILE"]

    missions = load_missions_data(data_dir_path)
    verify_data(missions, IN_GAME_DATA)

    maps_without_display_names = {m.map_name for m in missions if not m.display_name}
    if maps_without_display_names:
        log_msg = (
            f"{len(maps_without_display_names)} maps don't have a `display_name`: "
            f"{pretty_iterable_of_str(maps_without_display_names)}."
        )
        _LOGGER.warning(log_msg)

    maps_without_urls = {m.map_name for m in missions if not m.download_url}
    if maps_without_urls:
        log_msg = (
            f"{len(maps_without_urls)} maps don't have a `download_url`: "
            f"{pretty_iterable_of_str(maps_without_urls)}."
        )
        _LOGGER.warning(log_msg)

    markdown = (
        INTRO_MARKDOWN
        + markdown_total_missions(missions)
        + markdown_table(
            missions=sorted(missions, key=sort_missions_by_name), columns=_COLUMNS
        )
        + KNOWN_ISSUES_MARKDOWN
    )
    log_msg = "Generated Markdown."
    _LOGGER.info(log_msg)

    with Path.open(doc_file_path, "w", encoding="utf-8") as fp:
        fp.write(markdown)

    log_msg = f"Markdown saved to {doc_file_path}."
    _LOGGER.info(log_msg)


def load_missions_data(path: Path) -> list[Mission]:
    """Load `Missions` data from `path`."""
    json_files = [p for p in list(path.iterdir()) if p.suffix == ".json"]
    log_msg = f"Found {len(json_files)} files in {path}."
    _LOGGER.info(log_msg)

    missions = []
    for fp in json_files:
        with Path.open(fp, "r", encoding="utf-8") as file:
            map_info = structure(json.load(file), Mission)
            missions.append(map_info)

    log_msg = f"Loaded data for {len(missions)} missions."
    _LOGGER.info(log_msg)
    return missions


def verify_data(
    missions: Iterable[Mission], verification_data: dict[str, dict[str, int]]
) -> None:
    """Verify generated data against reference data."""
    map_names = {map_info.map_name for map_info in missions}
    reference_map_names = verification_data.keys()
    missing_reference_data = map_names - reference_map_names
    unused_reference_data = reference_map_names - map_names

    if missing_reference_data:
        log_msg = (
            f"No reference data to verify {len(missing_reference_data)} maps: "
            f"{pretty_iterable_of_str(missing_reference_data)}."
        )
        _LOGGER.warning(log_msg)

    if unused_reference_data:
        log_msg = (
            f"Unexpected {len(unused_reference_data)} reference data:"
            f"{pretty_iterable_of_str(unused_reference_data)}'."
        )
        _LOGGER.warning(log_msg)

    for mission in missions:
        reference_data = IN_GAME_DATA.get(mission.map_name, {})
        for field in reference_data:
            reference_value = reference_data.get(field)
            field_value = getattr(mission, field)
            if field_value != reference_value:
                log_msg = (
                    f"'{mission.map_name}' '{field}' verification failure: "
                    f"{field_value} != {reference_value}"
                )
                _LOGGER.warning(log_msg)
            else:
                log_msg = f"'{mission.map_name}' `{field}` OK."
                _LOGGER.info(log_msg)


def pretty_iterable_of_str(iterable: Iterable[str]) -> str:
    """Return e.g. `'a', 'b', 'c'`."""
    return f"'{"', '".join(iterable)}'"


def sort_missions_by_name(map_info: Mission) -> str:
    """Sort order for `Mission` instances."""
    if map_info.display_name is None:
        return map_info.map_name.casefold()
    return map_info.display_name.casefold()


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
    for map_info in missions:
        for col, details in columns.items():
            td_value = handle_missing_value(getattr(map_info, col))
            if details.get("link_cell_content") and map_info.download_url:
                td_value = f"[{td_value}]({map_info.download_url})"

            tbody += f"| {td_value} "
        tbody += "|\n"

    return thead + tdivider + tbody


def handle_missing_value(val: int | str | None) -> str:
    """
    Display `` instead of `0` if value is `None`.

    `None` is used to flag unknown/missing value, as opposed to calculated zero.
    """
    return "" if val is None else str(val)


def markdown_total_missions(missions: Sequence[Mission]) -> str:
    """Create Markdown total missions line."""
    return f"- {len(missions)} maps including season variants\n"


if __name__ == "__main__":
    main()
