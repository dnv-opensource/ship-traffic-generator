"""Tests for types and schema parsing."""

import json
from pathlib import Path

from trafficgen.types import ShipStatic, SituationInputJson


def test_situation_input_json_accepts_camel_case_payload() -> None:
    payload_path = (
        Path(__file__).resolve().parents[1] / "data" / "example_situations_config_json" / "example_situation_01_ts.json"
    )
    with payload_path.open(encoding="utf-8") as payload_file:
        payload = json.load(payload_file)

    parsed = SituationInputJson(**payload)

    assert not isinstance(parsed.traffic_situations, list)
    assert parsed.traffic_situations.title == "HO, CR-GW, OT-GW"
    assert parsed.traffic_situations.own_ship.initial.position.lat == 58.763449
    assert parsed.encounter_settings.disable_land_check is True


def test_ship_static_id_is_coerced_to_int() -> None:
    ship_static = ShipStatic.model_validate({"id": "2"})
    assert ship_static.id == 2
    assert isinstance(ship_static.id, int)
