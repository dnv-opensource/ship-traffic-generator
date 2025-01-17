"""Functions to clean traffic situations data before writing it to a json file."""

import json
from pathlib import Path
from typing import Any, TypeVar

from trafficgen.types import OwnShip, Ship, TargetShip, TrafficSituation
from trafficgen.utils import m_2_nm, m_pr_s_2_knot, rad_2_deg

T_ship = TypeVar("T_ship", Ship, OwnShip, TargetShip)


def write_traffic_situations_to_json_file(situations: list[TrafficSituation], write_folder: Path) -> None:
    """
    Write traffic situations to json file.

    Parameters
    ----------
    traffic_situations : list[TrafficSituation]
        List of traffic situations to be written to file
    write_folder : Path
        Path to the folder where the json files is to be written
    """
    Path(write_folder).mkdir(parents=True, exist_ok=True)
    for i, situation in enumerate(situations):
        file_number: int = i + 1
        output_file_path: Path = write_folder / f"traffic_situation_{file_number:02d}.json"
        situation = convert_situation_data_from_si_units_to__maritime(situation)  # noqa: PLW2901
        data: dict[str, Any] = situation.model_dump(
            by_alias=True, exclude_unset=True, exclude_defaults=False, exclude_none=True
        )

        # Remove the 'sogMax' field from the 'static' dictionary in ownShip
        if "static" in data.get("ownShip", {}):
            data["ownShip"]["static"].pop("sogMax", None)

        # Remove the 'sogMax' field from the 'static' dictionary in each targetShip
        for target_ship in data.get("targetShips", []):
            if "static" in target_ship:
                target_ship["static"].pop("sogMax", None)

        json_data: str = json.dumps(data, indent=4)
        with Path.open(output_file_path, "w", encoding="utf-8") as outfile:
            _ = outfile.write(json_data)


def convert_situation_data_from_si_units_to__maritime(situation: TrafficSituation) -> TrafficSituation:
    """
    Convert situation data which is given in SI units to maritime units.

    Parameters
    ----------
    situation : TrafficSituation
        Traffic situation data

    Returns
    -------
    situation : TrafficSituation
        Converted traffic situation data
    """
    assert situation.own_ship is not None
    situation.own_ship = convert_ship_data_from_si_units_to_maritime(situation.own_ship)

    assert situation.target_ships is not None
    for target_ship in situation.target_ships:
        target_ship = convert_ship_data_from_si_units_to_maritime(target_ship)  # noqa: PLW2901

    return situation


def convert_ship_data_from_si_units_to_maritime(ship: T_ship) -> T_ship:
    """
    Convert ship data which is given in SI units to maritime units.

    Parameters
    ----------
    ship : T_ship
        Ship data

    Returns
    -------
    ship : T_ship
        Converted ship data
    """
    assert ship.initial is not None
    assert ship.initial.heading is not None
    ship.initial.position.lon = round(rad_2_deg(ship.initial.position.lon), 8)
    ship.initial.position.lat = round(rad_2_deg(ship.initial.position.lat), 8)
    ship.initial.cog = round(rad_2_deg(ship.initial.cog), 2)
    ship.initial.sog = round(m_pr_s_2_knot(ship.initial.sog), 1)
    ship.initial.heading = round(rad_2_deg(ship.initial.heading), 2)

    if ship.waypoints is not None:
        for waypoint in ship.waypoints:
            waypoint.position.lat = round(rad_2_deg(waypoint.position.lat), 8)
            waypoint.position.lon = round(rad_2_deg(waypoint.position.lon), 8)
            if waypoint.turn_radius is not None:
                waypoint.turn_radius = round(m_2_nm(waypoint.turn_radius), 2)
            if waypoint.leg is not None:
                if waypoint.leg.starboard_xtd is not None:
                    waypoint.leg.starboard_xtd = round(m_2_nm(waypoint.leg.starboard_xtd), 2)
                if waypoint.leg.portside_xtd is not None:
                    waypoint.leg.portside_xtd = round(m_2_nm(waypoint.leg.portside_xtd), 2)
                if waypoint.leg.data is not None and waypoint.leg.data.sog is not None:
                    assert waypoint.leg.data.sog.value is not None
                    assert waypoint.leg.data.sog.interp_start is not None
                    assert waypoint.leg.data.sog.interp_end is not None
                    waypoint.leg.data.sog.value = round(m_pr_s_2_knot(waypoint.leg.data.sog.value), 2)
                    waypoint.leg.data.sog.interp_start = round(m_2_nm(waypoint.leg.data.sog.interp_start), 2)
                    waypoint.leg.data.sog.interp_end = round(m_2_nm(waypoint.leg.data.sog.interp_end), 2)

    return ship
