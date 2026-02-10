"""Render map images."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from matplotlib import pyplot as plt

from src.dem import DEM

if TYPE_CHECKING:
    from pathlib import Path

LOGGER = logging.getLogger(__name__)


def export_map_render(dem_filepath: Path, export_filepath: Path) -> None:
    """Load DEM (which must be `*.asc.gz`) and export a map render."""
    dem = DEM.from_esri_ascii_raster_gz(dem_filepath)
    elevation = dem.data_array
    elevation[elevation < 0] = -0.05
    elevation[elevation >= 0] = 4
    _fig, ax = plt.subplots()
    plt.imshow(dem.data_array, cmap="terrain", vmin=-0.25, vmax=1)
    ax.set_aspect("equal")
    plt.savefig(export_filepath)
    plt.close()
