"""
Functions to generate encounters consisting of one own ship and one to many target ships.
The generated encounters may be of type head-on, overtaking give-way and stand-on and
crossing give-way and stand-on.
"""

import random
from typing import List, Optional, Tuple, Union
from uuid import uuid4

import numpy as np
from maritime_schema.types.caga import (
    AISNavStatus,
    Initial,
    OwnShip,
    Position,
    ShipStatic,
    TargetShip,
    Waypoint,
)

from trafficgen.check_land_crossing import path_crosses_land
from trafficgen.marine_system_simulator import flat2llh, llh2flat
from trafficgen.types import (
    EncounterRelativeSpeed,
    EncounterSettings,
    EncounterType,
    SituationInput,
)
from trafficgen.utils import (
    calculate_bearing_between_waypoints,
    calculate_position_along_track_using_waypoints,
    calculate_position_at_certain_time,
    convert_angle_0_to_2_pi_to_minus_pi_to_pi,
    convert_angle_minus_pi_to_pi_to_0_to_2_pi,
)


def generate_encounter(
    desired_encounter_type: EncounterType,
    own_ship: OwnShip,
    target_ships_static: List[ShipStatic],
    encounter_number: int,
    beta_default: Optional[Union[List[float], float]],
    relative_sog_default: Optional[float],
    vector_time_default: Optional[float],
    settings: EncounterSettings,
) -> Tuple[TargetShip, bool]:
    """
    Generate an encounter.

    Params:
        * desired_encounter_type: Desired encounter to be generated
        * own_ship: Dict, information about own ship that will encounter a target ship
        * target_ships_static: List of target ships including static information that
          may be used in an encounter
        * encounter_number: Integer, used to naming the target ships. target_ship_1,2 etc.
        * beta_default: User defined beta. If not set, this is None.
        * relative_sog_default: User defined relative sog between own ship and
                                target ship. If not set, this is None.
        * vector_time_default: User defined vector time. If not set, this is None.
        * settings: Encounter settings

    Returns
    -------
        * target_ship: target ship information, such as initial position, sog and cog
        * encounter_found: True=encounter found, False=encounter not found
    """
    encounter_found: bool = False
    outer_counter: int = 0

    # Initiating some variables which later will be set if an encounter is found
    assert own_ship.initial is not None
    target_ship_initial_position: Position = own_ship.initial.position
    target_ship_sog: float = 0
    target_ship_cog: float = 0

    # Initial posision of own ship used as reference point for lat_lon0
    lat_lon0: Position = Position(
        latitude=own_ship.initial.position.latitude,
        longitude=own_ship.initial.position.longitude,
    )

    target_ship_static: ShipStatic = decide_target_ship(target_ships_static)
    assert target_ship_static is not None

    # Searching for encounter. Two loops used. Only vector time is locked in the
    # first loop. In the second loop, beta and sog are assigned.
    while not encounter_found and outer_counter < 5:
        outer_counter += 1
        inner_counter: int = 0

        # resetting vector_time, beta and relative_sog to default values before
        # new search for situation is done
        vector_time: Union[float, None] = vector_time_default

        if vector_time is None:
            vector_time = random.uniform(settings.vector_range[0], settings.vector_range[1])
        if beta_default is None:
            beta: float = assign_beta(desired_encounter_type, settings)
        elif isinstance(beta_default, List):
            beta: float = assign_beta_from_list(beta_default)
        else:
            beta: float = beta_default

        # Own ship
        assert own_ship.initial is not None
        assert own_ship.waypoints is not None
        # Assuming ship is pointing in the direction of wp1
        own_ship_cog = calculate_bearing_between_waypoints(
            own_ship.waypoints[0].position, own_ship.waypoints[1].position
        )
        own_ship_position_future = calculate_position_along_track_using_waypoints(
            own_ship.waypoints,
            own_ship.initial.sog,
            vector_time,
        )

        # Target ship
        target_ship_position_future: Position = assign_future_position_to_target_ship(
            own_ship_position_future, lat_lon0, settings.max_meeting_distance
        )

        while not encounter_found and inner_counter < 5:
            inner_counter += 1
            relative_sog = relative_sog_default
            if relative_sog is None:
                min_target_ship_sog = (
                    calculate_min_vector_length_target_ship(
                        own_ship.initial.position,
                        own_ship_cog,
                        target_ship_position_future,
                        beta,
                        lat_lon0,
                    )
                    / vector_time
                )

                target_ship_sog: float = assign_sog_to_target_ship(
                    desired_encounter_type,
                    own_ship.initial.sog,
                    min_target_ship_sog,
                    settings.relative_speed,
                )
            else:
                target_ship_sog: float = relative_sog * own_ship.initial.sog

            assert target_ship_static.speed_max is not None
            target_ship_sog = round(np.minimum(target_ship_sog, target_ship_static.speed_max), 1)

            target_ship_vector_length = target_ship_sog * vector_time
            start_position_target_ship, position_found = find_start_position_target_ship(
                own_ship.initial.position,
                lat_lon0,
                own_ship_cog,
                target_ship_position_future,
                target_ship_vector_length,
                beta,
                desired_encounter_type,
                settings,
            )

            if position_found:
                target_ship_initial_position: Position = start_position_target_ship
                target_ship_cog: float = calculate_ship_cog(
                    target_ship_initial_position, target_ship_position_future, lat_lon0
                )
                encounter_ok: bool = check_encounter_evolvement(
                    own_ship,
                    own_ship_cog,
                    own_ship.initial.position,
                    lat_lon0,
                    target_ship_sog,
                    target_ship_cog,
                    target_ship_position_future,
                    desired_encounter_type,
                    settings,
                )

                if settings.disable_land_check is False:
                    # Check if trajectory passes land
                    trajectory_on_land = path_crosses_land(
                        target_ship_initial_position,
                        target_ship_sog,
                        target_ship_cog,
                        lat_lon0,
                        settings.situation_length,
                    )
                    encounter_found = encounter_ok and not trajectory_on_land
                else:
                    encounter_found = encounter_ok

    if encounter_found:
        target_ship_static.id = uuid4()
        target_ship_static.name = f"target_ship_{encounter_number}"
        target_ship_initial: Initial = Initial(
            position=target_ship_initial_position,
            sog=target_ship_sog,
            cog=target_ship_cog,
            heading=target_ship_cog,
            nav_status=AISNavStatus.UNDER_WAY_USING_ENGINE,
        )
        target_ship_waypoint0 = Waypoint(
            position=target_ship_initial_position.model_copy(deep=True), turn_radius=None, data=None
        )

        future_position_target_ship = calculate_position_at_certain_time(
            target_ship_initial_position,
            lat_lon0,
            target_ship_sog,
            target_ship_cog,
            settings.situation_length,
        )

        target_ship_waypoint1 = Waypoint(
            position=future_position_target_ship, turn_radius=None, data=None
        )
        waypoints = [target_ship_waypoint0, target_ship_waypoint1]

        target_ship = TargetShip(
            static=target_ship_static, initial=target_ship_initial, waypoints=waypoints
        )
    else:
        # Since encounter is not found, using initial values from own ship. Will not be taken into use.
        target_ship = TargetShip(static=target_ship_static, initial=own_ship.initial, waypoints=None)
    return target_ship, encounter_found


