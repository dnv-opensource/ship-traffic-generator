import json

from flask import Flask, jsonify, request
from pydantic import BaseModel, ValidationError

from trafficgen.types import SituationInput

app = Flask(__name__)


@app.route("/")
def hello_world():
    return {"message": "Hello, World!"}, 200


@app.route("/api/generate", methods=["POST"])
def generate_situation():
    input_data = request.get_json()

    try:
        input_schema = SituationInput(**input_data)
    except ValidationError as e:
        return jsonify({"Error:", e}), 422

    output_schema = {"name": "BASTØ"}
    return jsonify(output_schema), 200


if __name__ == "__main__":
    app.run(debug=True)
