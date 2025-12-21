# A3-Antistasi-Ultimate-analysis

Source code for https://recreational-projects.github.io/A3-Antistasi-Ultimate-analysis/

- Aims to compare missions from the
  [Antistasi Ultimate ('AU')](https://antistasiultimate.com/) mod for
  [Arma 3](https://arma3.com/)
- Information is generated from
  [AU source code](https://github.com/SilenceIsFatto/A3-Antistasi-Ultimate)
  and reference data, and verified against in-game data
- NB: this is mostly a Python learning project


## Usage

### Pre-requisites 

- Cloned/downloaded copy of current
  [AU source code](https://github.com/SilenceIsFatto/A3-Antistasi-Ultimate).
  
  Only the contents of `A3A/addons/maps` folder is required (~ 120 MB)

- Arma 3 installation with
  [Gruppe Adler Map Exporter ('grad_meh`)](https://github.com/gruppe-adler/grad_meh) mod

### Initial setup/configuration

- Clone/download this repo and set up a Python environment
- Edit `scripts/config.toml`:
  - `AU_SOURCE_DIR_RELATIVE`: relative path to AU source's `A3A/addons/maps` directory
  - `GRAD_MEH_DATA_DIR_RELATIVE`: relative path to a folder where grad_meh data will be 
    put later

### Analyse missions and export data

Run Python script:

```shell
python -m scripts.analyse_missions
```
or equivalent to generate data from each AU mission, compare with reference data and
export temporary JSON files to `working_data/`.

- Analyses the mission's `mission.sqm` using
  [Armaclass library](https://github.com/overfl0/Armaclass) and `mapInfo.hpp` using a custom [pyparsing](https://github.com/pyparsing/pyparsing) parser
- Gets each mission's friendly map name and download URL from
  `static_data/map_index.py`
- Gets towns from [grad_meh](https://github.com/gruppe-adler/grad_meh) data if available
  and the mission doesn't explicitly define the towns used 
- Verifies the number of military zones (not towns) against information derived from
  Antistasi Ultimate's in-game screenshots from `static_data/in_game_data.py`
- Logs info and warnings

### Generate Markdown from data

- Edit `scripts/docs_includes.py` with relevant AU version number

- Run Python script:

  ```shell
  python -m scripts.build_docs
  ```
  or equivalent to load intermediate data and generate a single Markdown file
  in `docs/`.

  - Logs info and warnings

### Generate static site from Markdown and preview locally in browser

```shell
mkdocs serve
```

## License

`static_data/` contains data derived from Antistasi Ultimate assets and from 
other parties. See individual files for  licensing information.

Otherwise, the [MIT licence](/LICENSE) applies - the same as
[Antistasi Ultimate source code](https://github.com/SilenceIsFatto/A3-Antistasi-Ultimate).
