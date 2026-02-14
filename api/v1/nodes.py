"""Nodal graph endpoints."""

from flask import jsonify, request

from ai.nodal_vectorization.graph_builder import GraphBuilder
from ai.nodal_vectorization.node_analyzer import NodeAnalyzer
from ai.nodal_vectorization.vector_store import VectorStore
from api.v1 import api_v1
from loggers.system_logger import SystemLogger
from utilities.cot_logging import ChainOfThoughtLogger, LogLevel

_logger = SystemLogger()
vector_store = VectorStore()
graph_builder = GraphBuilder(vector_store)
node_analyzer = NodeAnalyzer()


@api_v1.route('/nodes', methods=['GET'])
def list_nodes():
    """
    List all nodes in the graph.

    Query parameters:
    - limit: Maximum number of nodes to return
    - offset: Offset for pagination
    """
    cot = ChainOfThoughtLogger()
    step_id = cot.start_step(action="API_LIST_NODES", input_data={'endpoint': '/api/v1/nodes'}, level=LogLevel.INFO)

    try:
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))

        all_nodes = graph_builder.nodes
        node_list = list(all_nodes.values())[offset:offset+limit]

        result = {
            'nodes': [node.to_dict() for node in node_list],
            'total': len(all_nodes),
            'limit': limit,
            'offset': offset
        }

        cot.end_step(step_id, output_data={'node_count': len(node_list)}, validation_passed=True)

        return jsonify(result), 200

    except Exception as e:
        cot.end_step(step_id, output_data={'error': str(e)}, validation_passed=False)
        _logger.log(f"Error in list_nodes endpoint: {str(e)}", level="ERROR")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_v1.route('/nodes/<node_id>', methods=['GET'])
def get_node(node_id: str):
    """Get a specific node by ID."""
    cot = ChainOfThoughtLogger()
    step_id = cot.start_step(action="API_GET_NODE", input_data={'node_id': node_id}, level=LogLevel.INFO)

    try:
        node = graph_builder.get_node(node_id)

        if not node:
            cot.end_step(step_id, output_data={'error': 'Node not found'}, validation_passed=False)
            return jsonify({'success': False, 'error': 'Node not found'}), 404

        result = node.to_dict()

        # Add graph information
        result['dependencies'] = list(graph_builder.get_dependencies(node_id))
        result['dependents'] = list(graph_builder.get_dependents(node_id))

        cot.end_step(step_id, output_data={'node_id': node_id}, validation_passed=True)

        return jsonify(result), 200

    except Exception as e:
        cot.end_step(step_id, output_data={'error': str(e)}, validation_passed=False)
        _logger.log(f"Error in get_node endpoint: {str(e)}", level="ERROR")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_v1.route('/nodes/analyze', methods=['POST'])
def analyze_directory():
    """
    Analyze a directory and add nodes to graph.

    Request body:
    {
        "directory": "/path/to/directory"
    }
    """
    cot = ChainOfThoughtLogger()
    step_id = cot.start_step(action="API_ANALYZE_DIRECTORY", input_data={'endpoint': '/api/v1/nodes/analyze'}, level=LogLevel.INFO)

    try:
        data = request.get_json()

        if not data or 'directory' not in data:
            cot.end_step(step_id, output_data={'error': 'Directory not provided'}, validation_passed=False)
            return jsonify({'success': False, 'error': 'Directory not provided'}), 400

        directory = data['directory']
        nodes = node_analyzer.analyze_directory(directory)

        for node in nodes:
            graph_builder.add_node(node)

        result = {
            'nodes_analyzed': len(nodes),
            'nodes': [node.to_dict() for node in nodes]
        }

        cot.end_step(step_id, output_data={'nodes_analyzed': len(nodes)}, validation_passed=True)

        return jsonify(result), 200

    except Exception as e:
        cot.end_step(step_id, output_data={'error': str(e)}, validation_passed=False)
        _logger.log(f"Error in analyze_directory endpoint: {str(e)}", level="ERROR")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_v1.route('/nodes/graph/statistics', methods=['GET'])
def graph_statistics():
    """Get graph statistics."""
    cot = ChainOfThoughtLogger()
    step_id = cot.start_step(action="API_GRAPH_STATISTICS", level=LogLevel.INFO)

    try:
        stats = graph_builder.get_statistics()
        cot.end_step(step_id, output_data={'statistics': stats}, validation_passed=True)

        return jsonify(stats), 200

    except Exception as e:
        cot.end_step(step_id, output_data={'error': str(e)}, validation_passed=False)
        _logger.log(f"Error in graph_statistics endpoint: {str(e)}", level="ERROR")
        return jsonify({'success': False, 'error': str(e)}), 500
