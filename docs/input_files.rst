===========
Input files
===========

Example 1: Complete specified situation::

    {
        "title": "HO",
        "description": "A head on situation with one target ship.",
        "ownShip": {
            "initial": {
                "position": {
                    "latitude": 58.763449,
                    "longitude": 10.490654
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

The values may be given in either maritime units or SI units, and which unit is used shall be specified in the `src/trafficgen/settings/encounter_settings.json` file.
The `common_vector` is given in minutes (maritime) or seconds (SI). For radar plotting (plotting vessel positions and relative motions),
the `common_vector` and `vector_time` are used together with ship speed to display where the ship will be in e.g. 10 minutes
(Common vector is the common time vector used on a radar plot, e.g 10, 15, 20 minutes. The length of the arrow in the plot
will then be the speed times this time vector).
Speed and course of the own ship, which is the ship to be tested, are given in knots and degrees (maritime) or m/s and radians (SI), respectively.
The own ship position is given both in latitudinal and longitudinal (degree/radians) together with north/east in meters from the reference point.
The reference point is the initial position of own ship.

An encounter may be fully described as shown above, but the user may also deside to input less data,
as demonstrated in Example 2. Desired encounter type is mandatory,
while the `beta`, `relative_speed` and `vector_time` parameters are optional:

 * `desired_encounter_type` is either head-on, overtaking-give-way, overtaking-stand-on, crossing-give-way, and crossing-stand-on.
 * `beta` is the relative bearing between the own ship and the target ship as seen from the own shop, given in degrees/radians.
 * `relative_speed` is relative speed between the own ship and the target ship as seen from the own ship, such that a relative speed of 1.2 means that the target ship's speed is 20% higher than the speed of the own ship.

An encounter is built using a maximum meeting distance [nm], see the paper linked in the introduction for more info.
At some time in the future, given by the `vector_time`, the target ship will be located somewhere inside a circle
with a radius given by `max_meeting_distance` and a center point given by the own ship position. This is not necessarily the
closest point of approach.

The `max_meeting_distance` parameter is common for all encounters and is specified in `src/trafficgen/settings/encounter_settings.json`.

Example 2: Minimum specified situation::

    {
        "title": "HO",
        "description": "A head on situation with one target ship.",
        "ownShip": {
            "initial": {
                "position": {
                    "latitude": 58.763449,
                    "longitude": 10.490654
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
                    "latitude": 58.763449,
                    "longitude": 10.490654
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
                "latitude": 58.763449,
                "longitude": 10.490654
            }
        },
        "encounter": [
            {
            "desired_encounter_type": "crossing-give-way",
            "beta": [45.0,120.0]
            }
        ]
    }
