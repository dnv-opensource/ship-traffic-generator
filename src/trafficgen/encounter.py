"""
Functions to generate encounters consisting of one own ship and one to many target ships.
The generated encounters may be of type head-on, overtaking give-way and stand-on and
crossing give-way and stand-on.
"""

import random
from operator import pos
from typing import List, Optional, Tuple, Union

import numpy as np

from trafficgen.check_land_crossing import path_crosses_land
from trafficgen.marine_system_simulator import flat2llh
from trafficgen.types import (
    EncounterRelativeSpeed,
    EncounterSettings,
    EncounterType,
    Initial,
    OwnShip,
    Position,
    TargetShip,
    Waypoint,
)
from trafficgen.utils import (
    calculate_position_at_certain_time,
    convert_angle_minus_180_to_180_to_0_to_360,
    deg_2_rad,
    knot_2_m_pr_min,
    m_pr_min_2_knot,
    nm_2_m,
    rad_2_deg,
)


def generate_encounter(
    desired_encounter_type: EncounterType,
    own_ship: OwnShip,
    target_ships: List[TargetShip],
    target_ship_id: int,
    beta_default: Optional[float],
    relative_sog_default: Optional[float],
    vector_time_default: Optional[float],
    settings: EncounterSettings,
) -> Tuple[TargetShip, bool]:
    """
    Generate an encounter.

    Params:
        * desired_encounter_type: Desired encounter to be generated
        * own_ship: Dict, information about own ship that will encounter a target ship
        * target_ships: List of target ships that may be used in an encounter
        * target_ship_id: ID which should be used on target ship
        * beta_default: User defined beta. If not set, this is None.
        * relative_sog_default: User defined relative sog between own ship and
                                  target ship. If not set, this is None.
        * vector_time_default: User defined vector time. If not set, this is None.
        * settings: Encounter settings

    Returns
    -------
        target_ship: target ship information, such as initial position, sog and cog
        encounter_found: True=encounter found, False=encounter not found
    """
    encounter_found: bool = False
    outer_counter: int = 0

    target_ship = decide_target_ship(target_ships)
    assert target_ship.static is not None

    # Searching for encounter. Two loops used. Only vector time is locked in the
    # first loop. In the second loop, beta and sog are assigned.
    while not encounter_found and outer_counter < 5:
        outer_counter += 1
        inner_counter: int = 0

        # resetting vector_time, beta and relative_sog to default values before
        # new search for situation is done
        vector_time: Union[float, None] = vector_time_default
        beta: Union[float, None] = beta_default

        if vector_time is None:
            vector_time = random.uniform(settings.vector_range[0], settings.vector_range[1])
        if beta is None:
            beta = assign_beta(desired_encounter_type, settings)

        # Own ship
        assert own_ship.initial is not None
        own_ship_position_future = calculate_position_at_certain_time(
            own_ship.initial.position,
            own_ship.initial.sog,
            own_ship.initial.cog,
            vector_time,
        )

        # Target ship
        target_ship.initial = Initial()  # reset initial of target_ship (if one existed)

        target_ship_position_future = assign_future_position_to_target_ship(
            own_ship_position_future, settings.max_meeting_distance
        )

        while not encounter_found and inner_counter < 5:
            inner_counter += 1
            relative_sog = relative_sog_default
            if relative_sog is None:
                min_target_ship_sog = m_pr_min_2_knot(
                    calculate_min_vector_length_target_ship(
                        own_ship.initial.position,
                        own_ship.initial.cog,
                        target_ship_position_future,
                        beta,
                    )
                    / vector_time
                )

                target_ship.initial.sog = assign_sog_to_target_ship(
                    desired_encounter_type,
                    own_ship.initial.sog,
                    min_target_ship_sog,
                    settings.relative_speed,
                )
            else:
                target_ship.initial.sog = relative_sog * own_ship.initial.sog

            target_ship.initial.sog = np.minimum(
                target_ship.initial.sog, target_ship.static.speed_max
            )

            target_ship_vector_length = knot_2_m_pr_min(target_ship.initial.sog) * vector_time
            start_position_target_ship, position_found = find_start_position_target_ship(
                own_ship.initial.position,
                own_ship.initial.cog,
                target_ship_position_future,
                target_ship_vector_length,
                beta,
                desired_encounter_type,
                settings,
            )

            if position_found:
                target_ship.initial.position = start_position_target_ship
                target_ship.initial.cog = calculate_ship_cog(
                    target_ship.initial.position, target_ship_position_future
                )
                encounter_ok: bool = check_encounter_evolvement(
                    own_ship,
                    own_ship_position_future,
                    target_ship,
                    target_ship_position_future,
                    desired_encounter_type,
                    settings,
                )

                # Check if trajectory passes land
                trajectory_on_land = path_crosses_land(
                    target_ship.initial.position,
                    target_ship.initial.sog,
                    target_ship.initial.cog,
                    settings.lat_lon_0,
                )

                encounter_found = encounter_ok and not trajectory_on_land

    if encounter_found:
        target_ship = update_position_data_target_ship(target_ship, settings.lat_lon_0)
    return target_ship, encounter_found


