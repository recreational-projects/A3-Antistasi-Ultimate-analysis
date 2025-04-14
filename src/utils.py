"""Utilities."""

import tomllib
from pathlib import Path


def load_config(path: Path) -> dict[str, str]:
    """Load config."""
    with path.open("rb") as fp:
        return tomllib.load(fp)
