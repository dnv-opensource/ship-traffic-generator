# The matplotlib package is unfortunately not fully typed. Hence the following pyright exemption.
# pyright: reportUnknownMemberType=false
"""Functions to prepare and plot traffic situations."""

import math
from typing import List, Optional, Tuple, Union

import matplotlib.pyplot as plt
import numpy as np
from folium import Map, Polygon
from matplotlib.axes import Axes as Axes
from matplotlib.patches import Circle

from trafficgen.marine_system_simulator import flat2llh, llh2flat
from trafficgen.types import EncounterSettings, GeoPosition, Ship, TargetShip, TrafficSituation
from trafficgen.utils import m_2_nm, rad_2_deg


def calculate_vector_arrow(
    position: GeoPosition,
    direction: float,
    vector_length: float,
    lat_lon0: GeoPosition,
) -> List[Tuple[float, float]]:
    """
    Calculate the arrow with length vector pointing in the direction of ship course.

    Params:
        * position: {lat}, {lon} position of the ship [rad]
        * direction: direction the arrow is pointing [rad]
        * vector_length: length of vector [m]
        * lat_lon0: Reference point, latitudinal [rad] and longitudinal [rad]

    Returns
    -------
        * arrow_points: Polygon points to draw the arrow [deg]
    """
    north_start, east_start, _ = llh2flat(position.lat, position.lon, lat_lon0.lat, lat_lon0.lon)

    side_length = vector_length / 10
    sides_angle = 25

    north_end = north_start + vector_length * np.cos(direction)
    east_end = east_start + vector_length * np.sin(direction)

    north_arrow_side_1 = north_end + side_length * np.cos(direction + np.pi - sides_angle)
    east_arrow_side_1 = east_end + side_length * np.sin(direction + np.pi - sides_angle)
    north_arrow_side_2 = north_end + side_length * np.cos(direction + np.pi + sides_angle)
    east_arrow_side_2 = east_end + side_length * np.sin(direction + np.pi + sides_angle)

    lat_start, lon_start, _ = flat2llh(north_start, east_start, lat_lon0.lat, lat_lon0.lon)
    lat_end, lon_end, _ = flat2llh(north_end, east_end, lat_lon0.lat, lat_lon0.lon)
    lat_arrow_side_1, lon_arrow_side_1, _ = flat2llh(
        north_arrow_side_1, east_arrow_side_1, lat_lon0.lat, lat_lon0.lon
    )
    lat_arrow_side_2, lon_arrow_side_2, _ = flat2llh(
        north_arrow_side_2, east_arrow_side_2, lat_lon0.lat, lat_lon0.lon
    )

    point_1 = (rad_2_deg(lat_start), rad_2_deg(lon_start))
    point_2 = (rad_2_deg(lat_end), rad_2_deg(lon_end))
    point_3 = (rad_2_deg(lat_arrow_side_1), rad_2_deg(lon_arrow_side_1))
    point_4 = (rad_2_deg(lat_arrow_side_2), rad_2_deg(lon_arrow_side_2))

    return [point_1, point_2, point_3, point_4, point_2]


