"""
Functions to generate encounters consisting of one own ship and one to many target ships.
The generated encounters may be of type head-on, overtaking give-way and stand-on and
crossing give-way and stand-on.
"""

import copy
import random

import numpy as np

from . import (
    calculate_position_at_certain_time,
    convert_angle_minus_180_to_180_to_0_to_360,
    deg_2_rad,
    flat2llh,
    knot_2_m_pr_min,
    m_pr_min_2_knot,
    nm_2_m,
    path_crosses_land,
    rad_2_deg,
)


def generate_encounter(
    desired_encounter_type,
    own_ship,
    target_ships,
    target_ship_id,
    beta_default,
    relative_speed_default,
    vector_time_default,
    settings,
):
    """
    Generate an encounter.

    Params:
        * desired_encounter_type: Desired encounter to be generated
        * own_ship: Dict, information about own ship that will encounter a target ship
        * target_ships: List of target ships that may be used in an encounter
        * target_ship_id: ID which should be used on target ship
        * beta_default: User defined beta. If not set, this is None.
        * relative_speed_default: User defined relative speed between own ship and
                                  target ship. If not set, this is None.
        * vector_time_default: User defined vector time. If not set, this is None.
        * settings: Encounter settings

    Returns
    -------
        target_ship: target ship information, such as initial position, speed and course
        encounter_found: 0=encounter not found, 1=encounter found
    """
    encounter_found = 0
    outer_counter = 0

    target_ship = decide_target_ship(target_ships)
    # Searching for encounter. Two loops used. Only vector time is locked in the
    # first loop. In the second loop, beta and speed are assigned.
    while encounter_found != 1 and outer_counter < 5:
        outer_counter += 1
        inner_counter = 0

        # resetting vector_time, beta and relative_speed to default values before
        # new search for situation is done
        vector_time = vector_time_default
        beta = beta_default

        if vector_time is None:
            vector_time = random.uniform(settings["vector_range"][0], settings["vector_range"][1])
        if beta is None:
            beta = assign_beta(desired_encounter_type, settings)

        # Own ship
        own_ship_position_future = calculate_position_at_certain_time(
            own_ship["start_pose"]["position"],
            own_ship["start_pose"]["speed"],
            own_ship["start_pose"]["course"],
            vector_time,
        )
        # @TODO: @TomArne: this variable is declared and assigned to but nowhere used.  Delete?
        #        Claas, 2023-11-24
        # own_ship_vector_length = knot_2_m_pr_min(own_ship["start_pose"]["speed"]) * vector_time

        # Target ship
        target_ship["id"] = target_ship_id
        target_ship["start_pose"] = {}
        target_ship_position_future = assign_future_position_to_target_ship(
            own_ship_position_future, settings["max_meeting_distance"]
        )

        while encounter_found != 1 and inner_counter < 5:
            inner_counter += 1
            relative_speed = relative_speed_default
            if relative_speed is None:
                min_target_ship_speed = m_pr_min_2_knot(
                    calculate_min_vector_length_target_ship(
                        own_ship["start_pose"]["position"],
                        own_ship["start_pose"]["course"],
                        target_ship_position_future,
                        beta,
                    )
                    / vector_time
                )

                target_ship["start_pose"]["speed"] = assign_speed_to_target_ship(
                    desired_encounter_type,
                    own_ship["start_pose"]["speed"],
                    min_target_ship_speed,
                    settings["relative_speed"],
                )
            else:
                target_ship["start_pose"]["speed"] = relative_speed * own_ship["start_pose"]["speed"]
            target_ship["start_pose"]["speed"] = np.minimum(
                target_ship["start_pose"]["speed"], target_ship["static"]["speed_max"]
            )

            target_ship_vector_length = knot_2_m_pr_min(target_ship["start_pose"]["speed"]) * vector_time
            start_position_target_ship, position_found = find_start_position_target_ship(
                own_ship["start_pose"]["position"],
                own_ship["start_pose"]["course"],
                target_ship_position_future,
                target_ship_vector_length,
                beta,
                desired_encounter_type,
                settings,
            )

            if position_found == 1:
                target_ship["start_pose"]["position"] = start_position_target_ship
                target_ship["start_pose"]["course"] = calculate_ship_course(
                    target_ship["start_pose"]["position"], target_ship_position_future
                )
                encounter_ok = check_encounter_evolvement(
                    own_ship,
                    own_ship_position_future,
                    target_ship,
                    target_ship_position_future,
                    desired_encounter_type,
                    settings,
                )

                # Check if trajectory passes land
                trajectory_on_land = path_crosses_land(
                    target_ship["start_pose"]["position"],
                    target_ship["start_pose"]["speed"],
                    target_ship["start_pose"]["course"],
                    settings["lat_lon_0"],
                )

                encounter_found = 1 if encounter_ok == 1 & ~trajectory_on_land else 0

    if encounter_found > 0.5:
        target_ship = update_position_data_target_ship(target_ship, settings["lat_lon_0"])
    return target_ship, encounter_found


