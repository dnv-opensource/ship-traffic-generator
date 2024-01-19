"""Functions to read the files needed to build one or more traffic situations."""

import json
import os
from pathlib import Path
from typing import List
from uuid import UUID, uuid4

from trafficgen.types import EncounterSettings, OwnShip, TargetShip, TrafficSituation


def camel_to_snake(string: str):
    """Convert a camel case string to snake case."""
    return ''.join([f'_{c.lower()}' if c.isupper() else c for c in string]).lstrip('_')

def replace_camel_case_with_snake_case(data):
    """Replace camel case keys with snake case keys in a dictionary."""
    return {camel_to_snake(key): value for key, value in data.items()}


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

        data = replace_camel_case_with_snake_case(data)
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

    if "static" in data and "id" not in data["static"]:
        ship_id: UUID = uuid4()
        data["static"].update({"id": ship_id})

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

        if "static" in data and "id" not in data["static"]:
            ship_id: UUID = uuid4()
            data["static"].update({"id": ship_id})
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
