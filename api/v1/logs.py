"""
PATH: api/v1/logs.py
PURPOSE: Real-time logging API with WebSocket streaming

WHY: Provides live log streaming to the frontend dashboard for monitoring
     system activity, debugging, and chain-of-thought visualization.
"""

from flask import Blueprint, jsonify, request
from collections import deque
from datetime import datetime
from typing import List, Dict, Any
import threading
import logging
import json

logs_bp = Blueprint('logs', __name__, url_prefix='/logs')

# In-memory log buffer (last 1000 logs)
log_buffer = deque(maxlen=1000)
log_lock = threading.Lock()
log_counter = 0

# Log levels
LOG_LEVELS = ['debug', 'info', 'warn', 'error']


def add_log(level: str, source: str, message: str, details: Dict[str, Any] = None):
    """Add a log entry to the buffer."""
    global log_counter
    
    with log_lock:
        log_counter += 1
        entry = {
            'id': log_counter,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'level': level,
            'source': source,
            'message': message,
            'details': details
        }
        log_buffer.append(entry)
        
        # Also emit via WebSocket if available
        try:
            from api.app import socketio
            socketio.emit('log_entry', entry)
        except Exception:
            pass
    
    return entry


def get_logs(limit: int = 100, level: str = None, source: str = None) -> List[Dict]:
    """Get logs with optional filtering."""
    with log_lock:
        logs = list(log_buffer)
    
    # Filter
    if level and level != 'all':
        logs = [l for l in logs if l['level'] == level]
    if source:
        logs = [l for l in logs if source.lower() in l['source'].lower()]
    
    # Sort by newest first and limit
    logs = sorted(logs, key=lambda x: x['id'], reverse=True)[:limit]
    
    return logs


# Custom log handler that adds to our buffer
class BufferedLogHandler(logging.Handler):
    """Custom log handler that adds logs to our buffer."""
    
    def emit(self, record):
        try:
            level_map = {
                logging.DEBUG: 'debug',
                logging.INFO: 'info',
                logging.WARNING: 'warn',
                logging.ERROR: 'error',
                logging.CRITICAL: 'error',
            }
            level = level_map.get(record.levelno, 'info')
            source = record.name.replace('PhysicsAI.', '').replace('physics.', '')
            
            details = None
            if hasattr(record, 'details'):
                details = record.details
            
            add_log(level, source, record.getMessage(), details)
        except Exception:
            pass


# Install the handler
buffered_handler = BufferedLogHandler()
buffered_handler.setLevel(logging.DEBUG)

# Add to root logger and physics loggers
logging.getLogger().addHandler(buffered_handler)
logging.getLogger('PhysicsAI').addHandler(buffered_handler)


@logs_bp.route('', methods=['GET'])
def list_logs():
    """
    Get recent logs.
    
    Query params:
    - limit: Max logs to return (default 100)
    - level: Filter by level (debug, info, warn, error)
    - source: Filter by source
    """
    limit = request.args.get('limit', 100, type=int)
    level = request.args.get('level')
    source = request.args.get('source')
    
    logs = get_logs(limit=limit, level=level, source=source)
    
    return jsonify({
        'success': True,
        'count': len(logs),
        'logs': logs
    })


@logs_bp.route('/stream', methods=['GET'])
def stream_info():
    """Info about log streaming via WebSocket."""
    ws_host = request.host  # Use the same host the client connected to
    ws_scheme = 'wss' if request.is_secure else 'ws'
    return jsonify({
        'success': True,
        'websocket': {
            'url': f'{ws_scheme}://{ws_host}',
            'event': 'log_entry',
            'description': 'Connect to WebSocket and listen for log_entry events'
        }
    })


@logs_bp.route('/add', methods=['POST'])
def post_log():
    """Add a log entry (for testing or external sources)."""
    data = request.get_json() or {}
    
    level = data.get('level', 'info')
    source = data.get('source', 'API')
    message = data.get('message', '')
    details = data.get('details')
    
    if level not in LOG_LEVELS:
        return jsonify({
            'success': False,
            'error': f'Invalid level. Must be one of: {LOG_LEVELS}'
        }), 400
    
    entry = add_log(level, source, message, details)
    
    return jsonify({
        'success': True,
        'log': entry
    })


@logs_bp.route('/clear', methods=['POST'])
def clear_logs():
    """Clear all logs."""
    global log_counter
    
    with log_lock:
        log_buffer.clear()
        log_counter = 0
    
    return jsonify({'success': True, 'message': 'Logs cleared'})


@logs_bp.route('/stats', methods=['GET'])
def log_stats():
    """Get log statistics."""
    with log_lock:
        logs = list(log_buffer)
    
    stats = {
        'total': len(logs),
        'by_level': {},
        'by_source': {},
    }
    
    for log in logs:
        level = log['level']
        source = log['source']
        
        stats['by_level'][level] = stats['by_level'].get(level, 0) + 1
        stats['by_source'][source] = stats['by_source'].get(source, 0) + 1
    
    return jsonify({
        'success': True,
        'stats': stats
    })


# Generate some initial logs
def generate_sample_logs():
    """Generate sample logs for demo."""
    samples = [
        ('info', 'PhysicsAI', 'System initialized with 522 equations loaded'),
        ('info', 'KnowledgeBase', 'Knowledge graph built with 12 physics domains'),
        ('debug', 'HotReload', 'Watching 7 directories for changes'),
        ('info', 'WebSocket', 'Real-time log streaming enabled'),
        ('info', 'API', 'REST API ready'),
    ]
    
    for level, source, message in samples:
        add_log(level, source, message)


# Initialize with sample logs
generate_sample_logs()
