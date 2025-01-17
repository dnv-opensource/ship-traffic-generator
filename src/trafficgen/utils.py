"""Utility functions that are used by several other functions."""

import numpy as np

from trafficgen.marine_system_simulator import flat2llh, llh2flat
from trafficgen.types import GeoPosition, Waypoint


def knot_2_m_pr_s(speed_in_knot: float) -> float:
    """
    Convert ship speed in knots to meters pr second.

    Parameters
    ----------
    speed_in_knot : float
        Ship speed given in knots

    Returns
    -------
    speed_in_m_pr_s : float
        Ship speed in meters pr second
    """
    knot_2_m_pr_sec: float = 0.5144
    return speed_in_knot * knot_2_m_pr_sec


def m_pr_s_2_knot(speed_in_m_pr_s: float) -> float:
    """
    Convert ship speed in knots to meters pr second.

    Parameters
    ----------
    speed_in_m_pr_s : float
        Ship speed given in meters pr second

    Returns
    -------
    speed_in_knot : float
    Ship speed in knots
    """
    knot_2_m_pr_sec: float = 0.5144
    return speed_in_m_pr_s / knot_2_m_pr_sec


def min_2_s(time_in_min: float) -> float:
    """
    Convert time given in minutes to time given in seconds.

    Parameters
    ----------
    time_in_min : float
        Time given in minutes

    Returns
    -------
    time_in_s : float
        Time in seconds
    """
    min_2_s_coeff: float = 60.0
    return time_in_min * min_2_s_coeff


def m_2_nm(length_in_m: float) -> float:
    """
    Convert length given in meters to length given in nautical miles.

    Parameters
    ----------
    length_in_m : float
        Length given in meters

    Returns
    -------
    length_in_nm : float
        Length given in nautical miles
    """
    m_2_nm_coeff: float = 1.0 / 1852.0
    return m_2_nm_coeff * length_in_m


def nm_2_m(length_in_nm: float) -> float:
    """
    Convert length given in nautical miles to length given in meters.

    Parameters
    ----------
    length_in_nm : float
        Length given in nautical miles

    Returns
    -------
    length_in_m : float
        Length given in meters
    """
    nm_2_m_factor: float = 1852.0
    return length_in_nm * nm_2_m_factor


def deg_2_rad(angle_in_degrees: float) -> float:
    """
    Convert angle given in degrees to angle give in radians.

    Parameters
    ----------
    angle_in_degrees : float
        Angle given in degrees

    Returns
    -------
    angle_in_radians : float
        Angle given in radians
    """
    return angle_in_degrees * np.pi / 180.0


def rad_2_deg(angle_in_radians: float) -> float:
    """
    Convert angle given in radians to angle give in degrees.

    Parameters
    ----------
    angle_in_degrees : float
        Angle given in degrees

    Returns
    -------
    angle_in_radians : float
        Angle given in radians
    """
    return angle_in_radians * 180.0 / np.pi


def convert_angle_minus_pi_to_pi_to_0_to_2_pi(angle_pi: float) -> float:
    """
    Angle conversion functions.

    Convert an angle given in the region -pi to pi degrees to an
    angle given in the region 0 to 2pi radians.

    Parameters
    ----------
    angle_pi : float
        Angle given in the region -pi to pi radians

    Returns
    -------
    angle_2_pi : float
        Angle given in the region 0 to 2pi radians

    """
    return angle_pi if angle_pi >= 0.0 else angle_pi + 2 * np.pi


def convert_angle_0_to_2_pi_to_minus_pi_to_pi(angle_2_pi: float) -> float:
    """
    Angle conversion functions.

    Convert an angle given in the region 0 to 2*pi degrees to an
    angle given in the region -pi to pi degrees.

    Parameters
    ----------
    angle_2_pi : float
        Angle given in the region 0 to 2pi radians

    Returns
    -------
    angle_pi : float
        Angle given in the region -pi to pi radians

    """
    return angle_2_pi if (angle_2_pi >= 0.0) & (angle_2_pi <= np.pi) else angle_2_pi - 2 * np.pi


