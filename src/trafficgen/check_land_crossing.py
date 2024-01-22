"""Module with helper functions to determine if a generated path is crossing land."""

from typing import List

from global_land_mask import globe

from trafficgen.marine_system_simulator import flat2llh
from trafficgen.types import Position
from trafficgen.utils import calculate_position_at_certain_time, deg_2_rad, rad_2_deg


def path_crosses_land(
    position_1: Position,
    speed: float,
    course: float,
    lat_lon0: List[float],
    time_interval: float = 50.0,
) -> bool:
    """
    Find if path is crossing land.

    Params:
        position_1: Ship position in (north, east) [m].
        speed: Ship speed [knots].
        course: Ship course [degree].
        lat_lon0: Reference point, latitudinal [degree] and longitudinal [degree].
        time_interval: The time interval the vessel should travel without crossing land [minutes]

    Returns
    -------
        is_on_land: True if parts of the path crosses land.
    """

    north_1 = position_1.north
    east_1 = position_1.east
    lat_0 = lat_lon0[0]
    lon_0 = lat_lon0[1]

    num_checks = 10
    for i in range(int(time_interval / num_checks)):
        position_2 = calculate_position_at_certain_time(
            Position(north=north_1, east=east_1), speed, course, i * time_interval / num_checks
        )
        lat, lon, _ = flat2llh(position_2.north, position_2.east, deg_2_rad(lat_0), deg_2_rad(lon_0))
        lat = rad_2_deg(lat)
        lon = rad_2_deg(lon)
        if globe.is_land(lat, lon):  # type: ignore  (The global_land_mask package is unfortunately not typed.)
            return True
    return False
