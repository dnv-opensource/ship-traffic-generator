"""Functions to read the files needed to build one or more traffic situations."""

import json
import logging
from pathlib import Path
from typing import Any, cast

from trafficgen.types import (
    Encounter,
    EncounterSettings,
    Initial,
    ShipStatic,
    SituationInput,
    TrafficSituation,
    Waypoint,
)
from trafficgen.utils import deg_2_rad, knot_2_m_pr_s, min_2_s, nm_2_m

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def read_situation_files(situation_folder: Path) -> list[SituationInput]:
    """
    Read traffic situation files.

    Parameters
    ----------
    situation_folder : Path
        Path to the folder where situation files are found

    Returns
    -------
    situations : list[SituationInput]
        List of desired traffic situations
    """
    situations: list[SituationInput] = []
    logger.info(f"Reading traffic situation input files from: {situation_folder}")
    for file_name in sorted([file for file in Path.iterdir(situation_folder) if str(file).endswith(".json")]):
        with Path.open(file_name, encoding="utf-8") as f:
            data = json.load(f)

        data = convert_keys_to_snake_case(data)

        if "num_situations" not in data:
            data["num_situations"] = 1

        situation: SituationInput = SituationInput(**data)
        situation = convert_situation_data_from_maritime_to_si_units(situation)

        situations.append(situation)
    return situations


def read_generated_situation_files(situation_folder: Path) -> list[TrafficSituation]:
    """
    Read the generated traffic situation files. Used for testing the trafficgen algorithm.

    Parameters
    ----------
    situation_folder : Path
        Path to the folder where situation files are found

    Returns
    -------
    situations : list[TrafficSituation]
        List of desired traffic situations
    """
    situations: list[TrafficSituation] = []
    for file_name in sorted([file for file in Path.iterdir(situation_folder) if str(file).endswith(".json")]):
        file_path = situation_folder / file_name
        with Path.open(file_path, encoding="utf-8") as f:
            data = json.load(f)
        data = convert_keys_to_snake_case(data)

        situation: TrafficSituation = TrafficSituation(**data)
        situations.append(situation)
    return situations


def convert_situation_data_from_maritime_to_si_units(situation: SituationInput) -> SituationInput:
    """
    Convert situation data which is given in maritime units to SI units.

    Parameters
    ----------
    situation : SituationInput
        Situation data to be converted

    Returns
    -------
    situation : SituationInput
        Converted situation data
    """
    assert situation.own_ship is not None
    assert situation.own_ship.initial is not None
    assert situation.own_ship.initial.heading is not None

    situation.own_ship.initial = convert_own_ship_initial_data(situation.own_ship.initial)
    if situation.own_ship.waypoints is not None:
        situation.own_ship.waypoints = convert_own_ship_waypoints(situation.own_ship.waypoints)

    assert situation.encounters is not None
    situation.encounters = convert_encounters(situation.encounters)

    return situation


def convert_own_ship_initial_data(initial: Initial) -> Initial:
    """
    Convert own ship initial data which is given in maritime units to SI units.

    Parameters
    ----------
    initial : Initial
        Own ship initial data to be converted

    Returns
    -------
    initial : Initial
        Converted own ship initial data
    """
    initial.position.lon = deg_2_rad(initial.position.lon)
    initial.position.lat = deg_2_rad(initial.position.lat)
    initial.cog = deg_2_rad(initial.cog)
    assert initial.heading is not None
    initial.heading = deg_2_rad(initial.heading)
    initial.sog = knot_2_m_pr_s(initial.sog)
    return initial


