"""Tests writing files."""

from pathlib import Path
from typing import List

from trafficgen.read_files import read_situation_files
from trafficgen.types import Situation
from trafficgen.write_traffic_situation_to_file import write_traffic_situations_to_json_file


def test_write_situations(
    situations_folder: Path,
    output_folder: Path,
):
    """Test writing traffic situations."""

    situations: List[Situation] = read_situation_files(situations_folder)
    write_traffic_situations_to_json_file(situations, output_folder)
    reread_situations: List[Situation] = read_situation_files(output_folder)

    assert len(situations) == len(reread_situations)

    # sourcery skip: no-loop-in-tests
    for situation, reread_situation in zip(situations, reread_situations):
        # single difference between the original and the reread situation should be the
        # input_file_name field
        reread_situation.input_file_name = situation.input_file_name
        assert situation == reread_situation
