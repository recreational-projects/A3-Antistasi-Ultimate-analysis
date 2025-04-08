"""`Marker` class."""

from typing import Any, Self

from attrs import define

from src.position import Position


@define
class Marker:
    """Represents a map marker."""

    name: str
    type_: str
    position: Position

    @classmethod
    def from_data(
        cls,
        data: dict[str, Any],
    ) -> Self:
        """Construct instance from data."""
        return cls(
            name=data["name"],
            type_=data["type"],
            position=Position.from_data(data["position"]),
        )

    @property
    def is_airport(self) -> bool:
        """Return `True` if an airport."""
        return self.name.startswith("airport")

    @property
    def is_base(self) -> bool:
        """Return `True` if a base."""
        return self.name.startswith("milbase")

    @property
    def is_factory(self) -> bool:
        """Return `True` if a factory."""
        return self.name.startswith("factory")

    @property
    def is_outpost(self) -> bool:
        """Return `True` if a outpost."""
        return self.name.startswith("outpost")

    @property
    def is_resource(self) -> bool:
        """Return `True` if a resource."""
        return self.name.startswith("resource")

    @property
    def is_waterport(self) -> bool:
        """Return `True` if a sea/riverport."""
        return self.name.startswith("seaport")
