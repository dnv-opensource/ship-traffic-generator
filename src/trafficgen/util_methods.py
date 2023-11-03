"""This module includes utillities methods that is used by several other functions."""

import numpy as np


def m_pr_min_2_knot(speed_in_m_pr_min):
    """
    Convert ship speed in meters pr minutes to knot.

    Params:
        speed_in_m_pr_min: Ship speed in meters pr second

    Returns:
        speed_in_knot: Ship speed given in knots
    """

    knot_2_m_pr_sec = 0.5144
    return speed_in_m_pr_min/(knot_2_m_pr_sec * 60)


def knot_2_m_pr_min(speed_in_knot):
    """
    Convert ship speed in knot to meters pr minutes.

    Params:
        speed_in_knot: Ship speed given in knots

    Returns:
        speed_in_m_pr_min: Ship speed in meters pr minutes
    """

    knot_2_m_pr_sec = 0.5144
    return speed_in_knot * knot_2_m_pr_sec * 60


def m2nm(length_in_m):
    """
    Convert length given in meters to length given in nautical miles.

    Params:
        length_in_m: Length given in meters

    Returns:
        length_in_nm: Length given in nautical miles
    """

    m_2_nm = 1/1852
    return m_2_nm * length_in_m


def nm_2_m(val):
    """
    Convert length given in nautical miles to length given in meters.

    Params:
        length_in_nm: Length given in nautical miles

    Returns:
        length_in_m: Length given in meters
    """

    nm_2_m_factor = 1852
    return val * nm_2_m_factor


def deg_2_rad(angle_in_degrees):
    """
    Convert angle given in degrees to angle give in radians.

    Params:
        angle_in_degrees: Angle given in degrees

    Returns:
        angle given in radians: Angle given in radians
    """

    return angle_in_degrees * np.pi / 180


def rad_2_deg(angle_in_radians):
    """
    Convert angle given in radians to angle give in degrees.

    Params:
        angle_in_degrees: Angle given in degrees

    Returns:
        angle given in radians: Angle given in radians

    """

    return angle_in_radians * 180 / np.pi


def convert_angle_minus_180_to_180_to_0_to_360(angle_180):
    """
    Convert an angle given in the region -180 to 180 degrees to an
    angle given in the region 0 to 360 degrees

    Params:
        angle_180: Angle given in the region -180 to 180 degrees

    Returns:
        angle_360: Angle given in the region 0 to 360 degrees

    """

    return angle_180 if angle_180 >= 0 else angle_180 + 360


def convert_angle_0_to_360_to_minus_180_to_180(angle_360):
    """
    Convert an angle given in the region 0 to 360 degrees to an
    angle given in the region -180 to 180 degrees

    Params:
        angle_360: Angle given in the region 0 to 360 degrees

    Returns:
        angle_180: Angle given in the region -180 to 180 degrees

    """

    return angle_360 if (angle_360 >= 0) & (angle_360 <= 180) else angle_360 - 360


def calculate_position_at_certain_time(position, speed, course, delta_time):
    """
    Calculates the position of the ship at a given time based on initial position
    and delta time, and constand speed and course.

    Params:
        position: Initial ship position [m]
        speed: Ship speed [knot]
        course: Ship course [deg]
        delta_time: Delta time from now to the time new position is being calculated [minutes]

    Returns:
        position{north, east}: Dict, north and east position given in meters

    """

    north = position['north'] + knot_2_m_pr_min(speed) * delta_time * np.cos(deg_2_rad(course))
    east = position['east'] + knot_2_m_pr_min(speed) * delta_time * np.sin(deg_2_rad(course))
    return {'north': north, 'east': east}