def check_encounter_evolvement(
    own_ship,
    own_ship_position_future,
    target_ship,
    target_ship_position_future,
    desired_encounter_type,
    settings,
):
    """
    Check encounter evolvement. The generated encounter should be the same type of
    encounter (head-on, crossing, give-way) also some time before the encounter is started.

    Params:
        * own_ship: Own ship information such as initial position, speed and course
        * target_ship: Target ship information such as initial position, speed and course
        * desired_encounter_type: Desired type of encounter to be generated
        * settings: Encounter settings

    Returns
    -------
        * returns 0 if encounter not ok, 1 if encounter ok
    """
    theta13_criteria = settings["classification"]["theta13_criteria"]
    theta14_criteria = settings["classification"]["theta14_criteria"]
    theta15_criteria = settings["classification"]["theta15_criteria"]
    theta15 = settings["classification"]["theta15"]

    own_ship_speed = own_ship["start_pose"]["speed"]
    own_ship_course = own_ship["start_pose"]["course"]
    target_ship_speed = target_ship["start_pose"]["speed"]
    target_ship_course = target_ship["start_pose"]["course"]
    evolve_time = settings["evolve_time"]

    # Calculating position back in time to ensure that the encounter do not change from one type
    # to another before the encounter is started
    encounter_preposition_target_ship = calculate_position_at_certain_time(
        target_ship_position_future, target_ship_speed, target_ship_course, -evolve_time
    )
    encounter_preposition_own_ship = calculate_position_at_certain_time(
        own_ship_position_future, own_ship_speed, own_ship_course, -evolve_time
    )
    pre_beta, pre_alpha = calculate_relative_bearing(
        encounter_preposition_own_ship,
        own_ship_course,
        encounter_preposition_target_ship,
        target_ship_course,
    )
    pre_colreg_state = determine_colreg(
        pre_alpha, pre_beta, theta13_criteria, theta14_criteria, theta15_criteria, theta15
    )

    return 1 if pre_colreg_state == desired_encounter_type else 0


def calculate_min_vector_length_target_ship(
    own_ship_position, own_ship_course, target_ship_position_future, desired_beta
):
    """
    Calculate minimum vector length (target ship speed x vector). This will
    ensure that ship speed is high enough to find proper situation.

    Params:
        * own_ship_position: Own ship initial position, speed and course
        * own_ship_course: Own ship initial course
        * target_ship_position_future: Target ship future position
        * desired_beta: Desired relative bearing between

    Returns: min_vector_length: Minimum vector length (target ship speed x vector)
    """
    psi = np.deg2rad(own_ship_course + desired_beta)

    p_1 = np.array([own_ship_position["north"], own_ship_position["east"]])
    p_2 = np.array([own_ship_position["north"] + np.cos(psi), own_ship_position["east"] + np.sin(psi)])
    p_3 = np.array([target_ship_position_future["north"], target_ship_position_future["east"]])

    return np.abs(np.cross(p_2 - p_1, p_3 - p_1) / np.linalg.norm(p_2 - p_1))


