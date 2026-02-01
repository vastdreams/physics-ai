"""
PATH: api/v1/knowledge.py
PURPOSE: API endpoints for the physics knowledge base (constants, equations, relationships)

ENDPOINTS:
- GET /api/v1/knowledge/constants - List all physical constants
- GET /api/v1/knowledge/constants/<symbol> - Get specific constant
- GET /api/v1/knowledge/equations - List all equations
- GET /api/v1/knowledge/equations/<name> - Get specific equation
- GET /api/v1/knowledge/equations/<name>/derivation - Get derivation tree
- GET /api/v1/knowledge/domains - List all domains
- GET /api/v1/knowledge/domains/<domain> - Get all knowledge for domain
- GET /api/v1/knowledge/search - Search constants and equations
- GET /api/v1/knowledge/statistics - Get database statistics

DEPENDENCIES:
- Flask: Web framework
- physics.knowledge: Knowledge base module
"""

from flask import Blueprint, jsonify, request
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from physics.knowledge import (
    get_knowledge_base,
    PhysicsDomain,
    EquationStatus
)

knowledge_bp = Blueprint('knowledge', __name__)


@knowledge_bp.route('/constants', methods=['GET'])
def list_constants():
    """
    List all physical constants.
    
    Query params:
    - domain: Filter by physics domain
    - exact_only: If true, only return exactly defined constants
    
    Returns:
        JSON with all constants
    """
    kb = get_knowledge_base()
    domain = request.args.get('domain')
    exact_only = request.args.get('exact_only', '').lower() == 'true'
    
    if domain:
        try:
            domain_enum = PhysicsDomain(domain)
            constants = kb.constants.list_by_domain(domain_enum)
        except ValueError:
            return jsonify({
                'error': f'Invalid domain: {domain}',
                'valid_domains': [d.value for d in PhysicsDomain]
            }), 400
    else:
        constants = kb.constants.list_all()
    
    if exact_only:
        constants = {k: v for k, v in constants.items() if v.is_exact}
    
    return jsonify({
        'count': len(constants),
        'constants': {k: v.to_dict() for k, v in constants.items()}
    })


@knowledge_bp.route('/constants/<symbol>', methods=['GET'])
def get_constant(symbol):
    """
    Get a specific physical constant.
    
    Args:
        symbol: The constant symbol (e.g., 'c', 'h', 'G')
    
    Returns:
        JSON with constant details
    """
    kb = get_knowledge_base()
    constant = kb.get_constant(symbol)
    
    if not constant:
        return jsonify({
            'error': f'Constant not found: {symbol}',
            'hint': 'Use /api/v1/knowledge/constants to list all available constants'
        }), 404
    
    return jsonify(constant.to_dict())


@knowledge_bp.route('/equations', methods=['GET'])
def list_equations():
    """
    List all physics equations.
    
    Query params:
    - domain: Filter by physics domain
    - status: Filter by verification status (fundamental, proven, empirical)
    - limit: Maximum number of results
    
    Returns:
        JSON with equations list
    """
    kb = get_knowledge_base()
    domain = request.args.get('domain')
    status = request.args.get('status')
    limit = request.args.get('limit', type=int)
    
    equations = kb.equations.list_all()
    
    if domain:
        try:
            domain_enum = PhysicsDomain(domain)
            equations = {k: v for k, v in equations.items() if v.domain == domain_enum}
        except ValueError:
            return jsonify({
                'error': f'Invalid domain: {domain}',
                'valid_domains': [d.value for d in PhysicsDomain]
            }), 400
    
    if status:
        try:
            status_enum = EquationStatus(status)
            equations = {k: v for k, v in equations.items() if v.status == status_enum}
        except ValueError:
            return jsonify({
                'error': f'Invalid status: {status}',
                'valid_statuses': [s.value for s in EquationStatus]
            }), 400
    
    if limit:
        equations = dict(list(equations.items())[:limit])
    
    return jsonify({
        'count': len(equations),
        'equations': {k: v.to_dict() for k, v in equations.items()}
    })


@knowledge_bp.route('/equations/<path:name>', methods=['GET'])
def get_equation(name):
    """
    Get a specific equation by name.
    
    Args:
        name: The equation name (e.g., "Newton's Second Law")
    
    Returns:
        JSON with equation details
    """
    kb = get_knowledge_base()
    equation = kb.get_equation(name)
    
    if not equation:
        # Try searching
        results = kb.equations.search(name)
        if results:
            suggestions = list(results.keys())[:5]
            return jsonify({
                'error': f'Equation not found: {name}',
                'suggestions': suggestions
            }), 404
        return jsonify({
            'error': f'Equation not found: {name}',
            'hint': 'Use /api/v1/knowledge/equations to list all equations'
        }), 404
    
    return jsonify(equation.to_dict())


