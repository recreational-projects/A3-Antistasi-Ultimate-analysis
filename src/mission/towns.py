"""Load data from GeoJSON files."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from arma3_offline_map_lib.geojson import (
    geojson_gz_files_in_dir,
    load_features_from_file,
)

if TYPE_CHECKING:
    from pathlib import Path

    from arma3_offline_map_lib.geojson import Feature


LOGGER = logging.getLogger(__name__)


def load_towns_from_dir(path: Path) -> list[Feature]:
    """
    Load town locations (subset of GeoJSON features) from files in a directory.

    Directory must exist.

    Returns:
         `dict`. Keys are `FILENAME_STEM` for each relevant
         `path/{FILENAME_STEM}.geojson.gz`.

    """
    towns: list[Feature] = []

    filepaths = [
        fp
        for fp in geojson_gz_files_in_dir(path)
        if fp.stem.removesuffix(".geojson")
        in ("namecitycapital", "namecity", "namevillage")
    ]
    for fp in filepaths:
        locations = load_features_from_file(fp)
        towns.extend(locations)

    return towns