def find_start_position_target_ship(
    own_ship_position,
    own_ship_course,
    target_ship_position_future,
    target_ship_vector_length,
    desired_beta,
    desired_encounter_type,
    settings,
):
    """
    Find start position of target ship using desired beta and vector length.

    Params:
        * own_ship_position: Own ship initial position, speed and course
        * own_ship_course: Own ship initial course
        * target_ship_position_future: Target ship future position
        * target_ship_vector_length: vector length (target ship speed x vector)
        * desired_beta: Desired bearing between own ship and target ship seen from own ship
        * desired_encounter_type: Desired type of encounter to be generated
        * settings: Encounter settings

    Returns
    -------
        * start_position_target_ship: Dict, initial position of target ship {north, east} [m]
        * start_position_found: 0=position not found, 1=position found
    """
    theta13_criteria = settings["classification"]["theta13_criteria"]
    theta14_criteria = settings["classification"]["theta14_criteria"]
    theta15_criteria = settings["classification"]["theta15_criteria"]
    theta15 = settings["classification"]["theta15"]

    n_1 = own_ship_position["north"]
    e_1 = own_ship_position["east"]
    n_2 = target_ship_position_future["north"]
    e_2 = target_ship_position_future["east"]
    v_r = target_ship_vector_length
    psi = np.deg2rad(own_ship_course + desired_beta)

    n_4 = n_1 + np.cos(psi)
    e_4 = e_1 + np.sin(psi)

    b = (
        -2 * e_2 * e_4
        - 2 * n_2 * n_4
        + 2 * e_1 * e_2
        + 2 * n_1 * n_2
        + 2 * e_1 * (e_4 - e_1)
        + 2 * n_1 * (n_4 - n_1)
    )
    a = (e_4 - e_1) ** 2 + (n_4 - n_1) ** 2
    c = e_2**2 + n_2**2 - 2 * e_1 * e_2 - 2 * n_1 * n_2 - v_r**2 + e_1**2 + n_1**2

    if b**2 - 4 * a * c > 0:
        s_1 = (-b + np.sqrt(b**2 - 4 * a * c)) / (2 * a)
        s_2 = (-b - np.sqrt(b**2 - 4 * a * c)) / (2 * a)

        e_31 = e_1 + s_1 * (e_4 - e_1)
        n_31 = n_1 + s_1 * (n_4 - n_1)
        e_32 = e_1 + s_2 * (e_4 - e_1)
        n_32 = n_1 + s_2 * (n_4 - n_1)

        target_ship_course_1 = calculate_ship_course(
            {"north": n_31, "east": e_31}, target_ship_position_future
        )
        beta1, alpha1 = calculate_relative_bearing(
            own_ship_position, own_ship_course, {"north": n_31, "east": e_31}, target_ship_course_1
        )
        colreg_state1 = determine_colreg(
            alpha1, beta1, theta13_criteria, theta14_criteria, theta15_criteria, theta15
        )
        target_ship_course_2 = calculate_ship_course(
            {"north": n_32, "east": e_32}, target_ship_position_future
        )
        beta2, alpha2 = calculate_relative_bearing(
            own_ship_position, own_ship_course, {"north": n_32, "east": e_32}, target_ship_course_2
        )
        colreg_state2 = determine_colreg(
            alpha2, beta2, theta13_criteria, theta14_criteria, theta15_criteria, theta15
        )
        if desired_encounter_type.lower() == colreg_state1 and np.abs(
            beta1 - desired_beta % 360
        ) < deg_2_rad(0.1):
            start_position_target_ship = {"north": n_31, "east": e_31}
            start_position_found = 1
        elif desired_encounter_type.lower() == colreg_state2 and np.abs(
            beta1 - desired_beta % 360
        ) < deg_2_rad(
            0.1
        ):  # noqa: E127
            start_position_target_ship = {"north": n_32, "east": e_32}
            start_position_found = 1
        else:
            start_position_found = 0
            start_position_target_ship = target_ship_position_future
    else:
        start_position_found = 0
        start_position_target_ship = target_ship_position_future

    return start_position_target_ship, start_position_found


