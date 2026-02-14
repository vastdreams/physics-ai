"""
PATH: api/v1/reasoning.py
PURPOSE: API endpoints for reasoning-based physics knowledge retrieval

Inspired by PageIndex (https://github.com/VectifyAI/PageIndex)
- Vectorless retrieval
- Reasoning-based navigation
- Explainable paths
"""

import json

from flask import Blueprint, jsonify, request

reasoning_bp = Blueprint('reasoning', __name__)


def get_retriever():
    """Lazy import and get the reasoning retriever."""
    from physics.knowledge.reasoning import ReasoningRetriever
    return ReasoningRetriever.from_knowledge_graph()


@reasoning_bp.route('/retrieve', methods=['POST'])
def retrieve():
    """
    Reasoning-based retrieval.

    POST /api/v1/reasoning/retrieve
    {
        "query": "What is the relationship between force and acceleration?",
        "max_results": 5,
        "include_derivations": true
    }
    """
    try:
        data = request.get_json() or {}
        query = data.get('query', '')

        if not query:
            return jsonify({
                'success': False,
                'error': 'Query is required'
            }), 400

        max_results = data.get('max_results', 5)
        include_derivations = data.get('include_derivations', True)

        retriever = get_retriever()
        result = retriever.retrieve(
            query=query,
            max_results=max_results,
            include_derivations=include_derivations
        )

        return jsonify({
            'success': True,
            'result': result.to_dict()
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@reasoning_bp.route('/answer', methods=['POST'])
def answer_question():
    """
    Answer a physics question using reasoning-based retrieval.

    POST /api/v1/reasoning/answer
    {
        "query": "How is kinetic energy derived from Newton's laws?"
    }
    """
    try:
        data = request.get_json() or {}
        query = data.get('query', '')

        if not query:
            return jsonify({
                'success': False,
                'error': 'Query is required'
            }), 400

        retriever = get_retriever()
        answer = retriever.answer_question(query)

        return jsonify({
            'success': True,
            'query': query,
            'answer': answer
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@reasoning_bp.route('/explain', methods=['POST'])
def explain_reasoning():
    """
    Get detailed explanation of reasoning process.

    POST /api/v1/reasoning/explain
    {
        "query": "What is the uncertainty principle?"
    }
    """
    try:
        data = request.get_json() or {}
        query = data.get('query', '')

        if not query:
            return jsonify({
                'success': False,
                'error': 'Query is required'
            }), 400

        retriever = get_retriever()
        explanation = retriever.explain_reasoning(query)

        return jsonify({
            'success': True,
            'query': query,
            'reasoning_explanation': explanation
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@reasoning_bp.route('/tree', methods=['GET'])
def get_tree():
    """Get the physics knowledge tree structure (PageIndex format)."""
    try:
        retriever = get_retriever()
        tree_json = retriever.get_tree_json()
        tree_data = json.loads(tree_json)

        return jsonify({
            'success': True,
            'tree': tree_data
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@reasoning_bp.route('/navigate', methods=['POST'])
def navigate_tree():
    """
    Navigate the tree from a specific node.

    POST /api/v1/reasoning/navigate
    {
        "node_id": "classical_mechanics",
        "query": "energy conservation"  // optional
    }
    """
    try:
        data = request.get_json() or {}
        node_id = data.get('node_id', 'root')
        query = data.get('query', '')

        retriever = get_retriever()
        context = retriever.tree.get_navigation_context(node_id)

        children = []
        node = retriever.tree.get_node(node_id)
        if node:
            for child in node.children:
                children.append({
                    'id': child.node_id,
                    'title': child.title,
                    'type': child.node_type.value,
                    'summary': child.summary[:200] if child.summary else ''
                })

        result = {
            'success': True,
            'node_id': node_id,
            'navigation_context': context,
            'children': children
        }

        # If query provided, score children by relevance
        if query:
            query_lower = query.lower()
            for child in children:
                score = 0
                if any(w in child['title'].lower() for w in query_lower.split()):
                    score += 0.5
                if any(w in child.get('summary', '').lower() for w in query_lower.split()):
                    score += 0.3
                child['relevance_score'] = score

            children.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
            result['children'] = children

        return jsonify(result)

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@reasoning_bp.route('/derivation/<node_id>', methods=['GET'])
def get_derivation_chain(node_id: str):
    """Get the derivation chain for a concept."""
    try:
        retriever = get_retriever()
        chain = retriever.reasoner.get_derivation_chain(node_id)

        chain_data = []
        for node in chain:
            chain_data.append({
                'id': node.node_id,
                'title': node.title,
                'type': node.node_type.value,
                'domain': node.domain,
                'summary': node.summary
            })

        return jsonify({
            'success': True,
            'node_id': node_id,
            'derivation_chain': chain_data,
            'chain_length': len(chain_data)
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@reasoning_bp.route('/concept/<node_id>/explain', methods=['GET'])
def explain_concept(node_id: str):
    """Get a detailed explanation of a concept."""
    try:
        retriever = get_retriever()
        explanation = retriever.reasoner.explain_concept(node_id)

        return jsonify({
            'success': True,
            'node_id': node_id,
            'explanation': explanation
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
