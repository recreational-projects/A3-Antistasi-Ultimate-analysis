"""Render map images."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from matplotlib import pyplot as plt

if TYPE_CHECKING:
    from collections.abc import Iterable
    from pathlib import Path

    from matplotlib.axes import Axes

    from src.mission.mission import Mission
    from src.mission.position_2d import Position2D

LOGGER = logging.getLogger(__name__)
MAP_IMAGE_SIZE_PX = 1000


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


def export_map_render(*, mission: Mission, export_filepath: Path) -> None:
    """Export a map render."""
    log_msg = f"'{mission.map_name}': plotting map..."
    LOGGER.info(log_msg)

    fig, ax = plt.subplots()
    size_inches = MAP_IMAGE_SIZE_PX / 100  # default 100 ppi
    fig.set_size_inches(size_inches, size_inches)

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
            LOGGER.error(log_msg)

        elif plottable_series:
            _plot_series(
                axes=ax,
                iterable_=plottable_series,
                marker=f"${marker_char}$",
            )
            log_msg = f"'{mission.map_name}': - plotted {series_name}."
            LOGGER.debug(log_msg)

        else:
            log_msg = f"'{mission.map_name}': - note: no {series_name}."
            LOGGER.info(log_msg)

    ax.set_aspect("equal")
    log_msg = f"'{mission.map_name}': - exporting..."
    LOGGER.info(log_msg)

    plt.savefig(export_filepath)
    plt.close()
    log_msg = f"'{mission.map_name}': exported '{export_filepath.name}'."
    LOGGER.info(log_msg)