def assign_future_position_to_target_ship(own_ship_position_future, max_meeting_distance):
    """
    Randomly assign future position of target ship. If drawing a circle with radius
    max_meeting_distance around future position of own ship, future position of
    target ship shall be somewhere inside this circle.

    Params:
        * own_ship_position_future: Dict, own ship position at a given time in the
            future, {north, east}
        * max_meeting_distance: Maximum distance between own ship and target ship at
            a given time in the future [nm]

    Returns
    -------
        future_position_target_ship: Dict, future position of target ship {north, east} [m]
    """
    random_angle = random.uniform(0, 1) * 2 * np.pi
    random_distance = random.uniform(0, 1) * nm_2_m(max_meeting_distance)

    north = own_ship_position_future["north"] + random_distance * np.cos(deg_2_rad(random_angle))
    east = own_ship_position_future["east"] + random_distance * np.sin(deg_2_rad(random_angle))
    return {"north": north, "east": east}


def determine_colreg(alpha, beta, theta13_criteria, theta14_criteria, theta15_criteria, theta15):
    """
    Determine the colreg type based on alpha, relative bearing between target ship and own
    ship seen from target ship, and beta, relative bearing between own ship and target ship
    seen from own ship.

    Params:
        * alpha: relative bearing between target ship and own ship seen from target ship
        * beta: relative bearing between own ship and target ship seen from own ship
        * theta13_criteria: Tolerance for "coming up with" relative bearing
        * theta14_criteria: Tolerance for "reciprocal or nearly reciprocal courses",
          "when in any doubt... assume... [head-on]"
        * theta15_criteria: Crossing aspect limit, used for classifying a crossing encounter
        * theta15: 22.5 deg aft of the beam, used for classifying a crossing and an overtaking
                   encounter

    Returns
    -------
        * encounter classification
    """
    # Mapping
    alpha0360 = alpha if alpha >= 0 else alpha + 360
    beta0180 = beta if (beta >= 0) & (beta <= 180) else beta - 360

    # Find appropriate rule set
    if (beta > theta15[0]) & (beta < theta15[1]) & (abs(alpha) - theta13_criteria <= 0.001):
        return "overtaking-stand-on"
    if (alpha0360 > theta15[0]) & (alpha0360 < theta15[1]) & (abs(beta0180) - theta13_criteria <= 0.001):
        return "overtaking-give-way"
    if (abs(beta0180) - theta14_criteria <= 0.001) & (abs(alpha) - theta14_criteria <= 0.001):
        return "head-on"
    if (beta > 0) & (beta < theta15[0]) & (alpha > -theta15[0]) & (alpha - theta15_criteria <= 0.001):
        return "crossing-give-way"
    if (
        (alpha0360 > 0)
        & (alpha0360 < theta15[0])
        & (beta0180 > -theta15[0])
        & (beta0180 - theta15_criteria <= 0.001)
    ):
        return "crossing-stand-on"
    return "noRiskCollision"


def calculate_relative_bearing(
    position_own_ship, heading_own_ship, position_target_ship, heading_target_ship
):
    """
    Calculate relative bearing between own ship and target ship, both seen from
    own ship and seen from target ship.

    Params:
        * position_own_ship: Dict, own ship position {north, east} [m]
        * heading_own_ship: Own ship course [deg]
        * position_target_ship: Dict, own ship position {north, east} [m]
        * heading_target_ship: Target ship course [deg]

    Returns
    -------
        * alpha: relative bearing between target ship and own ship seen from target ship [deg]
        * beta: relative bearing between own ship and target ship seen from own ship [deg]
    """
    heading_own_ship = np.deg2rad(heading_own_ship)
    heading_target_ship = np.deg2rad(heading_target_ship)

    # POSE combination of relative bearing and contact angle
    n_own_ship = position_own_ship["north"]
    e_own_ship = position_own_ship["east"]
    n_target_ship = position_target_ship["north"]
    e_target_ship = position_target_ship["east"]

    # Absolute bearing of target ship relative to own ship
    if e_own_ship == e_target_ship:
        if n_own_ship <= n_target_ship:
            bng_own_ship_target_ship = 0
        else:
            bng_own_ship_target_ship = np.pi
    else:
        if e_own_ship < e_target_ship:
            if n_own_ship <= n_target_ship:
                bng_own_ship_target_ship = 1 / 2 * np.pi - np.arctan(
                    abs(n_target_ship - n_own_ship) / abs(e_target_ship - e_own_ship)
                )
            else:
                bng_own_ship_target_ship = 1 / 2 * np.pi + np.arctan(
                    abs(n_target_ship - n_own_ship) / abs(e_target_ship - e_own_ship)
                )
        else:
            if n_own_ship <= n_target_ship:
                bng_own_ship_target_ship = 3 / 2 * np.pi + np.arctan(
                    abs(n_target_ship - n_own_ship) / abs(e_target_ship - e_own_ship)
                )
            else:
                bng_own_ship_target_ship = 3 / 2 * np.pi - np.arctan(
                    abs(n_target_ship - n_own_ship) / abs(e_target_ship - e_own_ship)
                )

    # Bearing of own ship from the perspective of the contact
    bng_target_ship_own_ship = bng_own_ship_target_ship + np.pi

    # Relative bearing of contact ship relative to own ship
    beta = bng_own_ship_target_ship - heading_own_ship
    while beta < 0:
        beta = beta + 2 * np.pi
    while beta >= 2 * np.pi:
        beta = beta - 2 * np.pi

    # Relative bearing of own ship relative to target ship
    alpha = bng_target_ship_own_ship - heading_target_ship
    while alpha < -np.pi:
        alpha = alpha + 2 * np.pi
    while alpha >= np.pi:
        alpha = alpha - 2 * np.pi

    beta = np.rad2deg(beta)
    alpha = np.rad2deg(alpha)
    return beta, alpha


