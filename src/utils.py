"""Utilities."""

from __future__ import annotations

import logging
import tomllib
from pathlib import Path
from typing import TYPE_CHECKING

from rich.logging import RichHandler

if TYPE_CHECKING:
    from collections.abc import Iterable


def pretty_iterable_of_str(iterable: Iterable[str]) -> str:
    """Return e.g. `'a', 'b', 'c'`."""
    return f"'{"', '".join(iterable)}'"


def project_version() -> str | None:
    """Get project version from `pyproject.toml`."""
    filepath = Path(__file__).resolve().parent / "../pyproject.toml"
    with filepath.open("rb") as fp:
        version = tomllib.load(fp).get("project", {}).get("version")
        return str(version)


def configure_logging() -> None:
    """Configure logging in scripts."""
    logging.basicConfig(
        level="INFO",
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler()],
    )
