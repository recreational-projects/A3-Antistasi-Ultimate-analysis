"""Utilities."""

import tomllib
from collections.abc import Iterable
from pathlib import Path


def load_config(path: Path) -> dict[str, str]:
    """Load config."""
    with path.open("rb") as fp:
        return tomllib.load(fp)


def pretty_iterable_of_str(iterable: Iterable[str]) -> str:
    """Return e.g. `'a', 'b', 'c'`."""
    return f"'{"', '".join(iterable)}'"
