"""Domain specific data types used in trafficgen."""

from enum import Enum
from typing import List, Union

from pydantic import BaseModel


class Position(BaseModel):
    """Data type for a ship's position with attributes north, east in [m]."""

    north: float = 0.0
    east: float = 0.0
    latitude: float = 0.0
    longitude: float = 0.0


class Pose(BaseModel):
    """Data type for a (ship) pose."""

    speed: float = 0.0
    course: float = 0.0
    position: Position = Position()


class ShipType(Enum):
    """Enumeration of ship types."""

    PASSENGER_RORO = "Passenger/Ro-Ro Cargo Ship"
    GENERAL_CARGO = "General Cargo Ship"
    FISHING = "Fishing"
    MILITARY = "Military ops"


class StaticShipData(BaseModel):
    """Data type for static ship data."""

    length: float
    width: float
    height: float
    speed_max: float
    mmsi: int
    name: str
    ship_type: ShipType


class Ship(BaseModel):
    """Data type for a ship."""

    static: Union[StaticShipData, None] = None
    start_pose: Union[Pose, None] = None
    waypoints: Union[List[Position], None] = None


class TargetShip(Ship):
    """Data type for a target ship."""

    id: Union[int, None] = None


class EncounterType(Enum):
    """Enumeration of encounter types."""

    OVERTAKING_STAND_ON = "overtaking-stand-on"
    OVERTAKING_GIVE_WAY = "overtaking-give-way"
    HEAD_ON = "head-on"
    CROSSING_GIVE_WAY = "crossing-give-way"
    CROSSING_STAND_ON = "crossing-stand-on"
    NO_RISK_COLLISION = "noRiskCollision"


class Encounter(BaseModel):
    """Data type for an encounter."""

    desired_encounter_type: EncounterType
    beta: Union[float, None] = None
    relative_speed: Union[float, None] = None
    vector_time: Union[float, None] = None


class Situation(BaseModel):
    """Data type for a traffic situation."""

    title: str
    input_file_name: Union[str, None] = None
    common_vector: Union[float, None] = None
    lat_lon_0: Union[List[float], None] = None
    own_ship: Union[Ship, None] = None
    num_situations: Union[int, None] = None
    encounter: Union[List[Encounter], None] = None
    target_ship: Union[List[TargetShip], None] = None


class EncounterClassification(BaseModel):
    """Data type for the encounter classification."""

    theta13_criteria: float
    theta14_criteria: float
    theta15_criteria: float
    theta15: List[float]


class EncounterRelativeSpeed(BaseModel):
    """Data type for relative speed between two ships in an encounter."""

    overtaking_stand_on: List[float]
    overtaking_give_way: List[float]
    head_on: List[float]
    crossing_give_way: List[float]
    crossing_stand_on: List[float]


class EncounterSettings(BaseModel):
    """Data type for encounter settings."""

    classification: EncounterClassification
    relative_speed: EncounterRelativeSpeed
    vector_range: List[float]
    situation_length: float
    max_meeting_distance: float
    evolve_time: float
    lat_lon_0: List[float]
