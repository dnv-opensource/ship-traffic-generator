"""Functions to clean traffic situations data before writing it to a json file."""

from pathlib import Path
from typing import List

from maritime_schema.types.caga import OwnShip, TargetShip, TrafficSituation

from trafficgen.utils import m_pr_s_2_knot, rad_2_deg


def write_traffic_situations_to_json_file(situations: List[TrafficSituation], write_folder: Path):
    """
    Write traffic situations to json file.

    Params:
        * traffic_situations: Traffic situations to be written to file
        * write_folder: Folder where the json files is to be written
    """

    Path(write_folder).mkdir(parents=True, exist_ok=True)
    for i, situation in enumerate(situations):
        file_number: int = i + 1
        output_file_path: Path = write_folder / f"traffic_situation_{file_number:02d}.json"
        situation = convert_situation_data_from_si_units_to__maritime(situation)
        data: str = situation.model_dump_json(
            by_alias=True, indent=4, exclude_unset=True, exclude_defaults=False, exclude_none=True
        )
        with open(output_file_path, "w", encoding="utf-8") as outfile:
            _ = outfile.write(data)


def convert_situation_data_from_si_units_to__maritime(situation: TrafficSituation) -> TrafficSituation:
    """
    Convert situation data which is given in SI units to maritime units.

    Params:
        * situation: Traffic situation data

    Returns
    -------
        * situation: Converted traffic situation data
    """
    assert situation.own_ship is not None
    situation.own_ship = convert_own_ship_data_from_si_units_to_maritime(situation.own_ship)

    assert situation.target_ships is not None
    for target_ship in situation.target_ships:
        target_ship = convert_target_ship_data_from_si_units_to_maritime(target_ship)

    return situation


def convert_own_ship_data_from_si_units_to_maritime(ship: OwnShip) -> OwnShip:
    """
    Convert ship data which is given in SI units to maritime units.

    Params:
        * ship: Ship data

    Returns
    -------
        * ship: Converted ship data
    """
    assert ship.initial is not None
    ship.initial.position.longitude = round(rad_2_deg(ship.initial.position.longitude), 8)
    ship.initial.position.latitude = round(rad_2_deg(ship.initial.position.latitude), 8)
    ship.initial.cog = round(rad_2_deg(ship.initial.cog), 2)
    ship.initial.sog = round(m_pr_s_2_knot(ship.initial.sog), 1)
    ship.initial.heading = round(rad_2_deg(ship.initial.heading), 2)

    if ship.waypoints is not None:
        for waypoint in ship.waypoints:
            waypoint.position.latitude = round(rad_2_deg(waypoint.position.latitude), 8)
            waypoint.position.longitude = round(rad_2_deg(waypoint.position.longitude), 8)
            if waypoint.data is not None:
                if waypoint.data.sog is not None:
                    waypoint.data.sog.value = round(m_pr_s_2_knot(waypoint.data.sog.value), 1)
                if waypoint.data.heading is not None:
                    waypoint.data.heading.value = round(m_pr_s_2_knot(waypoint.data.heading.value), 2)

    return ship


def convert_target_ship_data_from_si_units_to_maritime(ship: TargetShip) -> TargetShip:
    """
    Convert ship data which is given in SI units to maritime units.

    Params:
        * ship: Ship data

    Returns
    -------
        * ship: Converted ship data
    """
    assert ship.initial is not None
    ship.initial.position.longitude = round(rad_2_deg(ship.initial.position.longitude), 8)
    ship.initial.position.latitude = round(rad_2_deg(ship.initial.position.latitude), 8)
    ship.initial.cog = round(rad_2_deg(ship.initial.cog), 2)
    ship.initial.sog = round(m_pr_s_2_knot(ship.initial.sog), 1)
    ship.initial.heading = round(rad_2_deg(ship.initial.heading), 2)

    if ship.waypoints is not None:
        for waypoint in ship.waypoints:
            waypoint.position.latitude = round(rad_2_deg(waypoint.position.latitude), 8)
            waypoint.position.longitude = round(rad_2_deg(waypoint.position.longitude), 8)
            if waypoint.data is not None:
                if waypoint.data.sog is not None:
                    waypoint.data.sog.value = round(m_pr_s_2_knot(waypoint.data.sog.value), 1)
                if waypoint.data.heading is not None:
                    waypoint.data.heading.value = round(m_pr_s_2_knot(waypoint.data.heading.value), 2)

    return ship
