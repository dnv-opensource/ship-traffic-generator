"""Tests for types and schema parsing."""

from trafficgen.types import ShipStatic, SituationInputJson


def test_situation_input_json_accepts_camel_case_payload() -> None:
    payload = {
        "trafficSituations": {
            "title": "test",
            "description": "camelCase payload",
            "numSituations": 1,
            "ownShip": {
                "initial": {
                    "position": {"lat": 10.0, "lon": 20.0},
                    "sog": 12.0,
                    "cog": 45.0,
                }
            },
            "encounters": [{"desiredEncounterType": "head-on", "vectorTime": 10.0}],
        },
        "ownShipStatic": {"id": 1},
        "targetShipsStatic": [{"id": 2}],
        "encounterSettings": {
            "classification": {
                "theta13Criteria": 1.0,
                "theta14Criteria": 1.0,
                "theta15Criteria": 1.0,
                "theta15": [1.0, 2.0],
            },
            "relativeSpeed": {
                "overtakingStandOn": [1.0, 2.0],
                "overtakingGiveWay": [1.0, 2.0],
                "headOn": [1.0, 2.0],
                "crossingGiveWay": [1.0, 2.0],
                "crossingStandOn": [1.0, 2.0],
            },
            "commonVector": 5.0,
            "situationLength": 30.0,
            "maxMeetingDistance": 10.0,
            "situationDevelopTime": 15.0,
            "disableLandCheck": True,
        },
    }

    parsed = SituationInputJson(**payload)

    assert not isinstance(parsed.traffic_situations, list)
    assert parsed.traffic_situations.title == "test"
    assert parsed.traffic_situations.own_ship.initial.position.lat == 10.0
    assert parsed.encounter_settings.disable_land_check is True


def test_ship_static_id_is_coerced_to_int() -> None:
    ship_static = ShipStatic(id="2")
    assert ship_static.id == 2
    assert isinstance(ship_static.id, int)
