"""Functions to clean traffic situations data before writing it to a json file."""

from pathlib import Path
from typing import List

from .types import Situation


def write_traffic_situations_to_json_file(situations: List[Situation], write_folder: Path):
    """
    Write traffic situations to json file.

    Params:
        traffic_situations: Traffic situations to be written to file
        write_folder: Folder where the json files is to be written
    """

    Path(write_folder).mkdir(parents=True, exist_ok=True)
    for i, situation in enumerate(situations):
        file_number: int = i + 1
        output_file_path: Path = write_folder / f"traffic_situation_{file_number:02d}.json"
        data: str = situation.model_dump_json(
            indent=4,
            exclude_unset=True,
            exclude_defaults=False,
            exclude_none=True,
        )
        with open(output_file_path, "w", encoding="utf-8") as outfile:
            _ = outfile.write(data)
