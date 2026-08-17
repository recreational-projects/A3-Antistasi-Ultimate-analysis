"""Tests for the `Mission` class."""

import json

from src.mission.mission import Mission

JSON = """{
    "map_name": "stratis",
    "map_display_name": "Stratis",
    "map_url": "https://store.steampowered.com/app/107410",
    "climate": "arid",
    "towns": {
        "Camp Tempest": null,
        "Camp Maxwell": null,
        "Stratis Air Base": null,
        "Air Station Mike-26": null,
        "Kamino Firing Range": null,
        "Camp Rogain": null,
        "Girna": null,
        "Agia Marina": null
    },
    "disabled_towns": [],
    "airports": [],
    "factories": [],
    "bases": [],
    "outposts": [],
    "waterports": [],
    "resources": [],
    "exclude": true
}
"""


def test_from_json_data() -> None:
    """Test that a `Mission` can be loaded from JSON data."""
    # arrange
    mission_dict = json.loads(JSON)
    # act
    mission = Mission._from_json_data(mission_dict)
    # assert
    assert mission.map_name == "stratis"
