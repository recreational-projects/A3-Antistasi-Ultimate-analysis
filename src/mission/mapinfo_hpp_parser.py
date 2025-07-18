"""
Parse `mapInfo.hpp` file.

Simple `pyparsing` custom parser to get only critical info,  as `armaclass` parser
fails on common elements in `mapInfo.hpp` like `#INCLUDE`.
"""

import logging
from pathlib import Path
from typing import Any

import pyparsing as pp
from pyparsing import common as ppc

LOGGER = logging.getLogger(__name__)

_LBRACE, _RBRACE, _SEMICOLON, _COMMA, _EQ = map(
    pp.Suppress,
    "{};,=",
)
_MAP_INFO_STRING = pp.dblQuotedString().setParseAction(pp.removeQuotes)

CLIMATE = pp.Suppress("climate") + _EQ + _MAP_INFO_STRING + _SEMICOLON
POPULATIONS = (
    pp.Suppress("population[]")
    + _EQ
    + _LBRACE
    + pp.DelimitedList(
        pp.Group(
            _LBRACE + _MAP_INFO_STRING + _COMMA + ppc.integer + _RBRACE,
            aslist=True,
        ),
    )
    + _RBRACE
    + _SEMICOLON
)
DISABLED_TOWNS = (
    pp.Suppress("disabledTowns[]")
    + _EQ
    + _LBRACE
    + pp.DelimitedList(_MAP_INFO_STRING)
    + _RBRACE
    + _SEMICOLON
)


def get_map_info_data(filepath: Path) -> dict[str, Any]:
    """Get key data from the file."""
    with Path.open(filepath) as fp:
        map_info_file_data = fp.read()

    climate = str(CLIMATE.search_string(map_info_file_data)[0][0])
    try:
        populations_parse_result = POPULATIONS.search_string(
            map_info_file_data,
        )[0]
        populations = list(populations_parse_result)
    except IndexError:
        populations = []
    try:
        disabled_towns_parse_result = DISABLED_TOWNS.search_string(map_info_file_data)[
            0
        ]
        disabled_towns = list(disabled_towns_parse_result)
    except IndexError:
        disabled_towns = []

    log_msg = f"Parsed `{filepath}`."
    LOGGER.debug(log_msg)

    return {
        "climate": climate,
        "populations": populations,
        "disabled_towns": disabled_towns,
    }