def check_encounter_evolvement(
    own_ship: OwnShip,
    own_ship_position_future: Position,
    target_ship: TargetShip,
    target_ship_position_future: Position,
    desired_encounter_type: EncounterType,
    settings: EncounterSettings,
) -> bool:
    """
    Check encounter evolvement. The generated encounter should be the same type of
    encounter (head-on, crossing, give-way) also some time before the encounter is started.

    Params:
        * own_ship: Own ship information such as initial position, sog and cog
        * target_ship: Target ship information such as initial position, sog and cog
        * desired_encounter_type: Desired type of encounter to be generated
        * settings: Encounter settings

    Returns
    -------
        * returns True if encounter ok, False if encounter not ok
    """
    theta13_criteria: float = settings.classification.theta13_criteria
    theta14_criteria: float = settings.classification.theta14_criteria
    theta15_criteria: float = settings.classification.theta15_criteria
    theta15: List[float] = settings.classification.theta15

    assert own_ship.initial is not None
    assert target_ship.initial is not None

    own_ship_sog: float = own_ship.initial.sog
    own_ship_cog: float = own_ship.initial.cog
    target_ship_sog: float = target_ship.initial.sog
    target_ship_cog: float = target_ship.initial.cog
    evolve_time: float = settings.evolve_time

    # Calculating position back in time to ensure that the encounter do not change from one type
    # to another before the encounter is started
    encounter_preposition_target_ship = calculate_position_at_certain_time(
        target_ship_position_future,
        target_ship_sog,
        target_ship_cog,
        -evolve_time,
    )
    encounter_preposition_own_ship = calculate_position_at_certain_time(
        own_ship_position_future,
        own_ship_sog,
        own_ship_cog,
        -evolve_time,
    )
    pre_beta, pre_alpha = calculate_relative_bearing(
        encounter_preposition_own_ship,
        own_ship_cog,
        encounter_preposition_target_ship,
        target_ship_cog,
    )
    pre_colreg_state = determine_colreg(
        pre_alpha, pre_beta, theta13_criteria, theta14_criteria, theta15_criteria, theta15
    )

    encounter_ok: bool = pre_colreg_state == desired_encounter_type

    return encounter_ok


def calculate_min_vector_length_target_ship(
    own_ship_position: Position,
    own_ship_cog: float,
    target_ship_position_future: Position,
    desired_beta: float,
) -> float:
    """
    Calculate minimum vector length (target ship sog x vector). This will
    ensure that ship sog is high enough to find proper situation.

    Params:
        * own_ship_position: Own ship initial position, sog and cog
        * own_ship_cog: Own ship initial cog
        * target_ship_position_future: Target ship future position
        * desired_beta: Desired relative bearing between

    Returns: min_vector_length: Minimum vector length (target ship sog x vector)
    """
    psi: float = np.deg2rad(own_ship_cog + desired_beta)

    p_1 = np.array([own_ship_position.north, own_ship_position.east])
    p_2 = np.array([own_ship_position.north + np.cos(psi), own_ship_position.east + np.sin(psi)])
    p_3 = np.array([target_ship_position_future.north, target_ship_position_future.east])

    min_vector_length: float = float(np.abs(np.cross(p_2 - p_1, p_3 - p_1) / np.linalg.norm(p_2 - p_1)))

    return min_vector_length


