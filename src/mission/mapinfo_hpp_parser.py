"""Parse a mission's `mapInfo.hpp` file with `cxxheaderparser`."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Self

from cxxheaderparser.simple import parse_string

if TYPE_CHECKING:
    from collections.abc import Iterable
    from pathlib import Path

    from cxxheaderparser.simple import ClassScope
    from cxxheaderparser.tokfmt import Token

LOGGER = logging.getLogger(__name__)


def _unquote(value: str) -> str:
    """Remove double quotes from a string."""
    return value.strip('"')


def _filter_tokens(tokens: Iterable[Token]) -> list[str]:
    return [_unquote(token.value) for token in tokens if token.value not in "{},"]


def _field_lookup(*, field_name: str, class_scope: ClassScope) -> str | None:
    """Get field by name."""
    for field in class_scope.fields:
        t = field.type
        if (
            hasattr(t, "typename")
            and hasattr(t.typename.segments[0], "name")
            and t.typename.segments[0].name == field_name
        ):
            if field.value is None:
                err_msg = f"'{field_name}' field has no value."
                raise ValueError(err_msg)

            return field.value.tokens[0].value

    err_msg = f"Can't find '{field_name}' field."
    raise ValueError(err_msg)


def _field_array_lookup(*, field_name: str, class_scope: ClassScope) -> list[Token]:
    """Get field by name."""
    for field in class_scope.fields:
        t = field.type
        if (
            hasattr(t, "array_of")
            and hasattr(t.array_of, "typename")
            and hasattr(t.array_of.typename.segments[0], "name")
            and t.array_of.typename.segments[0].name == field_name
        ):
            if field.value is None:
                err_msg = f"'{field_name}' field has no value."
                raise ValueError(err_msg)

            return field.value.tokens

    err_msg = f"Can't find '{field_name}' field."
    raise ValueError(err_msg)


def _pairwise(t: Iterable[str | int]) -> Iterable[tuple[str | int, str | int]]:
    """Return pairs."""
    it = iter(t)
    return zip(it, it, strict=True)


def _get_climate(class_scope: ClassScope) -> str:
    """Get climate value."""
    value = _field_lookup(field_name="climate", class_scope=class_scope)
    return _unquote(str(value))


def _get_disabled_town_names(class_scope: ClassScope) -> list[str]:
    """Get disabled towns."""
    tokens = _field_array_lookup(field_name="disabledTowns", class_scope=class_scope)
    return _filter_tokens(tokens)


def _get_populations(class_scope: ClassScope) -> list[tuple[str, int]]:
    """
    Get population names and values.

    List of tuple instead of dict, as may include duplicate town names.
    """
    tokens = _field_array_lookup(field_name="population", class_scope=class_scope)
    values = _filter_tokens(tokens)
    return [
        (
            str(pair[0]),
            int(pair[1]),
        )
        for pair in _pairwise(values)
    ]


@dataclass(kw_only=True)
class MapInfoHppData:
    """Data from a mission's `mapInfo.hpp` file."""

    climate: str
    populations: list[tuple[str, int]]
    disabled_town_names: list[str]

    @classmethod
    def from_str(cls, str_: str) -> Self:
        """Parse str of file contents."""
        parsed_data = parse_string(str_)
        class_scope = parsed_data.namespace.classes[0]
        return cls(
            climate=_get_climate(class_scope),
            populations=_get_populations(class_scope),
            disabled_town_names=_get_disabled_town_names(class_scope),
        )

    @classmethod
    def from_file(cls, filepath: Path) -> Self:
        """Parse a `mapInfo.hpp` file."""
        with filepath.open() as fp:
            data = fp.read()

        log_msg = f"Parsing `{filepath}`."
        LOGGER.debug(log_msg)
        return cls.from_str(data)
