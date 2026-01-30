"""Test parsing a mission's `mapInfo.hpp` file."""

from cxxheaderparser.simple import parse_string

from src.mission.mapinfo_hpp_parser import (
    _get_climate,
    _get_disabled_towns,
    _get_populations,
)

# Cut down/edited version of `.../Antistasi_Altis.Altis/mapInfo.hpp`
MAP_INFO_HPP = r"""
#include "..\BuildObjectsList.hpp"
class altis {
	population[] = {
		{"Therisa",154},{"Zaros",371},{"Poliakko",136}
	};
	disabledTowns[] = {"Tikanen","toipela","hirvela"};
	antennas[] = {
		{14451.5,16338,0.000354767}, {15346.7,15894,-3.8147e-005}, {16085.1,16998,7.08781},
	};
	antennasBlacklistIndex[] = {4,10,12,15,17};
	banks[] = {
		{16586.6,12834.5,-0.638584},{16545.8,12784.5,-0.485485},{16633.3,12807,-0.635017}
	};
	garrison[] = {
		{},{"outpost_24", "factory_7", "factory_5","airport_2", "seaport_4", "outpost_5", "outpost_6", "milbase_4", "control_52", "control_33"},{},{"control_52","control_33"}
	};
	fuelStationTypes[] = {
		"Land_FuelStation_Feed_F","Land_fs_feed_F","Land_FuelStation_01_pump_malevil_F"
	};
	milAdministrations[] = {
		{3648.51,13196.9,0},{9282.15,12145.9,0},{11327,14143.8,0}
	};
	climate = "arid";
	buildObjects[] = {
		BUILDABLES_HISTORIC,
		BUILDABLES_MODERN_SAND,
		BUILDABLES_ARID,
		BUILDABLES_UNIVERSAL
	};
};"""  # noqa: E501


def test_get_climate() -> None:
    """Get climate value."""
    # arrange
    class_scope = parse_string(MAP_INFO_HPP).namespace.classes[0]
    # act
    value = _get_climate(class_scope)
    # assert
    assert value == "arid"


def test_get_populations() -> None:
    """Get populations value."""
    # arrange
    class_scope = parse_string(MAP_INFO_HPP).namespace.classes[0]
    # act
    value = _get_populations(class_scope)
    # assert
    assert value == [("Therisa", 154), ("Zaros", 371), ("Poliakko", 136)]


def test_get_disabled_towns() -> None:
    """Get populations value."""
    # arrange
    class_scope = parse_string(MAP_INFO_HPP).namespace.classes[0]
    # act
    value = _get_disabled_towns(class_scope)
    # assert
    assert value == [
        "Tikanen",
        "toipela",
        "hirvela",
    ]