@knowledge_bp.route('/equations/<path:name>/derivation', methods=['GET'])
def get_derivation(name):
    """
    Get the derivation tree for an equation.
    
    Shows what equations this derives from and what it leads to.
    
    Args:
        name: The equation name
    
    Returns:
        JSON with derivation relationships
    """
    kb = get_knowledge_base()
    tree = kb.equations.get_derivation_tree(name)
    
    if not tree:
        return jsonify({
            'error': f'Equation not found: {name}'
        }), 404
    
    return jsonify(tree)


@knowledge_bp.route('/domains', methods=['GET'])
def list_domains():
    """
    List all physics domains.
    
    Returns:
        JSON with domain list and counts
    """
    kb = get_knowledge_base()
    stats = kb.get_statistics()
    
    domains = []
    for domain in PhysicsDomain:
        domains.append({
            'name': domain.value,
            'equation_count': stats['equations_by_domain'].get(domain.value, 0)
        })
    
    return jsonify({
        'domains': domains
    })


@knowledge_bp.route('/domains/<domain>', methods=['GET'])
def get_domain(domain):
    """
    Get all knowledge for a specific domain.
    
    Args:
        domain: The domain name (e.g., 'classical_mechanics', 'quantum_mechanics')
    
    Returns:
        JSON with constants and equations for that domain
    """
    try:
        domain_enum = PhysicsDomain(domain)
    except ValueError:
        return jsonify({
            'error': f'Invalid domain: {domain}',
            'valid_domains': [d.value for d in PhysicsDomain]
        }), 400
    
    kb = get_knowledge_base()
    result = kb.get_domain(domain_enum)
    
    return jsonify({
        'domain': domain,
        'constants_count': len(result['constants']),
        'equations_count': len(result['equations']),
        'constants': {k: v.to_dict() for k, v in result['constants'].items()},
        'equations': {k: v.to_dict() for k, v in result['equations'].items()}
    })


@knowledge_bp.route('/search', methods=['GET'])
def search_knowledge():
    """
    Search the knowledge base.
    
    Query params:
    - q: Search query (required)
    
    Returns:
        JSON with matching constants and equations
    """
    query = request.args.get('q', '')
    
    if not query:
        return jsonify({
            'error': 'Search query required',
            'hint': 'Use ?q=your_search_term'
        }), 400
    
    kb = get_knowledge_base()
    results = kb.search_all(query)
    
    return jsonify({
        'query': query,
        'constants_count': len(results['constants']),
        'equations_count': len(results['equations']),
        'constants': {k: v.to_dict() for k, v in results['constants'].items()},
        'equations': {k: v.to_dict() for k, v in results['equations'].items()}
    })


@knowledge_bp.route('/statistics', methods=['GET'])
def get_statistics():
    """
    Get statistics about the knowledge base.
    
    Returns:
        JSON with counts and breakdowns
    """
    kb = get_knowledge_base()
    return jsonify(kb.get_statistics())


@knowledge_bp.route('/export', methods=['GET'])
def export_knowledge():
    """
    Export the entire knowledge base.
    
    Returns:
        JSON with all constants, equations, and statistics
    """
    kb = get_knowledge_base()
    return jsonify(kb.export_all())


@knowledge_bp.route('/fundamental', methods=['GET'])
def get_fundamental():
    """
    Get all fundamental equations (axioms/postulates).
    
    Returns:
        JSON with fundamental equations
    """
    kb = get_knowledge_base()
    fundamental = kb.equations.list_by_status(EquationStatus.FUNDAMENTAL)
    
    return jsonify({
        'count': len(fundamental),
        'equations': {k: v.to_dict() for k, v in fundamental.items()}
    })


@knowledge_bp.route('/relationships', methods=['GET'])
def get_relationships():
    """
    Get equation derivation relationships as a graph.
    
    Returns:
        JSON with nodes and edges for visualization
    """
    kb = get_knowledge_base()
    equations = kb.equations.list_all()
    
    nodes = []
    edges = []
    
    for name, eq in equations.items():
        nodes.append({
            'id': name,
            'domain': eq.domain.value,
            'status': eq.status.value
        })
        
        for parent in eq.derived_from:
            if parent in equations:
                edges.append({
                    'source': parent,
                    'target': name,
                    'type': 'derives'
                })
    
    return jsonify({
        'node_count': len(nodes),
        'edge_count': len(edges),
        'nodes': nodes,
        'edges': edges
    })
