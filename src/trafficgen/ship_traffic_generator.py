"""Functions to generate traffic situations."""

from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

import logging

from trafficgen.encounter import (
    define_own_ship,
    generate_encounter,
)
from trafficgen.read_files import (
    read_encounter_settings_file,
    read_own_ship_static_file,
    read_situation_files,
    read_target_ship_static_files,
)
from trafficgen.types import (
    EncounterSettings,
    EncounterType,
    GeoPosition,
    OwnShip,
    ShipStatic,
    SituationInput,
    TargetShip,
    TrafficSituation,
)

try:
    project_version = version("trafficgen")
except PackageNotFoundError:
    project_version = "Not found"


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_traffic_situations(
    situation_folder: Path,
    own_ship_file: Path,
    target_ship_folder: Path,
    settings_file: Path,
    ownship_coordinate: str | None = None,
) -> list[TrafficSituation]:
    """Generate traffic situations based on the provided input files.

    Parameters
    ----------
    situation_folder : Path
        Path to the folder containing situation files.
    own_ship_file : Path
        Path to the file containing own ship static data.
    target_ship_folder : Path
        Path to the folder containing target ship static files.
    settings_file : Path
        Path to the file containing encounter settings.
    ownship_coordinate : str | None
        The ownship start coordinate as 'lat,lon' in decimal degrees.

    Returns
    -------
    list[TrafficSituation]
        A list of generated traffic situations.
    """
    own_ship_static: ShipStatic = read_own_ship_static_file(own_ship_file)
    target_ships_static: list[ShipStatic] = read_target_ship_static_files(target_ship_folder)
    encounter_settings: EncounterSettings = read_encounter_settings_file(settings_file)
    desired_traffic_situations: list[SituationInput] = read_situation_files(situation_folder)
    traffic_situations: list[TrafficSituation] = []

    # if a (valid) ownship coordinate is provided on the commandline (lat,lon),
    # then this takes priority over any specified in the situation file
    overwrite_ownship_initial_coord = ownship_coordinate is not None
    if overwrite_ownship_initial_coord:
        try:
            lat_str, lon_str = ownship_coordinate.split(",")
            if lat_str.strip() == "" or lon_str.strip() == "":
                raise ValueError
        except (ValueError, AttributeError) as error:
            raise ValueError(
                "Ownship coordinate provided is not valid. "
                "Please provide in the format 'lat,lon' in decimal degrees."
            ) from error
        else:
            logger.info(
                f"Overwriting ownship initial coordinate with commandline value: "
                f"lat={lat_str}, lon={lon_str}"
            )

    for desired_traffic_situation in desired_traffic_situations:
        num_situations: int = desired_traffic_situation.num_situations
        assert encounter_settings.common_vector is not None
        assert desired_traffic_situation.own_ship is not None
        assert desired_traffic_situation.encounters is not None
        if overwrite_ownship_initial_coord:
            lat_lon0 = GeoPosition(lat=float(lat_str), lon=float(lon_str))
        else:
            lat_lon0: GeoPosition = desired_traffic_situation.own_ship.initial.position

        own_ship: OwnShip = define_own_ship(desired_traffic_situation, own_ship_static, encounter_settings, lat_lon0, overwrite_ownship_initial_coord)
        for _ in range(num_situations):
            target_ships: list[TargetShip] = []
            for i, encounter in enumerate(desired_traffic_situation.encounters):
                desired_encounter_type = EncounterType(encounter.desired_encounter_type)
                beta: list[float] | float | None = encounter.beta
                relative_speed: float | None = encounter.relative_speed
                vector_time: list[float] | float = encounter.vector_time

                target_ship, encounter_found = generate_encounter(
                    desired_encounter_type,
                    own_ship.model_copy(deep=True),
                    target_ships_static,
                    i + 1,
                    beta,
                    relative_speed,
                    vector_time,
                    encounter_settings,
                )
                if encounter_found:
                    target_ships.append(target_ship.model_copy(deep=True))

            traffic_situation: TrafficSituation = TrafficSituation(
                version=project_version,
                title=desired_traffic_situation.title,
                description=desired_traffic_situation.description,
                own_ship=own_ship.model_copy(deep=True),
                target_ships=target_ships,
                start_time=None,
            )
            traffic_situations.append(traffic_situation)
    return traffic_situations
