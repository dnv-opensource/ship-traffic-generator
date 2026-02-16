"""Domain specific data types used in trafficgen."""

from __future__ import annotations

import datetime
from enum import Enum
from importlib.metadata import PackageNotFoundError, version
from typing import Annotated, Any, Self

from pydantic import BaseModel, ConfigDict
from pydantic.fields import Field
from pyproj import Geod

try:
    project_version = version("trafficgen")
except PackageNotFoundError:
    project_version = "-.-"


def to_camel(string: str) -> str:
    """Return a camel case formated string from snake case string."""
    words = string.split("_")
    return words[0] + "".join(word.capitalize() for word in words[1:])


class BaseModelConfig(BaseModel):
    """Enables the alias_generator for all cases."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class StringIntEnumMixin(str, Enum):
    """
    A mixin class for Enums that allows both integers and strings to specify a type.

    This class supports the following input formats:
    - Integer: 1
    - Integer in string form: "1"
    - Case-insensitive string value: "underway using engine"
    - String value with underscores: "underway_using_engine"
    """

    def __init__(self, str_value: str, num_value: int) -> None:
        self._value_ = str_value
        self.num_value = num_value

    def __new__(cls: type[Self], str_value: str, num_value: int) -> Self:  # noqa: D102
        obj = str.__new__(cls, str_value)
        obj._value_ = str_value  # Assign the string value
        obj.num_value = num_value
        return obj

    @classmethod
    def _missing_(cls: type[Self], value: object) -> Self | None:
        # Handle case-insensitive string matching and underscores
        if isinstance(value, str):
            value_str = value.replace("_", " ").lower()
            for member in cls:
                if member.value.lower() == value_str:
                    return member
            # Handle numeric values disguised as strings
            if value.isdigit():
                value = int(value)
        # Handle numeric values
        if isinstance(value, int):
            for member in cls:
                if member.num_value == value:
                    return member
        return None


class AisShipType(StringIntEnumMixin):
    """
    AIS Ship Type (not including cargo type).

    Source: https://www.itu.int/dms_pubrec/itu-r/rec/m/R-REC-M.1371-5-201402-I!!PDF-E.pdf#page=116.
    """

    NOT_AVAILABLE = ("Not available", 0)
    WING_IN_GROUND = ("Wing in ground", 20)
    FISHING = ("Fishing", 30)
    TOWING = ("Towing", 31)
    TOWING_LARGE = ("Towing large", 32)  # exceeds 200m length or 25m breadth
    DREDGING_OR_UNDERWATER_OPS = ("Dredging or underwater operations", 33)
    DIVING_OPS = ("Diving operations", 34)
    MILITARY_OPS = ("Military operations", 35)
    SAILING = ("Sailing", 36)
    PLEASURE_CRAFT = ("Pleasure craft", 37)
    HIGH_SPEED_CRAFT = ("High speed craft", 40)
    PILOT_VESSEL = ("Pilot vessel", 50)
    SEARCH_AND_RESCUE_VESSEL = ("Search and rescue vessel", 51)
    TUG = ("Tug", 52)
    PORT_TENDER = ("Port tender", 53)
    ANTI_POLLUTION_EQUIPMENT = ("Anti-pollution equipment", 54)
    LAW_ENFORCEMENT = ("Law enforcement", 55)
    MEDICAL_TRANSPORT = ("Medical transport", 58)
    NONCOMBATANT = ("Noncombatant", 59)
    PASSENGER = ("Passenger", 60)
    CARGO = ("Cargo", 70)
    TANKER = ("Tanker", 80)
    OTHER = ("Other", 90)


class AisNavStatus(StringIntEnumMixin):
    """
    AIS Navigational Status.

    Source: https://www.itu.int/dms_pubrec/itu-r/rec/m/R-REC-M.1371-5-201402-I!!PDF-E.pdf#page=113.
    """

    UNDER_WAY_USING_ENGINE = ("Under way using engine", 0)
    AT_ANCHOR = ("At anchor", 1)
    NOT_UNDER_COMMAND = ("Not under command", 2)
    RESTRICTED_MANEUVERABILITY = ("Restricted maneuverability", 3)
    CONSTRAINED_BY_HER_DRAUGHT = ("Constrained by her draught", 4)
    MOORED = ("Moored", 5)
    AGROUND = ("Aground", 6)
    ENGAGED_IN_FISHING = ("Engaged in fishing", 7)
    UNDER_WAY_SAILING = ("Under way sailing", 8)
    RESERVED_FOR_FUTURE_AMENDMENT_DG_HS_MP_C_HSC = (
        "Reserved for future amendment DG, HS, MP, C, HSC",
        9,
    )
    RESERVED_FOR_FUTURE_AMENDMENT_DG_HS_MP_A_WIG = (
        "Reserved for future amendment DG, HS, MP, A, WIG",
        10,
    )
    POWER_DRIVEN_VESSEL_TOWING_ASTERN = ("Power-driven vessel towing astern", 11)
    POWER_DRIVEN_VESSEL_PUSHING_AHEAD_OR_TOWING_ALONGSIDE = (
        "Power-driven vessel pushing ahead or towing alongside",
        12,
    )
    RESERVED_FOR_FUTURE_USE = ("Reserved for future use", 13)
    AIS_SART_ACTIVE = ("AIS-SART (active)", 14)
    UNDEFINED = ("Undefined (default)", 15)


class PathType(str, Enum):
    """Specifies the control-point model used to define the path for the ship to follow."""

    RTZ = "rtz"
    BEZIER = "bezier"
    LINEAR = "linear"


class InterpolationMethod(str, Enum):
    """Specifies the interpolation method used to interpolate between two values."""

    LINEAR = "linear"
    COSINE = "cosine"
    SMOOTHSTEP = "smoothstep"
    ACCELERATE = "accelerate"
    DECELERATE = "decelerate"
    ORDINAL = "ordinal"


class Dimensions(BaseModelConfig):
    """
        Key Ship Dimensions.

                  Bow
                  (a)
                   ^
                  /┆\
                 / ┆ \
                /  ┆  \
               /   ┆   \
              /    ┆    \
             │     ┆     │
             │     ┆     │
             │     ┆     │
             │     ┆     │
    Port (c) │╌╌╌╌╌♦╌╌╌╌╌│ (d) Starboard
             │     ┆     │
             │     ┆     │
             │     ┆     │
             └─────┴─────┘
                  (b)
                 Stern

              ♦ = CCRP

    """

    length: Annotated[float, Field(gt=0, description="Width of the ship in meters", examples=[130.0])] | None = None
    width: Annotated[float, Field(gt=0, description="Width of the ship in meters", examples=[30.0])] | None = None
    height: Annotated[float, Field(gt=0, description="Height of the ship in meters", examples=[15.0])] | None = None
    draught: Annotated[float, Field(gt=0, description="Draught of the ship in meters", examples=[15.0])] | None = None

    a: Annotated[float, Field(gt=0, description="Distance in meters from CCRP to Bow", examples=[80])] | None = None
    b: Annotated[float, Field(gt=0, description="Distance in meters from CCRP to Stern", examples=[20])] | None = None
    c: Annotated[float, Field(gt=0, description="Distance in meters from CCRP to Port", examples=[20])] | None = None
    d: Annotated[float, Field(gt=0, description="Distance in meters from CCRP to Starboard", examples=[20])] | None = (
        None
    )

    def __init__(self, **data: Any) -> None:  # noqa: ANN401
        super().__init__(**data)
        """If length and width are given, and not a, b, c, d, calculate them, and vice-versa"""
        if self.length and self.width and not self.a and not self.b and not self.c and not self.d:
            self.a = self.length / 2
            self.b = self.length / 2
            self.c = self.width / 2
            self.d = self.width / 2
        if self.a and self.b and self.c and self.d:
            self.length = self.a + self.b
            self.width = self.c + self.d


class ShipStatic(BaseModelConfig):
    """Static ship data that will not change during the scenario."""

    id: Annotated[int, Field(ge=0, le=2**32, description="Ship Identifier", examples=[1])]
    mmsi: (
        Annotated[
            int,
            Field(
                ge=100000000, le=999999999, description="Maritime Mobile Service Identity (MMSI)", examples=[123456789]
            ),
        ]
        | None
    ) = None
    imo: Annotated[int, Field(ge=1000000, le=9999999, description="IMO Number", examples=[1234567])] | None = None
    name: Annotated[str, Field(description="Ship name", examples=["RMS Titanic"])] | None = None

    dimensions: Annotated[Dimensions, Field(description="Key ship dimensions")] | None = None

    ship_type: Annotated[AisShipType, Field(description="General ship type, based on AIS")] | None = None

    path_type: (
        Annotated[
            PathType,
            Field(
                description=(
                    "Specifies the control-point model (e.g., Bezier, RTZ) "
                    "used to define the path for the ship to follow."
                ),
            ),
        ]
        | None
    ) = PathType.RTZ

    sog_min: (
        Annotated[float, Field(ge=0, description="Minimum ship speed over ground in knots", examples=[5.0])] | None
    ) = None
    sog_max: (
        Annotated[float, Field(ge=0, description="Maximum ship speed over ground in knots", examples=[15.0])] | None
    ) = None

    model_config = ConfigDict(extra="allow")


class GeoPosition(BaseModelConfig):
    """Data type for a geographical position."""

    lon: Annotated[float, Field(ge=-180, le=180, description="WGS-84 lon", examples=[51.2131])]
    lat: Annotated[float, Field(ge=-90, le=90, description="WGS-84 lat", examples=[51.2131])]
    model_config = ConfigDict(extra="allow")


class Position(BaseModelConfig):
    """Data type for ship position."""

    x: Annotated[float, Field(description="x-coordinate. East is positive", examples=[1123])]
    y: Annotated[float, Field(description="y-coordinate. Noth is positive", examples=[231])]


def create_position_example() -> GeoPosition:
    """Create a position class."""
    return GeoPosition(lon=57.2343, lat=10.3432)


class Initial(BaseModelConfig):
    """Data type for initial data for a ship ."""

    position: Annotated[
        GeoPosition,
        Field(
            description="Initial lon and lat of the ship.",
            examples=[create_position_example()],
        ),
    ]
    sog: Annotated[float, Field(ge=0, description="Initial ship  (SOG) ground in knots", examples=[10.0])]
    cog: Annotated[
        float,
        Field(ge=0, le=360, description="Initial ship course over ground (COG) in degrees", examples=[45.0]),
    ]
    heading: (
        Annotated[float, Field(ge=0, le=360, description="Initial ship heading in degrees", examples=[45.2])] | None
    ) = None
    nav_status: Annotated[AisNavStatus, Field(description="AIS Navigational Status")] | None = None


class DataPoint(BaseModelConfig):
    """Data type for storing data which is numerical and continuos."""

    value: (
        Annotated[float, Field(description="the value of the data at the current waypoint", examples=[12.3])] | None
    ) = None
    interp_start: (
        Annotated[
            float,
            Field(
                description=(
                    "distance before start of the next leg (NM), to start interpolating to the next leg's value"
                ),
                examples=[10],
            ),
        ]
        | None
    ) = None
    interp_end: (
        Annotated[
            float,
            Field(
                description=(
                    "distance after the start of the next leg (NM) to finish interpolating to the next leg's value"
                ),
                examples=[10],
            ),
        ]
        | None
    ) = None
    interp_method: Annotated[InterpolationMethod | str, Field(description="Method used for interpolation")] | None = (
        None
    )


data_description = (
    "The `data` field can be used to store data, which is numerical and continuous."
    "One such example is the vessels speed over ground (SOG). Every `data` object, can have the 4 following attributes:"
    "\n`value`: This is the value of the data over the current leg."
    "\n`interpStart`: This is the distance (in NM) before the leg change, where the value will start changing"
    "(via interpolation) to the new value in the next leg."
    "\n`interpEnd`: This is the distance (in NM) after the leg change, where the value will finish changing"
    "(via interpolation) to the new value in the next leg."
    "\n`interpMethod`: This sets the interpolation (linear, cosine, smoothstep, etc.) "
    "that will be used to perform the interpolation."
)


class RouteData(BaseModelConfig):
    """Data type for data along a route."""

    sog: Annotated[DataPoint, Field(description=data_description)] | None = None


class Leg(BaseModelConfig):
    """Data type for a leg."""

    starboard_xtd: Annotated[float, Field(description="Starboard XTD in NM as defined in RTZ.")] | None = None
    portside_xtd: Annotated[float, Field(description="Starboard XTD in NM as defined in RTZ.")] | None = None
    sog: Annotated[float, Field(description="Speed reference for the waypoint leg in knots")] | None = None
    data: Annotated[RouteData, Field(description=data_description)] | None = None


class Waypoint(BaseModelConfig):
    """Data type for a waypoint."""

    position: Annotated[
        GeoPosition,
        Field(description="A geographical coordinate.", examples=[GeoPosition(lon=11.2313, lat=51.2123)]),
    ]
    turn_radius: (
        Annotated[
            float, Field(description="Orthodrome turn radius in nautical miles as defined in RTZ.", examples=[200])
        ]
        | None
    ) = None
    leg: Annotated[Leg, Field(description="Current Leg information.")] | None = None


def create_ship_static_example() -> ShipStatic:
    """Create a ShipStatic class."""
    return ShipStatic(
        id=1,
        dimensions=Dimensions(a=50, b=50, c=10, d=10),
        sog_max=20.0,
        mmsi=123456789,
        name="RMS Titanic",
        ship_type=AisShipType.FISHING,
        imo=1000001,
    )


def create_initial_example() -> Initial:
    """Create a (Ship) Initial class."""
    return Initial(
        position=create_position_example(),
        sog=12.3,
        cog=284.2,
        heading=283.1,
        nav_status=AisNavStatus.UNDER_WAY_USING_ENGINE,
    )


def create_data_point_example() -> DataPoint:
    """Create a DataPoint class."""
    return DataPoint(value=12.3, interp_start=100, interp_end=100, interp_method=InterpolationMethod.LINEAR)


def create_waypoint_example() -> Waypoint:
    """Create a Waypoint class."""
    return Waypoint(
        position=create_position_example(),
        turn_radius=1.0,
        leg=Leg(data=RouteData(sog=create_data_point_example())),
    )


static_description = "Static ship information which does not change during a scenario."
initial_description = (
    "Initial pose of the ship. If `waypoints` are provided,"
    "then these should correspond to the pose of the ship at the starting waypoint"
)
waypoints_description = (
    "An array of `Waypoint` objects. Each waypoint object must have a `position` property."
    "If no turn radius is provided, it will be assumed to be `0`."
    "Additional data can be added to each waypoint leg."
)


class Ship(BaseModelConfig):
    """Data type for a ship."""

    initial: Annotated[Initial, Field(description=initial_description, examples=[create_initial_example()])] | None = (
        None
    )
    waypoints: (
        Annotated[list[Waypoint], Field(description=waypoints_description, examples=[create_waypoint_example()])] | None
    ) = None

    def __init__(self, **data: Any) -> None:  # noqa: ANN401
        super().__init__(**data)
        if not self.waypoints:
            self.waypoints = self._generate_waypoints()

    def _generate_waypoints(self) -> list[Waypoint] | None:
        """Generate waypoints if they don't exist."""
        waypoints = []

        if self.initial:
            # Create waypoints from initial position
            g = Geod(ellps="WGS84")
            lon, lat, _ = g.fwd(
                self.initial.position.lon,
                self.initial.position.lat,
                self.initial.cog,
                self.initial.sog * 0.51444 * 3600 * 3,
            )
            position1 = GeoPosition(lat=lat, lon=lon)
            waypoint1 = Waypoint(position=position1)

            position0 = GeoPosition(
                lat=self.initial.position.lat,
                lon=self.initial.position.lon,
            )
            waypoint0 = Waypoint(position=position0)

            waypoints = [waypoint0, waypoint1]
            return waypoints

        return None


