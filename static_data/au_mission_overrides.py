"""Override AU mission data."""

EXCLUDED_MISSIONS: set[str] = {
    # Excluded from final data table
    # Mission filename stem
    "Antistasi_Stratis.Stratis",
}

LOCATION_TYPOS = {
    # exact to minimise false matches
    # chernarus variations
    "Solnychniy": "Solnichniy",
    # esseker
    "CahrdakResort": "Chardak Resort",
    # gulfcoast
    "cooperhead": "Copperhead",
    "eastwood": "Eastwoods",
    "heronlanding": "Herrons Landing",
    "hurpass": "Hurricane Pass",
    "iona": "Iona City",
    "orionport": "Port Orion",
    "sanbelcity": "Sanibel",
    "sanbelshores": "Sanibel Shores",
    # lythium
    "greencaampbase": "GreenCampBase",
    "loboriverbed": "LoboRiberBed",
    # staszow, staszowwinter
    "Lenartwoice": "Lenartowice",
    # vt7
    "Tikanen": "Tinkanen",
}
LOCATION_PREFIXES = [
    # Ignored when comparing location names.
    "city_",
    "City_",
    "gm_name_",
    "Sara_",
    "Settlement_",
    "vil_",
    "Vil_",
    "vill_",
]
LOCATION_SUFFIXES = [
    # Ignored when comparing location names.
    "01",
]