def calculate_position_at_certain_time(
    position: GeoPosition,
    lat_lon0: GeoPosition,
    sog: float,
    cog: float,
    delta_time: float,
) -> GeoPosition:
    """
    Calculate the position of the ship at a given time.

    The calculated position is based on initial position and delta time, in addition to constant speed and course.

    Parameters
    ----------
    position : GeoPosition
        Initial ship position {lat, lon} [rad]
    lat_lon0 : GeoPosition
        Reference position {lat, lon} [rad]
    sog : float
        Ship speed over ground[m/s]
    cog : float
        Ship course over ground [rad]
    delta_time : float
        Delta time from now to the time new position is being calculated [minutes]

    Returns
    -------
    position : GeoPosition
        Estimated ship position in delta time minutes {lat, lon} [rad]
    """
    north, east, _ = llh2flat(position.lat, position.lon, lat_lon0.lat, lat_lon0.lon)

    north = north + sog * delta_time * np.cos(cog)
    east = east + sog * delta_time * np.sin(cog)

    lat_future, lon_future, _ = flat2llh(north, east, lat_lon0.lat, lat_lon0.lon)

    position_future: GeoPosition = GeoPosition(
        lat=lat_future,
        lon=lon_future,
    )
    return position_future


def calculate_distance(position_prev: GeoPosition, position_next: GeoPosition) -> float:
    """
    Calculate the distance in meter between two waypoints.

    Parameters
    ----------
    position_prev : GeoPosition
        Previous waypoint {lat, lon}[rad]
    position_next : GeoPosition
        Next waypoint {lat, lon}[rad]

    Returns
    -------
    distance : float
        Distance between waypoints [m]
    """
    # Using position of previous waypoint as reference point
    north_next, east_next, _ = llh2flat(position_next.lat, position_next.lon, position_prev.lat, position_prev.lon)

    distance: float = np.sqrt(north_next**2 + east_next**2)

    return distance


def calculate_position_along_track_using_waypoints(
    waypoints: list[Waypoint],
    inital_speed: float,
    vector_time: float,
) -> GeoPosition:
    """
    Calculate the position along the track using waypoints.

    The position along the track is calculated based on initial position
    and delta time, and constant speed and course.

    Parameters
    ----------
    waypoints: list[Waypoint]
        List of ship waypoints Initial ship position {lat, lon}[rad]
    inital_speed : float
        Initial ship speed [m/s]
    vector_time : float
        Delta time from now to the time new position is being calculated [sec]

    Returns
    -------
    position : GeoPosition
        Estimated ship position in delta time seconds {lat, lon}[rad]
    """
    time_in_transit: float = 0

    for i in range(1, len(waypoints)):
        ship_speed: float = inital_speed
        waypoint: Waypoint = waypoints[i]
        if waypoint.leg is not None and waypoint.leg.data is not None and waypoint.leg.data.sog is not None:
            assert waypoint.leg.data.sog.value is not None
            ship_speed = waypoint.leg.data.sog.value

        dist_between_waypoints = calculate_distance(waypoints[i - 1].position, waypoints[i].position)

        # find distance ship will travel
        dist_travel = ship_speed * (vector_time - time_in_transit)

        if dist_travel > dist_between_waypoints:
            time_in_transit = time_in_transit + dist_between_waypoints / ship_speed
        else:
            bearing = calculate_bearing_between_waypoints(waypoints[i - 1].position, waypoints[i].position)
            position_along_track = calculate_destination_along_track(waypoints[i - 1].position, dist_travel, bearing)
            return position_along_track

    # if ship reach last waypoint in less time than vector_time, last waypoint is used
    return waypoints[-1].position


def calculate_bearing_between_waypoints(position_prev: GeoPosition, position_next: GeoPosition) -> float:
    """Calculate the bearing in rad between two waypoints.

    Parameters
    ----------
    position_prev : GeoPosition
        Previous waypoint {lat, lon}[rad]
    position_next : GeoPosition
        Next waypoint {lat, lon}[rad]

    Returns
    -------
    bearing : float
        Bearing between waypoints [rad]
    """
    # Using position of previous waypoint as reference point
    north_next, east_next, _ = llh2flat(position_next.lat, position_next.lon, position_prev.lat, position_prev.lon)

    bearing: float = convert_angle_minus_pi_to_pi_to_0_to_2_pi(np.arctan2(east_next, north_next))

    return bearing


def calculate_destination_along_track(position_prev: GeoPosition, distance: float, bearing: float) -> GeoPosition:
    """
    Calculate the destination along the track between two waypoints when distance along the track is given.

    Parameters
    ----------
    position_prev : GeoPosition
        Previous waypoint {lat, lon}[rad]
    distance : float
        Distance to travel [m]
    bearing : float
        Bearing from previous waypoint to next waypoint [rad]

    Returns
    -------
    destination : GeoPosition
        Destination along the track {lat, lon}[rad]
    """
    north = distance * np.cos(bearing)
    east = distance * np.sin(bearing)

    lat, lon, _ = flat2llh(north, east, position_prev.lat, position_prev.lon)
    destination = GeoPosition(lat=lat, lon=lon)

    return destination
