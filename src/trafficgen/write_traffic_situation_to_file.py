"""This module cleans traffic situations data before writing it to json-file."""

import json
from pathlib import Path
import os


def write_traffic_situations_to_json_file(traffic_situations, write_folder):
    """
    Write traffic situations to json file

    Params:
        traffic_situations: Traffic situations to be written to file
        write_folder: Folder where the json files is to be written
    """

    Path(write_folder).mkdir(parents=True, exist_ok=True)
    for i, traffic_situation in enumerate(traffic_situations):
        # traffic_situation = clean_traffic_situation_data(traffic_situation)
        json_object = json.dumps(traffic_situation, indent=4)
        output_file_path = os.path.join(write_folder, "traffic_situation_{0}.json".format(i + 1))
        with open(output_file_path, "w", encoding="utf-8") as outfile:
            outfile.write(json_object)


def clean_traffic_situation_data(traffic_situation):
    """
    Clean traffic situation data to json file

    Params:
        traffic_situation: Traffic situation to be cleaned

    Returns:
        traffic_situation: Cleaned traffic situation
    """

    # The target ships dict may include some data that is not necessary to write to file
    for i in range(len(traffic_situation["target_ship"])):
        if "position_future" in traffic_situation["target_ship"][i]:
            del traffic_situation["target_ship"][i]["position_future"]
        if "vector_length" in traffic_situation["target_ship"][i]:
            del traffic_situation["target_ship"][i]["vector_length"]

    return traffic_situation
