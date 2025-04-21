"""Override AU mission data."""

EXCLUDED_MISSIONS: set[str] = {
    # Excluded from final data table
    # Mission dir name
    "Antistasi_Stratis.Stratis",
}
DISABLED_TOWNS_IGNORED_PREFIXES = [
    # Ignored when comparing against canonical names
    "castle_",
    "Castle_",
    "Insel_",
    "Island_",
    "LandMark_",
    "Malden_C_",
    "Malden_L_",
    "Malden_V_",
    "mil_",
    "pass_",
]
