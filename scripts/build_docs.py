"""
Generate the Markdown doc representing site content.

Load all JSON files in `DATA_RELATIVE_DIR`; export Markdown
to `OUTPUT_RELATIVE_DIR`.
"""

import json
import logging
from pathlib import Path

from cattrs import structure
from rich.logging import RichHandler
from rich.progress import track

from src.map_information import MapInformation
from src.utils import load_config

_COLUMNS = ["map_name", "climate", "towns_count", "objectives_count"]
_INTRO_MARKDOWN = """
# Compare missions in a sortable table

- Generated from Antistasi Ultimate stable release v11.6.0
  [source code](https://github.com/SilenceIsFatto/A3-Antistasi-Ultimate)
- [Source code](https://github.com/recreational-projects/A3-Antistasi-Ultimate-analysis)
  for this site;
  [changelog](https://github.com/recreational-projects/A3-Antistasi-Ultimate-analysis/blob/main/CHANGELOG.md)
- Objectives = airports, bases, sea/riverports, factories, outposts, resources

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

    map_infos = sorted(map_infos, key=alphasort)

    table_header = f"\n|{'|'.join(_COLUMNS)}|\n"
    table_header += f"{len(_COLUMNS) * '|---'}|\n"
    table_data = ""
    for map_info in map_infos:
        for col in _COLUMNS:
            table_data += f"|{handle_missing_value(getattr(map_info, col))}"
        table_data += "|\n"

    markdown = _INTRO_MARKDOWN + table_header + table_data + _KNOWN_ISSUES_MARKDOWN

    with Path.open(doc_file_path, "w", encoding="utf-8") as fp:
        fp.write(markdown)


def alphasort(map_info: MapInformation) -> str:
    """Sort `MapInformation` instances."""
    return map_info.map_name.casefold()


def handle_missing_value(val: int | str | None) -> str:
    """Show `?` instead of `0` if value is missing/unknown."""
    if val is None or val == 0:
        return ""
    return str(val)


if __name__ == "__main__":
    main()
