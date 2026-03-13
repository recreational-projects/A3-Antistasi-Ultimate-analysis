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
    pyproject_filepath = (Path(__file__).parent / "../pyproject.toml").resolve()
    with pyproject_filepath.open("rb") as fp:
        version = tomllib.load(fp).get("project", {}).get("version")
        return str(version)


def load_config(path: Path) -> dict[str, str]:
    """Load config."""
    with path.open("rb") as fp:
        return tomllib.load(fp)


def configure_logging() -> None:
    """Configure logging in scripts."""
    config_filepath = (Path(__file__).parent / "../scripts/config.toml").resolve()
    config = load_config(config_filepath)
    logging.basicConfig(
        level=config["LOG_LEVEL"],
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler()],
    )
