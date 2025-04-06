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

_LOGGER = logging.getLogger(__name__)

_LBRACE, _RBRACE, _SEMICOLON, _COMMA, _EQ = map(
    pp.Suppress,
    "{};,=",
)
_MAP_INFO_STRING = pp.dblQuotedString().setParseAction(pp.removeQuotes)

MAPINFO_CLIMATE = pp.Suppress("climate") + _EQ + _MAP_INFO_STRING + _SEMICOLON
MAPINFO_POPULATIONS = (
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


def get_map_info_data(filepath: Path) -> dict[str, Any]:
    """Get key data from the file."""
    with Path.open(filepath) as fp:
        map_info_file_data = fp.read()

    try:
        climate = str(MAPINFO_CLIMATE.search_string(map_info_file_data)[0][0])
    except IndexError:
        climate = None
    try:
        populations_parse_result = MAPINFO_POPULATIONS.search_string(
            map_info_file_data,
        )[0]
        populations = list(populations_parse_result)
    except IndexError:
        populations = []

    log_msg = f"Parsed `{filepath}`."
    _LOGGER.debug(log_msg)

    return {"climate": climate, "populations": populations}
