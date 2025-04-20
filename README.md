# A3-Antistasi-Ultimate-analysis

Source code for https://recreational-projects.github.io/A3-Antistasi-Ultimate-analysis/

- Aims to compare missions from the
  [Antistasi Ultimate mod](https://antistasiultimate.com/Home/) for
  [Arma 3](https://arma3.com/)
- Data is generated from
  [Antistasi Ultimate source code](https://github.com/SilenceIsFatto/A3-Antistasi-Ultimate)
  and reference data, and verified against in-game data
- NB: this is mostly a learning project


## Usage

### Pre-requisites 

- Clone or download this repo
- Set up a Python environment 
- Clone or download Antistasi Ultimate source code repo
- Optional: use [grad_meh](https://github.com/gruppe-adler/grad_meh) to get locations
- Edit `/scripts/config.toml` to point to these two data sources 

### Analyse missions and export data

Run Python script:

```shell
/scripts/analyse_missions.py
```
to generate data from each AU mission, compare with reference data and export JSON files to `data/`.

- Analyses `/mission.sqm` using [Armaclass](https://github.com/overfl0/Armaclass)
  library and `mapInfo.hpp` using a custom [pyparsing](https://github.com/pyparsing/pyparsing) parser
- Gets each mission's friendly map name and download URL from
  `/static_data/map_index.py`
- Gets towns from [grad_meh](https://github.com/gruppe-adler/grad_meh) data if available and the
  mission doesn't explicitly define the towns used 
- Verifies the number of objectives (not towns) against information derived from
  Antistasi Ultimate's in-game screenshots from `/static_data/in_game_data.py`
- Logs info and warnings

### Generate Markdown from data

Run Python script

```shell
/scripts/build_docs.py
```
to load intermediate data and generate a
single Markdown file in `/docs/`.

- Logs info and warnings

### Generate static site from Markdown

#TODO


## License

`/static_data/` contains data derived from Antistasi Ultimate assets and from 
other parties. See individual files for  licensing information.

Otherwise, the [MIT licence](/LICENSE) applies - the same as
[Antistasi Ultimate source code](https://github.com/SilenceIsFatto/A3-Antistasi-Ultimate).

