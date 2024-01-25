"""Functions to read the files needed to build one or more traffic situations."""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Union
from uuid import UUID, uuid4

from trafficgen.types import (
    AISNavStatus,
    EncounterSettings,
    OwnShip,
    TargetShip,
    TrafficSituation,
    UnitType,
)
from trafficgen.utils import deg_2_rad, knot_2_m_pr_s, min_2_s, nm_2_m


def read_situation_files(situation_folder: Path, input_units: UnitType) -> List[TrafficSituation]:
    """
    Read traffic situation files.

    Params:
        situation_folder: Path to the folder where situation files are found
        input_units: Specify if the inputs are given in si or maritime units

    Returns
    -------
        situations: List of desired traffic situations
    """
    situations: List[TrafficSituation] = []
    for file_name in sorted([file for file in os.listdir(situation_folder) if file.endswith(".json")]):
        file_path = os.path.join(situation_folder, file_name)
        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)

        data = convert_keys_to_snake_case(data)
        situation: TrafficSituation = TrafficSituation(**data)
        if input_units.value == "maritime":
            situation = convert_situation_data_from_maritime_to_si_units(situation)

        situation.input_file_name = file_name
        situations.append(situation)
    return situations


def read_generated_situation_files(situation_folder: Path) -> List[TrafficSituation]:
    """
    Read the generated traffic situation files. Used for testing the trafficgen algorithm.

    Params:
        situation_folder: Path to the folder where situation files are found

    Returns
    -------
        situations: List of desired traffic situations
    """
    situations: List[TrafficSituation] = []
    for file_name in sorted([file for file in os.listdir(situation_folder) if file.endswith(".json")]):
        file_path = os.path.join(situation_folder, file_name)
        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)

        data = convert_keys_to_snake_case(data)
        situation: TrafficSituation = TrafficSituation(**data)

        situation.input_file_name = file_name
        situations.append(situation)
    return situations


def convert_situation_data_from_maritime_to_si_units(situation: TrafficSituation) -> TrafficSituation:
    """
    Convert situation data which is given in maritime units to SI units.

    Params:
        own_ship_file: Path to the own_ship_file file

    Returns
    -------
        own_ship information
    """
    assert situation.own_ship is not None
    assert situation.own_ship.initial is not None
    situation.own_ship.initial.position.longitude = round(
        deg_2_rad(situation.own_ship.initial.position.longitude), 6
    )
    situation.own_ship.initial.position.latitude = round(
        deg_2_rad(situation.own_ship.initial.position.latitude), 6
    )
    situation.own_ship.initial.cog = round(deg_2_rad(situation.own_ship.initial.cog), 4)
    situation.own_ship.initial.sog = round(knot_2_m_pr_s(situation.own_ship.initial.sog), 2)

    assert situation.encounter is not None
    for i in range(len(situation.encounter)):
        beta: Union[float, None] = situation.encounter[i].beta
        vector_time: Union[float, None] = situation.encounter[i].vector_time
        if beta is not None:
            situation.encounter[i].beta = round(deg_2_rad(beta), 4)
        if vector_time is not None:
            situation.encounter[i].vector_time = min_2_s(vector_time)
    return situation


def read_own_ship_file(own_ship_file: Path) -> OwnShip:
    """
    Read own ship file.

    Params:
        own_ship_file: Path to the own_ship_file file

    Returns
    -------
        own_ship information
    """
    with open(own_ship_file, encoding="utf-8") as f:
        data = json.load(f)
    data = convert_keys_to_snake_case(data)

    if "static" in data and "id" not in data["static"]:
        ship_id: UUID = uuid4()
        data["static"].update({"id": ship_id})
    if "initial" in data and "nav_status" not in data["initial"]:
        data["initial"].update({"nav_status": AISNavStatus.UNDER_WAY_USING_ENGINE})

    ship: OwnShip = OwnShip(**data)
    return ship


