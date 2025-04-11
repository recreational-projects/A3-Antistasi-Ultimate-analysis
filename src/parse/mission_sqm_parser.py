"""Parse `mission.sqm` file."""

import logging
from pathlib import Path
from typing import Any

import armaclass

from src.constants import INCLUDE_MARKER_NAMES_STARTS_WITH

_LOGGER = logging.getLogger(__name__)

type JSONNode = dict[str, Any]


def get_marker_nodes(
    filepath: Path,
) -> list[JSONNode]:
    """Get marker `JSONNode`s from the file."""
    with Path.open(filepath, errors="ignore") as fp:
        data = fp.read()

    try:
        mission = armaclass.parse(data)
        log_msg = f"Parsed `...{filepath}."
        _LOGGER.debug(log_msg)
        nodes = collect_marker_nodes(mission["Mission"])

    except armaclass.ParseError:
        nodes = []
        log_msg = f"Couldn't parse `...{filepath}` - may be binarized."
        _LOGGER.warning(log_msg)

    return nodes


def collect_marker_nodes(node: JSONNode) -> list[JSONNode]:
    """Return `node`'s relevant marker node descendants, recursively."""
    markers = _get_marker_nodes(node)
    children = _get_layer_nodes(node)
    if not children:
        return markers
    for child_layer in children:
        markers.extend(collect_marker_nodes(child_layer))
    return markers


def _get_marker_nodes(node: JSONNode) -> list[JSONNode]:
    """Return `node`'s relevant marker node children."""
    return [
        e
        for e in _get_entities(node)
        if e.get("dataType") == "Marker"
        and any(
            e["name"].lower().startswith(string)
            for string in INCLUDE_MARKER_NAMES_STARTS_WITH
        )
    ]


def _get_layer_nodes(node: JSONNode) -> list[JSONNode]:
    """Return `node`'s child layers."""
    return [e for e in _get_entities(node) if e.get("dataType") == "Layer"]


def _get_entities(node: JSONNode) -> list[JSONNode]:
    """Return `node`'s relevant data dict children.."""
    if "Entities" not in node:
        return []
    return [e for e in node["Entities"].values() if isinstance(e, dict)]
