# -*- coding: utf-8 -*-
"""Root level fixtures for `trafficgen`"""
import pytest
from pathlib import Path


@pytest.fixture
def your_fixture():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    return None


@pytest.fixture(scope="session")
def data_folder():
    """Path to test data folder"""
    return str(Path(__file__).parent / "data")


@pytest.fixture(scope="session")
def proj_data_folder():
    """Path to project data folder"""
    return str(Path(__file__).parent.parent / "data")


@pytest.fixture(scope="session")
def situations_folder(proj_data_folder):
    """Path to test data folder"""
    return str(Path(proj_data_folder) / "baseline_situations_input")


@pytest.fixture(scope="session")
def situations_folder_test_01():
    """Path to test 01 data folder"""
    return str(Path(__file__).parent / "data/test_01")


@pytest.fixture(scope="session")
def situations_folder_test_02():
    """Path to test 02 data folder"""
    return str(Path(__file__).parent / "data/test_02")


@pytest.fixture(scope="session")
def situations_folder_test_03():
    """Path to test 03 data folder"""
    return str(Path(__file__).parent / "data/test_03")


@pytest.fixture(scope="session")
def situations_folder_test_04():
    """Path to test 04 data folder"""
    return str(Path(__file__).parent / "data/test_04")


@pytest.fixture(scope="session")
def situations_folder_test_05():
    """Path to test 05 data folder"""
    return str(Path(__file__).parent / "data/test_05")


@pytest.fixture(scope="session")
def situations_folder_test_06():
    """Path to test 06 data folder"""
    return str(Path(__file__).parent / "data/test_06")


@pytest.fixture(scope="session")
def situations_folder_test_07():
    """Path to test 07 data folder"""
    return str(Path(__file__).parent / "data/test_07")


@pytest.fixture(scope="session")
def situations_folder_test_08():
    """Path to test 06 data folder"""
    return str(Path(__file__).parent / "data/test_08")


@pytest.fixture(scope="session")
def target_ships_folder(proj_data_folder):
    """Path to test data folder"""
    return str(Path(proj_data_folder) / "target_ships")


@pytest.fixture(scope="session")
def settings_file(data_folder):
    """Path to test data folder"""
    return str(
        Path(__file__).parent.parent / "src" / "trafficgen" / "settings" / "encounter_settings.json"
    )  # noqa: E501


@pytest.fixture(scope="session")
def own_ship_file(proj_data_folder):
    """Path to test data folder"""
    return str(Path(proj_data_folder) / "own_ship" / "own_ship.json")


@pytest.fixture(scope="function")
def output_folder(tmp_path_factory):
    """Path to test data folder"""
    return str(tmp_path_factory.mktemp("data"))
