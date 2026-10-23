"""Parse a mission's `mapInfo.hpp` file with `cxxheaderparser`."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from itertools import batched
from typing import TYPE_CHECKING, Self

from cxxheaderparser.simple import parse_string

if TYPE_CHECKING:
    from collections.abc import Iterable
    from pathlib import Path

    from cxxheaderparser.simple import ClassScope
    from cxxheaderparser.tokfmt import Token
    from cxxheaderparser.types import Value

LOGGER = logging.getLogger(__name__)


@dataclass(kw_only=True)
class MapInfoHppData:
    """Data from an AU mission's `mapInfo.hpp` file."""

    climate: str
    populations: list[tuple[str, int]]
    disabled_town_names: list[str]

    @classmethod
    def from_file(cls, filepath: Path) -> Self:
        """Parse a `mapInfo.hpp` file."""
        with filepath.open() as fp:
            data = fp.read()

        log_msg = f"Parsing `{filepath}`."
        LOGGER.debug(log_msg)
        return cls._from_str(data)

    @classmethod
    def _from_str(cls, str_: str) -> Self:
        """Parse str of file contents."""
        parsed_data = parse_string(str_)
        class_scope = parsed_data.namespace.classes[0]
        return cls(
            climate=_get_climate(class_scope),
            populations=_get_populations(class_scope),
            disabled_town_names=_get_disabled_town_names(class_scope),
        )


def _get_climate(class_scope: ClassScope) -> str:
    """Get climate value."""
    value = _field_lookup(name="climate", class_scope=class_scope)
    return _unquote(str(value))


def _field_lookup(*, name: str, class_scope: ClassScope) -> str | None:
    """Get value of a field by name."""
    field_value = _generic_field_lookup(name=name, class_scope=class_scope)
    return field_value.tokens[0].value


def _get_populations(class_scope: ClassScope) -> list[tuple[str, int]]:
    """
    Get population names and values.

    List of tuple instead of dict, as may include duplicate town names.
    """
    tokens = _field_array_lookup(name="population", class_scope=class_scope)
    values = _filter_tokens(tokens)
    return [(str(pair[0]), int(pair[1])) for pair in batched(values, 2, strict=True)]


def _get_disabled_town_names(class_scope: ClassScope) -> list[str]:
    """Get disabled towns."""
    tokens = _field_array_lookup(name="disabledTowns", class_scope=class_scope)
    return _filter_tokens(tokens)


def _field_array_lookup(*, name: str, class_scope: ClassScope) -> list[Token]:
    """Get array value of a field by `name`."""
    field_value = _generic_field_lookup(name=name, class_scope=class_scope)
    return field_value.tokens


def _generic_field_lookup(*, name: str, class_scope: ClassScope) -> Value:
    for field in class_scope.fields:
        try:
            field_name = field.type.typename.segments[0].name

        except AttributeError as e:
            err_msg = f"Field '{name}' doesn't support this operation."
            raise AttributeError(err_msg) from e

        if field_name == name:
            if field.value is None:
                err_msg = f"'{name}' field has no value."
                raise ValueError(err_msg)

            return field.value

    err_msg = f"Can't find '{name}' field."
    raise ValueError(err_msg)


def _filter_tokens(tokens: Iterable[Token]) -> list[str]:
    return [_unquote(token.value) for token in tokens if token.value not in "{},"]


def _unquote(value: str) -> str:
    """Remove double quotes from a string."""
    return value.strip('"')
