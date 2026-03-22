"""Markdown content chunks."""

INTRO_MARKDOWN = """---
hide:
  - navigation
  - toc
---
# Compare missions in a sortable table

- This site aims to compare missions from the
  [Antistasi Ultimate](https://antistasiultimate.com/) mod for
  [Arma 3](https://arma3.com/)
- Data is auto-generated from Antistasi Ultimate stable release v11.8.6
  [source code](https://github.com/SilenceIsFatto/A3-Antistasi-Ultimate) and verified
  against in-game information
"""
COLUMNS: dict[str, dict[str, str | bool]] = {
    "map_name": {
        "display_heading": "Map",
    },
    "climate": {
        "display_heading": "Climate",
    },
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
    "total_military_zones_count": {
        "display_heading": "Total<br>military<br>zones[^1]",
        "text-align": "right",
    },
    "towns_count": {
        "display_heading": "Towns",
        "text-align": "right",
    },
    "war_level_points_ratio_dynamic": {
        "display_heading": "Total<br>War Level<br>points[^2]<br>ratio<br>",
        "text-align": "right",
    },
}
OUTRO_MARKDOWN = """
[^1]:
    *Total military zones* = sum(*airports*, *sea/riverports*, *bases*,
    *outposts*, *factories*, *resources*)
[^2]:
    Ratio of mission's *total War Level Points* to the largest known value.<br>
    *Total War Level points* = sum(8 × *airports*, 6 × *bases*, 4 × *sea/riverports*,
    2 × *outposts*, 2 × *factories*, 2 × *resources*, 1 × *towns*) - thanks to Syrreal
    on AU Community Discord for pointing this out

## About this site

- [Source code](https://github.com/recreational-projects/A3-Antistasi-Ultimate-analysis)
  for this site;
  [changelog](https://github.com/recreational-projects/A3-Antistasi-Ultimate-analysis/blob/main/CHANGELOG.md);
  [raise a bug, question or feature request](https://github.com/recreational-projects/A3-Antistasi-Ultimate-analysis/issues)
"""
