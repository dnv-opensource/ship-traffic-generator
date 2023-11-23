"""
This module includes functions to prepare and plot traffic situations
"""
import math

from matplotlib.patches import Circle
from folium import Map, Polygon
import numpy as np
import matplotlib.pyplot as plt

from . import knot_2_m_pr_min
from . import m2nm
from . import flat2llh
from . import deg_2_rad
from . import rad_2_deg


def calculate_vector_arrow(position, direction, vector_length, lat_lon_0):
    """
    Calculates the arrow with length vector pointing in the direction of ship course

    Params:
        position: {north}, {east} position of the ship [m]
        direction: direction the arrow is pointing [deg]
        vector_length: length of vector
        lat_lon_0: Reference point, latitudinal [degree] and longitudinal [degree]

    Returns:
        arrow_points: Polygon points to draw the arrow
    """
    north_start = position["north"]
    east_start = position["east"]

    side_length = vector_length / 10
    sides_angle = 25

    north_end = north_start + vector_length * np.cos(deg_2_rad(direction))
    east_end = east_start + vector_length * np.sin(deg_2_rad(direction))

    north_arrow_side_1 = north_end + side_length * np.cos(deg_2_rad(direction + 180 - sides_angle))
    east_arrow_side_1 = east_end + side_length * np.sin(deg_2_rad(direction + 180 - sides_angle))
    north_arrow_side_2 = north_end + side_length * np.cos(deg_2_rad(direction + 180 + sides_angle))
    east_arrow_side_2 = east_end + side_length * np.sin(deg_2_rad(direction + 180 + sides_angle))

    lat_start, lon_start, _ = flat2llh(
        north_start, east_start, deg_2_rad(lat_lon_0[0]), deg_2_rad(lat_lon_0[1])
    )
    lat_end, lon_end, _ = flat2llh(north_end, east_end, deg_2_rad(lat_lon_0[0]), deg_2_rad(lat_lon_0[1]))
    lat_arrow_side_1, lon_arrow_side_1, _ = flat2llh(
        north_arrow_side_1, east_arrow_side_1, deg_2_rad(lat_lon_0[0]), deg_2_rad(lat_lon_0[1])
    )
    lat_arrow_side_2, lon_arrow_side_2, _ = flat2llh(
        north_arrow_side_2, east_arrow_side_2, deg_2_rad(lat_lon_0[0]), deg_2_rad(lat_lon_0[1])
    )

    point_1 = (rad_2_deg(lat_start), rad_2_deg(lon_start))
    point_2 = (rad_2_deg(lat_end), rad_2_deg(lon_end))
    point_3 = (rad_2_deg(lat_arrow_side_1), rad_2_deg(lon_arrow_side_1))
    point_4 = (rad_2_deg(lat_arrow_side_2), rad_2_deg(lon_arrow_side_2))

    return [point_1, point_2, point_3, point_4, point_2]


