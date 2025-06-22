"""
Used to verify generated data.

Derived from screen captures belonging to Antistasi Ultimate at:
https://drive.google.com/drive/u/0/folders/1jSvzJnzeNXdaE93TISdEt_U3j3zf__Tl

LICENSE:

Used under license: https://drive.google.com/file/d/1UrDAuN9-9us8Xb-AIFxLrvs6tzw2hbb5/view
"""

IN_GAME_DATA: dict[str, dict[str, int]] = {
    # NB: keys must be lower-case.
    "abramia": {"total_objectives_count": 30},
    "altis": {
        "resources_count": 12,
        "factories_count": 13,
        "outposts_count": 50,
        "waterports_count": 6,
        "bases_count": 5,
        "airports_count": 6,
        "total_objectives_count": 92,
    },
    "blud_vidda": {"total_objectives_count": 39},  # image filename (37) is incorrect
    "brf_sumava": {"total_objectives_count": 48},  # image (30) is outdated
    "cam_lao_nam": {"total_objectives_count": 75},
    "chernarus": {"total_objectives_count": 44},
    "chernarus_summer": {"total_objectives_count": 44},
    "chernarus_winter": {"total_objectives_count": 44},
    "chernarusredux": {"total_objectives_count": 64},
    "cup_chernarus_a3": {"total_objectives_count": 54},  # 2020
    "enoch": {"total_objectives_count": 51},
    "esseker": {"total_objectives_count": 24},
    "fapovo": {"total_objectives_count": 48},  # image filename (56) is incorrect
    "gm_weferlingen_summer": {
        "total_objectives_count": 38
    },  # image filename (45) is incorrect
    "gm_weferlingen_winter": {
        "total_objectives_count": 38
    },  # image filename (45) is incorrect
    "green_sea": {"total_objectives_count": 68},
    "gulfcoast": {"total_objectives_count": 67},
    "iron_excelsior_tobruk": {"total_objectives_count": 21},
    "isladuala3": {"total_objectives_count": 61},  # not in AU data
    "kapaulio": {"total_objectives_count": 99},
    "kunduz": {"total_objectives_count": 17},
    "kunduz_valley": {"total_objectives_count": 40},
    "lingor3": {"total_objectives_count": 48},  # image filename (49) is incorrect
    "lythium": {"total_objectives_count": 38},
    "malden": {"total_objectives_count": 32},
    "mehland": {"total_objectives_count": 59},
    "namalsk": {"total_objectives_count": 22},
    "napf": {"total_objectives_count": 43},
    "napfwinter": {"total_objectives_count": 43},
    "optre_madrigal": {"total_objectives_count": 31},
    "panthera3": {"total_objectives_count": 33},
    "psyfx_pht": {"total_objectives_count": 51},
    "pja310": {"total_objectives_count": 47},  # image filename (45) is incorrect
    "pulau": {"total_objectives_count": 33},
    "rhspkl": {"total_objectives_count": 26},
    "ruha": {"total_objectives_count": 27},
    "sara": {"total_objectives_count": 57},
    "sefrouramal": {"total_objectives_count": 21},
    "sehreno": {"total_objectives_count": 31},
    "spe_mortain": {"total_objectives_count": 25},
    "spe_normandy": {"total_objectives_count": 52},
    "spex_utah_beach": {"total_objectives_count": 29},
    "staszow": {"total_objectives_count": 30},
    "staszowwinter": {"total_objectives_count": 30},
    "stozec": {"total_objectives_count": 40},
    "stubbhult": {"total_objectives_count": 37},
    "takistan": {"total_objectives_count": 34},
    "tanoa": {"total_objectives_count": 42},
    "tem_anizay": {"total_objectives_count": 38},
    "tem_chernarus": {"total_objectives_count": 46},
    "tem_chernarusw": {"total_objectives_count": 46},
    "tem_kujari": {"total_objectives_count": 42},
    "tembelan": {"total_objectives_count": 36},
    "umb_colombia": {"total_objectives_count": 96},
    "vn_khe_sanh": {"total_objectives_count": 32},
    "vt7": {
        "resources_count": 14,
        "factories_count": 6,
        "outposts_count": 20,
        "waterports_count": 5,
        "bases_count": 2,
        "airports_count": 3,
        "total_objectives_count": 50,
    },
    "winthera3": {"total_objectives_count": 33},
    "ww2_omaha_beach": {"total_objectives_count": 18},
    "yulakia": {"total_objectives_count": 69},
}
