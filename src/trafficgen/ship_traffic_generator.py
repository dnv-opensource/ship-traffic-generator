"""Functions to generate traffic situations."""

from pathlib import Path
from typing import List

from trafficgen.types import EncounterSettings, Ship, Situation, TargetShip

from . import (
    generate_encounter,
    read_encounter_settings_file,
    read_own_ship_file,
    read_situation_files,
    read_target_ship_files,
    update_position_data_own_ship,
)


def generate_traffic_situations(
    situation_folder: Path,
    own_ship_file: Path,
    target_ship_folder: Path,
    settings_file: Path,
) -> List[Situation]:
    """
    Generate a set of traffic situations using input files.
    This is the main function for generating a set of traffic situations using input files
    specifying number and type of encounter, type of target ships etc.

    Params:
        * situation_folder: Path to situation folder, files describing the desired situations
        * target_ship_folder: Path to where different type of target ships is found
        * settings_file: Path to settings file

    Returns
    -------
        traffic_situations: List of generated traffic situations.
        One situation may consist of one or more encounters.
    """

    desired_traffic_situations: List[Situation] = read_situation_files(situation_folder)
    own_ship: Ship = read_own_ship_file(own_ship_file)
    target_ships: List[TargetShip] = read_target_ship_files(target_ship_folder)
    encounter_settings: EncounterSettings = read_encounter_settings_file(settings_file)
    traffic_situations: List[Situation] = []

    for desired_traffic_situation in desired_traffic_situations:
        num_situations: int = desired_traffic_situation.num_situations or 1
        assert desired_traffic_situation.common_vector is not None
        assert desired_traffic_situation.own_ship is not None
        assert desired_traffic_situation.encounter is not None

        for _ in range(num_situations):
            traffic_situation: Situation = Situation(
                title=desired_traffic_situation.title,
                input_file_name=desired_traffic_situation.input_file_name,
                common_vector=desired_traffic_situation.common_vector,
                lat_lon_0=desired_traffic_situation.lat_lon_0,
            )
            assert traffic_situation.common_vector is not None
            own_ship.start_pose = desired_traffic_situation.own_ship.start_pose
            own_ship = update_position_data_own_ship(
                own_ship,
                encounter_settings.lat_lon_0,
                traffic_situation.common_vector,
            )
            traffic_situation.own_ship = own_ship
            traffic_situation.target_ship = []
            for k in range(len(desired_traffic_situation.encounter)):
                desired_encounter_type = desired_traffic_situation.encounter[k].desired_encounter_type
                settings = encounter_settings
                beta: float | None = desired_traffic_situation.encounter[k].beta
                relative_speed: float | None = desired_traffic_situation.encounter[k].relative_speed
                vector_time: float | None = desired_traffic_situation.encounter[k].vector_time
                target_ship_id = k + 1
                target_ship, encounter_found = generate_encounter(
                    desired_encounter_type,
                    own_ship.model_copy(deep=True),
                    target_ships,
                    target_ship_id,
                    beta,
                    relative_speed,
                    vector_time,
                    settings,
                )
                if encounter_found:
                    traffic_situation.target_ship.append(target_ship)

            traffic_situations.append(traffic_situation)
    return traffic_situations