def convert_own_ship_waypoints(waypoints: list[Waypoint]) -> list[Waypoint]:
    """
    Convert own ship waypoint data which is given in maritime units to SI units.

    Parameters
    ----------
    waypoints : list[Waypoint]
        Waypoint data to be converted

    Returns
    -------
    waypoints : list[Waypoint]
        Converted waypoint data
    """
    for waypoint in waypoints:
        waypoint.position.lat = deg_2_rad(waypoint.position.lat)
        waypoint.position.lon = deg_2_rad(waypoint.position.lon)
        if waypoint.turn_radius is not None:
            waypoint.turn_radius = nm_2_m(waypoint.turn_radius)
        if waypoint.leg is not None:
            if waypoint.leg.starboard_xtd is not None:
                waypoint.leg.starboard_xtd = nm_2_m(waypoint.leg.starboard_xtd)
            if waypoint.leg.portside_xtd is not None:
                waypoint.leg.portside_xtd = nm_2_m(waypoint.leg.portside_xtd)
            if waypoint.leg.data is not None and waypoint.leg.data.sog is not None:
                assert waypoint.leg.data.sog.value is not None
                assert waypoint.leg.data.sog.interp_start is not None
                assert waypoint.leg.data.sog.interp_end is not None
                waypoint.leg.data.sog.value = knot_2_m_pr_s(waypoint.leg.data.sog.value)
                waypoint.leg.data.sog.interp_start = nm_2_m(waypoint.leg.data.sog.interp_start)
                waypoint.leg.data.sog.interp_end = nm_2_m(waypoint.leg.data.sog.interp_end)
    return waypoints


def convert_encounters(encounters: list[Encounter]) -> list[Encounter]:
    """
    Convert encounter data which is given in maritime units to SI units.

    Parameters
    ----------
    encounters : list[Encounter]
        Encounter data to be converted

    Returns
    -------
    encounters : list[Encounter]
        Converted encounter data
    """
    assert encounters is not None
    beta_list_length = 2

    for encounter in encounters:
        beta: list[float] | float | None = encounter.beta
        vector_time: float | None = encounter.vector_time
        if beta is not None:
            if isinstance(beta, list):
                assert len(beta) == beta_list_length
                for i in range(len(beta)):
                    beta[i] = deg_2_rad(beta[i])
                encounter.beta = beta
            else:
                encounter.beta = deg_2_rad(beta)
        if vector_time is not None:
            encounter.vector_time = min_2_s(vector_time)
    return encounters


def read_own_ship_static_file(own_ship_static_file: Path) -> ShipStatic:
    """
    Read own ship static data from file.

    Parameters
    ----------
    own_ship_file : Path
        Path to the own_ship_static_file file

    Returns
    -------
    own_ship : ShipStatic
        Own_ship static information
    """
    logger.info(f"Reading own ship static file from: {own_ship_static_file}")
    with Path.open(own_ship_static_file, encoding="utf-8") as f:
        data = json.load(f)
    data = convert_keys_to_snake_case(data)

    if "id" not in data:
        ship_id: int = 0
        data.update({"id": ship_id})

    ship_static: ShipStatic = ShipStatic(**data)
    ship_static = convert_ship_data_from_maritime_to_si_units(ship_static)

    return ship_static


def read_target_ship_static_files(target_ship_folder: Path) -> list[ShipStatic]:
    """
    Read target ship static data files.

    Parameters
    ----------
    target_ship_folder : Path
        Path to the folder where target ships are found

    Returns
    -------
    target_ships_static : list[ShipStatic]
        List of different target ships with static information
    """
    target_ships_static: list[ShipStatic] = []
    i = 0
    logger.info(f"Reading target ship static files from: {target_ship_folder}")
    for file_name in sorted([file for file in Path.iterdir(target_ship_folder) if str(file).endswith(".json")]):
        i = i + 1
        with Path.open(file_name, encoding="utf-8") as f:
            data = json.load(f)
        data = convert_keys_to_snake_case(data)

        if "id" not in data:
            ship_id: int = 10 + i
            data.update({"id": ship_id})

        target_ship_static: ShipStatic = ShipStatic(**data)
        target_ship_static = convert_ship_data_from_maritime_to_si_units(target_ship_static)
        target_ships_static.append(target_ship_static)
    return target_ships_static


