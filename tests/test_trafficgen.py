#!/usr/bin/env python

"""Tests for `trafficgen` package."""

import os
import json
import pytest


from click.testing import CliRunner

from trafficgen import cli


@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    return None


def test_content(response):
    """Sample pytest test function with the pytest fixture as an argument."""
    assert response is None


def test_basic_cli():
    """Test the CLI, no arguments and --help"""
    runner = CliRunner()
    result = runner.invoke(cli.main)
    assert result.exit_code == 0
    assert 'Usage:' in result.output
    help_result = runner.invoke(cli.main, ['--help'])
    assert help_result.exit_code == 0
    assert '--help' in help_result.output and 'Show this message and exit' in help_result.output  # noqa: E501


def test_gen_situations_cli(situations_folder, own_ship_file, target_ships_folder,
                            settings_file, output_folder):
    """Test generating traffic situations using the cli"""
    runner = CliRunner()
    result = runner.invoke(cli.main, ['gen-situation',
                                      '-s', situations_folder,
                                      '-os', own_ship_file,
                                      '-t', target_ships_folder,
                                      '-c', settings_file,
                                      '-o', output_folder])
    assert result.exit_code == 0
    assert 'Generating traffic situations' in result.output
    assert 'Plotting traffic situations' not in result.output
    assert 'Writing traffic situations to files' in result.output


def test_gen_situations_1_ts_full_spec_cli(situations_folder_test_01,
                                           own_ship_file,
                                           target_ships_folder,
                                           settings_file, output_folder):
    """
    Test generation of one traffic situation using full specification,
    meaning all parameters are specified. The generated situations
    should have only one target ship.
    """
    runner = CliRunner()
    result = runner.invoke(cli.main, ['gen-situation',
                                      '-s', situations_folder_test_01,
                                      '-os', own_ship_file,
                                      '-t', target_ships_folder,
                                      '-c', settings_file,
                                      '-o', output_folder])

    situations = read_situation_files(output_folder)
    number_of_situations = len(situations)
    number_of_target_ships = 0
    # TODO enumerate functionality not used, replace by for loop
    # for situation in situations:
    for _, situation in enumerate(situations):
        number_of_target_ships = len(situation['target_ship'])
        if number_of_target_ships != 1:
            print('test')
            break

    assert result.exit_code == 0
    assert 'Generating traffic situations' in result.output
    assert number_of_situations == 5
    assert number_of_target_ships == 1


def test_gen_situations_1_ts_partly_spec_cli(situations_folder_test_02,
                                             own_ship_file,
                                             target_ships_folder,
                                             settings_file, output_folder):
    """
    Test generation of one traffic situation using partly specification,
    meaning some of the parameters are specified. The generated situations
    should have only one target ship.
    """
    runner = CliRunner()
    result = runner.invoke(cli.main, ['gen-situation',
                                      '-s', situations_folder_test_02,
                                      '-os', own_ship_file,
                                      '-t', target_ships_folder,
                                      '-c', settings_file,
                                      '-o', output_folder])

    situations = read_situation_files(output_folder)
    number_of_situations = len(situations)
    number_of_target_ships = 0
    # TODO: enumerate functionality not used, replace by for loop
    for _, situation in enumerate(situations):
        number_of_target_ships = len(situation['target_ship'])
        if number_of_target_ships != 1:
            break

    assert result.exit_code == 0
    assert 'Generating traffic situations' in result.output
    assert number_of_situations == 2
    assert number_of_target_ships == 1


def test_gen_situations_1_ts_minimum_spec_cli(situations_folder_test_03,
                                              own_ship_file,
                                              target_ships_folder,
                                              settings_file, output_folder):
    """
    Test generation of one traffic situation using minimum specification,
    meaning only type of situation is specified. The generated situations
    should have only one target ship.
    """
    runner = CliRunner()
    result = runner.invoke(cli.main, ['gen-situation',
                                      '-s', situations_folder_test_03,
                                      '-os', own_ship_file,
                                      '-t', target_ships_folder,
                                      '-c', settings_file,
                                      '-o', output_folder])

    situations = read_situation_files(output_folder)
    number_of_situations = len(situations)
    number_of_target_ships = 0
    # TODO enumerate functionality not used, replace by for loop
    for _, situation in enumerate(situations):
        number_of_target_ships = len(situation['target_ship'])
        if number_of_target_ships != 1:
            break

    assert result.exit_code == 0
    assert 'Generating traffic situations' in result.output
    assert number_of_situations == 2
    assert number_of_target_ships == 1


