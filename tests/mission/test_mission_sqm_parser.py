"""Tests for `mission.sqm` parser."""

import pytest

from src.mission.mission_sqm_parser import (
    JSONNode,
    _get_entities,
    _get_layer_nodes,
    _get_marker_nodes,
)


@pytest.fixture
def parsed_root_fragment() -> JSONNode:
    """Cut-down fragment from root of parse result."""
    return {
        "Mission": {
            "Entities": {
                "Item0": {
                    "dataType": "Layer",
                    "name": "Basics",
                    "Entities": {
                        "Item0": {
                            "dataType": "Marker",
                            "name": "milbase_1",
                            "type": "flag_CSAT",
                        },
                    },
                },
                "Item1": {
                    "dataType": "Layer",
                    "name": "Airfields",
                    "Entities": {
                        "Item0": {
                            "dataType": "Marker",
                            "name": "airport",
                            "markerType": "RECTANGLE",
                            "type": "rectangle",
                            "colorName": "ColorEAST",
                        },
                    },
                },
            },
        }
    }


def test_get_entities(parsed_root_fragment: JSONNode) -> None:
    """Test that entities are derived from a given node."""
    # arrange
    # act
    my_entities = _get_entities(parsed_root_fragment["Mission"])
    # assert
    assert my_entities[0]["name"] == "Basics"
    assert my_entities[1]["name"] == "Airfields"


def test_get_marker_nodes(parsed_root_fragment: JSONNode) -> None:
    """Test that markers are derived from a given node."""
    # arrange
    # act
    my_markers = _get_marker_nodes(parsed_root_fragment["Mission"]["Entities"])
    # assert
    assert my_markers[0]["name"] == "milbase_1"


def test_get_layer_nodes(parsed_root_fragment: JSONNode) -> None:
    """Test that markers are derived from a given node."""
    # arrange
    # act
    my_layers = _get_layer_nodes(parsed_root_fragment["Mission"])
    # assert
    assert my_layers[0]["name"] == "Basics"
    assert my_layers[1]["name"] == "Airfields"
