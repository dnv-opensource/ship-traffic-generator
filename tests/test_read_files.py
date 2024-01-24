"""Tests reading files."""

from pathlib import Path
from typing import List, Set, Union

from trafficgen.read_files import (
    read_encounter_settings_file,
    read_own_ship_file,
    read_situation_files,
    read_target_ship_files,
)
from trafficgen.types import (
    EncounterSettings,
    EncounterType,
    GeneralShipType,
    Ship,
    TargetShip,
    TrafficSituation,
)


def test_read_situations_1_ts_full_spec(situations_folder_test_01: Path):
    """
    Test reading traffic situations with full specification,
    meaning all parameters are specified.
    """
    situations: List[TrafficSituation] = read_situation_files(situations_folder_test_01)
    assert len(situations) == 5

    # sourcery skip: no-loop-in-tests
    for situation in situations:
        assert situation.own_ship is not None
        assert situation.target_ships is None
        assert situation.encounter is not None
        assert len(situation.encounter) == 1
        assert situation.encounter[0].desired_encounter_type is not None
        assert situation.encounter[0].beta is None
        assert situation.encounter[0].relative_speed is not None
        assert situation.encounter[0].vector_time is not None


def test_read_situations_1_ts_partly_spec(situations_folder_test_02: Path):
    """
    Test reading traffic situations using partly specification,
    meaning some of the parameters are specified.
    """
    situations: List[TrafficSituation] = read_situation_files(situations_folder_test_02)
    assert len(situations) == 2

    # sourcery skip: no-loop-in-tests
    for situation in situations:
        assert situation.own_ship is not None
        assert situation.target_ships is None
        assert situation.encounter is not None
        assert len(situation.encounter) == 1
        assert situation.encounter[0].desired_encounter_type is not None
        assert situation.encounter[0].beta is None


def test_read_situations_1_ts_minimum_spec(situations_folder_test_03: Path):
    """
    Test reading traffic situations using using minimum specification,
    meaning only type of situation is specified.
    """
    situations: List[TrafficSituation] = read_situation_files(situations_folder_test_03)
    assert len(situations) == 2

    # sourcery skip: no-loop-in-tests
    for situation in situations:
        assert situation.own_ship is not None
        assert situation.target_ships is None
        assert situation.encounter is not None
        assert len(situation.encounter) == 1
        assert situation.encounter[0].desired_encounter_type is not None
        assert situation.encounter[0].beta is None
        assert situation.encounter[0].relative_speed is None
        assert situation.encounter[0].vector_time is None


def test_read_situations_2_ts_one_to_many_situations(situations_folder_test_04: Path):
    """
    Test reading a traffic situation file num_situations=5 and 2 encounter specifications.
    """
    situations: List[TrafficSituation] = read_situation_files(situations_folder_test_04)
    assert len(situations) == 1

    # sourcery skip: no-loop-in-tests
    for situation in situations:
        assert situation.own_ship is not None
        assert situation.target_ships is None
        assert situation.num_situations == 5
        assert situation.encounter is not None
        assert len(situation.encounter) == 2
        for encounter in situation.encounter:
            assert encounter.desired_encounter_type is not None
            assert encounter.beta is None
            assert encounter.relative_speed is None
            assert encounter.vector_time is None


def test_read_situations_one_to_many_situations(situations_folder_test_05: Path):
    """
    Test reading three traffic situation files 1, 2 and 3 encounter specifications.
    """
    situations: List[TrafficSituation] = read_situation_files(situations_folder_test_05)
    assert len(situations) == 3

    # sourcery skip: no-loop-in-tests
    num_situations_values_found: Set[Union[int, None]] = set()
    for situation in situations:
        assert situation.own_ship is not None
        assert situation.target_ships is None
        assert situation.encounter is not None
        assert len(situation.encounter) in {1, 2, 3}
        num_situations_values_found.add(situation.num_situations)
        for encounter in situation.encounter:
            assert encounter.desired_encounter_type is not None
            assert encounter.beta is None
            assert encounter.relative_speed is None
            assert encounter.vector_time is None

    assert num_situations_values_found == {6, 3, None}


def test_read_situations_with_different_encounter_types(situations_folder_test_07: Path):
    """
    Test reading 5 traffic situation files with different encounter types.
    """
    situations: List[TrafficSituation] = read_situation_files(situations_folder_test_07)
    assert len(situations) == 5

    # sourcery skip: no-loop-in-tests
    desired_encounter_types_found: Set[EncounterType] = set()
    for situation in situations:
        assert situation.own_ship is not None
        assert situation.target_ships is None
        assert situation.num_situations is None
        assert situation.encounter is not None
        assert len(situation.encounter) == 1
        desired_encounter_types_found.add(situation.encounter[0].desired_encounter_type)
        for encounter in situation.encounter:
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
    own_ship: Ship = read_own_ship_file(own_ship_file)
    assert own_ship.static is not None
    assert own_ship.initial is None
    assert own_ship.waypoints is None
    assert own_ship.static.ship_type is GeneralShipType.PASSENGER


def test_read_target_ships(target_ships_folder: Path):
    """
    Test reading target ship files.
    """
    target_ships: List[TargetShip] = read_target_ship_files(target_ships_folder)
    assert len(target_ships) == 3

    # sourcery skip: no-loop-in-tests
    ship_types_found: Set[GeneralShipType] = set()
    for target_ship in target_ships:
        assert target_ship.static is not None
        ship_types_found.add(target_ship.static.ship_type)
        assert target_ship.initial is None
        assert target_ship.waypoints is None

    assert ship_types_found == {
        GeneralShipType.PASSENGER,
        GeneralShipType.CARGO,
    }


def test_read_encounter_settings_file(settings_file: Path):
    """
    Test reading encounter settings file.
    """
    settings: EncounterSettings = read_encounter_settings_file(settings_file)
    assert settings.classification is not None
    assert settings.relative_speed is not None
    assert settings.vector_range is not None
    assert settings.max_meeting_distance == 0.0
    assert settings.evolve_time == 120.0

