"""Define types."""

from collections.abc import Mapping
from typing import Any

type MappingNode = Mapping[str, Any]
"""For hinting nodes in generic nested dicts, e.g. from JSON."""
