"""Plot map markers."""

from collections.abc import Sequence

from matplotlib import pyplot as plt
from matplotlib import ticker
from matplotlib.axes import Axes

from .marker import Marker

_MAP_PPI = 100
_MAP_IMAGE_SIZE_DEFAULT_PX = 800
"""Overall image dimensions."""


def setup_plot(size_px: int = _MAP_IMAGE_SIZE_DEFAULT_PX) -> Axes:
    """Set up the plot and return `Axes` instance."""
    fig, ax = plt.subplots()
    fig.set_size_inches(size_px / _MAP_PPI, size_px / _MAP_PPI)
    locator = ticker.MultipleLocator(base=1000)
    formatter = ticker.EngFormatter(unit="m")
    for a in ax.xaxis, ax.yaxis:
        a.set_major_locator(locator)
        a.set_major_formatter(formatter)
    ax.grid(axis="both", color="0.85")
    ax.set_box_aspect(1)  # square plot
    return ax


def plot_markers(
    *,
    axes: Axes,
    map_markers: Sequence[Marker],
    alpha: float = 1,
    marker: str | None = None,
) -> None:
    """Plot `map_markers` as a scatter series."""
    points = [m.position for m in map_markers]
    axes.scatter(
        [p.x for p in points],
        [p.y for p in points],
        alpha=alpha,
        marker=marker,
    )


def finalise_plot(ax: Axes) -> None:
    """Plot formatting that needs to be done after data is plotted."""
    ax.set_xlim(0, None)
    ax.set_ylim(0, None)
    ax.set_axisbelow(True)
