"""Parse a mission's `mapInfo.hpp` file."""

import logging
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from cxxheaderparser.simple import ClassScope, parse_string
from cxxheaderparser.tokfmt import Token

LOGGER = logging.getLogger(__name__)


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


def _unquote(value: str) -> str:
    """Remove double quotes from a string."""
    return value.strip('"')


def _get_climate(class_scope: ClassScope) -> str:
    """Get climate value."""
    value = _field_lookup(field_name="climate", class_scope=class_scope)
    return _unquote(str(value))


def pairwise(t: Iterable[str | int]) -> Any:
    """Return pairs."""
    it = iter(t)
    return zip(it, it, strict=True)


def _filter_tokens(tokens: list[Token]) -> list[str]:
    return [_unquote(token.value) for token in tokens if token.value not in "{},"]


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
        for pair in pairwise(values)
    ]


def _get_disabled_towns(class_scope: ClassScope) -> list[str]:
    """Get disabled towns."""
    tokens = _field_array_lookup(field_name="disabledTowns", class_scope=class_scope)
    return _filter_tokens(tokens)


def _parse(str_: str) -> dict[str, Any]:
    """Parse relevant contents of a `mapInfo.hpp` file."""
    parsed_data = parse_string(str_)
    class_scope = parsed_data.namespace.classes[0]
    climate = _get_climate(class_scope)
    populations = _get_populations(class_scope)
    disabled_towns = _get_disabled_towns(class_scope)
    return {
        "climate": climate,
        "populations": populations,
        "disabled_towns": disabled_towns,
    }


def parse_mapinfo_hpp_file(filepath: Path) -> dict[str, Any]:
    """Parse a `mapInfo.hpp` file."""
    with Path.open(filepath) as fp:
        data = fp.read()

    log_msg = f"Parsed `{filepath}`."
    LOGGER.debug(log_msg)
    return _parse(data)
