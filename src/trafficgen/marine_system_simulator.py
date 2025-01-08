"""
The Marine Systems Simulator (MSS) is a Matlab and Simulink library for marine systems.

It includes models for ships, underwater vehicles, unmanned surface vehicles, and floating structures.
The library also contains guidance, navigation, and control (GNC) blocks for real-time simulation.
The algorithms are described in:

T. I. Fossen (2021). Handbook of Marine Craft Hydrodynamics and Motion Control. 2nd. Edition,
Wiley. ISBN-13: 978-1119575054

Parts of the library have been re-implemented in Python and are found below.
"""

import numpy as np


def flat2llh(
    x_n: float,
    y_n: float,
    lat_0: float,
    lon_0: float,
    z_n: float = 0.0,
    height_ref: float = 0.0,
) -> tuple[float, float, float]:
    """
    Compute lon lon (rad), lat lat (rad) and height h (m) for the NED coordinates (xn,yn,zn).

    Method taken from the MSS (Marine System Simulator) toolbox which is a Matlab/Simulink
    library for marine systems.

    The method computes lon lon (rad), lat lat (rad) and height h (m) for the
    NED coordinates (xn,yn,zn) using a flat Earth coordinate system defined by the WGS-84
    ellipsoid. The flat Earth coordinate origin is located  at (lon_0, lat_0) with reference
    height h_ref in meters above the surface of the ellipsoid. Both height and h_ref
    are positive upwards, while zn is positive downwards (NED).
    Author:    Thor I. Fossen
    Date:      20 July 2018
    Revisions: 2023-02-04 updates the formulas for lat and lon

    Params:
        * xn: Ship position, north [m]
        * yn: Ship position, east [m]
        * zn=0.0: Ship position, down [m]
        * lat_0, lon_0: Flat earth coordinate located at (lon_0, lat_0)
        * h_ref=0.0: Flat earth coordinate with reference h_ref in meters above the surface
          of the ellipsoid

    Returns
    -------
        * lat: lat [rad]
        * lon: lon [rad]
        * h: Height [m]

    """
    # WGS-84 parameters
    a_radius = 6378137  # Semi-major axis
    f_factor = 1 / 298.257223563  # Flattening
    e_eccentricity = np.sqrt(2 * f_factor - f_factor**2)  # Earth eccentricity

    r_n = a_radius / np.sqrt(1 - e_eccentricity**2 * np.sin(lat_0) ** 2)
    r_m = r_n * ((1 - e_eccentricity**2) / (1 - e_eccentricity**2 * np.sin(lat_0) ** 2))

    d_lat = x_n / (r_m + height_ref)  # delta lat dmu = mu - mu0
    d_lon = y_n / ((r_n + height_ref) * np.cos(lat_0))  # delta lon dl = l - l0

    lat = ssa(lat_0 + d_lat)
    lon = ssa(lon_0 + d_lon)
    height = height_ref - z_n

    return lat, lon, height


def llh2flat(
    lat: float,
    lon: float,
    lat_0: float,
    lon_0: float,
    height: float = 0.0,
    height_ref: float = 0.0,
) -> tuple[float, float, float]:
    """
    Compute (north, east) for a flat Earth coordinate system from lon lon (rad) and lat lat (rad).

    Method taken from the MSS (Marine System Simulator) toolbox which is a Matlab/Simulink
    library for marine systems.

    The method computes (north, east) for a flat Earth coordinate system from lon
    lon (rad) and lat lat (rad) of the WGS-84 elipsoid. The flat Earth coordinate
    origin is located  at (lon_0, lat_0).
    Author:    Thor I. Fossen
    Date:      20 July 2018
    Revisions: 2023-02-04 updates the formulas for lat and lon

    Params:
        * lat: Ship position in lat [rad]
        * lon: Ship position in lon [rad]
        * h=0.0: Ship height in meters above the surface of the ellipsoid
        * lat_0, lon_0: Flat earth coordinate located at (lon_0, lat_0)
        * h_ref=0.0: Flat earth coordinate with reference h_ref in meters above
          the surface of the ellipsoid

    Returns
    -------
        * x_n: Ship position, north [m]
        * y_n: Ship position, east [m]
        * z_n: Ship position, down [m]
    """
    # WGS-84 parameters
    a_radius = 6378137  # Semi-major axis (equitorial radius)
    f_factor = 1 / 298.257223563  # Flattening
    e_eccentricity = np.sqrt(2 * f_factor - f_factor**2)  # Earth eccentricity

    d_lon = lon - lon_0
    d_lat = lat - lat_0

    r_n = a_radius / np.sqrt(1 - e_eccentricity**2 * np.sin(lat_0) ** 2)
    r_m = r_n * ((1 - e_eccentricity**2) / (1 - e_eccentricity**2 * np.sin(lat_0) ** 2))

    x_n = d_lat * (r_m + height_ref)
    y_n = d_lon * ((r_n + height_ref) * np.cos(lat_0))
    z_n = height_ref - height

    return x_n, y_n, z_n


def ssa(angle: float) -> float:
    """
    Return the "smallest signed angle" (SSA) or the smallest difference between two angles.

    Method taken from the MSS (Marine System Simulator) toolbox which is a Matlab/Simulink
    library for marine systems.

    Examples
    --------
    angle = ssa(angle) maps an angle in rad to the interval [-pi pi)

    Author:     Thor I. Fossen
    Date:       2018-09-21

    Param:
        * angle: angle given in radius

    Returns
    -------
        * smallest_angle: "smallest signed angle" or the smallest difference between two angles
    """
    return np.mod(angle + np.pi, 2 * np.pi) - np.pi
