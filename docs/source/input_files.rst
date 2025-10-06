.. _input_files:
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
                "vectorTime": 15.0,
                "beta": 2.0,
                "relativeSpeed": 1.2
            }
        ]
    }


The numerical values are given in maritime units:

* `title` and `description` are strings that describe the situation and are used for documentation purposes.
* `position` (initial) of the own ship is given by:
   * `lat` - the latitude in decimal degrees.
   * `lon` - the longitude in decimal degrees.
* `sog` is the speed over ground in knots.
* `cog` is the course over ground in degrees.
* `heading` is the heading in degrees.
* `navStatus` is the navigation status of the own ship, which can be one of the following: "Under way using engine", "At anchor", "Not under command", "Restricted maneuverability", "Constrained by draft", "Moored", "Aground", "Engaged in fishing", "Under way sailing", "Reserved for future use".
* `desiredEncounterType` is the desired encounter type, which can be one of the following: "head-on", "overtaking-give-way", "overtaking-stand-on", "crossing-give-way", "crossing-stand-on".
* `vectorTime` is the time in minutes for the situation to evolve, that is the time from the start of the situation until the target ship is within a specific range of the own ship, given in minutes (see below).
* `beta` is the relative bearing between the own ship and the target ship as seen from the own ship, given in degrees.
* `relativeSpeed` is the relative speed between the own ship and the target ship as seen from the own ship, such that a relative speed of 1.2 means that the target ship's speed is 20% higher than the speed of the own ship.


> **Note:** The initial position of the own ship serves as the reference point for converting to x/y coordinates. To change the location of the generated traffic situations, adjust the own ship's initial latitude and longitude in the input file. This position is treated as the origin (0,0) for all traffic scenarios derived from that file.

An encounter may be fully described as shown above, but the user may also decide to input less data,
as demonstrated in Example 2. The desired encounter type and vector time are mandatory, while the `beta` and `relativeSpeed` parameters are optional:

An encounter is built using a maximum meeting distance [nm], see the paper linked in the introduction for more info.
At some time in the future, given by the `vectorTime`, the target ship will be located somewhere inside a circle
with a radius given by `maxMeetingDistance` (see encounter settings below) and a center point given by the own ship position.
This is not necessarily the closest point of approach.
The `maxMeetingDistance` parameter is common for all encounters and is specified in `src/trafficgen/settings/encounter_settings.json`.


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
                "vectorTime": 15.0
            }
        ]
    }

> **Note:** All fields specified in this "Minimum specified" are required, and the tool will not work if you, for example, leave out either heading or cog. Both are required.

You can also request the generation of several traffic situations of the same encounter type by specifying `numSituations`:

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
                "vectorTime": 15.0
            }
        ]
    }

In this case, the tool will generate 5 situations with the same parameters as specified in the input file.
You may want to use this in combination with, for example, specifying a range for the `vectorTime`, so that you get 5 situations with slightly different encounter times as shown in the next example.

Example 4: Assign range for `vectorTime`::

    {
        "title": "CR_GW",
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
        "encounter": [
            {
            "desiredEncounterType": "crossing-give-way",
            "vectorTime": [15.0, 25.0]
            }
        ]
    }


The next example shows how it is possible to give a range for the relative bearing between own ship and target ship.

Example 5: Assign range for `beta`::

    {
        "title": "CR_GW",
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
        "encounter": [
            {
            "desiredEncounterType": "crossing-give-way",
            "vectorTime": 15.0,
            "beta": [45.0,120.0]
            }
        ]
    }

It is also possible to specify waypoints for the own ship. Waypoint 0 should then be the same as the initial
position of the own ship. If more than one waypoint is specified, the own ship will follow the
waypoints in the order they are given.

Example 5: Specifying `waypoints``::


    {
        "title": "CR-Waypoints",
        "description": "Crossing situations, waypoints added for own ship.",
        "ownShip": {
            "initial": {
                "position": {
                    "lat": 58.763449,
                    "lon": 10.490654
                },
                "sog": 4.5,
                "cog": 0.0,
                "heading": 0.0,
                "navStatus": "Under way using engine"
            },
            "waypoints": [
                {
                    "position": {
                        "lat": 58.763449,
                        "lon": 10.490654
                    },
                    "data": {
                        "sog": {
                            "value": 4.5
                        }
                    }
                },
                {
                    "position": {
                        "lat": 58.680833,
                        "lon": 10.355278
                    },
                    "data": {
                        "sog": {
                            "value": 4.5
                        }
                    }
                },
                {
                    "position": {
                        "lat": 58.571944,
                        "lon": 10.137778
                    },
                    "data": {
                        "sog": {
                            "value": 4.4
                        }
                    }
                }
            ]
        },
        "encounters": [
            {
                "desiredEncounterType": "crossing-give-way",
                "vectorTime": 20.0,
                "relativeSpeed": 1.2,
                "beta": [
                    45.0,
                    120.0
                ]
            }
        ]
    }


Own ship file
~~~~~~~~~~~~~~~
The own ship file specifies the own ship, which is the ship to be controlled by the control system under test.
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
Id should not be assigned to the target ships used for generating encounters because the "same" target ship may be used several times
in a situation consisting of several encounters. The target ships in the data/target_ships folder are randomly used in the generation of encounters.

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

By default, the ship traffic generator will randomly sample a target ship from the given set of target ships.

Encounter settings
~~~~~~~~~~~~~~~~~~

The encounter settings file specifies parameters that are common for all encounters.

The file is written in JSON format and located in the `src/trafficgen/settings/encounter_settings.json`::

    {
        "classification": {
            "theta13Criteria": 67.5,
            "theta14Criteria": 5.0,
            "theta15Criteria": 5.0,
            "theta15": [
                112.5,
                247.5
            ]
        },
        "relativeSpeed": {
            "overtakingStandOn": [
                1.5,
                2
            ],
            "overtakingGiveWay": [
                0.25,
                0.75
            ],
            "headOn": [
                0.5,
                1.5
            ],
            "crossingGiveWay": [
                0.5,
                1.5
            ],
            "crossingStandOn": [
                0.5,
                1.5
            ]
        },
        "vectorRange": [
            10.0,
            30.0
        ],
        "situationLength": 30.0,
        "maxMeetingDistance": 0.0,
        "commonVector": 5.0,
        "situationDevelopTime": 120.0,
        "disableLandCheck": true
    }

The values are given in maritime units.
The `theta13Criteria`, `theta14Criteria` and `theta15Criteria` are the criteria for the classification of the encounters.
The `theta15` is the range for the relative bearing between the own ship and the target ship for crossing situations.

The `relativeSpeed` is the range for the relative speed between the own ship and the target ship.
The `situationLength` is the length of the situation, given in minutes.
The `maxMeetingDistance` is the maximum meeting distance, given in nautical miles.
The `commonVector` is the common time vector used on a radar plot.
The `situationDevelopTime` specifies the number of minutes prior to the encounter that you would look back, ensuring the situation has had time to develop while still retaining the same encounter type. See the Usage section for more information.
The `disableLandCheck` is a boolean value that determines if the land check should be disabled or not.

We refer to the paper for more information on these parameters.
