# A3-Antistasi-Ultimate-analysis

Source code for https://recreational-projects.github.io/A3-Antistasi-Ultimate-analysis/

- Aims to compare missions from the
  [Antistasi Ultimate ('AU')](https://antistasiultimate.com/) mod for
  [Arma 3](https://arma3.com/)
- Information is generated from
  [AU source code](https://github.com/Antistasi-Ultimate-Community/A3-Antistasi-Ultimate)
  and reference data, and verified against in-game data
- NB: this is mostly a Python learning project


## Usage

### Pre-requisites 

- Cloned/downloaded copy of current
  [AU source code](https://github.com/Antistasi-Ultimate-Community/A3-Antistasi-Ultimate)
- Arma 3 map data exported with
  [Gruppe Adler Map Exporter ('grad_meh`)](https://github.com/gruppe-adler/grad_meh) mod

- These instructions assume you have [uv](http://docs.astral.sh/uv/) installed.

### Initial setup/configuration

- Clone/download this repo and set up a Python environment
- Copy `config_dist.toml` to `config.toml` and edit as required:
  - `AU_SOURCE_DIR_RELATIVE`: relative path to AU source directory
  - `GRAD_MEH_DATA_DIR_RELATIVE`: relative path to a folder with grad_meh data

### Analyse missions and export data

Run Python script:

```shell
uv run --frozen --module src.analyse_missions
```
to generate data from each AU mission, compare with reference data and
export temporary JSON files to `working_data/`.

- Analyses the mission's `mission.sqm` and `mapInfo.hpp`
- Gets each mission's friendly map name and download URL from
  `src/static_data/map_index.py`
- Gets towns from [grad_meh](https://github.com/gruppe-adler/grad_meh) data if available
  and the mission doesn't explicitly define the towns used 
- Verifies the number of military zones (not towns) against information derived from
  Antistasi Ultimate's in-game screenshots from `src/static_data/in_game_data.py`
- Logs info and warnings
- Should take around 5–10 seconds to complete

### Generate Markdown from data

- Edit `src/docs_includes.py` with relevant AU version number

- Run Python script:

  ```shell
  uv run --frozen --module src.build_docs
  ```
  to load intermediate data and generate a single Markdown file
  in `docs/`.

  - Logs info and warnings
  - Should take around one second to complete

### Generate static site from Markdown and preview locally in browser

```shell
uv run --frozen mkdocs serve
```

## License

`src/static_data/` contains data derived from Antistasi Ultimate assets and from 
other parties. See individual files for  licensing information.

Otherwise, the [MIT licence](/LICENSE) applies - the same as
[Antistasi Ultimate source code](https://github.com/SilenceIsFatto/A3-Antistasi-Ultimate).
