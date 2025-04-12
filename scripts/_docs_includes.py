INTRO_MARKDOWN = """---
hide:
  - navigation
  - toc
---
# Compare missions in a sortable table

- This site aims to compare missions from the
  [Antistasi Ultimate](https://antistasiultimate.com/Home/) mod for
  [Arma 3](https://arma3.com/)
- Data is generated from Antistasi Ultimate stable release v11.6.0
  [source code](https://github.com/SilenceIsFatto/A3-Antistasi-Ultimate) and verified
  against in-game information
"""

KNOWN_ISSUES_MARKDOWN = """
## Notes

- [Source code](https://github.com/recreational-projects/A3-Antistasi-Ultimate-analysis)
  for this site;
  [changelog](https://github.com/recreational-projects/A3-Antistasi-Ultimate-analysis/blob/main/CHANGELOG.md);
  [raise a bug, question or feature request](https://github.com/recreational-projects/A3-Antistasi-Ultimate-analysis/issues)
- *Total military objectives* = *airports* + *sea/riverports* + *bases* + *outposts* +
  *factories* + *resources*
- *Total War Level points* = 8 × *airports* + 6 × *bases* + 4 × *sea/riverports* +
  2 × *outposts* + 2 × *resources* + 2 × *factories* + *towns*. Thanks to Syrreal on
  AU Community Discord for pointing this out
  
## Known issues and limitations

- Towns aren't counted (and total War Level points can't be calculated) if they aren't
  explicitly declared in the mission files. Data will be manually compiled and added
  in future
"""
