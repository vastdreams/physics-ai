"""Chain-of-Thought logging endpoints."""

from flask import jsonify, request

from api.v1 import api_v1
from loggers.system_logger import SystemLogger
from utilities.cot_logging import ChainOfThoughtLogger, LogLevel

_logger = SystemLogger()

# Store active CoT loggers (in production, would use proper session management)
active_cot_loggers: dict = {}

# In-memory ring buffer for recent COT log entries
_cot_log_buffer: list[dict] = []
_COT_LOG_MAX = 200


def append_cot_log(entry: dict) -> None:
    """Append a COT entry to the shared buffer (called from loggers)."""
    _cot_log_buffer.append(entry)
    if len(_cot_log_buffer) > _COT_LOG_MAX:
        del _cot_log_buffer[:len(_cot_log_buffer) - _COT_LOG_MAX]


# Register so ChainOfThoughtLogger pushes step entries to the API buffer
ChainOfThoughtLogger.register_sink(append_cot_log)


@api_v1.route('/cot/logs', methods=['GET'])
def get_cot_logs():
    """
    Get recent Chain-of-Thought log entries.

    Query parameters:
    - limit: Max entries to return (default 50)
    """
    try:
        limit = int(request.args.get('limit', 50))
        entries = _cot_log_buffer[-limit:]
        return jsonify({'success': True, 'logs': entries, 'total': len(_cot_log_buffer)}), 200
    except Exception as e:
        _logger.log(f"Error in get_cot_logs: {str(e)}", level="ERROR")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_v1.route('/cot/tree', methods=['GET'])
def get_cot_tree():
    """
    Get full CoT tree.

    Query parameters:
    - session_id: Session ID (optional)
    """
    cot = ChainOfThoughtLogger()
    step_id = cot.start_step(action="API_GET_COT_TREE", level=LogLevel.INFO)

    try:
        session_id = request.args.get('session_id')

        if session_id and session_id in active_cot_loggers:
            cot = active_cot_loggers[session_id]
        else:
            cot.end_step(step_id, output_data={'tree': {}}, validation_passed=True)
            return jsonify({'tree': {}}), 200

        tree = cot.get_full_tree()
        cot.end_step(step_id, output_data={'tree_keys': list(tree.keys())}, validation_passed=True)

        return jsonify(tree), 200

    except Exception as e:
        cot.end_step(step_id, output_data={'error': str(e)}, validation_passed=False)
        _logger.log(f"Error in get_cot_tree endpoint: {str(e)}", level="ERROR")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_v1.route('/cot/statistics', methods=['GET'])
def get_cot_statistics():
    """Get CoT statistics."""
    cot = ChainOfThoughtLogger()
    step_id = cot.start_step(action="API_GET_COT_STATISTICS", level=LogLevel.INFO)

    try:
        session_id = request.args.get('session_id')

        if session_id and session_id in active_cot_loggers:
            cot = active_cot_loggers[session_id]
        else:
            cot.end_step(step_id, output_data={'statistics': {}}, validation_passed=True)
            return jsonify({'statistics': {}}), 200

        stats = cot.get_statistics()
        cot.end_step(step_id, output_data={'statistics': stats}, validation_passed=True)

        return jsonify(stats), 200

    except Exception as e:
        cot.end_step(step_id, output_data={'error': str(e)}, validation_passed=False)
        _logger.log(f"Error in get_cot_statistics endpoint: {str(e)}", level="ERROR")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_v1.route('/cot/export', methods=['POST'])
def export_cot():
    """
    Export CoT log to JSON file.

    Request body:
    {
        "session_id": "...",
        "filepath": "/path/to/output.json"
    }
    """
    cot = ChainOfThoughtLogger()
    step_id = cot.start_step(action="API_EXPORT_COT", level=LogLevel.INFO)

    try:
        data = request.get_json()

        if not data or 'filepath' not in data:
            cot.end_step(step_id, output_data={'error': 'filepath required'}, validation_passed=False)
            return jsonify({'success': False, 'error': 'filepath required'}), 400

        session_id = data.get('session_id')
        filepath = data['filepath']

        if session_id and session_id in active_cot_loggers:
            cot = active_cot_loggers[session_id]
        else:
            cot.end_step(step_id, output_data={'error': 'Session not found'}, validation_passed=False)
            return jsonify({'success': False, 'error': 'Session not found'}), 404

        cot.export_json(filepath)
        cot.end_step(step_id, output_data={'filepath': filepath}, validation_passed=True)

        return jsonify({'success': True, 'filepath': filepath}), 200

    except Exception as e:
        cot.end_step(step_id, output_data={'error': str(e)}, validation_passed=False)
        _logger.log(f"Error in export_cot endpoint: {str(e)}", level="ERROR")
        return jsonify({'success': False, 'error': str(e)}), 500