def find_start_position_target_ship(
    own_ship_position: Position,
    own_ship_cog: float,
    target_ship_position_future: Position,
    target_ship_vector_length: float,
    desired_beta: float,
    desired_encounter_type: EncounterType,
    settings: EncounterSettings,
):
    """
    Find start position of target ship using desired beta and vector length.

    Params:
        * own_ship_position: Own ship initial position, sog and cog
        * own_ship_cog: Own ship initial cog
        * target_ship_position_future: Target ship future position
        * target_ship_vector_length: vector length (target ship sog x vector)
        * desired_beta: Desired bearing between own ship and target ship seen from own ship
        * desired_encounter_type: Desired type of encounter to be generated
        * settings: Encounter settings

    Returns
    -------
        * start_position_target_ship: Dict, initial position of target ship {north, east} [m]
        * start_position_found: 0=position not found, 1=position found
    """
    theta13_criteria: float = settings.classification.theta13_criteria
    theta14_criteria: float = settings.classification.theta14_criteria
    theta15_criteria: float = settings.classification.theta15_criteria
    theta15: List[float] = settings.classification.theta15

    n_1: float = own_ship_position.north
    e_1: float = own_ship_position.east
    n_2: float = target_ship_position_future.north
    e_2: float = target_ship_position_future.east
    v_r: float = target_ship_vector_length
    psi: float = np.deg2rad(own_ship_cog + desired_beta)

    n_4: float = n_1 + np.cos(psi)
    e_4: float = e_1 + np.sin(psi)

    b: float = (
        -2 * e_2 * e_4
        - 2 * n_2 * n_4
        + 2 * e_1 * e_2
        + 2 * n_1 * n_2
        + 2 * e_1 * (e_4 - e_1)
        + 2 * n_1 * (n_4 - n_1)
    )
    a: float = (e_4 - e_1) ** 2 + (n_4 - n_1) ** 2
    c: float = e_2**2 + n_2**2 - 2 * e_1 * e_2 - 2 * n_1 * n_2 - v_r**2 + e_1**2 + n_1**2

    # Assign conservative fallback values to return variables
    start_position_found: bool = False
    start_position_target_ship = target_ship_position_future.model_copy()

    if b**2 - 4 * a * c <= 0.0:
        # Do not run calculation of target ship start position. Return fallback values.
        return start_position_target_ship, start_position_found

    # Calculation of target ship start position
    s_1 = (-b + np.sqrt(b**2 - 4 * a * c)) / (2 * a)
    s_2 = (-b - np.sqrt(b**2 - 4 * a * c)) / (2 * a)

    e_31 = e_1 + s_1 * (e_4 - e_1)
    n_31 = n_1 + s_1 * (n_4 - n_1)
    e_32 = e_1 + s_2 * (e_4 - e_1)
    n_32 = n_1 + s_2 * (n_4 - n_1)

    target_ship_cog_1 = calculate_ship_cog(
        pos_0=Position(north=n_31, east=e_31),
        pos_1=target_ship_position_future,
    )
    beta1, alpha1 = calculate_relative_bearing(
        position_own_ship=own_ship_position,
        heading_own_ship=own_ship_cog,
        position_target_ship=Position(north=n_31, east=e_31),
        heading_target_ship=target_ship_cog_1,
    )
    colreg_state1: EncounterType = determine_colreg(
        alpha1, beta1, theta13_criteria, theta14_criteria, theta15_criteria, theta15
    )
    target_ship_cog_2 = calculate_ship_cog(
        pos_0=Position(north=n_32, east=e_32),
        pos_1=target_ship_position_future,
    )
    beta2, alpha2 = calculate_relative_bearing(
        position_own_ship=own_ship_position,
        heading_own_ship=own_ship_cog,
        position_target_ship=Position(north=n_32, east=e_32),
        heading_target_ship=target_ship_cog_2,
    )
    colreg_state2: EncounterType = determine_colreg(
        alpha2, beta2, theta13_criteria, theta14_criteria, theta15_criteria, theta15
    )
    if desired_encounter_type is colreg_state1 and np.abs(beta1 - desired_beta % 360) < deg_2_rad(0.1):
        start_position_target_ship = Position(north=n_31, east=e_31)
        start_position_found = True
    elif desired_encounter_type is colreg_state2 and np.abs(beta1 - desired_beta % 360) < deg_2_rad(0.1):
        start_position_target_ship = Position(north=n_32, east=e_32)
        start_position_found = True

    return start_position_target_ship, start_position_found


