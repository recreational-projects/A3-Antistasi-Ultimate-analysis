"""Render map images."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from arma3_offline_map_lib.grad_meh.dem import DEM
from matplotlib import pyplot as plt

if TYPE_CHECKING:
    from collections.abc import Iterable
    from pathlib import Path

    from arma3_offline_map_lib.position_2d import Position2D
    from matplotlib.axes import Axes

    from src.mission.mission import Mission

_MAP_IMAGE_SIZE_PX = 1000
_LAND_COLOR_RGB = (230, 230, 230)  # light gray
_WATER_COLOR_RGB = (183, 203, 230)  # light blue

_LOGGER = logging.getLogger(__name__)


def export_map_render(
    *, mission: Mission, grad_meh_dem_filepath: Path, export_filepath: Path
) -> None:
    """Load gzipped DEM (must be `*.asc.gz`) and export a map render."""
    log_msg = f"'{mission.map_name}': plotting map..."
    _LOGGER.info(log_msg)
    fig, ax = plt.subplots()
    size_inches = _MAP_IMAGE_SIZE_PX / 100  # default 100 ppi
    fig.set_size_inches(size_inches, size_inches)
    if not grad_meh_dem_filepath.is_file():
        log_msg = f"'{mission.map_name}': - no DEM."
        _LOGGER.warning(log_msg)

    else:
        log_msg = f"'{mission.map_name}': - loading DEM..."
        _LOGGER.info(log_msg)
        dem = DEM.from_esri_ascii_raster_gz(grad_meh_dem_filepath)
        log_msg = f"'{mission.map_name}':   done."
        _LOGGER.info(log_msg)
        dem.render_land_sea_image(
            path=export_filepath,
            land_color=_LAND_COLOR_RGB,
            sea_color=_WATER_COLOR_RGB,
        )
    marker_series = {
        "airports": "A",
        "bases": "B",
        "waterports": "W",
        "outposts": "O",
        "factories": "F",
        "resources": "R",
    }
    for series_name, marker_char in marker_series.items():
        raw_series = mission.__getattribute__(series_name)
        plottable_series = [i.position for i in raw_series if i.position is not None]
        if raw_series and not plottable_series:
            log_msg = f"'{mission.map_name}': - no {series_name} positions to plot."
            _LOGGER.error(log_msg)

        elif plottable_series:
            _plot_series(
                axes=ax,
                iterable_=plottable_series,
                marker=f"${marker_char}$",
            )
            log_msg = f"'{mission.map_name}': - plotted {series_name}."
            _LOGGER.debug(log_msg)

        else:
            log_msg = f"'{mission.map_name}': - note: no {series_name}."
            _LOGGER.info(log_msg)

    log_msg = f"'{mission.map_name}': - exporting..."
    _LOGGER.info(log_msg)
    fig.savefig(export_filepath)
    plt.close()
    log_msg = f"'{mission.map_name}': exported '{export_filepath}'."
    _LOGGER.info(log_msg)


def _plot_series(
    *,
    axes: Axes,
    iterable_: Iterable[Position2D],
    marker: str | None = None,
) -> None:
    """Plot `iterable_` as a scatter series."""
    axes.scatter(
        [p.x for p in iterable_],
        [p.y for p in iterable_],
        marker=marker,
    )