def calculate_ship_course(waypoint_0, waypoint_1):
    """
    Calculate ship course between two waypoints.

    Params:
        * waypoint_0: Dict, waypoint {north, east} [m]
        * waypoint_1: Dict, waypoint {north, east} [m]

    Returns
    -------
        course: Ship course [deg]
    """
    course = np.arctan2(
        waypoint_1["east"] - waypoint_0["east"], waypoint_1["north"] - waypoint_0["north"]
    )
    if course < 0:
        course = course + 2 * np.pi
    return round(np.rad2deg(course), 1)


def assign_vector_time(setting_vector_time):
    """
    Assign random (uniform) vector time.

    Params:
        * setting_vector_time: Minimum and maximum value for vector time

    Returns
    -------
        vector_time: Vector time [min]
    """
    return setting_vector_time[0] + random.uniform(0, 1) * (
        setting_vector_time[1] - setting_vector_time[0]
    )


def assign_speed_to_target_ship(
    encounter_type, own_ship_speed, min_target_ship_speed, relative_speed_setting
):
    """
    Assign random (uniform) speed to target ship depending on type of encounter.

    Params:
        * encounter_type: Type of encounter
        * own_ship_speed: Own ship speed [knot]
        * min_target_ship_speed: Minimum target ship speed [knot]
        * relative_speed_setting: Relative speed setting dependent on encounter [-]

    Returns
    -------
        speed_target_ship: Target ship speed [knot]
    """
    if encounter_type.lower() == "overtaking-stand-on":
        relative_speed = relative_speed_setting["overtaking_stand_on"]
    elif encounter_type.lower() == "overtaking-give-way":
        relative_speed = relative_speed_setting["overtaking_give_way"]
    elif encounter_type.lower() == "head-on":
        relative_speed = relative_speed_setting["head_on"]
    elif encounter_type.lower() == "crossing-give-way":
        relative_speed = relative_speed_setting["crossing_give_way"]
    elif encounter_type.lower() == "crossing-stand-on":
        relative_speed = relative_speed_setting["crossing_stand_on"]
    else:
        relative_speed = [0.0, 0.0]

    # Check that minimum target ship speed is in the relative speed range
    if (
        min_target_ship_speed / own_ship_speed > relative_speed[0]
        and min_target_ship_speed / own_ship_speed < relative_speed[1]
    ):
        relative_speed[0] = min_target_ship_speed / own_ship_speed

    return (
        relative_speed[0] + random.uniform(0, 1) * (relative_speed[1] - relative_speed[0])
    ) * own_ship_speed