def convert_ship_data_from_maritime_to_si_units(ship: ShipStatic) -> ShipStatic:
    """
    Convert ship static data which is given in maritime units to SI units.

    Parameters
    ----------
    ship : ShipStatic
        Ship data to be converted

    Returns
    -------
    ship : ShipStatic
        Converted ship data
    """
    if ship.sog_max is not None:
        ship.sog_max = knot_2_m_pr_s(ship.sog_max)
    if ship.sog_min is not None:
        ship.sog_min = knot_2_m_pr_s(ship.sog_min)

    return ship


def read_encounter_settings_file(settings_file: Path) -> EncounterSettings:
    """
    Read encounter settings file.

    Parameters
    ----------
    settings_file : Path
        Path to the encounter setting file

    Returns
    -------
    encounter_settings : EncounterSettings
        Settings for the encounter
    """
    logger.info(f"Reading encounter settings file from: {settings_file}")
    with Path.open(settings_file, encoding="utf-8") as f:
        data = json.load(f)

    data = convert_keys_to_snake_case(data)

    encounter_settings: EncounterSettings = EncounterSettings(**data)

    encounter_settings = convert_settings_data_from_maritime_to_si_units(encounter_settings)

    return encounter_settings


def convert_settings_data_from_maritime_to_si_units(encounter_settings: EncounterSettings) -> EncounterSettings:
    """
    Convert situation data which is given in maritime units to SI units.

    Parameters
    ----------
    encounter_settings : EncounterSettings
        Encounter settings data to be converted

    Returns
    -------
    encounter_settings : EncounterSettings
        Converted encounter settings data
    """
    assert encounter_settings.classification is not None

    encounter_settings.classification.theta13_criteria = deg_2_rad(encounter_settings.classification.theta13_criteria)
    encounter_settings.classification.theta14_criteria = deg_2_rad(encounter_settings.classification.theta14_criteria)
    encounter_settings.classification.theta15_criteria = deg_2_rad(encounter_settings.classification.theta15_criteria)
    encounter_settings.classification.theta15[0] = deg_2_rad(encounter_settings.classification.theta15[0])
    encounter_settings.classification.theta15[1] = deg_2_rad(encounter_settings.classification.theta15[1])

    encounter_settings.vector_range[0] = min_2_s(encounter_settings.vector_range[0])
    encounter_settings.vector_range[1] = min_2_s(encounter_settings.vector_range[1])

    encounter_settings.situation_length = min_2_s(encounter_settings.situation_length)
    encounter_settings.max_meeting_distance = nm_2_m(encounter_settings.max_meeting_distance)
    encounter_settings.evolve_time = min_2_s(encounter_settings.evolve_time)
    encounter_settings.common_vector = min_2_s(encounter_settings.common_vector)

    return encounter_settings


def camel_to_snake(string: str) -> str:
    """Convert a camel case string to snake case."""
    return "".join([f"_{c.lower()}" if c.isupper() else c for c in string]).lstrip("_")


def convert_keys_to_snake_case(data: dict[str, Any]) -> dict[str, Any]:
    """Convert keys in a nested dictionary from camel case to snake case."""
    return cast("dict[str, Any]", _convert_keys_to_snake_case(data))


def _convert_keys_to_snake_case(
    data: dict[str, Any] | list[Any],
) -> dict[str, Any] | list[Any]:
    """Convert keys in a nested dictionary from camel case to snake case."""
    if isinstance(data, dict):  # Dict
        converted_dict: dict[str, Any] = {}
        for key, value in data.items():
            converted_key = camel_to_snake(key)
            converted_value = _convert_keys_to_snake_case(value) if isinstance(value, dict | list) else value
            converted_dict[converted_key] = converted_value
        return converted_dict

    # List
    converted_list: list[Any] = []
    for value in data:
        converted_value = _convert_keys_to_snake_case(value) if isinstance(value, dict | list) else value
        converted_list.append(value)
    return converted_list
