"""Functions to generate traffic situations."""

import logging
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from trafficgen.encounter import (
    define_own_ship,
    generate_encounter,
)
from trafficgen.read_files import (
    convert_settings_data_from_maritime_to_si_units,
    convert_ship_data_from_maritime_to_si_units,
    convert_situation_data_from_maritime_to_si_units,
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


def _validate_ownship_coordinate(ownship_coordinate: str | None) -> tuple[str, str]:
    if ownship_coordinate is None:
        raise ValueError(
            "Ownship coordinate provided is not valid. Please provide in the format 'lat,lon' in decimal degrees."
        )

    try:
        lat_str, lon_str = ownship_coordinate.split(",")
    except (ValueError, AttributeError) as error:
        raise ValueError(
            "Ownship coordinate provided is not valid. Please provide in the format 'lat,lon' in decimal degrees."
        ) from error

    if lat_str.strip() == "" or lon_str.strip() == "":
        raise ValueError(
            "Ownship coordinate provided is not valid. Please provide in the format 'lat,lon' in decimal degrees."
        )

    return lat_str, lon_str


def _resolve_own_ship_static(own_ship_input: Path | ShipStatic) -> ShipStatic:
    if isinstance(own_ship_input, Path):
        return read_own_ship_static_file(own_ship_input)

    return convert_ship_data_from_maritime_to_si_units(own_ship_input)


def _resolve_target_ships_static(target_ships_input: Path | list[ShipStatic]) -> list[ShipStatic]:
    if isinstance(target_ships_input, Path):
        return read_target_ship_static_files(target_ships_input)

    return [convert_ship_data_from_maritime_to_si_units(target_ship_data) for target_ship_data in target_ships_input]


def _resolve_encounter_settings(settings_input: Path | EncounterSettings) -> EncounterSettings:
    if isinstance(settings_input, Path):
        return read_encounter_settings_file(settings_input)

    return convert_settings_data_from_maritime_to_si_units(settings_input)


def _resolve_situation_inputs(situations_input: Path | SituationInput | list[SituationInput]) -> list[SituationInput]:
    if isinstance(situations_input, Path):
        return read_situation_files(situations_input)

    if isinstance(situations_input, list):
        raw_situations: list[SituationInput] = situations_input
    else:
        raw_situations = [situations_input]

    return [convert_situation_data_from_maritime_to_si_units(raw_situation) for raw_situation in raw_situations]


def generate_traffic_situations(
    situations_data: Path | SituationInput | list[SituationInput],
    own_ship_data: Path | ShipStatic,
    target_ships_data: Path | list[ShipStatic],
    settings_data: Path | EncounterSettings,
    ownship_coordinate: str | None = None,
) -> list[TrafficSituation]:
    """Generate traffic situations based on the provided input files.

    Parameters
    ----------
    situations_data : Path | SituationInput | list[SituationInput]
        Path to situation file/folder, or one/many situation JSON payloads.
    own_ship_data : Path | ShipStatic
        Path to own ship static file, or own ship static JSON payload.
    target_ships_data : Path | list[ShipStatic]
        Path to target ship static folder, or list of target ship static JSON payloads.
    settings_data : Path | EncounterSettings
        Path to encounter settings file, or encounter settings JSON payload.
    ownship_coordinate : str | None
        The ownship start coordinate as 'lat,lon' in decimal degrees.

    Returns
    -------
    list[TrafficSituation]
        A list of generated traffic situations.
    """
    own_ship_static: ShipStatic = _resolve_own_ship_static(own_ship_data)
    target_ships_static: list[ShipStatic] = _resolve_target_ships_static(target_ships_data)
    encounter_settings: EncounterSettings = _resolve_encounter_settings(settings_data)
    desired_traffic_situations: list[SituationInput] = _resolve_situation_inputs(situations_data)
    traffic_situations: list[TrafficSituation] = []

    # if a (valid) ownship coordinate is provided on the commandline (lat,lon),
    # then this takes priority over any specified in the situation file
    overwrite_ownship_initial_coord = ownship_coordinate is not None
    if overwrite_ownship_initial_coord:
        lat_str, lon_str = _validate_ownship_coordinate(ownship_coordinate)
        logger.info(f"Overwriting ownship initial coordinate with commandline value: lat={lat_str}, lon={lon_str}")

    for desired_traffic_situation in desired_traffic_situations:
        num_situations: int = desired_traffic_situation.num_situations
        assert encounter_settings.common_vector is not None
        assert desired_traffic_situation.own_ship is not None
        assert desired_traffic_situation.encounters is not None
        lat_lon0: GeoPosition
        if overwrite_ownship_initial_coord:
            lat_lon0 = GeoPosition(lat=float(lat_str), lon=float(lon_str))
        else:
            lat_lon0 = desired_traffic_situation.own_ship.initial.position

        own_ship: OwnShip = define_own_ship(
            desired_traffic_situation,
            own_ship_static,
            encounter_settings,
            lat_lon0,
            overwrite_ownship_initial_coord=overwrite_ownship_initial_coord,
        )
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
