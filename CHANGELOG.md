# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).


## UNRELEASED - TBC

### Added

- Log error when mission fails military zone count verification
- `scripts/build_docs.py`: log project version

### Changed

- Update military zone count reference value for Sumava in AU v11.7.0


## [0.10.0] - 2025-06-22

### Added

- Updated for AU v11.7.0 (adds Kunduz River map, changes Šumava)
- `scripts/analyse_missions.py`: improve logging when map not in indices


## [0.9.2] - 2025-05-03

### Added

- Completed in-game military zones data, so this is now verified for all missions

### Fixed

- URL to AU website was out of date


## [0.9.1] - 2025-04-21

### Fixed

- When towns are not defined in the mission and were pulled from grad_meh data,
  disabled towns were sometimes counted - affected Anizay, Malden 2035, Napf
  Island A3, Napf Island A3 (Winter)


## [0.9.0] - 2025-04-20

### Added

- All remaining towns counts except Sefrou-Ramal, derived from grad_meh
  locations extracts 
- Sort by War Level points initially


## [0.8.0] - 2025-04-19

### Added

- [Simple Analytics](https://www.simpleanalytics.com/) (non-tracking)

### Fixed

- Disabled towns were still counted


## [0.7.1] - 2025-04-17

### Fixed

- New Esseker missing


## [0.7.0] - 2025-04-17

### Added

- Exclude Stratis from table
- Replace Total war level points column with ratio
- Reorder table columns, improve headings
- Use footnotes
- Site version
- Auto dark mode
- Auto-hide site header
- Custom site icon
- CI: lint, format, type checking

### Fixed

- Missing friendly map names and links


## [0.6.0] - 2025-04-12

### Added

- Display friendly map names and link to download location
- Display map count

### Improved

- Site text and links; log messages


## [0.5.0] - 2025-04-11

### Added

- Data quality control: total outposts (and a few other data points) are checked against verified values

### Fixed

- Map `vt7` outposts and seaports weren't counted - marker collection and enumeration is now case-insensitive


## [0.4.0] - 2025-04-10

### Added

- Separate column for each objective type
- Outposts column
- Total war level points column
- Custom column headings, right align number columns

### Changed

- Don't show site navigation or TOC


## [0.3.1] - 2025-04-09

### Fixed

- Table Markdown issue

### Removed

- Inclusion of outposts in `objectives_count` - wasn't correctly calculated


## [0.3.0] - 2025-04-09

### Added

- This CHANGELOG
- Outposts included in `objectives_count`
- Update for Antistasi Ultimate v11.6.0 (already included new map, but text had old version number)
- Site text: point out table is sortable, link to CHANGELOG

### Fixed

- Airports weren't included in `objectives_count`
- Text implied bases weren't included in `objectives_count`
- Site text: Heading levels


## [0.2.0] - 2025-04-08

### Added

- `objectives_count` column


## [0.1.0] - 2025-04-08

Initial release


[0.10.0]: https://github.com/recreational-projects/A3-Antistasi-Ultimate-analysis/compare/v0.9.2...v0.10.0
[0.9.2]: https://github.com/recreational-projects/A3-Antistasi-Ultimate-analysis/compare/v0.9.1...v0.9.2
[0.9.1]: https://github.com/recreational-projects/A3-Antistasi-Ultimate-analysis/compare/v0.9.0...v0.9.1
[0.9.0]: https://github.com/recreational-projects/A3-Antistasi-Ultimate-analysis/compare/v0.8.0...v0.9.0
[0.8.0]: https://github.com/recreational-projects/A3-Antistasi-Ultimate-analysis/compare/v0.7.1...v0.8.0
[0.7.1]: https://github.com/recreational-projects/A3-Antistasi-Ultimate-analysis/compare/v0.7.0...v0.7.1
[0.7.0]: https://github.com/recreational-projects/A3-Antistasi-Ultimate-analysis/compare/v0.6.0...v0.7.0
[0.6.0]: https://github.com/recreational-projects/A3-Antistasi-Ultimate-analysis/compare/v0.5.0...v0.6.0
[0.5.0]: https://github.com/recreational-projects/A3-Antistasi-Ultimate-analysis/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/recreational-projects/A3-Antistasi-Ultimate-analysis/compare/v0.3.1...v0.4.0
[0.3.1]: https://github.com/recreational-projects/A3-Antistasi-Ultimate-analysis/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/recreational-projects/A3-Antistasi-Ultimate-analysis/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/recreational-projects/A3-Antistasi-Ultimate-analysis/compare/v0.2.0...v0.1.0
[0.1.0]: https://github.com/recreational-projects/A3-Antistasi-Ultimate-analysis/releases/tag/v0.1.0