"""Parse all maps in `INPUT_RELATIVE_DIR` and export JSON to `OUTPUT_RELATIVE_DIR`."""

import json
import logging
from pathlib import Path

from attrs import asdict
from rich.logging import RichHandler
from rich.progress import track

from src.mission.file import mission_dirs_in_dir
from src.mission.mission import Mission
from src.utils import load_config

_CONFIG_FILEPATH = "config.toml"
_LOGGER = logging.getLogger(__name__)


def main() -> None:
    """Parse all maps."""
    logging.basicConfig(
        level="INFO",
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler()],
    )
    base_filepath = Path(__file__).resolve().parent
    config = load_config(base_filepath / _CONFIG_FILEPATH)
    input_dir_path = base_filepath / config["INPUT_RELATIVE_DIR"]
    output_dir_path = base_filepath / config["DATA_RELATIVE_DIR"]
    output_dir_path.mkdir(parents=True, exist_ok=True)

    all_map_dirs = mission_dirs_in_dir(input_dir_path)
    map_exports_count = 0

    for dir_ in track(all_map_dirs, description="Analysing missions..."):
        mission = Mission.from_dir(dir_)

        if mission is None:
            log_msg = f"Couldn't get any data from {dir_}."
            _LOGGER.warning(log_msg)

        else:
            export_filename = f"{dir_.name}.json"
            with Path.open(
                output_dir_path / export_filename, "w", encoding="utf-8"
            ) as file:
                json.dump(
                    asdict(mission),
                    file,
                    ensure_ascii=False,
                    indent=4,
                    sort_keys=True,
                )
                map_exports_count += 1
                log_msg = f"Exported '{export_filename}'."
                _LOGGER.info(log_msg)

    log_msg = f"Exported data for {map_exports_count} missions."
    _LOGGER.info(log_msg)


if __name__ == "__main__":
    main()
