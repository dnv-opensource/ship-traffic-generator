===========
Input files
===========

Situation files
~~~~~~~~~~~~~~~
The situation files specify the traffic situations to be generated. The files are written in JSON format
and a predefined set of situation files with number of encounters in a situation ranging from 1 to 3 are located in the
`src/trafficgen/data/baseline_situations_input` directory.

Below are some examples given on how to specify a situation:

Example 1: Complete specified situation::

    {
        "title": "HO",
        "description": "A head on situation with one target ship.",
        "ownShip": {
            "initial": {
                "position": {
                    "lat": 58.763449,
                    "lon": 10.490654
                },
                "sog": 10.0,
                "cog": 0.0,
                "heading": 0.0,
                "navStatus": "Under way using engine"
            }
        },
        "encounters": [
            {
                "desiredEncounterType": "head-on",
                "beta": 2.0,
                "relativeSpeed": 1.2,
                "vectorTime": 15.0
            }
        ]
    }

The values are giben in maritime units. The `common_vector` is given in minutes. For radar plotting (plotting vessel positions and relative motions),
the `common_vector` and `vectorTime` are used together with ship speed to display where the ship will be in e.g. 10 minutes
(Common vector is the common time vector used on a radar plot, e.g 10, 15, 20 minutes. The length of the arrow in the plot
will then be the speed times this time vector, `common_vector`).
Speed and course of the own ship, which is the ship to be tested, are given in knots and degrees, respectively.
The own ship position is given in latitudinal and longitudinal (degree).
The reference point is the initial position of own ship.

An encounter may be fully described as shown above, but the user may also deside to input less data,
as demonstrated in Example 2. Desired encounter type is mandatory,
while the `beta`, `relative_speed` and `vectorTime` parameters are optional:

 * `desired_encounter_type` is either head-on, overtaking-give-way, overtaking-stand-on, crossing-give-way, and crossing-stand-on.
 * `beta` is the relative bearing between the own ship and the target ship as seen from the own shop, given in degrees.
 * `relative_speed` is relative speed between the own ship and the target ship as seen from the own ship, such that a relative speed of 1.2 means that the target ship's speed is 20% higher than the speed of the own ship.

An encounter is built using a maximum meeting distance [nm], see the paper linked in the introduction for more info.
At some time in the future, given by the `vectorTime`, the target ship will be located somewhere inside a circle
with a radius given by `max_meeting_distance` and a center point given by the own ship position. This is not necessarily the
closest point of approach.

The `max_meeting_distance` parameter is common for all encounters and is specified in `src/trafficgen/settings/encounter_settings.json`.
If you set max_meeting_distance to zero, you ensure a scenario where vessels would collide.

Example 2: Minimum specified situation::

    {
        "title": "HO",
        "description": "A head on situation with one target ship.",
        "ownShip": {
            "initial": {
                "position": {
                    "lat": 58.763449,
                    "lon": 10.490654
                },
                "sog": 10.0,
                "cog": 0.0,
                "heading": 0.0,
                "navStatus": "Under way using engine"
            }
        },
        "encounters": [
            {
                "desiredEncounterType": "head-on",
            }
        ]
    }


You can also request the generation of several traffic situations of the same encounter type by specifying `num_situations`:

Example 3: Generate multiple situations using `numSituations`::

    {
        "title": "HO",
        "description": "A head on situation with one target ship.",
        "numSituations": 5
        "ownShip": {
            "initial": {
                "position": {
                    "lat": 58.763449,
                    "lon": 10.490654
                },
                "sog": 10.0,
                "cog": 0.0,
                "heading": 0.0,
                "navStatus": "Under way using engine"
            }
        },
        "encounters": [
            {
                "desiredEncounterType": "head-on",
            }
        ]
    }

The next example show how it is possible to give a range for the relative bearing between own ship and target ship

Example 4: Assign range for `beta`::

    {
        "title": "CR_GW",
        "common_vector": 10.0,
        "own_ship": {
            "speed": 7.0,
            "course": 0.0,
            "position": {
                "lat": 58.763449,
                "lon": 10.490654
            }
        },
        "encounter": [
            {
            "desired_encounter_type": "crossing-give-way",
            "beta": [45.0,120.0]
            }
        ]
    }

Own ship file
~~~~~~~~~~~~~~~
The own ship file specify the own ship which is the ship to be controlled by the control system under test.
The file is written in JSON format and located in the `src/trafficgen/data/own_ship`::

    {
        "dimensions": {
            "length": 122,
            "width": 20,
            "height": 8
        },
        "sogMax": 17,
        "mmsi": 257847600,
        "name": "BASTO VI",
        "shipType": "Passenger"
    }

The values are given in maritime units. `sogMax` is the maximum speed over ground in knots, and the dimensions are given in meters.

Target ship files
~~~~~~~~~~~~~~~~~
The directory `src/trafficgen/data/target_ships` contains a set of target ships that can be used in the traffic generation.
The file is written in JSON format and is on the following structure::

    {
        "dimensions": {
            "length": 122,
            "width": 20,
            "height": 8
        },
        "sogMax": 17,
        "shipType": "Passenger"
    }

Encounter settings
~~~~~~~~~~~~~~~~~~
The encounter settings file specifies parameters that are common for all encounters.
The file is written in JSON format and located in the `src/trafficgen/settings/encounter_settings.json`::

    {
        "classification": {
            "theta13_criteria": 67.5,
            "theta14_criteria": 5.0,
            "theta15_criteria": 5.0,
            "theta15": [
                112.5,
                247.5
            ]
        },
        "relative_speed": {
            "overtaking_stand_on": [
                1.5,
                2
            ],
            "overtaking_give_way": [
                0.25,
                0.75
            ],
            "head_on": [
                0.5,
                1.5
            ],
            "crossing_give_way": [
                0.5,
                1.5
            ],
            "crossing_stand_on": [
                0.5,
                1.5
            ]
        },
        "vector_range": [
            10.0,
            30.0
        ],
        "situation_length": 30.0,
        "max_meeting_distance": 0.0,
        "common_vector": 5.0,
        "evolve_time": 120.0,
        "disable_land_check": true
    }

The values are given in maritime units. The `theta13_criteria`, `theta14_criteria` and `theta15_criteria` are the criteria for the classification of the encounters.
The `theta15` is the range for the relative bearing between own ship and target ship.
The `relative_speed` is the range for the relative speed between own ship and target ship.
The `vector_range` is the range for the vector time. If vector_time is not specified, a time point will be randomly sampled within vector_range.
The `situation_length` is the length of the situation in minutes. The ownship is by default planned to travel in a straight line from its start position, for situation_length minutes.
The `max_meeting_distance` is the maximum meeting distance in nautical miles. This is the range around the ownship, in which the target ship will be, at the encounter time.
The `common_vector` is the common time vector used on a radar plot.
The `evolve_time` is the time in minutes for the situation to evolve (before the encounter), ensuring the same COLREG type.
The `disable_land_check` is a boolean value that determines if the land check should be disabled or not.