class OwnShip(Ship):
    """Data type for the own ship."""

    static: Annotated[ShipStatic, Field(description=static_description, examples=[create_ship_static_example()])]

    def __init__(self, **data: Any) -> None:  # noqa: ANN401
        super().__init__(**data)
        if not self.static.name:
            self.static.name = "OS"


class TargetShip(Ship):
    """Data type for the target ship."""

    static: Annotated[ShipStatic, Field(description=static_description, examples=[create_ship_static_example()])]

    def __init__(self, **data: Any) -> None:  # noqa: ANN401
        super().__init__(**data)
        if not self.static.name:
            self.static.name = f"TGT {self.static.id}"


def create_ship_example() -> Ship:
    """Create a Ship class."""
    return Ship(
        static=create_ship_static_example(),
        initial=create_initial_example(),
        waypoints=[create_waypoint_example()],
    )


def create_own_ship_example() -> OwnShip:
    """Create a OwnShip class."""
    return OwnShip(static=create_ship_static_example(), initial=create_initial_example(), waypoints=None)


def create_target_example() -> TargetShip:
    """Create a TargetShip class."""
    return TargetShip(static=create_ship_static_example(), initial=create_initial_example(), waypoints=None)


class TrafficSituation(BaseModelConfig):
    """Data type for a traffic situation."""

    version: Annotated[str, Field(description="Ship traffic generator version number", examples=[project_version])]
    title: (
        Annotated[str, Field(description="The title of the traffic situation", examples=["overtaking_18"])] | None
    ) = None
    description: (
        Annotated[
            str,
            Field(
                description="A description of the traffic situation",
                examples=["Crossing situation with 3 target vessels in the Oslo fjord"],
            ),
        ]
        | None
    ) = None
    start_time: (
        Annotated[
            datetime.datetime,
            Field(
                description="Starting time of the situation in `ISO 8601` format `YYYY-MM-DDThh:mm:ssZ`",
                examples=[datetime.datetime(2025, 1, 1, 0, 0, 0, tzinfo=datetime.UTC)],
            ),
        ]
        | None
    ) = None
    own_ship: Annotated[OwnShip, Field(description="Own Ship (OS) data", examples=[create_ship_example()])]
    target_ships: (
        Annotated[list[TargetShip], Field(description="Target Ship (TGT) data", examples=[[create_ship_example()]])]
        | None
    ) = None


