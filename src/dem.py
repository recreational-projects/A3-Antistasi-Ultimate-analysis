"""Digital Elevation Model (DEM) class."""

from __future__ import annotations

import gzip
from dataclasses import dataclass
from typing import TYPE_CHECKING, Self

import numpy as np

if TYPE_CHECKING:
    from pathlib import Path

    from numpy.typing import NDArray

ESRI_ASCII_HEADER_PARAMETERS = {
    # ref https://desktop.arcgis.com/en/arcmap/latest/manage-data/raster-and-images/esri-ascii-raster-format.htm
    "NCOLS": "Number of cell columns",  # Integer greater than 0.
    "NROWS": "Number of cell rows",  # Integer greater than 0.
    "XLLCORNER": "X-coordinate of the origin (by lower left corner of the cell)",
    "YLLCORNER": "Y-coordinate of the origin (by lower left corner of the cell)",
    "CELLSIZE": "Cell size",  # Greater than 0.
    "NODATA_VALUE": "The input values to be NoData in the output raster",
    # Optional in spec. Default is -9999.
}


@dataclass
class DEM:
    """
    Digital Elevation Model class.

    Quick and dirty implementation.
    """

    elevation: NDArray[np.float16]
    cell_size: float

    @property
    def data_size(self) -> tuple[int, int]:
        """Return data dimensions."""
        return self.elevation.shape[0], self.elevation.shape[1]

    @property
    def extents(self) -> tuple[int, int]:
        """Return actual dimensions."""
        return (
            self.cell_size * self.elevation.shape[0],
            self.cell_size * self.elevation.shape[1],
        )

    @classmethod
    def from_esri_ascii_raster_gz(cls, file_path: Path) -> Self:
        """Load an ESRI ASCII raster from a gzipped file."""
        header = {}
        with gzip.open(file_path, "rt") as file:
            # np.loadtxt(file) does handle gzipped files, but we need the headers
            header_lines = [
                next(file) for _ in range(len(ESRI_ASCII_HEADER_PARAMETERS))
            ]
            for line in header_lines:
                elements = line.split(" ", 1)
                if elements[0].upper() in ESRI_ASCII_HEADER_PARAMETERS:
                    header[elements[0].upper()] = float(elements[1])

            data_array = np.loadtxt(file, dtype="float16")

            if data_array.ndim != 2:  # noqa: PLR2004
                err_msg = f"Data array dimensions {data_array.ndim} must be 2."
                raise ValueError(err_msg)

            if data_array.shape != (header["NROWS"], header["NCOLS"]):
                err_msg = (
                    f"Data array shape {data_array.shape} does not match "
                    f"header {header['NROWS'], header['NCOLS']}."
                )
                raise ValueError(err_msg)

        return cls(
            elevation=data_array,
            cell_size=header["CELLSIZE"],
        )
