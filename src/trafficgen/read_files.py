"""Functions to read the files needed to build one or more traffic situations."""

import json
import os
from pathlib import Path
from typing import List

from trafficgen.types import EncounterSettings, Ship, Situation, TargetShip


def read_situation_files(situation_folder: Path) -> List[Situation]:
    """
    Read traffic situation files.

    Params:
        situation_folder: Path to the folder where situation files are found

    Returns
    -------
        situations: List of desired traffic situations
    """
    situations: List[Situation] = []
    for file_name in [file for file in os.listdir(situation_folder) if file.endswith(".json")]:
        file_path = os.path.join(situation_folder, file_name)
        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)
        situation: Situation = Situation(**data)
        situation.input_file_name = file_name
        situations.append(situation)
    return situations


def read_own_ship_file(own_ship_file: Path) -> Ship:
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
    ship: Ship = Ship(**data)
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
    for file_name in [file for file in os.listdir(target_ship_folder) if file.endswith(".json")]:
        file_path = os.path.join(target_ship_folder, file_name)
        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)
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
