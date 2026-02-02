"""Parse a mission's `mission.sqm` file with armaclass."""

import logging
from pathlib import Path

import armaclass

from src.mission.marker import Marker
from src.types_ import Node

LOGGER = logging.getLogger(__name__)


def _get_entities(node: Node) -> list[Node]:
    """Return `node`'s relevant data dict children.."""
    if "Entities" not in node:
        return []

    return [e for e in node["Entities"].values() if isinstance(e, dict)]


def _is_relevant_marker(node: Node) -> bool:
    """Check if the node represents a relevant marker."""
    return node.get("dataType") == "Marker" and any(
        node.get("name", "").lower().startswith(prefix)
        for prefix in Marker.RELEVANT_PREFIXES
    )


def _get_marker_nodes(node: Node) -> list[Node]:
    """Return `node`'s relevant marker node children."""
    return [e for e in _get_entities(node) if _is_relevant_marker(e)]


def _get_layer_nodes(node: Node) -> list[Node]:
    """Return `node`'s child layers."""
    return [e for e in _get_entities(node) if e.get("dataType") == "Layer"]


def _collect_marker_nodes(node: Node) -> list[Node]:
    """Return `node`'s relevant marker node descendants, recursively."""
    markers = _get_marker_nodes(node)
    for child_layer in _get_layer_nodes(node):
        markers.extend(_collect_marker_nodes(child_layer))

    return markers


def get_military_zone_marker_nodes(filepath: Path) -> list[Node]:
    """Get relevant marker nodes from the file."""
    with filepath.open(errors="ignore") as fp:
        data = fp.read()
    try:
        mission = armaclass.parse(data)
        log_msg = f"Parsed `{filepath}."
        LOGGER.debug(log_msg)
    except armaclass.ParseError:
        log_msg = f"Couldn't parse `{filepath}`; may be binarized."
        LOGGER.warning(log_msg)
        return []

    return _collect_marker_nodes(mission["Mission"])
