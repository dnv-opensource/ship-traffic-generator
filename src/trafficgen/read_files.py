"""Functions to read the files needed to build one or more traffic situations."""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Union, cast
from uuid import UUID, uuid4

from maritime_schema.types.caga import (
    ShipStatic,
    TrafficSituation,
)

from trafficgen.types import EncounterSettings, SituationInput
from trafficgen.utils import deg_2_rad, knot_2_m_pr_s, min_2_s, nm_2_m


def read_situation_files(situation_folder: Path) -> List[SituationInput]:
    """
    Read traffic situation files.

    Params:
        * situation_folder: Path to the folder where situation files are found
        * input_units: Specify if the inputs are given in si or maritime units

    Returns
    -------
        * situations: List of desired traffic situations
    """
    situations: List[SituationInput] = []
    for file_name in sorted([file for file in os.listdir(situation_folder) if file.endswith(".json")]):
        file_path = os.path.join(situation_folder, file_name)
        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)

        data = convert_keys_to_snake_case(data)

        if "num_situations" not in data:
            data["num_situations"] = 1

        situation: SituationInput = SituationInput(**data)
        situation = convert_situation_data_from_maritime_to_si_units(situation)

        situations.append(situation)
    return situations


def read_generated_situation_files(situation_folder: Path) -> List[TrafficSituation]:
    """
    Read the generated traffic situation files. Used for testing the trafficgen algorithm.

    Params:
        * situation_folder: Path to the folder where situation files are found

    Returns
    -------
        * situations: List of desired traffic situations
    """
    situations: List[TrafficSituation] = []
    for file_name in sorted([file for file in os.listdir(situation_folder) if file.endswith(".json")]):
        file_path = os.path.join(situation_folder, file_name)
        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)
        data = convert_keys_to_snake_case(data)

        situation: TrafficSituation = TrafficSituation(**data)
        situations.append(situation)
    return situations


def convert_situation_data_from_maritime_to_si_units(situation: SituationInput) -> SituationInput:
    """
    Convert situation data which is given in maritime units to SI units.

    Params:
        * own_ship_file: Path to the own_ship_file file

    Returns
    -------
        * own_ship information
    """
    assert situation.own_ship is not None
    assert situation.own_ship.initial is not None
    situation.own_ship.initial.position.longitude = deg_2_rad(
        situation.own_ship.initial.position.longitude
    )
    situation.own_ship.initial.position.latitude = deg_2_rad(
        situation.own_ship.initial.position.latitude
    )
    situation.own_ship.initial.cog = deg_2_rad(situation.own_ship.initial.cog)
    situation.own_ship.initial.heading = deg_2_rad(situation.own_ship.initial.heading)
    situation.own_ship.initial.sog = knot_2_m_pr_s(situation.own_ship.initial.sog)

    if situation.own_ship.waypoints is not None:
        for waypoint in situation.own_ship.waypoints:
            waypoint.position.latitude = deg_2_rad(waypoint.position.latitude)
            waypoint.position.longitude = deg_2_rad(waypoint.position.longitude)
            if waypoint.data is not None:
                assert waypoint.data.model_extra
                if waypoint.data.model_extra.get("sog") is not None:
                    waypoint.data.model_extra["sog"]["value"] = knot_2_m_pr_s(waypoint.data.model_extra["sog"]["value"])  # type: ignore

    assert situation.encounters is not None
    for encounter in situation.encounters:
        beta: Union[List[float], float, None] = encounter.beta
        vector_time: Union[float, None] = encounter.vector_time
        if beta is not None:
            if isinstance(beta, List):
                for i in range(len(beta)):
                    beta[i] = deg_2_rad(beta[i])
                encounter.beta = beta
            else:
                encounter.beta = deg_2_rad(beta)
        if vector_time is not None:
            encounter.vector_time = min_2_s(vector_time)
    return situation


def read_own_ship_static_file(own_ship_static_file: Path) -> ShipStatic:
    """
    Read own ship static data from file.

    Params:
        * own_ship_file: Path to the own_ship_static_file file

    Returns
    -------
        * own_ship static information
    """
    with open(own_ship_static_file, encoding="utf-8") as f:
        data = json.load(f)
    data = convert_keys_to_snake_case(data)

    if "id" not in data:
        ship_id: UUID = uuid4()
        data.update({"id": ship_id})

    ship_static: ShipStatic = ShipStatic(**data)

    return ship_static


def read_target_ship_static_files(target_ship_folder: Path) -> List[ShipStatic]:
    """
    Read target ship static data files.

    Params:
        * target_ship_folder: Path to the folder where target ships are found

    Returns
    -------
        * target_ships_static: List of different target ships with static information
    """
    target_ships_static: List[ShipStatic] = []
    for file_name in sorted([file for file in os.listdir(target_ship_folder) if file.endswith(".json")]):
        file_path = os.path.join(target_ship_folder, file_name)
        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)
        data = convert_keys_to_snake_case(data)

        if "id" not in data:
            ship_id: UUID = uuid4()
            data.update({"id": ship_id})

        target_ship_static: ShipStatic = ShipStatic(**data)
        target_ships_static.append(target_ship_static)
    return target_ships_static


def read_encounter_settings_file(settings_file: Path) -> EncounterSettings:
    """
    Read encounter settings file.

    Params:
        * settings_file: Path to the encounter setting file

    Returns
    -------
        * encounter_settings: Settings for the encounter
    """
    with open(settings_file, encoding="utf-8") as f:
        data = json.load(f)
    data = check_input_units(data)
    encounter_settings: EncounterSettings = EncounterSettings(**data)

    encounter_settings = convert_settings_data_from_maritime_to_si_units(encounter_settings)

    return encounter_settings


def convert_settings_data_from_maritime_to_si_units(settings: EncounterSettings) -> EncounterSettings:
    """
    Convert situation data which is given in maritime units to SI units.

    Params:
        * own_ship_file: Path to the own_ship_file file

    Returns
    -------
        * own_ship information
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
    settings.common_vector = min_2_s(settings.common_vector)

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
    return cast(Dict[str, Any], _convert_keys_to_snake_case(data))


def _convert_keys_to_snake_case(
    data: Union[Dict[str, Any], List[Any]],
) -> Union[Dict[str, Any], List[Any]]:
    """Convert keys in a nested dictionary from camel case to snake case."""

    if isinstance(data, Dict):  # Dict
        converted_dict: Dict[str, Any] = {}
        for key, value in data.items():
            converted_key = camel_to_snake(key)
            if isinstance(value, (Dict, List)):
                converted_value = _convert_keys_to_snake_case(value)
            else:
                converted_value = value
            converted_dict[converted_key] = converted_value
        return converted_dict

    # List
    converted_list: List[Any] = []
    for value in data:
        if isinstance(value, (Dict, List)):
            converted_value = _convert_keys_to_snake_case(value)
        else:
            converted_value = value
        converted_list.append(value)
    return converted_list
