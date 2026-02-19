"""Flask API endpoints for generating ship traffic situations."""

import json
import os
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from flask import Flask, Response, jsonify, redirect, request
from flask.typing import ResponseReturnValue
from pydantic import ValidationError
from werkzeug.exceptions import RequestEntityTooLarge

from trafficgen.ship_traffic_generator import generate_traffic_situations
from trafficgen.types import SituationInputJson

app = Flask(__name__)
BASELINE_SITUATIONS_DIR = Path(__file__).resolve().parents[2] / "data" / "baseline_situations_input"
DEFAULT_SETTINGS_FILE = Path(__file__).resolve().parent / "settings" / "encounter_settings.json"
MAX_JSON_BYTES = int(os.getenv("TRAFFICGEN_MAX_JSON_BYTES", str(1024 * 1024)))
ENFORCE_HTTPS = os.getenv("TRAFFICGEN_ENFORCE_HTTPS", "1").lower() in {"1", "true"}
app.config["MAX_CONTENT_LENGTH"] = MAX_JSON_BYTES


def _is_https_request() -> bool:
    forwarded_proto = request.headers.get("X-Forwarded-Proto", "").lower()
    return request.is_secure or forwarded_proto == "https"


@app.before_request
def enforce_https() -> ResponseReturnValue | None:
    """Redirect non-HTTPS requests to HTTPS when enforcement is enabled."""
    if not ENFORCE_HTTPS:
        return None

    if _is_https_request():
        return None

    secure_url = request.url.replace("http://", "https://", 1)
    return redirect(secure_url, code=308)


@app.errorhandler(RequestEntityTooLarge)
def handle_request_too_large(_: RequestEntityTooLarge) -> ResponseReturnValue:
    """Return JSON error for oversized request payloads."""
    return (
        jsonify({"error": f"Request body exceeds maximum allowed size ({MAX_JSON_BYTES} bytes)."}),
        413,
    )


@app.after_request
def add_security_headers(response: Response) -> Response:
    """Add minimal security headers for server-to-server API use."""
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"

    if _is_https_request():
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

    return response


@app.route("/api/health", methods=["GET"])
def get_health() -> ResponseReturnValue:
    """Return basic health status for the API service."""
    return jsonify({"status": "ok"}), 200


@app.route("/api/version", methods=["GET"])
def get_version() -> ResponseReturnValue:
    """Return the current package version."""
    try:
        package_version = version("trafficgen")
    except PackageNotFoundError:
        package_version = "unknown"

    return jsonify({"version": package_version}), 200


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


@app.route("/api/baseline/<int:situation_id>", methods=["GET"])
def get_baseline_situation(situation_id: int) -> ResponseReturnValue:
    """Return a baseline situation JSON by its integer id."""
    if situation_id < 1:
        return jsonify({"error": "situation_id must be >= 1"}), 400

    baseline_path = next(BASELINE_SITUATIONS_DIR.glob(f"baseline_situation_{situation_id:02d}_*.json"), None)
    if baseline_path is None:
        return jsonify({"error": f"Baseline situation {situation_id} was not found"}), 404

    with baseline_path.open(encoding="utf-8") as baseline_file:
        baseline_situation = json.load(baseline_file)

    return jsonify(baseline_situation), 200


@app.route("/api/settings/default", methods=["GET"])
def get_default_settings() -> ResponseReturnValue:
    """Return the default encounter settings JSON payload."""
    if not DEFAULT_SETTINGS_FILE.exists():
        return jsonify({"error": "Default settings file was not found"}), 404

    with DEFAULT_SETTINGS_FILE.open(encoding="utf-8") as settings_file:
        default_settings = json.load(settings_file)

    return jsonify(default_settings), 200


if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "").lower() in {"1", "true"})
