"""`Marker` class."""

from typing import ClassVar, Self

from attrs import define
from cattrs import structure

from src.types_ import Node


@define
class Marker:
    """Represents a map marker."""

    INCLUDE_STARTS_WITH: ClassVar = {
        # case-insensitive
        "airport",
        "factory",
        "milbase",
        "outpost",
        "resource",
        "seaport",
    }

    name: str

    @classmethod
    def from_data(cls, data: Node) -> Self:
        """Construct instance from data."""
        return structure(data, cls)

    @property
    def is_airport(self) -> bool:
        """Return `True` if an airport."""
        return self.name.lower().startswith("airport")

    @property
    def is_waterport(self) -> bool:
        """
        Return `True` if a sea/riverport.

        Map `vt7` is the only known map to use "Seaport".
        """
        return self.name.lower().startswith("seaport")

    @property
    def is_base(self) -> bool:
        """Return `True` if a base."""
        return self.name.lower().startswith("milbase")

    @property
    def is_outpost(self) -> bool:
        """
        Return `True` if a outpost.

        Map `vt7` is the only known map to use "Outpost".
        """
        return self.name.lower().startswith("outpost")

    @property
    def is_factory(self) -> bool:
        """Return `True` if a factory."""
        return self.name.lower().startswith("factory")

    @property
    def is_resource(self) -> bool:
        """Return `True` if a resource."""
        return self.name.lower().startswith("resource")
