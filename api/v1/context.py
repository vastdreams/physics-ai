"""Context Memory API endpoints."""

from flask import jsonify, request

from ai.context_memory import ContextBubble, ContextTree, MicroAgent, PathOptimizer, TrafficAgent, UsageTracker
from api.v1 import api_v1
from loggers.system_logger import SystemLogger
from utilities.cot_logging import ChainOfThoughtLogger, LogLevel

_logger = SystemLogger()

# Global instances (in production, would use proper dependency injection)
context_tree = ContextTree()
traffic_agent = TrafficAgent(context_tree)
path_optimizer = PathOptimizer(traffic_agent)
usage_tracker = UsageTracker()


@api_v1.route('/context/tree', methods=['GET'])
def get_context_tree():
    """Get context tree structure."""
    cot = ChainOfThoughtLogger()
    step_id = cot.start_step(action="API_GET_CONTEXT_TREE", level=LogLevel.INFO)

    try:
        stats = context_tree.get_statistics()
        cot.end_step(step_id, output_data={'stats': stats}, validation_passed=True)

        return jsonify(stats), 200

    except Exception as e:
        cot.end_step(step_id, output_data={'error': str(e)}, validation_passed=False)
        _logger.log(f"Error in get_context_tree: {str(e)}", level="ERROR")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_v1.route('/context/bubbles', methods=['GET'])
def list_bubbles():
    """List all context bubbles."""
    cot = ChainOfThoughtLogger()
    step_id = cot.start_step(action="API_LIST_BUBBLES", level=LogLevel.INFO)

    try:
        bubbles = context_tree.get_all_bubbles()
        bubble_list = [
            {
                'bubble_id': bid,
                'statistics': bubble.get_statistics()
            }
            for bid, bubble in bubbles.items()
        ]

        cot.end_step(step_id, output_data={'count': len(bubble_list)}, validation_passed=True)

        return jsonify({'bubbles': bubble_list}), 200

    except Exception as e:
        cot.end_step(step_id, output_data={'error': str(e)}, validation_passed=False)
        _logger.log(f"Error in list_bubbles: {str(e)}", level="ERROR")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_v1.route('/context/bubbles', methods=['POST'])
def create_bubble():
    """
    Create context bubble.

    Request body:
    {
        "content": {...},
        "metadata": {...},
        "parent_id": "optional_parent_id"
    }
    """
    cot = ChainOfThoughtLogger()
    step_id = cot.start_step(action="API_CREATE_BUBBLE", level=LogLevel.INFO)

    try:
        data = request.get_json()

        if not data or 'content' not in data:
            cot.end_step(step_id, output_data={'error': 'content required'}, validation_passed=False)
            return jsonify({'success': False, 'error': 'content required'}), 400

        bubble = ContextBubble(
            bubble_id="",  # Auto-generated
            content=data['content'],
            metadata=data.get('metadata', {})
        )

        parent_id = data.get('parent_id')
        success = context_tree.add_bubble(bubble, parent_id)

        if not success:
            cot.end_step(step_id, output_data={'error': 'Failed to add bubble'}, validation_passed=False)
            return jsonify({'success': False, 'error': 'Failed to add bubble'}), 500

        cot.end_step(step_id, output_data={'bubble_id': bubble.bubble_id}, validation_passed=True)

        return jsonify({'bubble_id': bubble.bubble_id, 'statistics': bubble.get_statistics()}), 201

    except Exception as e:
        cot.end_step(step_id, output_data={'error': str(e)}, validation_passed=False)
        _logger.log(f"Error in create_bubble: {str(e)}", level="ERROR")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_v1.route('/context/pathways', methods=['POST'])
def find_pathway():
    """
    Find pathway between bubbles.

    Request body:
    {
        "start_bubble_id": "bubble1",
        "target_bubble_id": "bubble2",
        "max_depth": 10
    }
    """
    cot = ChainOfThoughtLogger()
    step_id = cot.start_step(action="API_FIND_PATHWAY", level=LogLevel.INFO)

    try:
        data = request.get_json()

        if not data or 'start_bubble_id' not in data or 'target_bubble_id' not in data:
            cot.end_step(step_id, output_data={'error': 'start_bubble_id and target_bubble_id required'}, validation_passed=False)
            return jsonify({'success': False, 'error': 'start_bubble_id and target_bubble_id required'}), 400

        path = path_optimizer.optimize_path(
            start=data['start_bubble_id'],
            target=data['target_bubble_id'],
            context_tree=context_tree
        )

        if path:
            for i in range(len(path) - 1):
                usage_tracker.record_usage(f"{path[i]}->{path[i+1]}")

        cot.end_step(step_id, output_data={'path_length': len(path) if path else 0}, validation_passed=True)

        return jsonify({'path': path}), 200

    except Exception as e:
        cot.end_step(step_id, output_data={'error': str(e)}, validation_passed=False)
        _logger.log(f"Error in find_pathway: {str(e)}", level="ERROR")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_v1.route('/context/pathways/optimize', methods=['POST'])
def optimize_pathways():
    """Optimize pathways based on usage."""
    cot = ChainOfThoughtLogger()
    step_id = cot.start_step(action="API_OPTIMIZE_PATHWAYS", level=LogLevel.INFO)

    try:
        usage_data = usage_tracker.pathway_counts
        path_optimizer.update_weights_from_usage(usage_data)

        stats = path_optimizer.get_optimization_statistics()
        cot.end_step(step_id, output_data={'stats': stats}, validation_passed=True)

        return jsonify(stats), 200

    except Exception as e:
        cot.end_step(step_id, output_data={'error': str(e)}, validation_passed=False)
        _logger.log(f"Error in optimize_pathways: {str(e)}", level="ERROR")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_v1.route('/context/statistics', methods=['GET'])
def get_context_statistics():
    """Get context memory statistics."""
    cot = ChainOfThoughtLogger()
    step_id = cot.start_step(action="API_GET_CONTEXT_STATISTICS", level=LogLevel.INFO)

    try:
        tree_stats = context_tree.get_statistics()
        traffic_stats = traffic_agent.get_statistics()
        usage_stats = usage_tracker.get_all_statistics()
        opt_stats = path_optimizer.get_optimization_statistics()

        combined = {
            'tree': tree_stats,
            'traffic': traffic_stats,
            'usage': usage_stats,
            'optimization': opt_stats
        }

        cot.end_step(step_id, output_data={'stats': combined}, validation_passed=True)

        return jsonify(combined), 200

    except Exception as e:
        cot.end_step(step_id, output_data={'error': str(e)}, validation_passed=False)
        _logger.log(f"Error in get_context_statistics: {str(e)}", level="ERROR")
        return jsonify({'success': False, 'error': str(e)}), 500
