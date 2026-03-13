"""Define constants."""

from __future__ import annotations

from pathlib import Path

from src.utils import load_config

_BASE_PATH = Path(__file__).parent
_CONFIG = load_config(_BASE_PATH / "config.toml")
_PATHS = {
    "AU_MAPS_DIR": (_BASE_PATH / _CONFIG["AU_SOURCE_DIR_RELATIVE"] / "A3A/addons/maps"),
    "GRAD_MEH_DIR": (_BASE_PATH / _CONFIG["GRAD_MEH_DATA_DIR_RELATIVE"]),
    "DATA_DIR": (_BASE_PATH / _CONFIG["INTERMEDIATE_DATA_DIR_RELATIVE"]),
    "MARKDOWN_OUTPUT_DIR": (_BASE_PATH / _CONFIG["MARKDOWN_OUTPUT_DIR_RELATIVE"]),
}
PATHS = {}
for name, path in _PATHS.items():
    PATHS[name] = path.resolve()
    if not path.is_dir():
        err_msg = f"{name}: {path} not found"
        raise RuntimeError(err_msg)
