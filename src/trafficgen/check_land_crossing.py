"""Module with helper functions to determine if a generated path is crossing land."""

from global_land_mask import globe
from maritime_schema.types.caga import Position

from trafficgen.utils import calculate_position_at_certain_time, rad_2_deg


def path_crosses_land(
    position_1: Position,
    speed: float,
    course: float,
    lat_lon0: Position,
    time_interval: float = 300.0,
) -> bool:
    """
    Find if path is crossing land.

    Params:
        position_1: Ship position in latitude/longitude [rad].
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
            Position(latitude=position_1.latitude, longitude=position_1.longitude),
            lat_lon0,
            speed,
            course,
            i * time_interval / num_checks,
        )

        lat = rad_2_deg(position_2.latitude)
        lon = rad_2_deg(position_2.longitude)
        if globe.is_land(lat, lon):  # type: ignore  (The global_land_mask package is unfortunately not typed.)
            return True
    return False
