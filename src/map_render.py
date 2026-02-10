"""Render map images."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import matplotlib as mpl
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.colors import LightSource

from src.dem import DEM

if TYPE_CHECKING:
    from collections.abc import Iterable
    from pathlib import Path

    from matplotlib.axes import Axes

    from src.mission.marker import Marker
    from src.mission.mission import Mission
    from src.mission.town import Town

LOGGER = logging.getLogger(__name__)
MAP_IMAGE_SIZE_PX = 1000


def _plot_elevation(dem: DEM) -> None:
    z = dem.elevation
    ls = LightSource(azdeg=315, altdeg=45)
    plt.imshow(
        ls.hillshade(z, vert_exag=10),
        cmap=mpl.colormaps["gray"],
        extent=(0, dem.extents[0], 0, dem.extents[1]),  # `extent` order: l, r, btm, top
    )


def _plot_water(dem: DEM) -> None:
    z = dem.elevation
    ones = np.zeros(z.shape)
    alphas = (z <= 0).astype(float)
    plt.imshow(
        ones,
        cmap="terrain",
        extent=(0, dem.extents[0], 0, dem.extents[1]),  # `extent` order: l, r, btm, top
        alpha=alphas,
    )


def _plot_series(
    *,
    axes: Axes,
    iterable_: Iterable[Marker | Town],
    marker: str | None = None,
) -> None:
    """Plot `iterable_` as a scatter series."""
    positions = [i.position for i in iterable_ if i.position is not None]
    axes.scatter(
        [p.x for p in positions],
        [p.y for p in positions],
        color="red",
        marker=marker,
    )


def export_map(
    *, mission: Mission, grad_meh_dem_filepath: Path, export_filepath: Path
) -> None:
    """Load DEM (which must be `*.asc.gz`) and export a map render."""
    log_msg = f"'{mission.map_name}': plotting map..."
    LOGGER.info(log_msg)

    log_msg = f"'{mission.map_name}': - loading elevation..."
    LOGGER.info(log_msg)
    dem = DEM.from_esri_ascii_raster_gz(grad_meh_dem_filepath)
    log_msg = f"'{mission.map_name}':   done."
    LOGGER.info(log_msg)

    fig, ax = plt.subplots()
    size_inches = MAP_IMAGE_SIZE_PX / 100  # default 100 ppi
    fig.set_size_inches(size_inches, size_inches)

    log_msg = f"'{mission.map_name}': - rendering elevation..."
    LOGGER.info(log_msg)
    _plot_elevation(dem=dem)
    log_msg = f"'{mission.map_name}':   done."
    LOGGER.info(log_msg)

    log_msg = f"'{mission.map_name}': - rendering water..."
    LOGGER.info(log_msg)
    _plot_water(dem=dem)
    log_msg = f"'{mission.map_name}':   done."
    LOGGER.info(log_msg)

    marker_series = {
        "airports": "A",
        "bases": "B",
        "waterports": "W",
        "outposts": "O",
        "factories": "F",
        "resources": "R",
        "towns": "T",
    }
    for series_name, marker_char in marker_series.items():
        raw_series = mission.__getattribute__(series_name)
        plottable_series = [i for i in raw_series if i.position is not None]
        if raw_series and not plottable_series:
            log_msg = f"'{mission.map_name}': - no {series_name} positions to plot."
            LOGGER.error(log_msg)

        elif plottable_series:
            log_msg = f"'{mission.map_name}': - {series_name}..."
            LOGGER.info(log_msg)
            _plot_series(
                axes=ax,
                iterable_=plottable_series,
                marker=f"${marker_char}$",
            )

        else:
            log_msg = f"'{mission.map_name}': no {series_name}."
            LOGGER.info(log_msg)

    ax.set_aspect("equal")
    log_msg = f"'{mission.map_name}': - exporting..."
    LOGGER.info(log_msg)

    plt.savefig(export_filepath)
    plt.close()
    log_msg = f"'{mission.map_name}': exported '{export_filepath.name}'."
    LOGGER.info(log_msg)
