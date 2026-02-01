"""
PATH: api/v1/knowledge.py
PURPOSE: REST API endpoints for the micro-modular physics knowledge base

ENDPOINTS:
- GET /knowledge/statistics     - Graph statistics
- GET /knowledge/nodes          - List all nodes
- GET /knowledge/nodes/:id      - Get specific node
- GET /knowledge/constants      - List constants
- GET /knowledge/equations      - List equations  
- GET /knowledge/domains        - List domains
- GET /knowledge/domains/:name  - Get domain contents
- GET /knowledge/path/:from/:to - Find derivation path
- GET /knowledge/derivation/:id - Get derivation tree
- GET /knowledge/search         - Search nodes
"""

from flask import Blueprint, jsonify, request
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

knowledge_bp = Blueprint('knowledge', __name__)


def get_graph():
    """Lazy import and get the knowledge graph."""
    from physics.knowledge import get_knowledge_graph
    return get_knowledge_graph()


def get_builder():
    """Get a graph builder instance."""
    from physics.knowledge import get_loader, GraphBuilder
    return GraphBuilder(get_loader())


def node_to_dict(node):
    """Convert a node to a serializable dictionary."""
    if hasattr(node, 'to_dict'):
        return node.to_dict()
    return {'id': str(node)}


@knowledge_bp.route('/statistics', methods=['GET'])
def get_statistics():
    """Get knowledge graph statistics."""
    try:
        graph = get_graph()
        stats = graph.get('statistics', {})
        
        # Add domain breakdown
        domains = graph.get('domains', {})
        stats['domains'] = {d: len(nodes) for d, nodes in domains.items()}
        
        return jsonify({
            'success': True,
            'statistics': stats
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@knowledge_bp.route('/nodes', methods=['GET'])
def list_nodes():
    """List all nodes with optional filtering."""
    try:
        graph = get_graph()
        nodes = graph.get('nodes', {})
        
        # Query parameters
        node_type = request.args.get('type')
        domain = request.args.get('domain')
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Filter
        result = []
        for node_id, node in nodes.items():
            if node_type and node.node_type.value != node_type:
                continue
            if domain and node.domain != domain:
                continue
            result.append(node_to_dict(node))
        
        # Paginate
        total = len(result)
        if limit:
            result = result[offset:offset + limit]
        
        return jsonify({
            'success': True,
            'total': total,
            'offset': offset,
            'count': len(result),
            'nodes': result
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@knowledge_bp.route('/nodes/<node_id>', methods=['GET'])
def get_node(node_id):
    """Get a specific node by ID."""
    try:
        graph = get_graph()
        nodes = graph.get('nodes', {})
        
        if node_id not in nodes:
            return jsonify({
                'success': False,
                'error': f'Node not found: {node_id}'
            }), 404
        
        node = nodes[node_id]
        node_dict = node_to_dict(node)
        
        # Add relation info
        outgoing = graph.get('outgoing', {}).get(node_id, [])
        incoming = graph.get('incoming', {}).get(node_id, [])
        
        node_dict['relations'] = {
            'outgoing': outgoing,
            'incoming': incoming
        }
        
        return jsonify({
            'success': True,
            'node': node_dict
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@knowledge_bp.route('/constants', methods=['GET'])
def list_constants():
    """List all physical constants."""
    try:
        graph = get_graph()
        nodes = graph.get('nodes', {})
        
        from physics.knowledge.base import ConstantNode
        
        constants = [
            node_to_dict(n) for n in nodes.values()
            if isinstance(n, ConstantNode)
        ]
        
        return jsonify({
            'success': True,
            'count': len(constants),
            'constants': constants
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@knowledge_bp.route('/constants/<constant_id>', methods=['GET'])
def get_constant(constant_id):
    """Get a specific constant."""
    try:
        graph = get_graph()
        nodes = graph.get('nodes', {})
        
        if constant_id not in nodes:
            return jsonify({
                'success': False,
                'error': f'Constant not found: {constant_id}'
            }), 404
        
        from physics.knowledge.base import ConstantNode
        node = nodes[constant_id]
        
        if not isinstance(node, ConstantNode):
            return jsonify({
                'success': False,
                'error': f'{constant_id} is not a constant'
            }), 400
        
        return jsonify({
            'success': True,
            'constant': node_to_dict(node)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@knowledge_bp.route('/equations', methods=['GET'])
def list_equations():
    """List all equations."""
    try:
        graph = get_graph()
        nodes = graph.get('nodes', {})
        
        from physics.knowledge.base import EquationNode
        
        domain = request.args.get('domain')
        limit = request.args.get('limit', type=int)
        
        equations = []
        for n in nodes.values():
            if isinstance(n, EquationNode):
                if domain and n.domain != domain:
                    continue
                equations.append(node_to_dict(n))
        
        if limit:
            equations = equations[:limit]
        
        return jsonify({
            'success': True,
            'count': len(equations),
            'equations': equations
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@knowledge_bp.route('/equations/<equation_id>', methods=['GET'])
def get_equation(equation_id):
    """Get a specific equation."""
    try:
        graph = get_graph()
        nodes = graph.get('nodes', {})
        
        if equation_id not in nodes:
            return jsonify({
                'success': False,
                'error': f'Equation not found: {equation_id}'
            }), 404
        
        node = nodes[equation_id]
        node_dict = node_to_dict(node)
        
        # Add derivation tree
        builder = get_builder()
        tree = builder.get_derivation_tree(equation_id, graph, depth=2)
        node_dict['derivation_tree'] = tree
        
        return jsonify({
            'success': True,
            'equation': node_dict
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@knowledge_bp.route('/domains', methods=['GET'])
def list_domains():
    """List all physics domains."""
    try:
        graph = get_graph()
        domains = graph.get('domains', {})
        
        domain_list = [
            {'name': name, 'node_count': len(nodes)}
            for name, nodes in domains.items()
        ]
        
        return jsonify({
            'success': True,
            'count': len(domain_list),
            'domains': domain_list
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@knowledge_bp.route('/domains/<domain_name>', methods=['GET'])
def get_domain(domain_name):
    """Get all nodes in a domain."""
    try:
        graph = get_graph()
        domains = graph.get('domains', {})
        nodes = graph.get('nodes', {})
        
        if domain_name not in domains:
            return jsonify({
                'success': False,
                'error': f'Domain not found: {domain_name}'
            }), 404
        
        node_ids = domains[domain_name]
        domain_nodes = [node_to_dict(nodes[nid]) for nid in node_ids if nid in nodes]
        
        return jsonify({
            'success': True,
            'domain': domain_name,
            'count': len(domain_nodes),
            'nodes': domain_nodes
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@knowledge_bp.route('/path/<start_id>/<end_id>', methods=['GET'])
def find_path(start_id, end_id):
    """Find derivation path between two nodes."""
    try:
        graph = get_graph()
        builder = get_builder()
        
        path = builder.find_path(start_id, end_id, graph)
        
        if path is None:
            return jsonify({
                'success': False,
                'error': f'No path found from {start_id} to {end_id}'
            }), 404
        
        # Get full node info for path
        nodes = graph.get('nodes', {})
        path_nodes = [node_to_dict(nodes[nid]) for nid in path if nid in nodes]
        
        return jsonify({
            'success': True,
            'path': path,
            'path_nodes': path_nodes,
            'length': len(path)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@knowledge_bp.route('/derivation/<node_id>', methods=['GET'])
def get_derivation(node_id):
    """Get the derivation tree for a node."""
    try:
        graph = get_graph()
        builder = get_builder()
        
        depth = request.args.get('depth', 3, type=int)
        tree = builder.get_derivation_tree(node_id, graph, depth=depth)
        
        if not tree:
            return jsonify({
                'success': False,
                'error': f'Node not found: {node_id}'
            }), 404
        
        return jsonify({
            'success': True,
            'derivation_tree': tree
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@knowledge_bp.route('/search', methods=['GET'])
def search_nodes():
    """Search nodes by name, description, or tags."""
    try:
        graph = get_graph()
        nodes = graph.get('nodes', {})
        
        query = request.args.get('q', '').lower()
        if not query:
            return jsonify({
                'success': False,
                'error': 'Query parameter q is required'
            }), 400
        
        results = []
        for node_id, node in nodes.items():
            # Search in name, description, tags
            searchable = ' '.join([
                node.name.lower(),
                node.description.lower() if hasattr(node, 'description') else '',
                ' '.join(node.tags) if hasattr(node, 'tags') else '',
                node.domain.lower()
            ])
            
            if query in searchable:
                results.append(node_to_dict(node))
        
        return jsonify({
            'success': True,
            'query': query,
            'count': len(results),
            'results': results
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@knowledge_bp.route('/export', methods=['GET'])
def export_graph():
    """Export the entire knowledge graph."""
    try:
        graph = get_graph()
        
        # Convert nodes to dicts
        nodes_dict = {nid: node_to_dict(n) for nid, n in graph.get('nodes', {}).items()}
        relations_dict = {rid: r.to_dict() for rid, r in graph.get('relations', {}).items()}
        
        return jsonify({
            'success': True,
            'graph': {
                'nodes': nodes_dict,
                'relations': relations_dict,
                'domains': graph.get('domains', {}),
                'statistics': graph.get('statistics', {})
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
