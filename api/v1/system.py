"""
System-level endpoints: settings persistence, health extensions.
"""

import json
import os

from flask import jsonify, request

from api.v1 import api_v1

_SETTINGS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data")
_SETTINGS_FILE = os.path.join(_SETTINGS_DIR, "settings.json")


def _load_settings() -> dict:
    """Load settings from JSON file."""
    try:
        if os.path.exists(_SETTINGS_FILE):
            with open(_SETTINGS_FILE, "r") as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def _save_settings(settings: dict) -> bool:
    """Persist settings to JSON file."""
    try:
        os.makedirs(_SETTINGS_DIR, exist_ok=True)
        with open(_SETTINGS_FILE, "w") as f:
            json.dump(settings, f, indent=2, default=str)
        return True
    except Exception:
        return False


@api_v1.route("/settings", methods=["GET"])
def get_settings():
    """Get persisted user settings. Merges with defaults."""
    try:
        stored = _load_settings()
        # Return stored settings; frontend can merge with its defaults
        return jsonify({"success": True, "settings": stored}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_v1.route("/settings", methods=["POST"])
def post_settings():
    """
    Persist user settings.

    Request body: full settings object (e.g. from Settings page).
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No settings provided"}), 400
        if _save_settings(data):
            return jsonify({"success": True}), 200
        return jsonify({"success": False, "error": "Failed to save settings"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
