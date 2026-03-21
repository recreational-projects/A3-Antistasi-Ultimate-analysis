"""Parse a mission's `mission.sqm` file with `armaclass`."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Self

import armaclass

from src.mission.marker import Marker

if TYPE_CHECKING:
    from pathlib import Path

    from src.types_ import DictNode

LOGGER = logging.getLogger(__name__)
RELEVANT_MARKER_PREFIXES = {
    # case-insensitive
    "airport",
    "factory",
    "milbase",
    "outpost",
    "resource",
    "seaport",
}


def _get_entities(node: DictNode) -> list[DictNode]:
    """Return `node`'s relevant data dict children.."""
    if "Entities" not in node:
        return []

    return [e for e in node["Entities"].values() if isinstance(e, dict)]


def _is_relevant_marker(node: DictNode) -> bool:
    """Check if the node represents a relevant marker."""
    return node.get("dataType") == "Marker" and any(
        node.get("name", "").lower().startswith(prefix)
        for prefix in RELEVANT_MARKER_PREFIXES
    )


def _get_child_layers(node: DictNode) -> list[DictNode]:
    """Return `node`'s child layers."""
    return [e for e in _get_entities(node) if e.get("dataType") == "Layer"]


def _collect_markers(node: DictNode) -> list[Marker]:
    """Return `node`'s relevant descendants as `Marker`s, recursively."""
    markers = [
        Marker.from_mission_sqm_data(e)
        for e in _get_entities(node)
        if _is_relevant_marker(e)
    ]
    for layer_node in _get_child_layers(node):
        markers.extend(_collect_markers(layer_node))

    return markers


@dataclass(kw_only=True)
class MissionSqmData:
    """Data from a mission's `mission.sqm` file."""

    military_zone_markers: dict[str, list[Marker]]

    @classmethod
    def from_file(cls, filepath: Path) -> Self | None:
        """Parse a `mission.sqm` file."""
        with filepath.open(errors="ignore") as f:
            data = f.read()

        try:
            mission = armaclass.parse(data)
            log_msg = f"Parsed `{filepath}`."
            LOGGER.debug(log_msg)
        except armaclass.ParseError:
            log_msg = f"Couldn't parse `{filepath}`; may be binarized."
            LOGGER.warning(log_msg)
            return None

        marker_list = _collect_markers(mission["Mission"])
        markers: dict[str, list[Marker]] = {
            prefix: [] for prefix in RELEVANT_MARKER_PREFIXES
        }
        for marker in marker_list:
            for prefix, list_ in markers.items():
                if marker.name.lower().startswith(prefix):
                    list_.append(marker)

        return cls(military_zone_markers=markers)
