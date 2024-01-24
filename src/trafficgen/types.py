"""Domain specific data types used in trafficgen."""

from enum import Enum
from typing import List, Union
from uuid import UUID

from pydantic import BaseModel


def to_camel(string: str) -> str:
    """Return a camel case formated string from snake case string."""

    words = string.split("_")
    return words[0] + "".join(word.capitalize() for word in words[1:])


class Position(BaseModel):
    """Data type for a ship's position with attributes north, east in [m]."""

    north: float = 0.0
    east: float = 0.0
    latitude: float = 0.0
    longitude: float = 0.0


class Initial(BaseModel):
    """Data type for a (ship) initial data."""

    position: Position = Position()
    sog: float = 0.0
    cog: float = 0.0
    heading: float = 0.0


class Waypoint(BaseModel):
    """Data type for a (ship) waypoint."""

    position: Position = Position()
    sog: float = 0.0
    heading: float = 0.0


class GeneralShipType(str, Enum):
    """Enumeration of ship types."""

    WING_IN_GROUND = "Wing in ground"
    FISHING = "Fishing"
    TOWING = "Towing"
    DREDGING_OR_UNDERWATER_OPS = "Dredging or underwater ops"
    DIVING_OPS = "Diving ops"
    MILITARY_OPS = "Military ops"
    SAILING = "Sailing"
    PLEASURE_CRAFT = "Pleasure Craft"
    HIGH_SPEED_CRAFT = "High speed craft"
    PILOT_VESSEL = "Pilot Vessel"
    SEARCH_AND_RESCUE_VESSEL = "Search and Rescue vessel"
    TUG = "Tug"
    PORT_TENDER = "Port Tender"
    ANTI_POLLUTION = "Anti-pollution"
    LAW_ENFORCEMENT = "Law Enforcement"
    MEDICAL_TRANSPORT = "Medical Transport"
    NONCOMBATANT_SHIP = "Noncombatant ship"
    PASSENGER = "Passenger/Ro-Ro Cargo Ship"
    CARGO = "Cargo"
    TANKER = "Tanker"
    OTHER_TYPE = "Other Type"


class AISNavStatus(str, Enum):
    """Enumeration of AIS navigation status types."""

    UNDER_WAY_USING_ENGINE = "Under way using engine"
    AT_ANCHOR = "At anchor"
    NOT_UNDER_COMMAND = "Not under command"
    RESTRICTED_MANOEUVERABILITY = "Restricted manoeuverability"
    CONSTRAINED_BY_HER_DRAUGHT = "Constrained by her draught"
    MOORED = "Moored"
    AGROUND = "Aground"
    ENGAGED_IN_FISHING = "Engaged in fishing"
    UNDER_WAY_SAILING = "Under way sailing"
    RESERVED_FOR_FUTURE_AMENDMENT_OF_NAVIGATIONAL_STATUS_FOR_HSC = (
        "Reserved for future amendment of navigational status for HSC"
    )
    RESERVED_FOR_FUTURE_AMENDMENT_OF_NAVIGATIONAL_STATUS_FOR_WIG = (
        "Reserved for future amendment of navigational status for WIG"
    )
    RESERVED_FOR_FUTURE_USE_1 = "Reserved for future use 1"
    RESERVED_FOR_FUTURE_USE_2 = "Reserved for future use 2"
    RESERVED_FOR_FUTURE_USE_3 = "Reserved for future use 3"
    AIS_SART_IS_ACTIVE = "AIS SART is active"
    NOT_DEFINED_DEFAULT = "Not defined (default)"


class ShipStatic(BaseModel):
    """Static ship data that will not change during the scenario."""

    id: UUID
    length: float
    width: float
    height: float
    speed_max: float
    mmsi: int
    name: str
    ship_type: GeneralShipType

    class Config:
        """For converting parameters written to file from snake to camel case."""

        alias_generator = to_camel
        populate_by_name = True


class Ship(BaseModel):
    """Data type for a ship."""

    static: Union[ShipStatic, None] = None
    initial: Union[Initial, None] = None
    waypoints: Union[List[Waypoint], None] = None


class OwnShip(Ship):
    """Data type for own ship."""

    pass


class TargetShip(Ship):
    """Data type for a target ship."""

    pass


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


class TrafficSituation(BaseModel):
    """Data type for a traffic situation."""

    title: str
    input_file_name: Union[str, None] = None
    common_vector: Union[float, None] = None
    own_ship: Union[Ship, None] = None
    num_situations: Union[int, None] = None
    encounter: Union[List[Encounter], None] = None
    target_ships: Union[List[TargetShip], None] = None

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
    situation_length: float
    max_meeting_distance: float
    evolve_time: float

    class Config:
        """For converting parameters written to file from snake to camel case."""

        alias_generator = to_camel
        populate_by_name = True
