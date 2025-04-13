"""Generate the Markdown doc representing site content."""

import logging
import unicodedata
from collections.abc import Sequence
from pathlib import Path

from rich.logging import RichHandler

from scripts._docs_includes import INTRO_MARKDOWN, OUTRO_MARKDOWN
from src.geojson.feature import Feature
from src.geojson.load import load_towns_from_dir
from src.mission.file import load_missions_data
from src.mission.mission import Mission
from src.utils import load_config, pretty_iterable_of_str, project_version
from static_data.au_mission_overrides import (
    EXCLUDED_MISSIONS,
    LOCATION_PREFIXES,
    LOCATION_SUFFIXES,
    LOCATION_TYPOS,
)
from static_data.in_game_data import IN_GAME_DATA
from static_data.map_index import MAP_INDEX

_COLUMNS: dict[str, dict[str, str | bool]] = {
    "map_name": {
        "display_heading": "Map",
    },
    "climate": {},
    "airports_count": {
        "display_heading": "Airports",
        "text-align": "right",
    },
    "bases_count": {
        "display_heading": "Bases",
        "text-align": "right",
    },
    "waterports_count": {
        "display_heading": "Sea/<br>riverports",
        "text-align": "right",
    },
    "outposts_count": {
        "display_heading": "Outposts",
        "text-align": "right",
    },
    "factories_count": {
        "display_heading": "Factories",
        "text-align": "right",
    },
    "resources_count": {
        "display_heading": "Resources",
        "text-align": "right",
    },
    "total_objectives_count": {
        "display_heading": "Total<br>military<br>objectives[^1]",
        "text-align": "right",
    },
    "towns_count": {
        "display_heading": "Towns[^2]",
        "text-align": "right",
    },
    "war_level_points_ratio_dynamic": {
        "display_heading": "Total<br>War Level<br>points[^3]<br>ratio<br>",
        "text-align": "right",
    },
}
_CONFIG_FILEPATH = "config.toml"
_LOGGER = logging.getLogger(__name__)


def main() -> None:
    """Generate the Markdown doc representing site content."""
    logging.basicConfig(
        level="INFO",
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler()],
    )
    base_filepath = Path(__file__).resolve().parent
    config = load_config(base_filepath / _CONFIG_FILEPATH)

    au_missions = load_missions_data(
        base_filepath / config["INTERMEDIATE_DATA_DIR_RELATIVE"],
        excludes=EXCLUDED_MISSIONS,
    )
    mission_map_names = {m.map_name for m in au_missions}
    unused_map_index_names = MAP_INDEX.keys() - mission_map_names
    if unused_map_index_names:
        log_msg = (
            f"Unexpected {len(unused_map_index_names)} map index data:"
            f"{pretty_iterable_of_str(list(unused_map_index_names))}'."
        )
        _LOGGER.warning(log_msg)

    unused_in_game_map_names = IN_GAME_DATA.keys() - mission_map_names
    if unused_in_game_map_names:
        log_msg = (
            f"Unexpected {len(unused_in_game_map_names)} reference data:"
            f"{pretty_iterable_of_str(list(unused_in_game_map_names))}'."
        )
        _LOGGER.warning(log_msg)

    gm_towns = load_towns_from_dir(
        base_filepath / config["GRAD_MEH_DATA_RELATIVE_DIR"]
    )
    log_msg = f"Loaded towns from {len(gm_towns)} grad-meh data sets."
    _LOGGER.info(log_msg)

    for mission in au_missions:
        map_name = mission.map_name

        if map_name not in MAP_INDEX:
            log_msg = f"'{map_name}': not in map index."
            _LOGGER.warning(log_msg)
        else:
            verify_vs_map_index(map_name=map_name, data=MAP_INDEX[map_name])

        if map_name not in IN_GAME_DATA:
            log_msg = f"'{map_name}': no in-game data."
            _LOGGER.warning(log_msg)
        else:
            verify_vs_in_game_data(au_mission=mission, data=IN_GAME_DATA[map_name])

        if map_name not in gm_towns:
            log_msg = f"'{map_name}': no grad-meh towns data"
            _LOGGER.warning(log_msg)
        else:
            verify_and_enrich_vs_grad_meh_data(au_mission=mission, data=gm_towns)

    max_war_level_points = max(
        mission.war_level_points for mission in au_missions if mission.war_level_points
    )

    markdown = (
        INTRO_MARKDOWN
        + markdown_total_missions(au_missions)
        + markdown_table(
            au_missions=sorted(au_missions, key=sort_missions_by_name),
            columns=_COLUMNS,
            max_war_level_points=max_war_level_points,
        )
        + OUTRO_MARKDOWN
        + markdown_version()
    )
    log_msg = "Generated Markdown."
    _LOGGER.info(log_msg)

    doc_file_path = base_filepath / config["MARKDOWN_OUTPUT_FILE_RELATIVE"]
    with Path.open(doc_file_path, "w", encoding="utf-8") as fp:
        fp.write(markdown)

    log_msg = f"Markdown saved to {doc_file_path}."
    _LOGGER.info(log_msg)