def check_encounter_evolvement(
    own_ship: OwnShip,
    own_ship_cog: float,
    own_ship_position_future: Position,
    lat_lon0: Position,
    target_ship_sog: float,
    target_ship_cog: float,
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

    own_ship_sog: float = own_ship.initial.sog
    evolve_time: float = settings.evolve_time

    # Calculating position back in time to ensure that the encounter do not change from one type
    # to another before the encounter is started
    encounter_preposition_target_ship = calculate_position_at_certain_time(
        target_ship_position_future,
        lat_lon0,
        target_ship_sog,
        target_ship_cog,
        -evolve_time,
    )
    encounter_preposition_own_ship = calculate_position_at_certain_time(
        own_ship_position_future,
        lat_lon0,
        own_ship_sog,
        own_ship_cog,
        -evolve_time,
    )
    pre_beta, pre_alpha = calculate_relative_bearing(
        encounter_preposition_own_ship,
        own_ship_cog,
        encounter_preposition_target_ship,
        target_ship_cog,
        lat_lon0,
    )

    pre_colreg_state = determine_colreg(
        pre_alpha, pre_beta, theta13_criteria, theta14_criteria, theta15_criteria, theta15
    )

    encounter_ok: bool = pre_colreg_state == desired_encounter_type

    return encounter_ok


def define_own_ship(
    desired_traffic_situation: SituationInput,
    own_ship_static: ShipStatic,
    encounter_settings: EncounterSettings,
    lat_lon0: Position,
) -> OwnShip:
    """
    Define own ship based on information in desired traffic situation.

    Params:
        * desired_traffic_situation: Information about type of traffic situation to generate
        * own_ship_static: Static information of own ship.
        * encounter_settings: Necessary setting for the encounter
        * lat_lon0: Reference position [deg]

    Returns
    -------
        * own_ship: Own ship
    """
    own_ship_initial: Initial = desired_traffic_situation.own_ship.initial
    if desired_traffic_situation.own_ship.waypoints is None:
        # If waypoints are not given, let initial position be the first waypoint,
        # then calculate second waypoint some time in the future
        own_ship_waypoint0 = Waypoint(
            position=own_ship_initial.position.model_copy(deep=True), turn_radius=None, data=None
        )
        ship_position_future = calculate_position_at_certain_time(
            own_ship_initial.position,
            lat_lon0,
            own_ship_initial.sog,
            own_ship_initial.cog,
            encounter_settings.situation_length,
        )
        own_ship_waypoint1 = Waypoint(position=ship_position_future, turn_radius=None, data=None)
        own_ship_waypoints: List[Waypoint] = [own_ship_waypoint0, own_ship_waypoint1]
    elif len(desired_traffic_situation.own_ship.waypoints) == 1:
        # If one waypoint is given, use initial position as first waypoint
        own_ship_waypoint0 = Waypoint(
            position=own_ship_initial.position.model_copy(deep=True), turn_radius=None, data=None
        )
        own_ship_waypoint1 = desired_traffic_situation.own_ship.waypoints[0]
        own_ship_waypoints: List[Waypoint] = [own_ship_waypoint0, own_ship_waypoint1]
    else:
        own_ship_waypoints: List[Waypoint] = desired_traffic_situation.own_ship.waypoints

    own_ship = OwnShip(
        static=own_ship_static,
        initial=own_ship_initial,
        waypoints=own_ship_waypoints,
    )

    return own_ship


def calculate_min_vector_length_target_ship(
    own_ship_position: Position,
    own_ship_cog: float,
    target_ship_position_future: Position,
    desired_beta: float,
    lat_lon0: Position,
) -> float:
    """
    Calculate minimum vector length (target ship sog x vector). This will
    ensure that ship sog is high enough to find proper situation.

    Params:
        * own_ship_position: Own ship initial position, latitudinal [rad] and longitudinal [rad]
        * own_ship_cog: Own ship initial cog
        * target_ship_position_future: Target ship future position
        * desired_beta: Desired relative bearing between
        * lat_lon0: Reference point, latitudinal [rad] and longitudinal [rad]

    Returns
    -------
        * min_vector_length: Minimum vector length (target ship sog x vector)
    """
    psi: float = own_ship_cog + desired_beta

    own_ship_position_north, own_ship_position_east, _ = llh2flat(
        own_ship_position.latitude, own_ship_position.longitude, lat_lon0.latitude, lat_lon0.longitude
    )
    target_ship_position_future_north, target_ship_position_future_east, _ = llh2flat(
        target_ship_position_future.latitude,
        target_ship_position_future.longitude,
        lat_lon0.latitude,
        lat_lon0.longitude,
    )

    p_1 = np.array([own_ship_position_north, own_ship_position_east])
    p_2 = np.array([own_ship_position_north + np.cos(psi), own_ship_position_east + np.sin(psi)])
    p_3 = np.array([target_ship_position_future_north, target_ship_position_future_east])

    min_vector_length: float = float(np.abs(np.cross(p_2 - p_1, p_3 - p_1) / np.linalg.norm(p_2 - p_1)))

    return min_vector_length


def find_start_position_target_ship(
    own_ship_position: Position,
    lat_lon0: Position,
    own_ship_cog: float,
    target_ship_position_future: Position,
    target_ship_vector_length: float,
    desired_beta: float,
    desired_encounter_type: EncounterType,
    settings: EncounterSettings,
) -> Tuple[Position, bool]:
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

    n_1, e_1, _ = llh2flat(
        own_ship_position.latitude, own_ship_position.longitude, lat_lon0.latitude, lat_lon0.longitude
    )
    n_2, e_2, _ = llh2flat(
        target_ship_position_future.latitude,
        target_ship_position_future.longitude,
        lat_lon0.latitude,
        lat_lon0.longitude,
    )
    v_r: float = target_ship_vector_length
    psi: float = own_ship_cog + desired_beta

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
    start_position_target_ship = target_ship_position_future.model_copy(deep=True)

    if b**2 - 4 * a * c <= 0.0:
        # Do not run calculation of target ship start position. Return fallback values.
        return start_position_target_ship, start_position_found

    # Calculation of target ship start position
    s_1 = (-b + np.sqrt(b**2 - 4 * a * c)) / (2 * a)
    s_2 = (-b - np.sqrt(b**2 - 4 * a * c)) / (2 * a)

    e_31 = round(e_1 + s_1 * (e_4 - e_1), 0)
    n_31 = round(n_1 + s_1 * (n_4 - n_1), 0)
    e_32 = round(e_1 + s_2 * (e_4 - e_1), 0)
    n_32 = round(n_1 + s_2 * (n_4 - n_1), 0)

    lat31, lon31, _ = flat2llh(n_31, e_31, lat_lon0.latitude, lat_lon0.longitude)
    target_ship_cog_1: float = calculate_ship_cog(
        pos_0=Position(latitude=lat31, longitude=lon31),
        pos_1=target_ship_position_future,
        lat_lon0=lat_lon0,
    )
    beta1, alpha1 = calculate_relative_bearing(
        position_own_ship=own_ship_position,
        heading_own_ship=own_ship_cog,
        position_target_ship=Position(latitude=lat31, longitude=lon31),
        heading_target_ship=target_ship_cog_1,
        lat_lon0=lat_lon0,
    )
    colreg_state1: EncounterType = determine_colreg(
        alpha1, beta1, theta13_criteria, theta14_criteria, theta15_criteria, theta15
    )

    lat32, lon32, _ = flat2llh(n_32, e_32, lat_lon0.latitude, lat_lon0.longitude)
    target_ship_cog_2 = calculate_ship_cog(
        pos_0=Position(latitude=lat32, longitude=lon32),
        pos_1=target_ship_position_future,
        lat_lon0=lat_lon0,
    )
    beta2, alpha2 = calculate_relative_bearing(
        position_own_ship=own_ship_position,
        heading_own_ship=own_ship_cog,
        position_target_ship=Position(latitude=lat32, longitude=lon32),
        heading_target_ship=target_ship_cog_2,
        lat_lon0=lat_lon0,
    )
    colreg_state2: EncounterType = determine_colreg(
        alpha2, beta2, theta13_criteria, theta14_criteria, theta15_criteria, theta15
    )

    if (
        desired_encounter_type is colreg_state1
        and np.abs(convert_angle_0_to_2_pi_to_minus_pi_to_pi(np.abs(beta1 - desired_beta))) < 0.01
    ):
        start_position_target_ship = Position(latitude=lat31, longitude=lon31)
        start_position_found = True
    elif (
        desired_encounter_type is colreg_state2
        and np.abs(convert_angle_0_to_2_pi_to_minus_pi_to_pi(np.abs(beta2 - desired_beta))) < 0.01
    ):
        start_position_target_ship = Position(latitude=lat32, longitude=lon32)
        start_position_found = True

    return start_position_target_ship, start_position_found


def assign_future_position_to_target_ship(
    own_ship_position_future: Position,
    lat_lon0: Position,
    max_meeting_distance: float,
) -> Position:
    """
    Randomly assign future position of target ship. If drawing a circle with radius
    max_meeting_distance around future position of own ship, future position of
    target ship shall be somewhere inside this circle.

    Params:
        * own_ship_position_future: Dict, own ship position at a given time in the
            future, {north, east}
        * lat_lon0: Reference point, latitudinal [rad] and longitudinal [rad]
        * max_meeting_distance: Maximum distance between own ship and target ship at
            a given time in the future [m]

    Returns
    -------
        future_position_target_ship: Future position of target ship {north, east} [m]
    """
    random_angle = random.uniform(0, 1) * 2 * np.pi
    random_distance = random.uniform(0, 1) * max_meeting_distance

    own_ship_position_future_north, own_ship_position_future_east, _ = llh2flat(
        own_ship_position_future.latitude,
        own_ship_position_future.longitude,
        lat_lon0.latitude,
        lat_lon0.longitude,
    )
    north: float = own_ship_position_future_north + random_distance * np.cos(random_angle)
    east: float = own_ship_position_future_east + random_distance * np.sin(random_angle)
    latitude, longitude, _ = flat2llh(north, east, lat_lon0.latitude, lat_lon0.longitude)
    return Position(latitude=latitude, longitude=longitude)


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
    alpha_2_pi: float = alpha if alpha >= 0.0 else alpha + 2 * np.pi
    beta_pi: float = beta if (beta >= 0.0) & (beta <= np.pi) else beta - 2 * np.pi

    # Find appropriate rule set
    if (beta > theta15[0]) & (beta < theta15[1]) & (abs(alpha) - theta13_criteria <= 0.001):
        return EncounterType.OVERTAKING_STAND_ON
    if (
        (alpha_2_pi > theta15[0])
        & (alpha_2_pi < theta15[1])
        & (abs(beta_pi) - theta13_criteria <= 0.001)
    ):
        return EncounterType.OVERTAKING_GIVE_WAY
    if (abs(beta_pi) - theta14_criteria <= 0.001) & (abs(alpha) - theta14_criteria <= 0.001):
        return EncounterType.HEAD_ON
    if (beta > 0) & (beta < theta15[0]) & (alpha > -theta15[0]) & (alpha - theta15_criteria <= 0.001):
        return EncounterType.CROSSING_GIVE_WAY
    if (
        (alpha_2_pi > 0)
        & (alpha_2_pi < theta15[0])
        & (beta_pi > -theta15[0])
        & (beta_pi - theta15_criteria <= 0.001)
    ):
        return EncounterType.CROSSING_STAND_ON
    return EncounterType.NO_RISK_COLLISION


def calculate_relative_bearing(
    position_own_ship: Position,
    heading_own_ship: float,
    position_target_ship: Position,
    heading_target_ship: float,
    lat_lon0: Position,
) -> Tuple[float, float]:
    """
    Calculate relative bearing between own ship and target ship, both seen from
    own ship and seen from target ship.

    Params:
        * position_own_ship: Own ship position {latitude, longitude} [rad]
        * heading_own_ship: Own ship heading [rad]
        * position_target_ship: Target ship position {latitude, longitude} [rad]
        * heading_target_ship: Target ship heading [rad]
        * lat_lon0: Reference point, latitudinal [rad] and longitudinal [rad]

    Returns
    -------
        * beta: relative bearing between own ship and target ship seen from own ship [rad]
        * alpha: relative bearing between target ship and own ship seen from target ship [rad]
    """
    # POSE combination of relative bearing and contact angle
    n_own_ship, e_own_ship, _ = llh2flat(
        position_own_ship.latitude, position_own_ship.longitude, lat_lon0.latitude, lat_lon0.longitude
    )
    n_target_ship, e_target_ship, _ = llh2flat(
        position_target_ship.latitude,
        position_target_ship.longitude,
        lat_lon0.latitude,
        lat_lon0.longitude,
    )

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

    return beta, alpha


def calculate_ship_cog(pos_0: Position, pos_1: Position, lat_lon0: Position) -> float:
    """
    Calculate ship cog between two waypoints.

    Params:
        * waypoint_0: Dict, waypoint {latitude, longitude} [rad]
        * waypoint_1: Dict, waypoint {latitude, longitude} [rad]

    Returns
    -------
        * cog: Ship cog [rad]
    """
    n_0, e_0, _ = llh2flat(pos_0.latitude, pos_0.longitude, lat_lon0.latitude, lat_lon0.longitude)
    n_1, e_1, _ = llh2flat(pos_1.latitude, pos_1.longitude, lat_lon0.latitude, lat_lon0.longitude)

    cog: float = np.arctan2(e_1 - e_0, n_1 - n_0)
    if cog < 0.0:
        cog += 2 * np.pi
    return round(cog, 3)


def assign_vector_time(vector_time_range: List[float]):
    """
    Assign random (uniform) vector time.

    Params:
        * vector_range: Minimum and maximum value for vector time

    Returns
    -------
        * vector_time: Vector time [min]
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
        * own_ship_sog: Own ship sog [m/s]
        * min_target_ship_sog: Minimum target ship sog [m/s]
        * relative_sog_setting: Relative sog setting dependent on encounter [-]

    Returns
    -------
        * target_ship_sog: Target ship sog [m/s]
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


def assign_beta_from_list(beta_limit: List[float]) -> float:
    """
    Assign random (uniform) relative bearing beta between own ship
    and target ship depending between the limits given by beta_limit.

    Params:
        * beta_limit: Limits for beta

    Returns
    -------
        * Relative bearing between own ship and target ship seen from own ship [rad]
    """
    assert len(beta_limit) == 2
    beta: float = beta_limit[0] + random.uniform(0, 1) * (beta_limit[1] - beta_limit[0])
    return beta


def assign_beta(encounter_type: EncounterType, settings: EncounterSettings) -> float:
    """
    Assign random (uniform) relative bearing beta between own ship
    and target ship depending on type of encounter.

    Params:
        * encounter_type: Type of encounter
        * settings: Encounter settings

    Returns
    -------
        * Relative bearing between own ship and target ship seen from own ship [rad]
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
        return convert_angle_minus_pi_to_pi_to_0_to_2_pi(
            -theta15[1] + random.uniform(0, 1) * (theta15[1] + theta15_crit)
        )
    return 0.0


def decide_target_ship(target_ships_static: List[ShipStatic]) -> ShipStatic:
    """
    Randomly pick a target ship from a list of target ships.

    Params:
        * target_ships: list of target ships with static information

    Returns
    -------
        * The target ship, info of type, size etc.
    """
    num_target_ships: int = len(target_ships_static)
    target_ship_to_use: int = random.randint(1, num_target_ships)
    target_ship_static: ShipStatic = target_ships_static[target_ship_to_use - 1]
    return target_ship_static.model_copy(deep=True)
