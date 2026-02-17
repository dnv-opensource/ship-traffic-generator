from flask import Flask, jsonify, request
from pydantic import ValidationError

from trafficgen.types import SituationInputJson

app = Flask(__name__)


@app.route("/")
def hello_world():
    return {"message": "Hello, World!"}, 200


@app.route("/api/generate", methods=["POST"])
def generate_situation():
    input_data = request.get_json(silent=True)
    parsed_json = None

    if input_data is None:
        return jsonify({"error": "Invalid or missing JSON request body or content-type header."}), 400

    try:
        parsed_json = SituationInputJson(**input_data)
    except ValidationError as e:
        app.logger.exception(e.json(indent=2))
        return jsonify({"errors": e.errors()}), 422

    return jsonify(parsed_json.model_dump_json()), 200


if __name__ == "__main__":
    app.run(debug=True)