def calculate_ship_outline(
    position: GeoPosition,
    course: float,
    lat_lon0: GeoPosition,
    ship_length: float = 100.0,
    ship_width: float = 15.0,
) -> List[Tuple[float, float]]:
    """
    Calculate the outline of the ship pointing in the direction of ship course.

    Params:
        * position: {lat}, {lon} position of the ship [rad]
        * course: course of the ship [rad]
        * lat_lon0: Reference point, latitudinal [rad] and longitudinal [rad]
        * ship_length: Ship length. If not given, ship length is set to 100
        * ship_width: Ship width. If not given, ship width is set to 15

    Returns
    -------
        * ship_outline_points: Polygon points to draw the ship [deg]
    """
    north_start, east_start, _ = llh2flat(position.lat, position.lon, lat_lon0.lat, lat_lon0.lon)

    # increase size for visualizing
    ship_length *= 10
    ship_width *= 10

    north_pos1 = north_start + np.cos(course) * (-ship_length / 2) - np.sin(course) * ship_width / 2
    east_pos1 = east_start + np.sin(course) * (-ship_length / 2) + np.cos(course) * ship_width / 2
    lat_pos1, lon_pos1, _ = flat2llh(north_pos1, east_pos1, lat_lon0.lat, lat_lon0.lon)

    north_pos2 = (
        north_start
        + np.cos(course) * (ship_length / 2 - ship_length * 0.1)
        - np.sin(course) * ship_width / 2
    )
    east_pos2 = (
        east_start
        + np.sin(course) * (ship_length / 2 - ship_length * 0.1)
        + np.cos(course) * ship_width / 2
    )
    lat_pos2, lon_pos2, _ = flat2llh(north_pos2, east_pos2, lat_lon0.lat, lat_lon0.lon)

    north_pos3 = north_start + np.cos(course) * (ship_length / 2)
    east_pos3 = east_start + np.sin(course) * (ship_length / 2)
    lat_pos3, lon_pos3, _ = flat2llh(north_pos3, east_pos3, lat_lon0.lat, lat_lon0.lon)

    north_pos4 = (
        north_start
        + np.cos(course) * (ship_length / 2 - ship_length * 0.1)
        - np.sin(course) * (-ship_width / 2)
    )
    east_pos4 = (
        east_start
        + np.sin(course) * (ship_length / 2 - ship_length * 0.1)
        + np.cos(course) * (-ship_width / 2)
    )
    lat_pos4, lon_pos4, _ = flat2llh(north_pos4, east_pos4, lat_lon0.lat, lat_lon0.lon)

    north_pos5 = north_start + np.cos(course) * (-ship_length / 2) - np.sin(course) * (-ship_width / 2)
    east_pos5 = east_start + np.sin(course) * (-ship_length / 2) + np.cos(course) * (-ship_width / 2)
    lat_pos5, lon_pos5, _ = flat2llh(north_pos5, east_pos5, lat_lon0.lat, lat_lon0.lon)

    point_1 = (rad_2_deg(lat_pos1), rad_2_deg(lon_pos1))
    point_2 = (rad_2_deg(lat_pos2), rad_2_deg(lon_pos2))
    point_3 = (rad_2_deg(lat_pos3), rad_2_deg(lon_pos3))
    point_4 = (rad_2_deg(lat_pos4), rad_2_deg(lon_pos4))
    point_5 = (rad_2_deg(lat_pos5), rad_2_deg(lon_pos5))

    return [point_1, point_2, point_3, point_4, point_5, point_1]


def plot_specific_traffic_situation(
    traffic_situations: List[TrafficSituation],
    situation_number: int,
    encounter_settings: EncounterSettings,
):
    """
    Plot a specific situation in map.

    Params:
        * traffic_situations: Generated traffic situations
        * situation_number: The specific situation to be plotted
    """

    num_situations = len(traffic_situations)
    if situation_number > num_situations:
        print(
            f"Situation_number specified higher than number of situations available, plotting last situation: {num_situations}"
        )
        situation_number = num_situations

    situation: TrafficSituation = traffic_situations[situation_number - 1]
    assert situation.own_ship is not None
    assert situation.own_ship.initial is not None
    assert encounter_settings.common_vector is not None

    lat_lon0 = situation.own_ship.initial.position

    map_plot = Map(location=(rad_2_deg(lat_lon0.lat), rad_2_deg(lat_lon0.lon)), zoom_start=10)
    map_plot = add_ship_to_map(
        situation.own_ship,
        encounter_settings.common_vector,
        lat_lon0,
        map_plot,
        "black",
    )

    target_ships: Union[List[TargetShip], None] = situation.target_ships
    assert target_ships is not None
    for target_ship in target_ships:
        map_plot = add_ship_to_map(
            target_ship,
            encounter_settings.common_vector,
            lat_lon0,
            map_plot,
            "red",
        )
    map_plot.show_in_browser()


def add_ship_to_map(
    ship: Ship,
    vector_time: float,
    lat_lon0: GeoPosition,
    map_plot: Optional[Map],
    color: str = "black",
) -> Map:
    """
    Add the ship to the map.

    Params:
        * ship: Ship information
        * vector_time: Vector time [sec]
        * lat_lon0=Reference point, latitudinal [rad] and longitudinal [rad]
        * map_plot: Instance of Map. If not set, instance is set to None
        * color: Color of the ship. If not set, color is 'black'

    Returns
    -------
        * m: Updated instance of Map.
    """
    if map_plot is None:
        map_plot = Map(location=(rad_2_deg(lat_lon0.lat), rad_2_deg(lat_lon0.lon)), zoom_start=10)

    assert ship.initial is not None
    vector_length = vector_time * ship.initial.sog
    _ = map_plot.add_child(
        Polygon(
            calculate_vector_arrow(ship.initial.position, ship.initial.cog, vector_length, lat_lon0),
            fill=True,
            fill_opacity=1,
            color=color,
        )
    )
    _ = map_plot.add_child(
        Polygon(
            calculate_ship_outline(ship.initial.position, ship.initial.cog, lat_lon0),
            fill=True,
            fill_opacity=1,
            color=color,
        )
    )
    return map_plot


