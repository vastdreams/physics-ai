"""
Experiment database API — store and query experimental results.
"""

import json
import os

from flask import jsonify, request

from api.v1 import api_v1

_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data")
_EXPERIMENTS_FILE = os.path.join(_DATA_DIR, "experiments.json")


def _load_experiments() -> list:
    try:
        if os.path.exists(_EXPERIMENTS_FILE):
            with open(_EXPERIMENTS_FILE) as f:
                return json.load(f)
    except Exception:
        pass
    return []


def _save_experiments(experiments: list) -> bool:
    try:
        os.makedirs(_DATA_DIR, exist_ok=True)
        with open(_EXPERIMENTS_FILE, "w") as f:
            json.dump(experiments, f, indent=2, default=str)
        return True
    except Exception:
        return False


@api_v1.route("/experiments", methods=["GET"])
def list_experiments():
    """List experiments with optional domain/limit filters."""
    domain = request.args.get("domain")
    limit = int(request.args.get("limit", 50))
    exps = _load_experiments()
    if domain:
        exps = [e for e in exps if e.get("domain") == domain]
    exps = exps[-limit:]
    return jsonify({"success": True, "experiments": exps, "count": len(exps)}), 200


@api_v1.route("/experiments", methods=["POST"])
def add_experiment():
    """
    Add an experiment.

    Request body:
    {
        "name": "...",
        "domain": "quantum_mechanics",
        "quantity": "g-2",
        "value": 0.00231930436,
        "uncertainty": 0.00000000028,
        "unit": "...",
        "source": "paper id or description",
        "theory_value": 0.00231930436,
        "tags": ["precision", "standard_model"]
    }
    """
    data = request.get_json()
    if not data or "name" not in data:
        return jsonify({"success": False, "error": "name required"}), 400
    exps = _load_experiments()
    data["id"] = f"exp_{len(exps) + 1}"
    exps.append(data)
    if _save_experiments(exps):
        return jsonify({"success": True, "experiment": data}), 201
    return jsonify({"success": False, "error": "Failed to save"}), 500


@api_v1.route("/experiments/<exp_id>", methods=["GET"])
def get_experiment(exp_id: str):
    """Get a single experiment by id."""
    exps = _load_experiments()
    for e in exps:
        if e.get("id") == exp_id:
            return jsonify(e), 200
    return jsonify({"success": False, "error": "Not found"}), 404