def assign_future_position_to_target_ship(
    own_ship_position_future: Position,
    max_meeting_distance: float,
) -> Position:
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
        future_position_target_ship: Future position of target ship {north, east} [m]
    """
    random_angle = random.uniform(0, 1) * 2 * np.pi
    random_distance = random.uniform(0, 1) * nm_2_m(max_meeting_distance)

    north: float = own_ship_position_future.north + random_distance * np.cos(deg_2_rad(random_angle))
    east: float = own_ship_position_future.east + random_distance * np.sin(deg_2_rad(random_angle))
    return Position(north=north, east=east)


def determine_colreg(
    alpha: float,
    beta: float,
    theta13_criteria: float,
    theta14_criteria: float,
    theta15_criteria: float,
    theta15: List[float],
) -> EncounterType:
    """
    Determine the colreg type based on alpha, relative bearing between target ship and own
    ship seen from target ship, and beta, relative bearing between own ship and target ship
    seen from own ship.

    Params:
        * alpha: relative bearing between target ship and own ship seen from target ship
        * beta: relative bearing between own ship and target ship seen from own ship
        * theta13_criteria: Tolerance for "coming up with" relative bearing
        * theta14_criteria: Tolerance for "reciprocal or nearly reciprocal cogs",
          "when in any doubt... assume... [head-on]"
        * theta15_criteria: Crossing aspect limit, used for classifying a crossing encounter
        * theta15: 22.5 deg aft of the beam, used for classifying a crossing and an overtaking
                   encounter

    Returns
    -------
        * encounter classification
    """
    # Mapping
    alpha0360: float = alpha if alpha >= 0.0 else alpha + 360.0
    beta0180: float = beta if (beta >= 0.0) & (beta <= 180.0) else beta - 360.0

    # Find appropriate rule set
    if (beta > theta15[0]) & (beta < theta15[1]) & (abs(alpha) - theta13_criteria <= 0.001):
        return EncounterType.OVERTAKING_STAND_ON
    if (alpha0360 > theta15[0]) & (alpha0360 < theta15[1]) & (abs(beta0180) - theta13_criteria <= 0.001):
        return EncounterType.OVERTAKING_GIVE_WAY
    if (abs(beta0180) - theta14_criteria <= 0.001) & (abs(alpha) - theta14_criteria <= 0.001):
        return EncounterType.HEAD_ON
    if (beta > 0) & (beta < theta15[0]) & (alpha > -theta15[0]) & (alpha - theta15_criteria <= 0.001):
        return EncounterType.CROSSING_GIVE_WAY
    if (
        (alpha0360 > 0)
        & (alpha0360 < theta15[0])
        & (beta0180 > -theta15[0])
        & (beta0180 - theta15_criteria <= 0.001)
    ):
        return EncounterType.CROSSING_STAND_ON
    return EncounterType.NO_RISK_COLLISION


def calculate_relative_bearing(
    position_own_ship: Position,
    heading_own_ship: float,
    position_target_ship: Position,
    heading_target_ship: float,
) -> Tuple[float, float]:
    """
    Calculate relative bearing between own ship and target ship, both seen from
    own ship and seen from target ship.

    Params:
        * position_own_ship: Dict, own ship position {north, east} [m]
        * heading_own_ship: Own ship cog [deg]
        * position_target_ship: Dict, own ship position {north, east} [m]
        * heading_target_ship: Target ship cog [deg]

    Returns
    -------
        * beta: relative bearing between own ship and target ship seen from own ship [deg]
        * alpha: relative bearing between target ship and own ship seen from target ship [deg]
    """
    heading_own_ship = np.deg2rad(heading_own_ship)
    heading_target_ship = np.deg2rad(heading_target_ship)

    # POSE combination of relative bearing and contact angle
    n_own_ship: float = position_own_ship.north
    e_own_ship: float = position_own_ship.east
    n_target_ship: float = position_target_ship.north
    e_target_ship: float = position_target_ship.east

    # Absolute bearing of target ship relative to own ship
    bng_own_ship_target_ship: float = 0.0
    if e_own_ship == e_target_ship:
        if n_own_ship <= n_target_ship:
            bng_own_ship_target_ship = 0.0
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
    bng_target_ship_own_ship: float = bng_own_ship_target_ship + np.pi

    # Relative bearing of contact ship relative to own ship
    beta: float = bng_own_ship_target_ship - heading_own_ship
    while beta < 0:
        beta += 2 * np.pi
    while beta >= 2 * np.pi:
        beta -= 2 * np.pi

    # Relative bearing of own ship relative to target ship
    alpha: float = bng_target_ship_own_ship - heading_target_ship
    while alpha < -np.pi:
        alpha += 2 * np.pi
    while alpha >= np.pi:
        alpha -= 2 * np.pi

    beta = np.rad2deg(beta)
    alpha = np.rad2deg(alpha)

    return beta, alpha


def calculate_ship_cog(pos_0: Position, pos_1: Position) -> float:
    """
    Calculate ship cog between two waypoints.

    Params:
        * waypoint_0: Dict, waypoint {north, east} [m]
        * waypoint_1: Dict, waypoint {north, east} [m]

    Returns
    -------
        cog: Ship cog [deg]
    """
    cog: float = np.arctan2(pos_1.east - pos_0.east,
                            pos_1.north - pos_0.north)
    if cog < 0.0:
        cog += 2 * np.pi
    return round(np.rad2deg(cog), 1)


def assign_vector_time(vector_time_range: List[float]):
    """
    Assign random (uniform) vector time.

    Params:
        * vector_range: Minimum and maximum value for vector time

    Returns
    -------
        vector_time: Vector time [min]
    """
    vector_time: float = vector_time_range[0] + random.uniform(0, 1) * (
        vector_time_range[1] - vector_time_range[0]
    )
    return vector_time


def assign_sog_to_target_ship(
    encounter_type: EncounterType,
    own_ship_sog: float,
    min_target_ship_sog: float,
    relative_sog_setting: EncounterRelativeSpeed,
):
    """
    Assign random (uniform) sog to target ship depending on type of encounter.

    Params:
        * encounter_type: Type of encounter
        * own_ship_sog: Own ship sog [knot]
        * min_target_ship_sog: Minimum target ship sog [knot]
        * relative_sog_setting: Relative sog setting dependent on encounter [-]

    Returns
    -------
        target_ship_sog: Target ship sog [knot]
    """
    if encounter_type is EncounterType.OVERTAKING_STAND_ON:
        relative_sog = relative_sog_setting.overtaking_stand_on
    elif encounter_type is EncounterType.OVERTAKING_GIVE_WAY:
        relative_sog = relative_sog_setting.overtaking_give_way
    elif encounter_type is EncounterType.HEAD_ON:
        relative_sog = relative_sog_setting.head_on
    elif encounter_type is EncounterType.CROSSING_GIVE_WAY:
        relative_sog = relative_sog_setting.crossing_give_way
    elif encounter_type is EncounterType.CROSSING_STAND_ON:
        relative_sog = relative_sog_setting.crossing_stand_on
    else:
        relative_sog = [0.0, 0.0]

    # Check that minimum target ship sog is in the relative sog range
    if (
        min_target_ship_sog / own_ship_sog > relative_sog[0]
        and min_target_ship_sog / own_ship_sog < relative_sog[1]
    ):
        relative_sog[0] = min_target_ship_sog / own_ship_sog

    target_ship_sog: float = (
        relative_sog[0] + random.uniform(0, 1) * (relative_sog[1] - relative_sog[0])
    ) * own_ship_sog

    return target_ship_sog


def assign_beta(encounter_type: EncounterType, settings: EncounterSettings) -> float:
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
    theta13_crit: float = settings.classification.theta13_criteria
    theta14_crit: float = settings.classification.theta14_criteria
    theta15_crit: float = settings.classification.theta15_criteria
    theta15: List[float] = settings.classification.theta15

    if encounter_type is EncounterType.OVERTAKING_STAND_ON:
        return theta15[0] + random.uniform(0, 1) * (theta15[1] - theta15[0])
    if encounter_type is EncounterType.OVERTAKING_GIVE_WAY:
        return -theta13_crit + random.uniform(0, 1) * (theta13_crit - (-theta13_crit))
    if encounter_type is EncounterType.HEAD_ON:
        return -theta14_crit + random.uniform(0, 1) * (theta14_crit - (-theta14_crit))
    if encounter_type is EncounterType.CROSSING_GIVE_WAY:
        return 0 + random.uniform(0, 1) * (theta15[0] - 0)
    if encounter_type is EncounterType.CROSSING_STAND_ON:
        return convert_angle_minus_180_to_180_to_0_to_360(
            -theta15[1] + random.uniform(0, 1) * (theta15[1] + theta15_crit)
        )
    return 0.0


def update_position_data_target_ship(
    target_ship: TargetShip,
    lat_lon_0: List[float],
) -> TargetShip:
    """
    Update position data of the target ship to also include latitude and longitude
    position of the target ship.

    Params:
        * target_ship: Target ship data
        * lat_lon_0: Reference point, latitudinal [degree] and longitudinal [degree]

    Returns
    -------
        ship: Updated target ship data
    """
    assert target_ship.initial is not None

    lat_0 = lat_lon_0[0]
    lon_0 = lat_lon_0[1]

    lat, lon, _ = flat2llh(
        target_ship.initial.position.north,
        target_ship.initial.position.east,
        deg_2_rad(lat_0),
        deg_2_rad(lon_0),
    )
    target_ship.initial.position.latitude = round(rad_2_deg(lat), 6)
    target_ship.initial.position.longitude = round(rad_2_deg(lon), 6)
    return target_ship


def update_position_data_own_ship(
    ship: OwnShip,
    lat_lon_0: List[float],
    delta_time: float,
) -> OwnShip:
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
    assert ship.initial is not None

    lat_0 = lat_lon_0[0]
    lon_0 = lat_lon_0[1]

    ship_position_future = calculate_position_at_certain_time(
        ship.initial.position,
        ship.initial.sog,
        ship.initial.cog,
        delta_time,
    )
    lat, lon, _ = flat2llh(
        ship.initial.position.north,
        ship.initial.position.east,
        deg_2_rad(lat_0),
        deg_2_rad(lon_0),
    )
    ship.initial.position.latitude = round(rad_2_deg(lat), 6)
    ship.initial.position.longitude = round(rad_2_deg(lon), 6)

    lat_future, lon_future, _ = flat2llh(
        ship_position_future.north,
        ship_position_future.east,
        deg_2_rad(lat_0),
        deg_2_rad(lon_0),
    )
    ship_position_future.latitude = round(rad_2_deg(lat_future), 6)
    ship_position_future.longitude = round(rad_2_deg(lon_future), 6)


    ship.waypoints = [
        Waypoint(position=ship.initial.position.model_copy()),
        Waypoint(position=ship_position_future),
    ]

    return ship


def decide_target_ship(target_ships: List[TargetShip]) -> TargetShip:
    """
    Randomly pick a target ship from a list of target ships.

    Params:
        * target_ships: list of target ships

    Returns
    -------
        The target ship, info of type, size etc.
    """
    num_target_ships: int = len(target_ships)
    target_ship_to_use: int = random.randint(1, num_target_ships)
    target_ship: TargetShip = target_ships[target_ship_to_use - 1]
    return target_ship.model_copy(deep=True)