def calculate_ship_outline(position, course, lat_lon_0, ship_length=100, ship_width=15):
    """
    Calculates the outline of the ship pointing in the direction of ship course

    Params:
        position: {north}, {east} position of the ship [m]
        course: course of the ship [deg]
        lat_lon_0: Reference point, latitudinal [degree] and longitudinal [degree]
        ship_length: Ship length. If not given, ship length is set to 100
        ship_width: Ship width. If not given, ship width is set to 15

    Returns:
        ship_outline_points: Polygon points to draw the ship
    """
    north_start = position["north"]
    east_start = position["east"]

    # increase size for visualizing
    ship_length = ship_length * 10
    ship_width = ship_width * 10

    north_pos1 = (
        north_start
        + np.cos(deg_2_rad(course)) * (-ship_length / 2)
        - np.sin(deg_2_rad(course)) * ship_width / 2
    )
    east_pos1 = (
        east_start
        + np.sin(deg_2_rad(course)) * (-ship_length / 2)
        + np.cos(deg_2_rad(course)) * ship_width / 2
    )
    lat_pos1, lon_pos1, _ = flat2llh(
        north_pos1, east_pos1, deg_2_rad(lat_lon_0[0]), deg_2_rad(lat_lon_0[1])
    )

    north_pos2 = (
        north_start
        + np.cos(deg_2_rad(course)) * (ship_length / 2 - ship_length * 0.1)
        - np.sin(deg_2_rad(course)) * ship_width / 2
    )
    east_pos2 = (
        east_start
        + np.sin(deg_2_rad(course)) * (ship_length / 2 - ship_length * 0.1)
        + np.cos(deg_2_rad(course)) * ship_width / 2
    )
    lat_pos2, lon_pos2, _ = flat2llh(
        north_pos2, east_pos2, deg_2_rad(lat_lon_0[0]), deg_2_rad(lat_lon_0[1])
    )

    north_pos3 = north_start + np.cos(deg_2_rad(course)) * (ship_length / 2)
    east_pos3 = east_start + np.sin(deg_2_rad(course)) * (ship_length / 2)
    lat_pos3, lon_pos3, _ = flat2llh(
        north_pos3, east_pos3, deg_2_rad(lat_lon_0[0]), deg_2_rad(lat_lon_0[1])
    )

    north_pos4 = (
        north_start
        + np.cos(deg_2_rad(course)) * (ship_length / 2 - ship_length * 0.1)
        - np.sin(deg_2_rad(course)) * (-ship_width / 2)
    )
    east_pos4 = (
        east_start
        + np.sin(deg_2_rad(course)) * (ship_length / 2 - ship_length * 0.1)
        + np.cos(deg_2_rad(course)) * (-ship_width / 2)
    )
    lat_pos4, lon_pos4, _ = flat2llh(
        north_pos4, east_pos4, deg_2_rad(lat_lon_0[0]), deg_2_rad(lat_lon_0[1])
    )

    north_pos5 = (
        north_start
        + np.cos(deg_2_rad(course)) * (-ship_length / 2)
        - np.sin(deg_2_rad(course)) * (-ship_width / 2)
    )
    east_pos5 = (
        east_start
        + np.sin(deg_2_rad(course)) * (-ship_length / 2)
        + np.cos(deg_2_rad(course)) * (-ship_width / 2)
    )
    lat_pos5, lon_pos5, _ = flat2llh(
        north_pos5, east_pos5, deg_2_rad(lat_lon_0[0]), deg_2_rad(lat_lon_0[1])
    )

    point_1 = (rad_2_deg(lat_pos1), rad_2_deg(lon_pos1))
    point_2 = (rad_2_deg(lat_pos2), rad_2_deg(lon_pos2))
    point_3 = (rad_2_deg(lat_pos3), rad_2_deg(lon_pos3))
    point_4 = (rad_2_deg(lat_pos4), rad_2_deg(lon_pos4))
    point_5 = (rad_2_deg(lat_pos5), rad_2_deg(lon_pos5))

    return [point_1, point_2, point_3, point_4, point_5, point_1]


def plot_specific_traffic_situation(traffic_situations, situation_number):
    """
    Plots a specific situation in map

    Params:
        traffic_situations: Generated traffic situations
        situation_number: The specific situation to be plotted
    """

    num_situations = len(traffic_situations)
    if situation_number > num_situations:
        situation_number = num_situations
        print(
            f"Situation_number specified higher than number of situations available, plotting last situation: {num_situations}"
        )  # noqa: E501

    lat_lon_0 = traffic_situations[situation_number - 1]["lat_lon_0"]
    map_plot = Map(location=(lat_lon_0[0], lat_lon_0[1]), zoom_start=10)
    map_plot = add_ship_to_map(
        traffic_situations[situation_number - 1]["own_ship"],
        traffic_situations[situation_number - 1]["common_vector"],
        lat_lon_0,
        map_plot,
        "black",
    )

    for target_ship in traffic_situations[situation_number - 1]["target_ship"]:
        map_plot = add_ship_to_map(
            target_ship,
            traffic_situations[situation_number - 1]["common_vector"],
            lat_lon_0,
            map_plot,
            "red",
        )
    map_plot.show_in_browser()


