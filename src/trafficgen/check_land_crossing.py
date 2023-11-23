"""This module finds if the generated path is crossing land."""

from global_land_mask import globe
from . import flat2llh
from . import deg_2_rad, rad_2_deg
from . import calculate_position_at_certain_time


def path_crosses_land(position_1, speed, course, lat_lon_0, time_interval=50):
    """
    Find if path is crossing land.

    Params:
        position_1: Ship position in (north, east) [m].
        speed: Ship speed [knots].
        course: Ship course [degree].
        lat_lon_0: Reference point, latitudinal [degree] and longitudinal [degree].
        time_interval: The time interval the vessel should travel without crossing land [minutes]

    Returns:
        is_on_land: True if parts of the path crosses land.
    """

    north_1 = position_1["north"]
    east_1 = position_1["east"]
    lat_0 = lat_lon_0[0]
    lon_0 = lat_lon_0[1]

    num_checks = 10
    for i in range(int(time_interval / num_checks)):
        position_2 = calculate_position_at_certain_time(
            {"north": north_1, "east": east_1}, speed, course, i * time_interval / num_checks
        )
        lat, lon, _ = flat2llh(
            position_2["north"], position_2["east"], deg_2_rad(lat_0), deg_2_rad(lon_0)
        )
        lat = rad_2_deg(lat)
        lon = rad_2_deg(lon)
        if globe.is_land(lat, lon):
            return True
    return False
