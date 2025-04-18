# A3-Antistasi-Ultimate-analysis

Source code for https://recreational-projects.github.io/A3-Antistasi-Ultimate-analysis/

- Aims to compare missions from the
  [Antistasi Ultimate](https://antistasiultimate.com/Home/) mod for
  [Arma 3](https://arma3.com/)
- Data is generated from Antistasi Ultimate 
  [source code](https://github.com/SilenceIsFatto/A3-Antistasi-Ultimate) and verified
  against in-game information
- NB: this is mostly a learning project


## Usage

### Pre-requisites: 

- Clone or download this repo
- Set up a Python environment 
- Clone or download Antistasi Ultimate source code repo
- Configure `scripts/config.toml` to point to the AU source code

### Analyse missions and export intermediate data

Run Python script `scripts/analyse_missions.py` to generate data from each AU mission 
and export JSON files to `data/`

- Analyses `mission.sqm` using [Armaclass](https://github.com/overfl0/Armaclass)
  library
- Analyses `mapInfo.hpp` using a custom
  [pyparsing](https://github.com/pyparsing/pyparsing) parser
- Logs info and warnings

### Generate Markdown from data

Run Python script `scripts/build_docs.py` to load intermediate data, compare with
reference data and generate a single Markdown file in `/docs`

- Gets each mission's friendly map name and download URL from
  `static_data/map_index.py`
- Verifies the number of objectives (not towns) against information derived from
  Antistasi Ultimate's in-game screenshots from `static_data/in_game_data.py`
- Logs info and warnings

### Generate static site from Markdown

#TODO