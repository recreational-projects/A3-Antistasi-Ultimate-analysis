"""Render map images."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from arma3_offline_map_lib.grad_meh.dem import DEM
from arma3_offline_map_lib.grad_meh.metadata import Metadata
from arma3_offline_map_lib.mission.mission_sqm import Marker
from matplotlib import pyplot as plt
from PIL import Image

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

# basic map with background plotted for:
# abramia, altis, bornholm, chernarus, chernarus_summer, chernarus_winter, enoch,
# gm_weferlingen_summer (no river), gm_weferlingen_winter (no river), gulfcoast,
# iron_excelsior_tobruk, kapaulio, kunduz, lythium, malden, mehland, napf, napfwinter,
# panthera3, rhspkl, sara, spex_utah_beach, staszow, staszowwinter, stratis, takistan,
# tanoa, tem_anizay, umb_colombia, vt7, winthera3, yulakia

# wip:
# pja310, tem_kujari,


def export_map_render(
    *, mission: Mission, grad_meh_mission_dir: Path, export_dir: Path
) -> None:
    """
    Export a map render, with coastline if DEM is available.

    Coastline images are cached.
    """
    log_msg = f"'{mission.map_name}': plotting map..."
    _LOGGER.info(log_msg)
    fig, ax = plt.subplots()
    size_inches = _MAP_IMAGE_SIZE_PX / 100  # default 100 ppi
    fig.set_size_inches(size_inches, size_inches)
    coastline_img_path = export_dir / f"{mission.map_name}_coastline.png"
    _render_coastline_if_needed(
        coastline_img_path=coastline_img_path,
        grad_meh_mission_dir=grad_meh_mission_dir,
        map_name=mission.map_name,
    )

    if coastline_img_path.is_file():
        land_sea_image = Image.open(coastline_img_path)
        metadata = Metadata.from_file(grad_meh_mission_dir / "meta.json")
        ax.imshow(
            land_sea_image, extent=(0, metadata.world_size, 0, metadata.world_size)
        )
        log_msg = f"'{mission.map_name}': map plot: coastline embedded."
        _LOGGER.info(log_msg)

    marker_series = {
        "airports": "A",
        "bases": "B",
        "waterports": "W",
        "outposts": "O",
        "factories": "F",
        "resources": "R",
        "redfor_support_corridor": "X",
        "blufor_support_corridor": "Y",
    }
    for series_name, marker_char in marker_series.items():
        markers_ = mission.__getattribute__(series_name)
        if isinstance(markers_, Marker):
            markers_ = [markers_]  # handle single Marker by wrapping in list

        if not markers_:
            log_msg = (
                f"'{mission.map_name}`: map plot: can't plot empty `{series_name}`."
            )
            _LOGGER.warning(log_msg)
            continue

        _plot_marker_series(
            ax=ax,
            markers=markers_,
            marker_char=marker_char,
            map_name=mission.map_name,
            series_name=series_name,
        )

    map_path = export_dir / f"{mission.map_name}_map.png"
    fig.savefig(map_path)
    plt.close()
    log_msg = f"'{mission.map_name}': map plot: exported '{map_path}'."
    _LOGGER.info(log_msg)


def _render_coastline_if_needed(
    *, coastline_img_path: Path, grad_meh_mission_dir: Path, map_name: str
) -> None:
    """`map_name` used for logging only."""
    if coastline_img_path.is_file():
        log_msg = f"'{map_name}': map plot: coastline already exists."
        _LOGGER.info(log_msg)
    else:
        grad_meh_dem_filepath = grad_meh_mission_dir / "dem.asc.gz"
        if not grad_meh_dem_filepath.is_file():
            log_msg = f"'{map_name}': map plot: no DEM - can't render coastline."
            _LOGGER.warning(log_msg)
        else:
            dem = DEM.from_esri_ascii_raster_gz(grad_meh_dem_filepath)
            dem.export_land_sea_image(
                path=coastline_img_path,
                land_color=_LAND_COLOR_RGB,
                sea_color=_WATER_COLOR_RGB,
            )
            log_msg = f"'{map_name}': map plot: coastline rendered."
            _LOGGER.info(log_msg)


def _plot_marker_series(
    *,
    ax: Axes,
    markers: list[Marker],
    marker_char: str,
    map_name: str,
    series_name: str,
) -> None:
    """`map_name` and `series_name` used for logging only."""
    plottable_markers = [m.position for m in markers if m.position is not None]
    if markers and not plottable_markers:
        log_msg = f"'{map_name}': map plot: no {series_name} positions to plot."
        _LOGGER.error(log_msg)

    elif plottable_markers:
        _plot_iterable(
            axes=ax,
            iterable_=plottable_markers,
            marker=f"${marker_char}$",
        )
        log_msg = f"'{map_name}': map plot: plotted {series_name}."
        _LOGGER.debug(log_msg)

    else:
        log_msg = f"'{map_name}': map plot: no {series_name}."
        if series_name == "waterports":
            _LOGGER.info(log_msg)
        else:
            _LOGGER.error(log_msg)


def _plot_iterable(
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
