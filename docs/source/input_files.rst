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


The numerical values are given in maritime units:

* `title` and `description` are strings that describe the situation and used for documentation purposes.
* `position` (initial) of own ship is given by:
   * `lat` as the latitude in decimal degrees
   * `lon` as the longitude in decimal degrees.
* `lon` is the longitude in decimal degrees.
* `sog` is the speed over ground in knots.
* `cog` is the course over ground in degrees.
* `heading` is the heading in degrees.
* `navStatus` is the navigation status of the own ship, which can be one of the following: "Under way using engine", "At anchor", "Not under command", "Restricted maneuverability", "Constrained by draft", "Moored", "Aground", "Engaged in fishing", "Under way sailing", "Reserved for future use".
* `desiredEncounterType` is the desired encounter type, which can be one of the following: "head-on", "overtaking-give-way", "overtaking-stand-on", "crossing-give-way", "crossing-stand-on".
* `beta` is the relative bearing between the own ship and the target ship as seen from the own ship, given in degrees.
* `relativeSpeed` is the relative speed between the own ship and the target ship as seen from the own ship, such that a relative speed of 1.2 means that the target ship's speed is 20% higher than the speed of the own ship.
* `vectorTime` is the time in minutes for the situation to evolve.

The reference point, used for conversion to x/y, is the initial position of own ship.

> **Note:** in order to change the location of the traffic situations you are generating, you should change the initial lat/lon position of the own ship, in the input file(s). This is used as the origin point or reference point for all generated traffic situations, i.e. the (0,0) location.

An encounter may be fully described as shown above, but the user may also deside to input less data,
as demonstrated in Example 2. Desired encounter type is mandatory, while the `beta`, `relativeSpeed` and `vectorTime` parameters are optional:

An encounter is built using a maximum meeting distance [nm], see the paper linked in the introduction for more info.
At some time in the future, given by the `vectorTime`, the target ship will be located somewhere inside a circle
with a radius given by `maxMeetingDistance` (see encounter settings below) and a center point given by the own ship position. This is not necessarily the
closest point of approach. The `maxMeetingDistance` parameter is common for all encounters and is specified in `src/trafficgen/settings/encounter_settings.json`.


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
            }
        ]
    }

The next example shows how it is possible to give a range for the relative bearing between own ship and target ship.

Example 4: Assign range for `beta`::

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
            "beta": [45.0,120.0]
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

The encounter setting file specified parameters that are common for all encounters.

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
        "evolveTime": 120.0,
        "disableLandCheck": true
    }

The values are given in maritime units. The `theta13Criteria`, `theta14Criteria` and `theta15Criteria` are the criteria for the classification of the encounters.
The `theta15` is the range for the relative bearing between own ship and target ship.

The `relativeSpeed` is the range for the relative speed between own ship and target ship.
The `vectorRange` is the range for the vector time given in minutes.
The `situationLength` is the length of the situation in minutes.
The `maxMeetingDistance` is the maximum meeting distance in nautical miles.
The `commonVector` is the common time vector used on a radar plot.
The `evolveTime` is the time in minutes for the situation to evolve.
The `disableLandCheck` is a boolean value that determines if the land check should be disabled or not.

We refer to the paper for more information on these parameters.
