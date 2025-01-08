"""Functions to generate traffic situations."""

from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

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


def generate_traffic_situations(
    situation_folder: Path,
    own_ship_file: Path,
    target_ship_folder: Path,
    settings_file: Path,
) -> list[TrafficSituation]:
    """
    Generate a set of traffic situations using input files.

    This is the main function for generating a set of traffic situations using input files
    specifying number and type of encounter, type of target ships etc.

    Params:
        * situation_folder: Path to situation folder, files describing the desired situations
        * own_ship_file: Path to where own ships is found
        * target_ship_folder: Path to where different type of target ships is found
        * settings_file: Path to settings file

    Returns
    -------
        * traffic_situations: List of generated traffic situations.
        * One situation may consist of one or more encounters.
    """
    own_ship_static: ShipStatic = read_own_ship_static_file(own_ship_file)
    target_ships_static: list[ShipStatic] = read_target_ship_static_files(target_ship_folder)
    encounter_settings: EncounterSettings = read_encounter_settings_file(settings_file)
    desired_traffic_situations: list[SituationInput] = read_situation_files(situation_folder)
    traffic_situations: list[TrafficSituation] = []

    for desired_traffic_situation in desired_traffic_situations:
        num_situations: int = desired_traffic_situation.num_situations
        assert encounter_settings.common_vector is not None
        assert desired_traffic_situation.own_ship is not None
        assert desired_traffic_situation.encounters is not None

        lat_lon0: GeoPosition = desired_traffic_situation.own_ship.initial.position

        own_ship: OwnShip = define_own_ship(desired_traffic_situation, own_ship_static, encounter_settings, lat_lon0)
        for _ in range(num_situations):
            target_ships: list[TargetShip] = []
            for i, encounter in enumerate(desired_traffic_situation.encounters):
                desired_encounter_type = EncounterType(encounter.desired_encounter_type)
                beta: list[float] | float | None = encounter.beta
                relative_speed: float | None = encounter.relative_speed
                vector_time: float | None = encounter.vector_time

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
