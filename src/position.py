"""`Position` class."""

from typing import Self

from attrs import define


@define
class Position:
    """3D coordinate for `Marker`."""

    x: float
    y: float
    z: float

    @classmethod
    def from_data(
        cls,
        data: list[float],
    ) -> Self:
        """Construct instance from data."""
        return cls(
            x=data[0],
            y=data[2],
            z=data[1],
        )
