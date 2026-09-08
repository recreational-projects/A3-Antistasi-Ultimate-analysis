"""Filter data from a `mission.sqm` file."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from arma3_offline_map_lib.mission.mission_sqm import Marker

RELEVANT_MARKER_PREFIXES = {
    # case-insensitive
    "airport",
    "factory",
    "milbase",
    "outpost",
    "resource",
    "seaport",
}


def military_zone_markers(marker_list: list[Marker]) -> dict[str, list[Marker]]:
    """Derive military zone markers from a list of markers."""
    marker_dict: dict[str, list[Marker]] = {
        prefix: [] for prefix in RELEVANT_MARKER_PREFIXES
    }
    for marker in marker_list:
        for prefix, list_ in marker_dict.items():
            if marker.name and marker.name.lower().startswith(prefix):
                list_.append(marker)

    return marker_dict
