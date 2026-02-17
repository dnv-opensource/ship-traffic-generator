"""Flask API endpoints for generating ship traffic situations."""

import os

from flask import Flask, jsonify, request
from flask.typing import ResponseReturnValue
from pydantic import ValidationError

from trafficgen.ship_traffic_generator import generate_traffic_situations
from trafficgen.types import SituationInputJson

app = Flask(__name__)


@app.route("/api/generate", methods=["POST"])
def generate_situation() -> ResponseReturnValue:
    """Validate request payload and return generated traffic situations as JSON."""
    input_data = request.get_json(silent=True)

    if input_data is None:
        return jsonify({"error": "Invalid or missing JSON request body or content-type header."}), 400

    try:
        parsed_json = SituationInputJson(**input_data)
    except ValidationError as e:
        app.logger.exception(e.json(indent=2))
        return jsonify({"errors": e.errors()}), 422

    situations = generate_traffic_situations(
        situations_data=parsed_json.traffic_situations,
        own_ship_data=parsed_json.own_ship_static,
        target_ships_data=parsed_json.target_ships_static,
        settings_data=parsed_json.encounter_settings,
    )

    response_payload = [situation.model_dump(mode="json", by_alias=True) for situation in situations]
    return jsonify(response_payload), 200


if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "").lower() in {"1", "true", "yes"})
