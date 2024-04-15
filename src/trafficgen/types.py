"""Domain specific data types used in trafficgen."""

from enum import Enum
from typing import List, Optional, Union

from maritime_schema.types.caga import Initial, Waypoint
from pydantic import BaseModel
from pydantic.fields import Field


def to_camel(string: str) -> str:
    """Return a camel case formated string from snake case string."""

    words = string.split("_")
    return words[0] + "".join(word.capitalize() for word in words[1:])


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

    class Config:
        """For converting parameters written to file from snake to camel case."""

        alias_generator = to_camel
        populate_by_name = True


class EncounterClassification(BaseModel):
    """Data type for the encounter classification."""

    theta13_criteria: float
    theta14_criteria: float
    theta15_criteria: float
    theta15: List[float]

    class Config:
        """For converting parameters written to file from snake to camel case."""

        alias_generator = to_camel
        populate_by_name = True


class EncounterRelativeSpeed(BaseModel):
    """Data type for relative speed between two ships in an encounter."""

    overtaking_stand_on: List[float]
    overtaking_give_way: List[float]
    head_on: List[float]
    crossing_give_way: List[float]
    crossing_stand_on: List[float]

    class Config:
        """For converting parameters written to file from snake to camel case."""

        alias_generator = to_camel
        populate_by_name = True


class EncounterSettings(BaseModel):
    """Data type for encounter settings."""

    classification: EncounterClassification
    relative_speed: EncounterRelativeSpeed
    vector_range: List[float]
    common_vector: float
    situation_length: float
    max_meeting_distance: float
    evolve_time: float
    disable_land_check: bool

    class Config:
        """For converting parameters written to file from snake to camel case."""

        alias_generator = to_camel
        populate_by_name = True


class OwnShipInitial(BaseModel):
    """Data type for initial data for the own ship used for generating a situation."""

    initial: Initial
    waypoints: Optional[List[Waypoint]] = Field(None, description="An array of `Waypoint` objects.")


class SituationInput(BaseModel):
    """Data type for inputs needed for generating a situations."""

    title: str
    description: str
    num_situations: int
    own_ship: OwnShipInitial
    encounters: List[Encounter]

    class Config:
        """For converting parameters written to file from snake to camel case."""

        alias_generator = to_camel
        populate_by_name = True