class EncounterType(Enum):
    """Enumeration of encounter types."""

    OVERTAKING_STAND_ON = "overtaking-stand-on"
    OVERTAKING_GIVE_WAY = "overtaking-give-way"
    HEAD_ON = "head-on"
    CROSSING_GIVE_WAY = "crossing-give-way"
    CROSSING_STAND_ON = "crossing-stand-on"
    NO_RISK_COLLISION = "noRiskCollision"


class Encounter(BaseModelConfig):
    """Data type for an encounter."""

    desired_encounter_type: EncounterType
    beta: list[float] | float | None = None
    relative_speed: float | None = None
    vector_time: list[float] | float

    model_config = ConfigDict(extra="allow")


class EncounterClassification(BaseModelConfig):
    """Data type for the encounter classification."""

    theta13_criteria: float
    theta14_criteria: float
    theta15_criteria: float
    theta15: list[float]

    model_config = ConfigDict(extra="allow")


class EncounterRelativeSpeed(BaseModelConfig):
    """Data type for relative speed between two ships in an encounter."""

    overtaking_stand_on: list[float]
    overtaking_give_way: list[float]
    head_on: list[float]
    crossing_give_way: list[float]
    crossing_stand_on: list[float]

    model_config = ConfigDict(extra="allow")


class EncounterSettings(BaseModelConfig):
    """Data type for encounter settings."""

    classification: EncounterClassification
    relative_speed: EncounterRelativeSpeed
    common_vector: float
    situation_length: float
    max_meeting_distance: float
    situation_develop_time: float
    disable_land_check: bool

    model_config = ConfigDict(extra="allow")


class OwnShipInitial(BaseModelConfig):
    """Data type for initial data for the own ship used for generating a situation."""

    initial: Initial
    waypoints: list[Waypoint] | None = Field(None, description="An array of `Waypoint` objects.")


class SituationInput(BaseModelConfig):
    """Data type for inputs needed for generating a situations."""

    title: str
    description: str
    num_situations: int = 1
    own_ship: OwnShipInitial
    encounters: list[Encounter]

    model_config = ConfigDict(extra="allow")
