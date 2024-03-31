"""Utility functions that are used by several other functions."""

from typing import List

import numpy as np
from maritime_schema.types.caga import Position

from trafficgen.marine_system_simulator import flat2llh, llh2flat


def knot_2_m_pr_s(speed_in_knot: float) -> float:
    """
    Convert ship speed in knots to meters pr second.

    Params:
        * speed_in_knot: Ship speed given in knots

    Returns
    -------
        * speed_in_m_pr_s: Ship speed in meters pr second
    """

    knot_2_m_pr_sec: float = 0.5144
    return speed_in_knot * knot_2_m_pr_sec


def min_2_s(time_in_min: float) -> float:
    """
    Convert time given in minutes to time given in seconds.

    Params:
        * time_in_min: Time given in minutes

    Returns
    -------
        * time_in_s: Time in seconds
    """

    min_2_s_coeff: float = 60.0
    return time_in_min * min_2_s_coeff


def m_2_nm(length_in_m: float) -> float:
    """
    Convert length given in meters to length given in nautical miles.

    Params:
        * length_in_m: Length given in meters

    Returns
    -------
        * length_in_nm: Length given in nautical miles
    """

    m_2_nm_coeff: float = 1.0 / 1852.0
    return m_2_nm_coeff * length_in_m


def nm_2_m(length_in_nm: float) -> float:
    """
    Convert length given in nautical miles to length given in meters.

    Params:
        * length_in_nm: Length given in nautical miles

    Returns
    -------
        * length_in_m: Length given in meters
    """

    nm_2_m_factor: float = 1852.0
    return length_in_nm * nm_2_m_factor


def deg_2_rad(angle_in_degrees: float) -> float:
    """
    Convert angle given in degrees to angle give in radians.

    Params:
        * angle_in_degrees: Angle given in degrees

    Returns
    -------
        * angle given in radians: Angle given in radians
    """

    return angle_in_degrees * np.pi / 180.0


def rad_2_deg(angle_in_radians: float) -> float:
    """
    Convert angle given in radians to angle give in degrees.

    Params:
        * angle_in_degrees: Angle given in degrees

    Returns
    -------
        * angle given in radians: Angle given in radians

    """

    return angle_in_radians * 180.0 / np.pi


def convert_angle_minus_pi_to_pi_to_0_to_2_pi(angle_pi: float) -> float:
    """
    Convert an angle given in the region -pi to pi degrees to an
    angle given in the region 0 to 2pi radians.

    Params:
        * angle_pi: Angle given in the region -pi to pi radians

    Returns
    -------
        * angle_2_pi: Angle given in the region 0 to 2pi radians

    """

    return angle_pi if angle_pi >= 0.0 else angle_pi + 2 * np.pi


def convert_angle_0_to_2_pi_to_minus_pi_to_pi(angle_2_pi: float) -> float:
    """
    Convert an angle given in the region 0 to 2*pi degrees to an
    angle given in the region -pi to pi degrees.

    Params:
        * angle_2_pi: Angle given in the region 0 to 2pi radians

    Returns
    -------
        * angle_pi: Angle given in the region -pi to pi radians

    """

    return angle_2_pi if (angle_2_pi >= 0.0) & (angle_2_pi <= np.pi) else angle_2_pi - 2 * np.pi


def calculate_position_at_certain_time(
    position: Position,
    lat_lon0: Position,
    speed: float,
    course: float,
    delta_time: float,
) -> Position:
    """
    Calculate the position of the ship at a given time based on initial position
    and delta time, and constant speed and course.

    Params:
        * position{latitude, longitude}: Initial ship position [rad]
        * speed: Ship speed [m/s]
        * course: Ship course [rad]
        * delta_time: Delta time from now to the time new position is being calculated [minutes]

    Returns
    -------
        * position{latitude, longitude}: Estimated ship position in delta time minutes [rad]
    """

    north, east, _ = llh2flat(
        position.latitude, position.longitude, lat_lon0.latitude, lat_lon0.longitude
    )

    north = north + speed * delta_time * np.cos(course)
    east = east + speed * delta_time * np.sin(course)

    lat_future, lon_future, _ = flat2llh(north, east, lat_lon0.latitude, lat_lon0.longitude)

    position_future: Position = Position(
        latitude=lat_future,
        longitude=lon_future,
    )
    return position_future
