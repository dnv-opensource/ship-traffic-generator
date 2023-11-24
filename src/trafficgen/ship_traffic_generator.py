"""Functions to generate traffic situations."""

import copy

from . import (
    generate_encounter,
    read_encounter_setting_file,
    read_own_ship_file,
    read_situation_files,
    read_target_ship_files,
    update_position_data_own_ship,
)


def generate_traffic_situations(situation_folder, own_ship_file, target_ship_folder, settings_file):
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

    desired_traffic_situations = read_situation_files(situation_folder)
    own_ship = read_own_ship_file(own_ship_file)
    target_ships = read_target_ship_files(target_ship_folder)
    encounter_setting = read_encounter_setting_file(settings_file)
    traffic_situations = []

    for _, desired_traffic_situation in enumerate(desired_traffic_situations):
        if "num_situations" in desired_traffic_situation:
            num_situations = desired_traffic_situation["num_situations"]
        else:
            num_situations = 1

        for _ in range(num_situations):
            traffic_situation = {}
            traffic_situation = {
                "title": desired_traffic_situation["title"],
                "input_file_name": desired_traffic_situation["input_file_name"],
                "common_vector": desired_traffic_situation["common_vector"],
                "lat_lon_0": encounter_setting["lat_lon_0"],
            }

            own_ship["start_pose"] = desired_traffic_situation["own_ship"]["start_pose"]
            own_ship = update_position_data_own_ship(
                own_ship, encounter_setting["lat_lon_0"], traffic_situation["common_vector"]
            )
            traffic_situation["own_ship"] = own_ship
            traffic_situation["target_ship"] = []
            for k in range(len(desired_traffic_situation["encounter"])):
                desired_encounter_type = desired_traffic_situation["encounter"][k][
                    "desired_encounter_type"
                ]
                settings = encounter_setting
                beta = find_value(desired_traffic_situation["encounter"][k], "beta")
                relative_speed = find_value(desired_traffic_situation["encounter"][k], "relative_speed")
                vector_time = find_value(desired_traffic_situation["encounter"][k], "vector_time")
                target_ship_id = k + 1
                target_ship, encounter_found = generate_encounter(
                    desired_encounter_type,
                    copy.deepcopy(own_ship),
                    target_ships,
                    target_ship_id,
                    beta,
                    relative_speed,
                    vector_time,
                    settings,
                )
                if encounter_found > 0.5:
                    traffic_situation["target_ship"].append(target_ship)

            traffic_situations.append(traffic_situation)
    return traffic_situations


def find_value(parameters, parameter):
    """
    Find a key, value pair in a dict. If the key is there,
    the value is returned. If not, None is returned.

    Params:
        * parameters: Dict of parameters
        * parameter: Parameter key to look for in parameters

    Returns
    -------
        value: value of the key parameter
    """
    return parameters[parameter] if parameter in parameters else None