def plot_traffic_situations(
    traffic_situations: List[TrafficSituation],
    col: int,
    row: int,
    encounter_settings: EncounterSettings,
):
    """
    Plot the traffic situations in one more figures.

    Params:
        * traffic_situations: Traffic situations to be plotted
        * col: Number of columns in each figure
        * row: Number of rows in each figure
    """
    max_columns = col
    max_rows = row
    num_subplots_pr_plot = max_columns * max_rows
    small_size = 6
    bigger_size = 10

    plt.rc("axes", titlesize=small_size)  # fontsize of the axes title
    plt.rc("axes", labelsize=small_size)  # fontsize of the x and y labels
    plt.rc("xtick", labelsize=small_size)  # fontsize of the tick labels
    plt.rc("ytick", labelsize=small_size)  # fontsize of the tick labels
    plt.rc("figure", titlesize=bigger_size)  # fontsize of the figure title

    # The axes should have the same x/y limits, thus find max value for
    # north/east position to be used for plotting
    max_value: float = 0.0
    for situation in traffic_situations:
        assert situation.own_ship is not None
        assert situation.own_ship.initial is not None
        lat_lon0 = situation.own_ship.initial.position
        max_value = find_max_value_for_plot(situation.own_ship, max_value, lat_lon0)
        assert situation.target_ships is not None
        for target_ship in situation.target_ships:
            max_value = find_max_value_for_plot(target_ship, max_value, lat_lon0)

    plot_number: int = 1
    _ = plt.figure(plot_number)
    for i, situation in enumerate(traffic_situations):
        if math.floor(i / num_subplots_pr_plot) + 1 > plot_number:
            plot_number += 1
            _ = plt.figure(plot_number)

        axes: Axes = plt.subplot(
            max_rows,
            max_columns,
            int(1 + i - (plot_number - 1) * num_subplots_pr_plot),
            xlabel="[nm]",
            ylabel="[nm]",
        )
        _ = axes.set_title(str(situation.title))
        assert situation.own_ship is not None
        assert situation.own_ship.initial
        assert encounter_settings.common_vector is not None
        lat_lon0 = situation.own_ship.initial.position
        axes = add_ship_to_plot(
            situation.own_ship,
            encounter_settings.common_vector,
            lat_lon0,
            axes,
            "black",
        )
        assert situation.target_ships is not None
        for target_ship in situation.target_ships:
            axes = add_ship_to_plot(
                target_ship,
                encounter_settings.common_vector,
                lat_lon0,
                axes,
                "red",
            )
        axes.set_aspect("equal")

        _ = plt.xlim(-max_value, max_value)
        _ = plt.ylim(-max_value, max_value)
        _ = plt.subplots_adjust(wspace=0.4, hspace=0.4)

    plt.show()


def find_max_value_for_plot(
    ship: Ship,
    max_value: float,
    lat_lon0: GeoPosition,
) -> float:
    """
    Find the maximum deviation from the Reference point in north and east direction.

    Params:
        * ship: Ship information
        * max_value: maximum deviation in north, east direction
        * lat_lon0: Reference point, latitudinal [rad] and longitudinal [rad]

    Returns
    -------
        * max_value: updated maximum deviation in north, east direction
    """
    assert ship.initial is not None

    north, east, _ = llh2flat(
        ship.initial.position.lat,
        ship.initial.position.lon,
        lat_lon0.lat,
        lat_lon0.lon,
    )
    max_value = np.max(
        [
            max_value,
            np.abs(m_2_nm(north)),
            np.abs(m_2_nm(east)),
        ]
    )
    return max_value


def add_ship_to_plot(
    ship: Ship,
    vector_time: float,
    lat_lon0: GeoPosition,
    axes: Optional[Axes],
    color: str = "black",
):
    """
    Add the ship to the plot.

    Params:
        * ship: Ship information
        * vector_time: Vector time [sec]
        * axes: Instance of figure axis. If not set, instance is set to None
        * color: Color of the ship. If not set, color is 'black'
    """
    if axes is None:
        axes = plt.gca()
    assert isinstance(axes, Axes)

    assert ship.initial is not None
    pos_0_north, pos_0_east, _ = llh2flat(
        ship.initial.position.lat,
        ship.initial.position.lon,
        lat_lon0.lat,
        lat_lon0.lon,
    )
    pos_0_north = m_2_nm(pos_0_north)
    pos_0_east = m_2_nm(pos_0_east)
    course = ship.initial.cog
    speed = ship.initial.sog

    vector_length = m_2_nm(vector_time * speed)

    _ = axes.arrow(
        pos_0_east,
        pos_0_north,
        vector_length * np.sin(course),
        vector_length * np.cos(course),
        edgecolor=color,
        facecolor=color,
        width=0.0001,
        head_length=0.2,
        head_width=0.2,
        length_includes_head=True,
    )
    circle = Circle(
        xy=(pos_0_east, pos_0_north),
        radius=vector_time / 3000.0,  # type: ignore
        color=color,
    )
    _ = axes.add_patch(circle)

    return axes
