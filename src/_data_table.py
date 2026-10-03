"""Generate the Markdown data table."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

from attrs import define, field
from attrs.validators import in_

if TYPE_CHECKING:
    from collections.abc import Iterable

    from .mission.mission import Mission

_COLUMN_CONFIG_DATA: dict[str, Any] = {
    "map_name": {
        "display_heading": "Map",
    },
    "climate": {
        "display_heading": "Climate",
    },
    "airports_count": {
        "display_heading": "Airports",
        "text_align": "RIGHT",
    },
    "bases_count": {
        "display_heading": "Bases",
        "text_align": "RIGHT",
    },
    "waterports_count": {
        "display_heading": "Sea/<br>riverports",
        "text_align": "RIGHT",
    },
    "outposts_count": {
        "display_heading": "Outposts",
        "text_align": "RIGHT",
    },
    "factories_count": {
        "display_heading": "Factories",
        "text_align": "RIGHT",
    },
    "resources_count": {
        "display_heading": "Resources",
        "text_align": "RIGHT",
    },
    "total_military_zones_count": {
        "display_heading": "Total<br>military<br>zones[^1]",
        "text_align": "RIGHT",
    },
    "towns_count": {
        "display_heading": "Towns",
        "text_align": "RIGHT",
    },
    "war_level_points_ratio_dynamic": {
        "display_heading": "Total<br>War Level<br>points[^2]<br>ratio<br>",
        "text_align": "RIGHT",
    },
}


@define(frozen=True, kw_only=True)
class _ColumnConfig:
    display_heading: str | None = field(default=None)
    """Column display heading. If `None`, the column name will be used."""
    text_align: Literal["LEFT", "RIGHT"] = field(
        default="LEFT", validator=in_(("LEFT", "RIGHT"))
    )

    @classmethod
    def dict_from_data(cls, data: dict[str, Any]) -> dict[str, _ColumnConfig]:
        return {col_config: cls(**data[col_config]) for col_config in data}


def markdown_table(missions: Iterable[Mission]) -> str:
    """Create Markdown table."""
    missions = sorted(missions, key=_sort_missions_by_points, reverse=True)
    max_war_level_points = max(
        m.war_level_points for m in missions if m.war_level_points
    )
    column_configs = _ColumnConfig.dict_from_data(_COLUMN_CONFIG_DATA)
    header = _table_header(column_configs)
    rows = [
        _table_row(
            mission=mission_,
            column_configs=column_configs,
            max_war_level_points=max_war_level_points,
        )
        for mission_ in missions
    ]
    return header + "".join(rows) + "\n"


def _table_header(column_configs: dict[str, _ColumnConfig]) -> str:
    th_values = [
        getattr(config, "display_heading", col)
        for col, config in column_configs.items()
    ]
    thead = f"\n| {' <br>| '.join(th_values)} |\n"
    # <br> prevents sort indicator disrupting right-aligned text
    tdivider = ""
    for column_config in column_configs.values():
        tdivider += "| ---"
        tdivider += ":" if column_config.text_align == "RIGHT" else " "

    tdivider += "|\n"
    return thead + tdivider


def _table_row(
    *,
    mission: Mission,
    column_configs: dict[str, _ColumnConfig],
    max_war_level_points: int,
) -> str:
    """Create Markdown table row."""
    tr = ""
    for col in column_configs:
        if col == "map_name":
            td_value = _map_name_cell_value(mission)
        elif col == "war_level_points_ratio_dynamic":
            td_value = _war_level_points_ratio_cell_value(mission, max_war_level_points)
        else:
            td_value = _markdown_handle_missing_value(getattr(mission, col))

        tr += f"| {td_value} "

    tr += "|\n"
    return tr


def _map_name_cell_value(mission: Mission) -> str:
    if mission.map_url:
        return f"[{mission.map_display_name}]({mission.map_url})"

    return f"{mission.map_display_name}"


def _war_level_points_ratio_cell_value(
    mission: Mission, max_war_level_points: int
) -> str:
    ratio = mission.war_level_points_ratio(max_war_level_points)
    return f"{ratio:.2f}" if ratio else ""


def _markdown_handle_missing_value(val: int | str | None) -> str:
    """
    Display '' instead of '0' if value is `None`.

    `None` is used to flag unknown/missing value, as opposed to calculated zero.
    """
    return "" if val is None else str(val)


def _sort_missions_by_points(mission: Mission) -> int:
    """Sort order for `Mission`s table."""
    return 0 if mission.war_level_points is None else mission.war_level_points
