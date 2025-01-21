"""Root level fixtures for `trafficgen`"""

from pathlib import Path

import pytest


@pytest.fixture
def your_fixture():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    return


@pytest.fixture(scope="session")
def data_folder() -> Path:
    """Path to test data folder"""
    return Path(__file__).parent / "data"


@pytest.fixture(scope="session")
def proj_data_folder() -> Path:
    """Path to project data folder"""
    return Path(__file__).parent.parent / "data"


@pytest.fixture(scope="session")
def situations_folder(proj_data_folder: Path) -> Path:
    """Path to test data folder"""
    return Path(proj_data_folder) / "baseline_situations_input"


@pytest.fixture(scope="session")
def situations_folder_test_01() -> Path:
    """Path to test 01 data folder"""
    return Path(__file__).parent / "data/test_01"


@pytest.fixture(scope="session")
def situations_folder_test_02() -> Path:
    """Path to test 02 data folder"""
    return Path(__file__).parent / "data/test_02"


@pytest.fixture(scope="session")
def situations_folder_test_03() -> Path:
    """Path to test 03 data folder"""
    return Path(__file__).parent / "data/test_03"


@pytest.fixture(scope="session")
def situations_folder_test_04() -> Path:
    """Path to test 04 data folder"""
    return Path(__file__).parent / "data/test_04"


@pytest.fixture(scope="session")
def situations_folder_test_05() -> Path:
    """Path to test 05 data folder"""
    return Path(__file__).parent / "data/test_05"


@pytest.fixture(scope="session")
def situations_folder_test_06() -> Path:
    """Path to test 06 data folder"""
    return Path(__file__).parent / "data/test_06"


@pytest.fixture(scope="session")
def situations_folder_test_07() -> Path:
    """Path to test 07 data folder"""
    return Path(__file__).parent / "data/test_07"


@pytest.fixture(scope="session")
def situations_folder_test_08() -> Path:
    """Path to test 06 data folder"""
    return Path(__file__).parent / "data/test_08"


@pytest.fixture(scope="session")
def target_ships_folder(proj_data_folder: Path) -> Path:
    """Path to target ships folder"""
    return Path(proj_data_folder) / "target_ships"


@pytest.fixture(scope="session")
def settings_file(data_folder: Path) -> Path:
    """Path to encounter settings file"""
    return Path(__file__).parent.parent / "src" / "trafficgen" / "settings" / "encounter_settings.json"


@pytest.fixture(scope="session")
def own_ship_file(proj_data_folder: Path) -> Path:
    """Path to own ship file"""
    return Path(proj_data_folder) / "own_ship" / "own_ship.json"


@pytest.fixture
def output_folder(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Path to temporary data folder used to write output files to in a test"""
    return tmp_path_factory.mktemp("output_", numbered=True)