def read_target_ship_files(target_ship_folder: Path) -> List[TargetShip]:
    """
    Read target ship files.

    Params:
        target_ship_folder: Path to the folder where target ships are found

    Returns
    -------
        target_ships: List of different target ships
    """
    target_ships: List[TargetShip] = []
    for file_name in sorted([file for file in os.listdir(target_ship_folder) if file.endswith(".json")]):
        file_path = os.path.join(target_ship_folder, file_name)
        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)
        data = convert_keys_to_snake_case(data)

        if "static" in data and "id" not in data["static"]:
            ship_id: UUID = uuid4()
            data["static"].update({"id": ship_id})
        if "initial" in data and "nav_status" not in data["initial"]:
            data["initial"].update({"nav_status": AISNavStatus.UNDER_WAY_USING_ENGINE})
        target_ship: TargetShip = TargetShip(**data)
        target_ships.append(target_ship)
    return target_ships


def read_encounter_settings_file(settings_file: Path) -> EncounterSettings:
    """
    Read encounter settings file.

    Params:
        settings_file: Path to the encounter setting file

    Returns
    -------
        Encounter settings
    """
    with open(settings_file, encoding="utf-8") as f:
        data = json.load(f)
    data = check_input_units(data)
    encounter_settings: EncounterSettings = EncounterSettings(**data)

    # assert encounter_settings.input_units is not None
    if encounter_settings.input_units.value == "maritime":
        encounter_settings = convert_settings_data_from_maritime_to_si_units(encounter_settings)

    return encounter_settings


def convert_settings_data_from_maritime_to_si_units(settings: EncounterSettings) -> EncounterSettings:
    """
    Convert situation data which is given in maritime units to SI units.

    Params:
        own_ship_file: Path to the own_ship_file file

    Returns
    -------
        own_ship information
    """
    assert settings.classification is not None

    settings.classification.theta13_criteria = deg_2_rad(settings.classification.theta13_criteria)
    settings.classification.theta14_criteria = deg_2_rad(settings.classification.theta14_criteria)
    settings.classification.theta15_criteria = deg_2_rad(settings.classification.theta15_criteria)
    settings.classification.theta15[0] = deg_2_rad(settings.classification.theta15[0])
    settings.classification.theta15[1] = deg_2_rad(settings.classification.theta15[1])

    settings.vector_range[0] = min_2_s(settings.vector_range[0])
    settings.vector_range[1] = min_2_s(settings.vector_range[1])

    settings.situation_length = min_2_s(settings.situation_length)
    settings.max_meeting_distance = nm_2_m(settings.max_meeting_distance)
    settings.evolve_time = min_2_s(settings.evolve_time)

    return settings


def check_input_units(data: Dict[str, Any]) -> Dict[str, Any]:
    """Check if input unit is specified, if not specified it is set to SI."""

    if "input_units" not in data:
        data["input_units"] = "si"

    return data


def camel_to_snake(string: str) -> str:
    """Convert a camel case string to snake case."""
    return "".join([f"_{c.lower()}" if c.isupper() else c for c in string]).lstrip("_")


def convert_keys_to_snake_case(data: Dict[str, Any]) -> Dict[str, Any]:
    """Convert keys in a nested dictionary from camel case to snake case."""
    converted_dict = {}
    for key, value in data.items():
        converted_key = camel_to_snake(key)
        if isinstance(value, dict):
            converted_value = convert_keys_to_snake_case(value)
        elif isinstance(value, list):
            converted_value = convert_list_of_dict_to_snake_case(value)
        else:
            converted_value = value
        converted_dict[converted_key] = converted_value
    return converted_dict


def convert_list_of_dict_to_snake_case(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Loops through a list of dics to convert keys from camel case to snake case."""

    converted_list: List[Dict[str, Any]] = []
    for item in data:
        if not isinstance(item, dict):
            return data
        converted_item = convert_keys_to_snake_case(item)
        converted_list.append(converted_item)
    return converted_list
