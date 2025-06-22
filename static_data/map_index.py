"""
Information about maps.

Manually compiled.

This should have an entry for every Antistasi Utimate mission.
"""

MAP_INDEX: dict[str, dict[str, str]] = {
    # key: `map_name`, derived from directory name and normalised to lower case.
    #   `display_name` as per Steam app/workshop titles/text except where noted.
    "abramia": {  # mod
        "display_name": "Isla Abramia",
        "url": "https://steamcommunity.com/sharedfiles/filedetails/?id=648775794",
    },
    "altis": {  # base game
        "display_name": "Altis",
        "url": "https://store.steampowered.com/app/107410",
    },
    "blud_vidda": {  # mod
        "display_name": "Vidda",  # a.k.a. r"Vidda \| legacy version"
        "url": "https://steamcommunity.com/sharedfiles/filedetails/?id=1282716647",
    },
    "brf_sumava": {  # mod
        "display_name": "Šumava",
        "url": "https://steamcommunity.com/sharedfiles/filedetails/?id=2947655994",
    },
    "cam_lao_nam": {  # creator DLC: S.O.G. Prairie Fire
        "display_name": "Cam Lao Nam",
        "url": "https://store.steampowered.com/app/1227700",
    },
    "chernarus": {  # mod: CUP Terrains - Maps
        "display_name": "Chernarus (Autumn)",
        "url": "https://steamcommunity.com/sharedfiles/filedetails/?id=583544987",
    },
    "chernarus_summer": {  # mod: CUP Terrains - Maps
        "display_name": "Chernarus (Summer)",
        "url": "https://steamcommunity.com/sharedfiles/filedetails/?id=583544987",
    },
    "chernarus_winter": {  # mod: CUP Terrains - Maps
        "display_name": "Chernarus (Winter)",
        "url": "https://steamcommunity.com/sharedfiles/filedetails/?id=583544987",
    },
    "chernarusredux": {  # mod
        "display_name": "Chernarus Redux",
        "url": "https://steamcommunity.com/workshop/filedetails/?id=1128256978",
    },
    "cup_chernarus_a3": {  # mod: CUP Terrains - Maps 2.0
        "display_name": "Chernarus 2020",
        "url": "https://steamcommunity.com/sharedfiles/filedetails/?id=1981964169",
    },
    "enoch": {  # DLC: Contact
        "display_name": "Livonia",
        "url": "https://store.steampowered.com/app/1021790",
    },
    "esseker": {  # mod
        "display_name": "New Esseker",
        "url": "https://steamcommunity.com/sharedfiles/filedetails/?id=2712204589",
    },
    "fapovo": {  # mod
        "display_name": "Fapovo",
        "url": "https://steamcommunity.com/sharedfiles/filedetails/?id=1910457930",
    },
    "gm_weferlingen_summer": {  # CDLC: Global Mobilization - Cold War Germany
        "display_name": "Weferlingen (Summer)",
        "url": "https://store.steampowered.com/app/1042220",
    },
    "gm_weferlingen_winter": {  # CDLC: Global Mobilization - Cold War Germany
        "display_name": "Weferlingen (Winter)",
        "url": "https://store.steampowered.com/app/1042220",
    },
    "green_sea": {  # mod
        "display_name": "Green Sea",  # officially "Green Sea Terrain"
        "url": "https://steamcommunity.com/sharedfiles/filedetails/?id=2645015212",
    },
    "gulfcoast": {  # mod
        "display_name": "Gulfcoast Islands",  # sic
        "url": "https://steamcommunity.com/sharedfiles/filedetails/?id=1617004814",
    },
    "iron_excelsior_tobruk": {  # mod: IFA3 AIO
        "display_name": "Tobruk",
        "url": "https://steamcommunity.com/sharedfiles/filedetails/?id=2648308937",
    },
    "isladuala3": {  # mod
        "display_name": "Isla Duala",
        "url": "https://steamcommunity.com/sharedfiles/filedetails/?id=714149065",
    },
    "kapaulio": {  # mod
        "display_name": "Saint Kapaulio",
        "url": "https://steamcommunity.com/sharedfiles/filedetails/?id=939686262",
    },
    "kunduz": {  # mod
        "display_name": "Kunduz, Afghanistan",
        "url": "https://steamcommunity.com/sharedfiles/filedetails/?id=421620913",
    },
    "kunduz_valley": {  # mod
        "display_name": "Kunduz River",
        "url": "https://steamcommunity.com/sharedfiles/filedetails/?id=3078351739",
    },
    "lingor3": {  # mod
        "display_name": "Lingor Island",
        "url": "https://steamcommunity.com/sharedfiles/filedetails/?id=718649903",
    },
    "lythium": {  # mod
        "display_name": "Lythium",
        "url": "https://steamcommunity.com/sharedfiles/filedetails/?id=909547724",
    },
    "malden": {  # free DLC
        "display_name": "Malden 2035",
        "url": "https://store.steampowered.com/app/639600",
    },
    "mehland": {  # mod
        "display_name": "Mehland",
        "url": "https://steamcommunity.com/sharedfiles/filedetails/?id=3317364155",
    },
    "namalsk": {  # mod
        "display_name": "Namalsk [R]",  # aka Namalsk Revamped
        "url": "https://steamcommunity.com/sharedfiles/filedetails/?id=3013966707",
    },
    "napf": {  # mod
        "display_name": "Napf Island A3",
        "url": "https://steamcommunity.com/sharedfiles/filedetails/?id=1425442364",
    },
    "napfwinter": {  # mod
        "display_name": "Napf Island A3 (Winter)",
        "url": "https://steamcommunity.com/sharedfiles/filedetails/?id=1425442364",
    },
    "optre_madrigal": {  # mod: Operation TREBUCHET
        "display_name": "Madrigal",
        "url": "https://steamcommunity.com/sharedfiles/filedetails/?id=769440155",
    },
    "panthera3": {  # mod
        "display_name": "Island Panthera",
        "url": "https://steamcommunity.com/sharedfiles/filedetails/?id=708278910",
    },
    "pja310": {  # mod
        "display_name": "G.O.S Al Rayak",
        "url": "https://steamcommunity.com/sharedfiles/filedetails/?id=648172507",
    },
    "psyfx_pht": {  # mod: Unsung
        "display_name": "Phuoc Tuy",
        "url": "https://steamcommunity.com/sharedfiles/filedetails/?id=943001311",
    },
    "pulau": {  # mod
        "display_name": "Pulau",
        "url": "https://steamcommunity.com/sharedfiles/filedetails/?id=1423583812",
    },
    "rhspkl": {  # mod
        "display_name": "Prei Khmaoch Luong",  # aka RHSPKL
        "url": "https://steamcommunity.com/sharedfiles/filedetails/?id=1978754337",
    },
    "ruha": {  # mod
        "display_name": "Ruha",
        "url": "https://steamcommunity.com/sharedfiles/filedetails/?id=1368857262",
    },
    "sara": {  # mod: CUP Terrains - Maps
        "display_name": "Sahrani",
        "url": "https://steamcommunity.com/sharedfiles/filedetails/?id=583544987",
    },
    "sefrouramal": {  # Creator DLC: Western Sahara
        "display_name": "Sefrou-Ramal",
        "url": "https://store.steampowered.com/app/1681170",
    },
    "sehreno": {  # mod
        "display_name": "Sehreno",
        "url": "https://steamcommunity.com/sharedfiles/filedetails/?id=2876540929",
    },
    "spe_mortain": {  # Creator DLC: Spearhead 1994
        "display_name": "Mortain",
        "url": "https://store.steampowered.com/app/1175380",
    },
    "spe_normandy": {  # Creator DLC: Spearhead 1994
        "display_name": "Normandy",
        "url": "https://store.steampowered.com/app/1175380",
    },
    "spex_utah_beach": {  # requires Creator DLC: Spearhead 1944
        "display_name": "Utah Beach",
        "url": "https://steamcommunity.com/sharedfiles/filedetails/?id=3117898674",
    },
    "staszow": {  # mod: IFA3 AIO
        "display_name": "Staszow",
        "url": "https://steamcommunity.com/sharedfiles/filedetails/?id=2648308937",
    },
    "staszowwinter": {  # mod: IFA3 AIO
        "display_name": "Staszow (Winter)",
        "url": "https://steamcommunity.com/sharedfiles/filedetails/?id=2648308937",
    },
    "stozec": {  # Creator DLC: CSLA Iron Curtain
        "display_name": "Gabreta",
        "url": "https://store.steampowered.com/app/1294440",
    },
    "stratis": {  # base game
        "display_name": "Stratis",
        "url": "https://store.steampowered.com/app/107410",
    },
    "stubbhult": {  # mod
        "display_name": "Stubbhult",
        "url": "https://steamcommunity.com/sharedfiles/filedetails/?id=3353189981",
    },
    "takistan": {  # mod: CUP Terrains - Maps
        "display_name": "Takistan",
        "url": "https://steamcommunity.com/sharedfiles/filedetails/?id=583544987",
    },
    "tanoa": {  # DLC: Apex
        "display_name": "Tanoa",
        "url": "https://store.steampowered.com/app/395180",
    },
    "tem_anizay": {  # mod
        "display_name": "Anizay",
        "url": "https://steamcommunity.com/sharedfiles/filedetails/?id=1537973181",
    },
    "tem_chernarus": {  # mod: Northern Fronts Terrains
        "display_name": "Svartmarka (Summer)",
        "url": "https://steamcommunity.com/sharedfiles/filedetails/?id=1630816076",
    },
    "tem_chernarusw": {  # mod: Northern Fronts Terrains
        "display_name": "Svartmarka (Winter)",
        "url": "https://steamcommunity.com/sharedfiles/filedetails/?id=1630816076",
    },
    "tem_kujari": {  # mod
        "display_name": "Kujari",
        "url": "https://steamcommunity.com/sharedfiles/filedetails/?id=1726494027",
    },
    "tembelan": {  # mod
        "display_name": "Tembelan Island",
        "url": "https://steamcommunity.com/sharedfiles/filedetails/?id=1252091296",
    },
    "umb_colombia": {  # mod
        "display_name": "UMB Colombia",
        "url": "https://steamcommunity.com/sharedfiles/filedetails/?id=2266710560",
    },
    "vn_khe_sanh": {  # CDLC: SOG Prairie Fire
        "display_name": "Khe Sanh",
        "url": "https://store.steampowered.com/app/1227700",
    },
    "vt7": {  # mod
        "display_name": "Virolahti - Valtatie 7",
        "url": "https://steamcommunity.com/sharedfiles/filedetails/?id=1926513010",
    },
    "winthera3": {  # mod
        "display_name": "Island Panthera (Winter)",  # aka "Island Winthera"
        "url": "https://steamcommunity.com/sharedfiles/filedetails/?id=708278910",
    },
    "ww2_omaha_beach": {  # mod
        "display_name": "Omaha Beach",
        "url": "https://steamcommunity.com/sharedfiles/filedetails/?id=2993515557",
    },
    "yulakia": {  # mod
        "display_name": "Yulakia",
        "url": "https://steamcommunity.com/sharedfiles/filedetails/?id=2950257727",
    },
}
