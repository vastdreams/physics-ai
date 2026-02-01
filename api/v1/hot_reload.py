"""
PATH: api/v1/hot_reload.py
PURPOSE: API endpoints for hot reload control and monitoring

WHY: Provides REST endpoints to monitor and control the hot reload system,
     enabling integration with the frontend dashboard.

DEPENDENCIES:
- flask: Web framework
- utilities.hot_reload: Hot reload system
"""

from flask import Blueprint, jsonify, request
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

hot_reload_bp = Blueprint('hot_reload', __name__, url_prefix='/api/v1/hot-reload')

# Will be set when the reloader is started
_reloader = None


def set_reloader(reloader):
    """Set the global reloader reference for API access."""
    global _reloader
    _reloader = reloader


@hot_reload_bp.route('/status', methods=['GET'])
def get_status():
    """
    Get hot reload system status.
    
    Returns:
        JSON with status information
    """
    if _reloader is None:
        return jsonify({
            "enabled": False,
            "message": "Hot reload not initialized"
        })
    
    status = _reloader.get_status()
    return jsonify({
        "enabled": True,
        **status
    })


@hot_reload_bp.route('/modules', methods=['GET'])
def get_modules():
    """
    Get list of watched modules and their states.
    
    Returns:
        JSON with module states
    """
    if _reloader is None:
        return jsonify({"modules": [], "error": "Hot reload not initialized"})
    
    modules = _reloader.get_module_states()
    return jsonify({"modules": modules})


@hot_reload_bp.route('/reload', methods=['POST'])
def trigger_reload():
    """
    Trigger manual reload of specific module or all modules.
    
    Body (optional):
        {"module": "module.name"} - Reload specific module
        {} or no body - Reload all changed modules
        
    Returns:
        JSON with reload results
    """
    if _reloader is None:
        return jsonify({"success": False, "error": "Hot reload not initialized"}), 503
    
    data = request.get_json() or {}
    module_name = data.get('module')
    
    if module_name:
        # Reload specific module
        event = _reloader.reload_module(module_name)
        if event:
            return jsonify({
                "success": event.success,
                "module": event.module_name,
                "error": event.error,
                "reload_time_ms": event.reload_time_ms,
            })
        else:
            return jsonify({
                "success": False,
                "error": f"Module '{module_name}' not found in watched modules"
            }), 404
    else:
        # Reload all
        events = _reloader.reload_all()
        return jsonify({
            "success": all(e.success for e in events),
            "reloaded": len([e for e in events if e.success]),
            "failed": len([e for e in events if not e.success]),
            "modules": [
                {"module": e.module_name, "success": e.success, "error": e.error}
                for e in events
            ]
        })


@hot_reload_bp.route('/toggle', methods=['POST'])
def toggle_auto_reload():
    """
    Toggle auto-reload on/off.
    
    Body:
        {"enabled": true/false}
        
    Returns:
        JSON with new state
    """
    if _reloader is None:
        return jsonify({"success": False, "error": "Hot reload not initialized"}), 503
    
    data = request.get_json() or {}
    enabled = data.get('enabled')
    
    if enabled is not None:
        _reloader.auto_reload = bool(enabled)
    
    return jsonify({
        "success": True,
        "auto_reload": _reloader.auto_reload
    })