def verify_vs_map_index(*, map_name: str, data: dict[str, str]) -> None:
    """Verify generated data against reference data."""
    if not data.get("map_display_name"):
        log_msg = f"'{map_name}': no `map_display_name` in index."
        _LOGGER.warning(log_msg)

    if not data.get("url"):
        log_msg = f"'{map_name}' no `url` in index."
        _LOGGER.warning(log_msg)


def verify_vs_in_game_data(*, au_mission: Mission, data: dict[str, int]) -> None:
    """Verify generated data against in-game reference data."""
    for field in data:
        field_value = getattr(au_mission, field)
        reference_value = data.get(field)
        if field_value != reference_value:
            log_msg = (
                f"'{au_mission.map_name}': '{field}' verification failure: "
                f"{field_value} != {reference_value}."
            )
            _LOGGER.warning(log_msg)
        else:
            log_msg = f"'{au_mission.map_name}': `{field}` matches in-game data."
            _LOGGER.debug(log_msg)


def verify_and_enrich_vs_grad_meh_data(
    *, au_mission: Mission, data: dict[str, list[Feature]]
) -> None:
    """Verify generated data against grad-meh data."""
    gm_towns_ = {}
    for kind, towns in data.items():
        for town in towns:
            gm_towns_[town.properties.get("name")] = kind

    gm_towns_count = len(gm_towns_.keys())
    log_msg = f"Towns in grad-meh data: {gm_towns_count}"
    _LOGGER.info(log_msg)

    if not au_mission.towns_count:
        au_mission.towns = dict.fromkeys(gm_towns_.keys(), 0)
        log_msg = "Used grad-meh towns."
        _LOGGER.info(log_msg)

    else:
        difference = (
            gm_towns_count - au_mission.towns_count - len(au_mission.disabled_towns)
        )
        if difference:
            log_msg = f"MISMATCH OF {difference}."
            _LOGGER.warning(log_msg)


def normalise_town_name(name: str) -> str:
    """Normalise town names to enable fuzzy matching."""
    remove_chars = " .,_-'"

    for k, v in LOCATION_TYPOS.items():
        name = name.replace(k, v)
    for prefix in LOCATION_PREFIXES:
        name = name.removeprefix(prefix)
    for suffix in LOCATION_SUFFIXES:
        name = name.removesuffix(suffix)
    for char in list(remove_chars):
        name = name.replace(char, "")
    return strip_accents(name).lower()


def strip_accents(str_: str) -> str:
    """Normalize accented chars."""
    return "".join(
        c for c in unicodedata.normalize("NFD", str_) if unicodedata.category(c) != "Mn"
    )


def sort_missions_by_name(mission: Mission) -> str:
    """Sort order for `Mission`s table."""
    if mission.map_display_name is None:
        return mission.map_name.casefold()
    return mission.map_display_name.casefold()


def markdown_table(
    *,
    au_missions: Sequence[Mission],
    columns: dict[str, dict[str, str | bool]],
    max_war_level_points: int,
) -> str:
    """Create Markdown table."""
    th_values = [
        str(properties.get("display_heading", col))
        for col, properties in columns.items()
    ]
    thead = f"\n| {' <br>| '.join(th_values)} |\n"
    # <br> prevents sort indicator disrupting right-aligned text

    tdivider = ""
    for col_details in columns.values():
        tdivider += "| ---"
        tdivider += ":" if col_details.get("text-align") == "right" else " "

    tdivider += "|\n"

    tbody = ""
    for mission in au_missions:
        for col in columns:
            td_value = ""
            if col == "map_name":
                td_value = str(mission.map_display_name)
                if mission.download_url:
                    td_value = f"[{td_value}]({mission.download_url})"

            elif col == "war_level_points_ratio_dynamic":
                ratio = mission.war_level_points_ratio(max_war_level_points)
                if ratio:
                    td_value = f"{ratio:.2f}"
            else:
                td_value = markdown_handle_missing_value(getattr(mission, col))

            tbody += f"| {td_value} "
        tbody += "|\n"

    return thead + tdivider + tbody


def markdown_handle_missing_value(val: int | str | None) -> str:
    """
    Display `` instead of `0` if value is `None`.

    `None` is used to flag unknown/missing value, as opposed to calculated zero.
    """
    return "" if val is None else str(val)


def markdown_total_missions(missions: Sequence[Mission]) -> str:
    """Create Markdown total missions line."""
    return (
        f"- {len(missions)} maps total including season variants, excluding Stratis\n"
    )


def markdown_version() -> str:
    """
    Create Markdown project version line.

    Version from `pyproject.toml`.
    """
    version = project_version()
    return f"\n- Version {version}\n"


if __name__ == "__main__":
    main()
