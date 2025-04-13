"""TO DO."""

import gzip
import logging
from pathlib import Path

import msgspec

from src.geojson.feature import Feature

_LOGGER = logging.getLogger(__name__)


def load_towns_from_dir(path: Path) -> dict[str, list[Feature]]:
    """
    Load town locations (subset of GeoJSON features) from files in a directory.

    Returns:
         `dict`. Keys are `FILENAME_STEM` for each relevant
         `path/{FILENAME_STEM}.geojson.gz`.

    """
    locations: dict[str, list[Feature]] = {}

    filepaths = [
        fp
        for fp in geojson_gz_files_in_dir(path)
        if fp.stem.removesuffix(".geojson")
        in ("namecitycapital", "namecity", "namevillage")
    ]

    for fp in filepaths:
        locations_data = load_features_from_file(path=fp)
        kind = fp.stem.removesuffix(".geojson")
        locations[kind] = locations_data

    return locations


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
        features = msgspec.json.decode(file.read(), type=list[Feature])

    if not features:
        log_msg = f"- No valid features in `{path.name}`."
        _LOGGER.warning(log_msg)
        return []

    return features
