"""Parse all maps in `INPUT_RELATIVE_DIR` and export JSON to `OUTPUT_RELATIVE_DIR`."""

import json
import logging
from pathlib import Path

from attrs import asdict
from rich.logging import RichHandler
from rich.progress import track

from src.map_information import MapInformation
from src.utils import load_config, maps_in_dir

_LOGGER = logging.getLogger(__name__)


def main() -> None:
    """Parse all maps."""
    logging.basicConfig(
        level="INFO",
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler()],
    )
    config = load_config()
    base_filepath = Path(__file__).resolve().parent
    input_dir_path = base_filepath / config["INPUT_RELATIVE_DIR"]
    output_dir_path = base_filepath / config["DATA_RELATIVE_DIR"]
    output_dir_path.mkdir(parents=True, exist_ok=True)

    all_map_dirs = maps_in_dir(input_dir_path)
    map_exports_count = 0

    for map_dir in track(all_map_dirs, description="Analysing maps..."):
        map_info = MapInformation.from_files(map_dir)

        if map_info is None:
            log_msg = f"Couldn't get any data from {map_dir}."
            _LOGGER.warning(log_msg)

        else:
            export_filepath = output_dir_path / f"{map_dir.name}.json"

            with Path.open(export_filepath, "w", encoding="utf-8") as file:
                json.dump(
                    asdict(map_info),
                    file,
                    ensure_ascii=False,
                    indent=4,
                    sort_keys=True,
                )
                map_exports_count += 1
                log_msg = f"Exported '{export_filepath}'."
                _LOGGER.info(log_msg)

    log_msg = f"Exported data for {map_exports_count} maps."
    _LOGGER.info(log_msg)


if __name__ == "__main__":
    main()