def assign_beta(encounter_type, settings):
    """
    Assign random (uniform) relative bearing beta between own ship
    and target ship depending on type of encounter.

    Params:
        * encounter_type: Type of encounter
        * settings: Encounter settings

    Returns
    -------
        Relative bearing between own ship and target ship seen from own ship [deg]
    """
    theta13_crit = settings["classification"]["theta13_criteria"]
    theta14_crit = settings["classification"]["theta14_criteria"]
    theta15_crit = settings["classification"]["theta15_criteria"]
    theta15 = settings["classification"]["theta15"]

    if encounter_type.lower() == "overtaking-stand-on":
        return theta15[0] + random.uniform(0, 1) * (theta15[1] - theta15[0])
    if encounter_type.lower() == "overtaking-give-way":
        return -theta13_crit + random.uniform(0, 1) * (theta13_crit - (-theta13_crit))
    if encounter_type.lower() == "head-on":
        return -theta14_crit + random.uniform(0, 1) * (theta14_crit - (-theta14_crit))
    if encounter_type.lower() == "crossing-give-way":
        return 0 + random.uniform(0, 1) * (theta15[0] - 0)
    if encounter_type.lower() == "crossing-stand-on":
        return convert_angle_minus_180_to_180_to_0_to_360(
            -theta15[1] + random.uniform(0, 1) * (theta15[1] + theta15_crit)
        )
    return 0


def update_position_data_target_ship(ship, lat_lon_0):
    """
    Update position data of the target ship to also include latitude and longitude
    position of the target ship.

    Params:
        * ship: Target ship data
        * lat_lon_0: Reference point, latitudinal [degree] and longitudinal [degree]

    Returns
    -------
        ship: Updated target ship data
    """
    lat_0 = lat_lon_0[0]
    lon_0 = lat_lon_0[1]

    lat, lon, _ = flat2llh(
        ship["start_pose"]["position"]["north"],
        ship["start_pose"]["position"]["east"],
        deg_2_rad(lat_0),
        deg_2_rad(lon_0),
    )
    ship["start_pose"]["position"] = {
        "north": ship["start_pose"]["position"]["north"],
        "east": ship["start_pose"]["position"]["east"],
        "latitude": round(rad_2_deg(lat), 6),
        "longitude": round(rad_2_deg(lon), 6),
    }
    return ship


def update_position_data_own_ship(ship, lat_lon_0, delta_time):
    """
    Update position data of the target ship to also include latitude and longitude
    position of the target ship.

    Params:
        * ship: Own ship data
        * lat_lon_0: Reference point, latitudinal [degree] and longitudinal [degree]
        * delta_time: Delta time from now to the time new position is being calculated [minutes]

    Returns
    -------
        ship: Updated own ship data
    """
    lat_0 = lat_lon_0[0]
    lon_0 = lat_lon_0[1]

    ship_position_future = calculate_position_at_certain_time(
        ship["start_pose"]["position"],
        ship["start_pose"]["speed"],
        ship["start_pose"]["course"],
        delta_time,
    )
    lat, lon, _ = flat2llh(
        ship["start_pose"]["position"]["north"],
        ship["start_pose"]["position"]["east"],
        deg_2_rad(lat_0),
        deg_2_rad(lon_0),
    )
    lat_future, lon_future, _ = flat2llh(
        ship_position_future["north"], ship_position_future["east"], deg_2_rad(lat_0), deg_2_rad(lon_0)
    )

    ship["start_pose"]["position"] = {
        "north": ship["start_pose"]["position"]["north"],
        "east": ship["start_pose"]["position"]["east"],
        "latitude": round(rad_2_deg(lat), 6),
        "longitude": round(rad_2_deg(lon), 6),
    }
    ship["waypoints"] = [
        {"latitude": round(rad_2_deg(lat), 6), "longitude": round(rad_2_deg(lon), 6)},
        {"latitude": round(rad_2_deg(lat_future), 6), "longitude": round(rad_2_deg(lon_future), 6)},
    ]

    return ship


def decide_target_ship(target_ships):
    """
    Randomly pick a target ship from a dict of target ships.

    Params:
        * target_ships: dict of target ships

    Returns
    -------
        The target ship, info of type, size etc.
    """
    num_target_ships = len(target_ships)
    target_ship_to_use = random.randint(1, num_target_ships)
    return copy.deepcopy(target_ships[target_ship_to_use - 1])