def test_gen_situations_2_ts_one_to_many_situations_cli(
                                                situations_folder_test_04,
                                                own_ship_file,
                                                target_ships_folder,
                                                settings_file,
                                                output_folder):
    """
    Testing situation generation where one file is used to give 5 situations
    where two target ships are included.
    """
    runner = CliRunner()
    result = runner.invoke(cli.main, ['gen-situation',
                                      '-s', situations_folder_test_04,
                                      '-os', own_ship_file,
                                      '-t', target_ships_folder,
                                      '-c', settings_file,
                                      '-o', output_folder])

    situations = read_situation_files(output_folder)
    number_of_situations = len(situations)
    # TODO enumerate functionality not used, replace by for loop
    for _, situation in enumerate(situations):
        number_of_target_ships = len(situation['target_ship'])
        if number_of_target_ships != 2:
            break

    assert result.exit_code == 0
    assert 'Generating traffic situations' in result.output
    assert number_of_situations == 5
    assert number_of_target_ships == 2


def test_gen_situations_one_to_many_situations_cli(situations_folder_test_05,own_ship_file,
                                                   target_ships_folder,
                                                   settings_file,
                                                   output_folder):
    """
    Testing situation generation where three files are used to give
    10 situations where one, two or three target ship are included.
    """
    runner = CliRunner()
    result = runner.invoke(cli.main, ['gen-situation',
                                      '-s', situations_folder_test_05,
                                      '-os', own_ship_file,
                                      '-t', target_ships_folder,
                                      '-c', settings_file,
                                      '-o', output_folder])

    situations = read_situation_files(output_folder)
    number_of_situations = len(situations)
    # TODO enumerate functionality not used, replace by for loop
    for _, situation in enumerate(situations):
        number_of_target_ships = len(situation['target_ship'])
        if number_of_target_ships == 1 or number_of_target_ships == 2 or number_of_target_ships == 3:  # noqa: E501
            number_of_target_ships_ok = 1
        else:
            number_of_target_ships_ok = 0
            break

    assert result.exit_code == 0
    assert 'Generating traffic situations' in result.output
    assert number_of_situations == 10
    assert number_of_target_ships_ok == 1


def test_gen_situations_ot_gw_target_ship_speed_too_high_cli(
                                                    situations_folder_test_06,
                                                    own_ship_file,
                                                    target_ships_folder,
                                                    settings_file,
                                                    output_folder):
    """
    Testing situation were the target ship has a higher speed than own ship,
    still the situation file specifies overtaking give way scenario. The result
    should be that number of target ships are 0.
    """
    runner = CliRunner()
    result = runner.invoke(cli.main, ['gen-situation',
                                      '-s', situations_folder_test_06,
                                      '-os', own_ship_file,
                                      '-t', target_ships_folder,
                                      '-c', settings_file,
                                      '-o', output_folder])

    situations = read_situation_files(output_folder)
    number_of_situations = len(situations)
    # TODO enumerate functionality not used, replace by for loop
    for _, situation in enumerate(situations):
        number_of_target_ships = len(situation['target_ship'])
        if number_of_target_ships == 1 or number_of_target_ships == 2 or number_of_target_ships == 3:  # noqa: E501
            number_of_target_ships_ok = 1
            break
        else:
            number_of_target_ships_ok = 0

    assert result.exit_code == 0
    assert 'Generating traffic situations' in result.output
    assert number_of_situations == 3
    assert number_of_target_ships_ok == 0


def test_gen_situations_baseline_cli(situations_folder_test_08,
                                     own_ship_file,
                                     target_ships_folder,
                                     settings_file, output_folder):
    """
    Testing situation were desired beta does not match desired encounter
    situation. The result should be that number of target ships are 0 for
    all situations.
    """
    runner = CliRunner()
    result = runner.invoke(cli.main, ['gen-situation',
                                      '-s', situations_folder_test_08,
                                      '-os', own_ship_file,
                                      '-t', target_ships_folder,
                                      '-c', settings_file,
                                      '-o', output_folder])

    situations = read_situation_files(output_folder)
    # TODO enumerate functionality not used, replace by for loop
    for _, situation in enumerate(situations):
        number_of_target_ships = len(situation['target_ship'])
        if number_of_target_ships == 1 or number_of_target_ships == 2 or number_of_target_ships == 3:  # noqa: E501
            number_of_target_ships_ok = 1
            break
        else:
            number_of_target_ships_ok = 0

    assert result.exit_code == 0
    assert 'Generating traffic situations' in result.output
    assert number_of_target_ships_ok == 1


def read_situation_files(situation_folder):
    """
    Reads situation files.

    Params:
        situation_folder: Path to the folder where situation files are found

    Returns:
        situations: List of desired traffic situations
    """
    situations = []
    for file_name in [file for file in os.listdir(situation_folder) if file.endswith('.json')]:  # noqa: E501
        file_path = os.path.join(situation_folder, file_name)
        with open(file_path, encoding="utf-8") as json_file:
            situation = json.load(json_file)
            situation['file_name'] = file_name
            situations.append(situation)
    return situations
