"""Define constants."""

import tomllib
from pathlib import Path

BASE_PATH = Path(__file__).resolve().parent
_CONFIG_FILENAME = "config.toml"


def load_config(path: Path) -> dict[str, str]:
    """Load config."""
    with path.open("rb") as fp:
        return tomllib.load(fp)


CONFIG = load_config(BASE_PATH / _CONFIG_FILENAME)
