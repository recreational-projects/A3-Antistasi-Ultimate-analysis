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
from src.static_data.static_data import STATIC_DATA
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

    log_msg = (
        f"Loaded info for {len(map_infos)} maps; {len(STATIC_DATA)} reference keys."
    )
    _LOGGER.info(log_msg)

    map_names_without_display_names = [
        map_info.map_name for map_info in map_infos if not map_info.display_name
    ]
    if map_names_without_display_names:
        log_msg = (
            f"{len(map_names_without_display_names)} maps don't have a `display_name`: "
            f"{pretty_iterable_of_str(map_names_without_display_names)}."
        )
        _LOGGER.warning(log_msg)

    map_names = {map_info.map_name for map_info in map_infos}
    unmatched_reference_maps = {
        map_name for map_name in STATIC_DATA if map_name not in map_names
    }
    unreferenced_maps = {
        map_name for map_name in map_names if map_name not in STATIC_DATA
    }
    if unreferenced_maps:
        log_msg = (
            f"QC: {len(unreferenced_maps)} unreferenced maps: "
            f"{pretty_iterable_of_str(unreferenced_maps)}."
        )
        _LOGGER.warning(log_msg)
    if unmatched_reference_maps:
        log_msg = (
            f"QC: {len(unmatched_reference_maps)} unmatched reference maps:"
            f"{pretty_iterable_of_str(unmatched_reference_maps)}'."
        )
        _LOGGER.warning(log_msg)

    for map_info in map_infos:
        map_info_reference_data = STATIC_DATA.get(map_info.map_name)
        if map_info_reference_data:
            for field in map_info_reference_data:
                field_value = getattr(map_info, field)
                reference_value = map_info_reference_data.get(field)
                if reference_value is None:
                    return
                if field_value != reference_value:
                    log_msg = (
                        f"QC: {map_info.map_name} '{field}' mismatch: "
                        f"{field_value} != {reference_value}"
                    )
                    _LOGGER.warning(log_msg)
                else:
                    log_msg = f"QC: {map_info.map_name} `{field}` OK."
                    _LOGGER.debug(log_msg)

    with Path.open(doc_file_path, "w", encoding="utf-8") as fp:
        fp.write(
            _INTRO_MARKDOWN
            + markdown_table(
                map_infos=sorted(map_infos, key=alphasort), columns=_COLUMNS
            )
            + _KNOWN_ISSUES_MARKDOWN
        )


def alphasort(map_info: MapInformation) -> str:
    """Sort `MapInformation` instances."""
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


def pretty_iterable_of_str(iterable: Iterable[str]) -> str:
    """Return e.g. `'a', 'b', 'c'`."""
    return f"'{"', '".join(iterable)}'"


if __name__ == "__main__":
    main()
