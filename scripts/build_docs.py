"""
Generate the Markdown doc representing site content.

Load all JSON files in `DATA_RELATIVE_DIR`; export Markdown
to `OUTPUT_RELATIVE_DIR`.
"""

import json
import logging
from collections.abc import Sequence
from pathlib import Path

from cattrs import structure
from rich.logging import RichHandler
from rich.progress import track

from src.map_information import MapInformation
from src.utils import load_config

_COLUMNS = {
    "map_name": {
        "display_heading": "map",
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

- Towns aren't counted if they aren't explicitly declared in the mission files.
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
    return map_info.map_name.casefold()


def markdown_table(
    *, map_infos: Sequence[MapInformation], columns: dict[str, dict[str, str]]
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
        td_values = [handle_missing_value(getattr(map_info, col)) for col in columns]
        tbody += f"| {' | '.join(td_values)} |\n"

    return thead + tdivider + tbody


def handle_missing_value(val: int | str | None) -> str:
    """
    Display `` instead of `0` if value is `None`.

    `None` is used to flag unknown/missing value, as opposed to calculated zero.
    """
    return "" if val is None else str(val)


if __name__ == "__main__":
    main()
