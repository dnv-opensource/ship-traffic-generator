"""Tests reading files."""

from pathlib import Path

from trafficgen.read_files import (
    read_encounter_settings_file,
    read_own_ship_static_file,
    read_situation_files,
    read_target_ship_static_files,
)
from trafficgen.types import (
    AisShipType,
    EncounterSettings,
    EncounterType,
    ShipStatic,
    SituationInput,
)


def test_read_situations_1_ts_full_spec(situations_folder_test_01: Path):
    """
    Test reading traffic situations with full specification,
    meaning all parameters are specified.
    """
    desired_traffic_situations: list[SituationInput] = read_situation_files(situations_folder_test_01)
    assert len(desired_traffic_situations) == 5

    # sourcery skip: no-loop-in-tests
    for situation in desired_traffic_situations:
        assert situation.title is not None
        assert situation.description is not None
        assert situation.own_ship is not None
        assert situation.num_situations is not None
        assert situation.encounters is not None
        assert len(situation.encounters) == 1
        assert situation.encounters[0].desired_encounter_type is not None
        assert situation.encounters[0].beta is None
        assert situation.encounters[0].relative_speed is not None
        assert situation.encounters[0].vector_time is not None


def test_read_situations_1_ts_partly_spec(situations_folder_test_02: Path):
    """
    Test reading traffic situations using partly specification,
    meaning some of the parameters are specified.
    """
    desired_traffic_situations: list[SituationInput] = read_situation_files(situations_folder_test_02)
    assert len(desired_traffic_situations) == 2

    # sourcery skip: no-loop-in-tests
    for situation in desired_traffic_situations:
        assert situation.own_ship is not None
        assert situation.encounters is not None
        assert len(situation.encounters) == 1
        assert situation.encounters[0].desired_encounter_type is not None
        assert situation.encounters[0].beta is None


def test_read_situations_1_ts_minimum_spec(situations_folder_test_03: Path):
    """
    Test reading traffic situations using using minimum specification,
    meaning only type of situation is specified.
    """
    desired_traffic_situations: list[SituationInput] = read_situation_files(situations_folder_test_03)
    assert len(desired_traffic_situations) == 2

    # sourcery skip: no-loop-in-tests
    for situation in desired_traffic_situations:
        assert situation.own_ship is not None
        assert situation.encounters is not None
        assert len(situation.encounters) == 1
        assert situation.encounters[0].desired_encounter_type is not None
        assert situation.encounters[0].beta is None
        assert situation.encounters[0].relative_speed is None
        assert situation.encounters[0].vector_time is None


def test_read_situations_2_ts_one_to_many_situations(situations_folder_test_04: Path):
    """
    Test reading a traffic situation file num_situations=5 and 2 encounter specifications.
    """
    desired_traffic_situations: list[SituationInput] = read_situation_files(situations_folder_test_04)
    assert len(desired_traffic_situations) == 1

    # sourcery skip: no-loop-in-tests
    for situation in desired_traffic_situations:
        assert situation.own_ship is not None
        assert situation.num_situations == 5
        assert situation.encounters is not None
        assert len(situation.encounters) == 2
        for encounter in situation.encounters:
            assert encounter.desired_encounter_type is not None
            assert encounter.beta is None
            assert encounter.relative_speed is None
            assert encounter.vector_time is None


def test_read_situations_one_to_many_situations(situations_folder_test_05: Path):
    """
    Test reading three traffic situation files 1, 2 and 3 encounter specifications.
    """
    desired_traffic_situations: list[SituationInput] = read_situation_files(situations_folder_test_05)
    assert len(desired_traffic_situations) == 3

    # sourcery skip: no-loop-in-tests
    num_situations_values_found: set[int] = set()
    for situation in desired_traffic_situations:
        assert situation.own_ship is not None
        assert situation.encounters is not None
        assert len(situation.encounters) in {1, 2, 3}
        num_situations_values_found.add(situation.num_situations)
        for encounter in situation.encounters:
            assert encounter.desired_encounter_type is not None
            assert encounter.beta is None
            assert encounter.relative_speed is None
            assert encounter.vector_time is None

    assert num_situations_values_found == {6, 3, 1}


def test_read_situations_with_different_encounter_types(situations_folder_test_07: Path):
    """
    Test reading 5 traffic situation files with different encounter types.
    """
    desired_traffic_situations: list[SituationInput] = read_situation_files(situations_folder_test_07)
    assert len(desired_traffic_situations) == 5

    # sourcery skip: no-loop-in-tests
    desired_encounter_types_found: set[EncounterType] = set()
    for situation in desired_traffic_situations:
        assert situation.own_ship is not None
        assert situation.encounters is not None
        assert len(situation.encounters) == 1
        desired_encounter_types_found.add(situation.encounters[0].desired_encounter_type)
        for encounter in situation.encounters:
            assert encounter.desired_encounter_type is not None
            assert encounter.beta is not None
            assert encounter.relative_speed is None
            assert encounter.vector_time is None

    assert desired_encounter_types_found == {
        EncounterType.HEAD_ON,
        EncounterType.OVERTAKING_GIVE_WAY,
        EncounterType.OVERTAKING_STAND_ON,
        EncounterType.CROSSING_GIVE_WAY,
        EncounterType.CROSSING_STAND_ON,
    }


def test_read_own_ship(own_ship_file: Path):
    """
    Test reading own ship file.
    """
    own_ship_static: ShipStatic = read_own_ship_static_file(own_ship_file)
    assert own_ship_static.dimensions is not None
    assert own_ship_static.dimensions.length is not None
    assert own_ship_static.dimensions.width is not None
    assert own_ship_static.sog_max is not None
    assert own_ship_static.mmsi is not None
    assert own_ship_static.ship_type is AisShipType.PASSENGER


def test_read_target_ships(target_ships_folder: Path):
    """
    Test reading target ship files.
    """
    target_ships_static: list[ShipStatic] = read_target_ship_static_files(target_ships_folder)

    # sourcery skip: no-loop-in-tests
    for target_ship_static in target_ships_static:
        assert target_ship_static.dimensions is not None
        assert target_ship_static.dimensions.length is not None
        assert target_ship_static.dimensions.width is not None
        assert target_ship_static.sog_max is not None


def test_read_encounter_settings_file(settings_file: Path):
    """
    Test reading encounter settings file.
    """
    settings: EncounterSettings = read_encounter_settings_file(settings_file)
    assert settings.classification is not None
    assert settings.relative_speed is not None
    assert settings.vector_range is not None
    assert settings.max_meeting_distance == 0.0
    assert settings.evolve_time == 120.0 * 60
