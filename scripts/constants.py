"""Define constants."""

from pathlib import Path

from src.utils import load_config

BASE_PATH = Path(__file__).resolve().parent
_CONFIG_FILENAME = "config.toml"
CONFIG = load_config(BASE_PATH / _CONFIG_FILENAME)
