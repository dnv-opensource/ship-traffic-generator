"""Functions to read the files needed to build one or more traffic situations."""

import json
import os
from pathlib import Path
from typing import Any, Dict, List
from uuid import UUID, uuid4

from trafficgen.types import AISNavStatus, EncounterSettings, OwnShip, TargetShip, TrafficSituation


def read_situation_files(situation_folder: Path) -> List[TrafficSituation]:
    """
    Read traffic situation files.

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
    encounter_settings: EncounterSettings = EncounterSettings(**data)
    return encounter_settings


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
