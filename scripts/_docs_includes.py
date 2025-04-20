INTRO_MARKDOWN = """---
hide:
  - navigation
  - toc
---
# Compare missions in a sortable table

- This site aims to compare missions from the
  [Antistasi Ultimate](https://antistasiultimate.com/Home/) mod for
  [Arma 3](https://arma3.com/)
- Data is auto-generated from Antistasi Ultimate stable release v11.6.0
  [source code](https://github.com/SilenceIsFatto/A3-Antistasi-Ultimate) and verified
  against in-game information
"""

OUTRO_MARKDOWN = """
[^1]:
    *Total military objectives* = sum(*airports*, *sea/riverports*, *bases*,
    *outposts*, *factories*, *resources*)
[^2]:
    Known issue: towns aren't counted (and total War Level points can't be calculated)
    if they aren't explicitly declared in the mission files.<br>
    Missing towns counts will be added in future
[^3]:
    Ratio of mission's *total War Level Points* to the largest known value.<br>
    *Total War Level points* = sum(8 × *airports*, 6 × *bases*, 4 × *sea/riverports*,
    2 × *outposts*, 2 × *factories*, 2 × *resources*, *towns*) - thanks to Syrreal on
    AU Community Discord for pointing this out

## About this site

- [Source code](https://github.com/recreational-projects/A3-Antistasi-Ultimate-analysis)
  for this site;
  [changelog](https://github.com/recreational-projects/A3-Antistasi-Ultimate-analysis/blob/main/CHANGELOG.md);
  [raise a bug, question or feature request](https://github.com/recreational-projects/A3-Antistasi-Ultimate-analysis/issues)
"""
