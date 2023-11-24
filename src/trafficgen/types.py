"""Domain specific data types used in trafficgen."""

from enum import StrEnum
from typing import List

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


class ShipType(StrEnum):
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

    static: StaticShipData | None = None
    start_pose: Pose | None = None
    waypoints: List[Position] | None = None


class TargetShip(Ship):
    """Data type for a target ship."""

    id: int | None = None


class EncounterType(StrEnum):
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
    beta: float | None = None
    relative_speed: float | None = None
    vector_time: float | None = None


class Situation(BaseModel):
    """Data type for a traffic situation."""

    title: str
    input_file_name: str | None = None
    common_vector: float | None = None
    lat_lon_0: List[float] | None = None
    own_ship: Ship | None = None
    num_situations: int | None = None
    encounter: List[Encounter] | None = None
    target_ship: List[TargetShip] | None = None


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
    max_meeting_distance: float
    evolve_time: float
    lat_lon_0: List[float]