def add_ship_to_map(ship, vector_time, lat_lon_0, map_plot=None, color="black"):
    """
    Adds the ship to the map

    Params:
        ship: Ship information
        vector_time: Vector time [min]
        lat_lon_0=Reference point, latitudinal [degree] and longitudinal [degree]
        m: Instance of Map. If not set, instance is set to None
        color: Color of the ship. If not set, color is 'black'

    Returns
        m: Updated instance of Map.
    """
    if map_plot is None:
        map_plot = Map(location=(lat_lon_0[0], lat_lon_0[1]), zoom_start=10)

    vector_length = vector_time * knot_2_m_pr_min(ship["start_pose"]["speed"])
    map_plot.add_child(
        Polygon(
            calculate_vector_arrow(
                ship["start_pose"]["position"], ship["start_pose"]["course"], vector_length, lat_lon_0
            ),
            fill=True,
            fill_opacity=1,
            color=color,
        )
    )
    map_plot.add_child(
        Polygon(
            calculate_ship_outline(
                ship["start_pose"]["position"], ship["start_pose"]["course"], lat_lon_0
            ),
            fill=True,
            fill_opacity=1,
            color=color,
        )
    )
    return map_plot


def plot_traffic_situations(traffic_situations, col, row):
    """
    Plots the traffic situations in one more figures

    Params:
        traffic_situations: Traffic situations to be plotted
        col: Number of columns in each figure
        row: Number of rows in each figure
    """
    num_situations = len(traffic_situations)
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
    max_value = 0
    for i in range(num_situations):
        max_value = find_max_value_for_plot(traffic_situations[i]["own_ship"], max_value)
        for j in range(len(traffic_situations[i]["target_ship"])):
            max_value = find_max_value_for_plot(traffic_situations[i]["target_ship"][j], max_value)

    plot_number = 1
    plt.figure(plot_number)
    for i in range(num_situations):
        if math.floor(i / num_subplots_pr_plot) + 1 > plot_number:
            plot_number += 1
            plt.figure(plot_number)

        axes = plt.subplot(
            max_rows,
            max_columns,
            int(1 + i - (plot_number - 1) * num_subplots_pr_plot),
            xlabel="[nm]",
            ylabel="[nm]",
        )
        axes.set_title(traffic_situations[i]["title"])
        axes = add_ship_to_plot(
            traffic_situations[i]["own_ship"], traffic_situations[i]["common_vector"], axes, "black"
        )
        for j in range(len(traffic_situations[i]["target_ship"])):
            axes = add_ship_to_plot(
                traffic_situations[i]["target_ship"][j],
                traffic_situations[i]["common_vector"],
                axes,
                "red",
            )
        axes.set_aspect("equal")

        plt.xlim(-max_value, max_value)
        plt.ylim(-max_value, max_value)
        plt.subplots_adjust(wspace=0.4, hspace=0.4)

    plt.show()


def find_max_value_for_plot(ship, max_value):
    """
    Finds the maximum deviation from the Reference point in north and east direction

    Params:
        ship: Ship information
        max_value: maximum deviation in north, east direction

    Returns:
        max_value: updated maximum deviation in north, east direction
    """
    max_value = np.max(
        [
            max_value,
            np.abs(m2nm(ship["start_pose"]["position"]["north"])),
            np.abs(m2nm(ship["start_pose"]["position"]["east"])),
        ]
    )
    return max_value


def add_ship_to_plot(ship, vector_time, axes=None, color="black"):
    """
    Adds the ship to the plot

    Params:
        ship: Ship information
        vector_time: Vector time [min]
        ax: Instance of figure axis. If not set, instance is set to None
        color: Color of the ship. If not set, color is 'black'
    """
    if axes is None:
        axes = plt.gca()

    pos_0_north = m2nm(ship["start_pose"]["position"]["north"])
    pos_0_east = m2nm(ship["start_pose"]["position"]["east"])
    course = ship["start_pose"]["course"]
    speed = ship["start_pose"]["speed"]

    vector_length = m2nm(vector_time * knot_2_m_pr_min(speed))

    axes.arrow(
        pos_0_east,
        pos_0_north,
        vector_length * np.sin(deg_2_rad(course)),
        vector_length * np.cos(deg_2_rad(course)),
        edgecolor=color,
        facecolor=color,
        width=0.0001,
        head_length=0.2,
        head_width=0.2,
        length_includes_head=True,
    )
    circle = Circle((pos_0_east, pos_0_north), vector_time / 100, color=color)
    axes.add_patch(circle)
    return axes
