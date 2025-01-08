"""Tests writing files."""

from pathlib import Path
from typing import TYPE_CHECKING

from trafficgen.read_files import (
    read_generated_situation_files,
)
from trafficgen.ship_traffic_generator import generate_traffic_situations
from trafficgen.write_traffic_situation_to_file import write_traffic_situations_to_json_file

if TYPE_CHECKING:
    from trafficgen.types import (
        TrafficSituation,
    )


def test_write_situations_multiple(
    situations_folder: Path,
    own_ship_file: Path,
    target_ships_folder: Path,
    settings_file: Path,
    output_folder: Path,
):
    """Test writing multiple traffic situations in one call."""

    situations: list[TrafficSituation] = generate_traffic_situations(
        situation_folder=situations_folder,
        own_ship_file=own_ship_file,
        target_ship_folder=target_ships_folder,
        settings_file=settings_file,
    )
    write_traffic_situations_to_json_file(situations, output_folder)
    reread_situations: list[TrafficSituation] = read_generated_situation_files(output_folder)

    assert len(situations) == len(reread_situations)


# def test_write_situations_single(
#     situations_folder: Path,
#     settings_file: Path,
#     output_folder: Path,
# ):
#     """Test writing multiple traffic situations, each in a separate single call."""

#     encounter_settings: EncounterSettings = read_encounter_settings_file(settings_file)
#     situations: List[TrafficSituation] = read_situation_files(
#         situations_folder, encounter_settings.input_units
#     )

#     # sourcery skip: no-loop-in-tests
#     # sourcery skip: no-conditionals-in-tests
#     for situation in situations:
#         # clean output folder
#         for file in output_folder.glob("*"):
#             if file.is_file():
#                 file.unlink()
#         write_traffic_situations_to_json_file([situation], output_folder)
#         reread_situation: TrafficSituation = read_generated_situation_files(output_folder)[0]
#         # single difference between the original and the reread situation should be the
#         # input_file_name field
#         reread_situation.input_file_name = situation.input_file_name
#         assert situation == reread_situation
