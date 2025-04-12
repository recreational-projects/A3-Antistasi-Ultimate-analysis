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
from rich.progress import track

from src.map_information import MapInformation
from src.static_data.verification_data import VERIFICATION_DATA
from src.utils import load_config

_COLUMNS = {
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
        "display_heading": "total<br>objectives",
        "text-align": "right",
    },
    "towns_count": {
        "display_heading": "towns<br>",
        "text-align": "right",
    },
    "war_level_points": {
        "display_heading": "war<br>level<br>points<br>",
        "text-align": "right",
    },
}
_INTRO_MARKDOWN = """---
hide:
  - navigation
  - toc
---
# Compare missions in a sortable table

- Generated from Antistasi Ultimate stable release v11.6.0
  [source code](https://github.com/SilenceIsFatto/A3-Antistasi-Ultimate)
- [Source code](https://github.com/recreational-projects/A3-Antistasi-Ultimate-analysis)
  for this site;
  [changelog](https://github.com/recreational-projects/A3-Antistasi-Ultimate-analysis/blob/main/CHANGELOG.md)
"""
_KNOWN_ISSUES_MARKDOWN = """
## Known issues

- Towns aren't counted (and total War Level points can't be calculated) if they aren't
  explicitly declared in the mission files.
"""
_LOGGER = logging.getLogger(__name__)


def main() -> None:
    """Generate the Markdown doc representing site content."""
    logging.basicConfig(
        level="INFO",
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler()],
    )
    config = load_config()
    base_filepath = Path(__file__).resolve().parent
    data_dir_path = base_filepath / config["DATA_RELATIVE_DIR"]
    doc_file_path = base_filepath / config["OUTPUT_RELATIVE_FILE"]

    json_files = [p for p in list(data_dir_path.iterdir()) if p.suffix == ".json"]
    log_msg = f"Found {len(json_files)} files in {data_dir_path}."
    _LOGGER.info(log_msg)

    map_infos = []
    for fp in track(json_files, description="Building docs..."):
        with Path.open(fp, "r", encoding="utf-8") as file:
            map_info = structure(json.load(file), MapInformation)
            map_infos.append(map_info)

    log_msg = f"Loaded info for {len(map_infos)} maps."
    _LOGGER.info(log_msg)

    verify_data(map_infos, VERIFICATION_DATA)

    maps_without_display_names = {m.map_name for m in map_infos if not m.display_name}
    if maps_without_display_names:
        log_msg = (
            f"{len(maps_without_display_names)} maps don't have a `display_name`: "
            f"{pretty_iterable_of_str(maps_without_display_names)}."
        )
        _LOGGER.warning(log_msg)

    markdown = (
        _INTRO_MARKDOWN
        + markdown_total_maps(map_infos)
        + markdown_table(
            map_infos=sorted(map_infos, key=sort_maps_by_name), columns=_COLUMNS
        )
        + _KNOWN_ISSUES_MARKDOWN
    )
    log_msg = "Generated Markdown."
    _LOGGER.info(log_msg)

    with Path.open(doc_file_path, "w", encoding="utf-8") as fp:
        fp.write(markdown)

    log_msg = f"Markdown saved to {doc_file_path}."
    _LOGGER.info(log_msg)


def verify_data(
    map_infos: Iterable[MapInformation], verification_data: dict[str, dict[str, int]]
) -> None:
    """Verify generated data against reference data."""
    map_names = {map_info.map_name for map_info in map_infos}
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

    for map_info in map_infos:
        reference_data = VERIFICATION_DATA.get(map_info.map_name, {})
        for field in reference_data:
            reference_value = reference_data.get(field)
            field_value = getattr(map_info, field)
            if field_value != reference_value:
                log_msg = (
                    f"{map_info.map_name} '{field}' verification failure: "
                    f"{field_value} != {reference_value}"
                )
                _LOGGER.warning(log_msg)
            else:
                log_msg = f"QC: {map_info.map_name} `{field}` OK."
                _LOGGER.debug(log_msg)


def pretty_iterable_of_str(iterable: Iterable[str]) -> str:
    """Return e.g. `'a', 'b', 'c'`."""
    return f"'{"', '".join(iterable)}'"


def sort_maps_by_name(map_info: MapInformation) -> str:
    """Sort order for `MapInformation` instances."""
    if map_info.display_name is None:
        return map_info.map_name.casefold()
    return map_info.display_name.casefold()


def markdown_table(
    *, map_infos: Sequence[MapInformation], columns: dict[str, dict[str, str | bool]]
) -> str:
    """Create Markdown table."""
    th_values = [
        properties.get("display_heading", col).capitalize()
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
    for map_info in map_infos:
        for col, details in columns.items():
            td_value = handle_missing_value(getattr(map_info, col))
            if details.get("link_cell_content"):
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


def markdown_total_maps(map_infos: Sequence[MapInformation]) -> str:
    """Create Markdown total maps line."""
    return f"- {len(map_infos)} maps including season variants\n"


if __name__ == "__main__":
    main()
