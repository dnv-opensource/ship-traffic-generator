"""
This module is used to read the files needed to build one or more traffic situations
"""

import json
import os


def read_situation_files(situation_folder):
    """
    Reads traffic situation files.

    Params:
        situation_folder: Path to the folder where situation files are found

    Returns:
        situations: List of desired traffic situations
    """
    situations = []
    for file_name in [file for file in os.listdir(situation_folder) if file.endswith(".json")]:
        file_path = os.path.join(situation_folder, file_name)
        with open(file_path, encoding="utf-8") as json_file:
            situation = json.load(json_file)
            situation["input_file_name"] = file_name
            situations.append(situation)
    return situations


def read_own_ship_file(own_ship_file):
    """
    Reads the own ship file.

    Params:
        own_ship_file: Path to the own_ship_file file

    Returns:
        own_ship information
    """
    with open(own_ship_file, encoding="utf-8") as user_file:
        return json.load(user_file)


def read_target_ship_files(target_ship_folder):
    """
    Reads target ship files.

    Params:
        target_ship_folder: Path to the folder where target ships are found

    Returns:
        target_ships: List of different target ships
    """
    target_ships = []
    for file_name in [file for file in os.listdir(target_ship_folder) if file.endswith(".json")]:
        file_path = os.path.join(target_ship_folder, file_name)
        with open(file_path, encoding="utf-8") as json_file:
            target_ships.append(json.load(json_file))
    return target_ships


def read_encounter_setting_file(settings_file):
    """
    Reads the encounter setting file.

    Params:
        settings_file: Path to the encounter setting file

    Returns:
        Encounter settings
    """
    with open(settings_file, encoding="utf-8") as user_file:
        return json.load(user_file)
