"""Define constants and non-core functions used by multiple scripts."""

import logging
import tomllib
from pathlib import Path

from rich.logging import RichHandler

LOGGER = logging.getLogger(__name__)


def load_config(path: Path) -> dict[str, str]:
    """Load config."""
    with path.open("rb") as fp:
        return tomllib.load(fp)


def configure_logging() -> None:
    """Configure logging in scripts."""
    logging.basicConfig(
        level="INFO",
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler()],
    )


def require_dir(path: Path) -> None:
    """Require that the path is a directory."""
    if not path.is_dir():
        err_msg = f"No such directory: `{path}` (resolves to `{path.resolve()}`)"
        raise RuntimeError(err_msg)


_BASE_PATH = Path(__file__).resolve().parent
_CONFIG = load_config(_BASE_PATH / "config.toml")

AU_MAPS_DIRPATH = Path(_CONFIG["AU_SOURCE_DIR_RELATIVE"]) / "A3A/addons/maps"
GRAD_MEH_DIRPATH = Path(_CONFIG["GRAD_MEH_DATA_DIR_RELATIVE"])
DATA_DIRPATH = Path(_CONFIG["INTERMEDIATE_DATA_DIR_RELATIVE"])
DOC_DIRPATH = Path(_CONFIG["MARKDOWN_OUTPUT_DIR_RELATIVE"])
