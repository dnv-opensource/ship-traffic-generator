"""Tests writing files."""

from pathlib import Path
from typing import List

from trafficgen.read_files import read_situation_files
from trafficgen.types import TrafficSituation
from trafficgen.write_traffic_situation_to_file import write_traffic_situations_to_json_file


def test_write_situations_multiple(
    situations_folder: Path,
    output_folder: Path,
):
    """Test writing multiple traffic situations in one call."""

    situations: List[TrafficSituation] = read_situation_files(situations_folder)
    write_traffic_situations_to_json_file(situations, output_folder)
    reread_situations: List[TrafficSituation] = read_situation_files(output_folder)

    assert len(situations) == len(reread_situations)


def test_write_situations_single(
    situations_folder: Path,
    output_folder: Path,
):
    """Test writing multiple traffic situations, each in a separate single call."""

    situations: List[TrafficSituation] = read_situation_files(situations_folder)

    # sourcery skip: no-loop-in-tests
    # sourcery skip: no-conditionals-in-tests
    for situation in situations:
        # clean output folder
        for file in output_folder.glob("*"):
            if file.is_file():
                file.unlink()
        write_traffic_situations_to_json_file([situation], output_folder)
        reread_situation: TrafficSituation = read_situation_files(output_folder)[0]
        # single difference between the original and the reread situation should be the
        # input_file_name field
        reread_situation.input_file_name = situation.input_file_name
        assert situation == reread_situation
