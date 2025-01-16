"""Module with helper functions to determine if a generated path is crossing land."""

from global_land_mask import globe

from trafficgen.types import GeoPosition
from trafficgen.utils import calculate_position_at_certain_time, rad_2_deg


def path_crosses_land(
    position_1: GeoPosition,
    speed: float,
    course: float,
    lat_lon0: GeoPosition,
    time_interval: float = 300.0,
) -> bool:
    """
    Find if path is crossing land.

    Params:
        position_1: Ship position in lat/lon [rad].
        speed: Ship speed [m/s].
        course: Ship course [rad].
        lat_lon0: Reference point, latitudinal [rad] and longitudinal [rad].
        time_interval: The time interval the vessel should travel without crossing land [sec]

    Returns
    -------
        is_on_land: True if parts of the path crosses land.
    """
    num_checks = 10
    for i in range(int(time_interval / num_checks)):
        position_2 = calculate_position_at_certain_time(
            GeoPosition(lat=position_1.lat, lon=position_1.lon),
            lat_lon0,
            speed,
            course,
            i * time_interval / num_checks,
        )

        lat = rad_2_deg(position_2.lat)
        lon = rad_2_deg(position_2.lon)
        if globe.is_land(lat, lon):  # type: ignore  # noqa: PGH003
            return True
    return False
