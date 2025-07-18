"""Load data from GeoJSON files."""

import gzip
import logging
from pathlib import Path

import msgspec

from src.geojson.feature import Feature

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


def geojson_gz_files_in_dir(path: Path) -> list[Path]:
    """Return all `*.geojson.gz` files in `path`."""
    return [p for p in list(path.iterdir()) if p.suffixes == [".geojson", ".gz"]]


def load_features_from_file(path: Path) -> list[Feature]:
    """
    Load GeoJSON features from a `.geojson.gz` file.

    NB: grad_meh source files are gzipped JSON arrays of GeoJSON features, not GeoJSON
    compliant files.
    """
    with gzip.open(path, "rt", encoding="utf-8") as file:
        try:
            features = msgspec.json.decode(file.read(), type=list[Feature])
        except msgspec.ValidationError as err:
            err_msg = f"Error decoding JSON: {path}."
            raise ValueError(err_msg) from err

    if not features:
        log_msg = f"No valid GeoJSON features in `{path.name}`."
        LOGGER.warning(log_msg)
        return []

    return features
