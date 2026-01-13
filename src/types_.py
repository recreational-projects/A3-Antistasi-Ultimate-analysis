"""Define types."""

from typing import Any

type Node = dict[str, Any]
"""For hinting nodes in generic nested dicts."""
type JSONNode = Node
"""For hinting nodes in nested dicts derived from JSON."""
