"""
PATH: api/v1/evolution_api.py
PURPOSE: REST API for self-evolution system

ENDPOINTS:
- GET  /evolution/status         - Get evolution system status
- GET  /evolution/proposals      - List proposals
- GET  /evolution/proposals/:id  - Get specific proposal
- POST /evolution/proposals      - Create new proposal
- POST /evolution/validate/:id   - Validate a proposal
- POST /evolution/approve/:id    - Approve a proposal
- POST /evolution/apply/:id      - Apply a proposal
- POST /evolution/rollback/:id   - Rollback a proposal
- POST /evolution/rate/:id       - Rate a proposal
- GET  /evolution/metrics        - Get evolution metrics
"""

import asyncio

from flask import Blueprint, jsonify, request

from ai.evolution.engine import get_evolution_engine
from ai.evolution.proposal import ProposalStatus, ProposalType

evolution_bp = Blueprint('evolution_api', __name__, url_prefix='/evolution')


@evolution_bp.route('/status', methods=['GET'])
def get_status():
    """Get evolution system status."""
    engine = get_evolution_engine()
    return jsonify({
        'success': True,
        'status': engine.get_evolution_status()
    })


@evolution_bp.route('/proposals', methods=['GET'])
def list_proposals():
    """List evolution proposals."""
    status_filter = request.args.get('status')
    limit = request.args.get('limit', 50, type=int)

    status = None
    if status_filter:
        try:
            status = ProposalStatus(status_filter)
        except ValueError:
            pass

    engine = get_evolution_engine()
    proposals = engine.get_proposal_history(limit=limit, status=status)

    return jsonify({
        'success': True,
        'count': len(proposals),
        'proposals': proposals
    })


@evolution_bp.route('/proposals/<proposal_id>', methods=['GET'])
def get_proposal(proposal_id: str):
    """Get a specific proposal."""
    engine = get_evolution_engine()
    proposal = engine.tracker.get_proposal(proposal_id)

    if not proposal:
        return jsonify({
            'success': False,
            'error': f'Proposal not found: {proposal_id}'
        }), 404

    return jsonify({
        'success': True,
        'proposal': proposal.to_dict()
    })


@evolution_bp.route('/proposals', methods=['POST'])
def create_proposal():
    """Create a new evolution proposal."""
    data = request.get_json() or {}

    proposal_type_str = data.get('type', 'code_improvement')
    try:
        proposal_type = ProposalType(proposal_type_str)
    except ValueError:
        return jsonify({
            'success': False,
            'error': f'Invalid proposal type: {proposal_type_str}'
        }), 400

    engine = get_evolution_engine()

    # Handle equation proposals specially
    if proposal_type == ProposalType.NEW_EQUATION:
        required = ['name', 'latex', 'sympy', 'variables', 'domain']
        missing = [f for f in required if f not in data]
        if missing:
            return jsonify({
                'success': False,
                'error': f'Missing required fields for equation: {missing}'
            }), 400

        proposal = engine.create_equation_proposal(
            equation_name=data['name'],
            latex=data['latex'],
            sympy=data['sympy'],
            variables=data['variables'],
            domain=data['domain'],
            description=data.get('description', ''),
            motivation=data.get('motivation', ''),
        )
    else:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        proposal = loop.run_until_complete(
            engine.generate_proposal(
                trigger=data.get('trigger', 'user_request'),
                context=data.get('context', {}),
                proposal_type=proposal_type,
            )
        )

    return jsonify({
        'success': True,
        'proposal': proposal.to_dict()
    })


@evolution_bp.route('/validate/<proposal_id>', methods=['POST'])
def validate_proposal(proposal_id: str):
    """Validate a proposal."""
    engine = get_evolution_engine()
    proposal = engine.tracker.get_proposal(proposal_id)

    if not proposal:
        return jsonify({
            'success': False,
            'error': f'Proposal not found: {proposal_id}'
        }), 404

    result = engine.validate_proposal(proposal)

    return jsonify({
        'success': True,
        'validation': result.to_dict(),
        'proposal_status': proposal.status.value
    })


@evolution_bp.route('/approve/<proposal_id>', methods=['POST'])
def approve_proposal(proposal_id: str):
    """Manually approve a proposal."""
    engine = get_evolution_engine()
    proposal = engine.tracker.get_proposal(proposal_id)

    if not proposal:
        return jsonify({
            'success': False,
            'error': f'Proposal not found: {proposal_id}'
        }), 404

    if proposal.status not in [ProposalStatus.PENDING, ProposalStatus.REJECTED]:
        return jsonify({
            'success': False,
            'error': f'Proposal cannot be approved in status: {proposal.status.value}'
        }), 400

    proposal.status = ProposalStatus.APPROVED
    engine.tracker.update_proposal(proposal)

    return jsonify({
        'success': True,
        'message': 'Proposal approved',
        'proposal': proposal.to_dict()
    })


@evolution_bp.route('/apply/<proposal_id>', methods=['POST'])
def apply_proposal(proposal_id: str):
    """Apply an approved proposal."""
    engine = get_evolution_engine()
    proposal = engine.tracker.get_proposal(proposal_id)

    if not proposal:
        return jsonify({
            'success': False,
            'error': f'Proposal not found: {proposal_id}'
        }), 404

    if proposal.status != ProposalStatus.APPROVED:
        return jsonify({
            'success': False,
            'error': f'Proposal must be approved first (current status: {proposal.status.value})'
        }), 400

    success = engine.apply_proposal(proposal)

    return jsonify({
        'success': success,
        'message': 'Proposal applied' if success else 'Apply failed',
        'proposal': proposal.to_dict()
    })


@evolution_bp.route('/rollback/<proposal_id>', methods=['POST'])
def rollback_proposal(proposal_id: str):
    """Rollback an applied proposal."""
    engine = get_evolution_engine()

    success = engine.rollback_proposal(proposal_id)

    if not success:
        return jsonify({
            'success': False,
            'error': 'Rollback failed. Proposal may not be applied or rollback data unavailable.'
        }), 400

    proposal = engine.tracker.get_proposal(proposal_id)

    return jsonify({
        'success': True,
        'message': 'Proposal rolled back',
        'proposal': proposal.to_dict() if proposal else None
    })


@evolution_bp.route('/rate/<proposal_id>', methods=['POST'])
def rate_proposal(proposal_id: str):
    """Rate a proposal for learning."""
    data = request.get_json() or {}

    rating = data.get('rating')
    if not rating or not isinstance(rating, int) or rating < 1 or rating > 5:
        return jsonify({
            'success': False,
            'error': 'Rating must be an integer 1-5'
        }), 400

    feedback = data.get('feedback', '')

    engine = get_evolution_engine()
    engine.rate_proposal(proposal_id, rating, feedback)

    proposal = engine.tracker.get_proposal(proposal_id)

    return jsonify({
        'success': True,
        'message': 'Rating recorded',
        'proposal': proposal.to_dict() if proposal else None
    })


@evolution_bp.route('/metrics', methods=['GET'])
def get_metrics():
    """Get evolution metrics."""
    engine = get_evolution_engine()
    metrics = engine.tracker.get_metrics()

    return jsonify({
        'success': True,
        'metrics': metrics.to_dict()
    })


@evolution_bp.route('/patterns', methods=['GET'])
def get_patterns():
    """Get success and failure patterns."""
    engine = get_evolution_engine()

    return jsonify({
        'success': True,
        'patterns': {
            'success': engine.tracker.get_successful_patterns(),
            'failure': engine.tracker.get_failure_patterns(),
        }
    })


@evolution_bp.route('/timeline', methods=['GET'])
def get_timeline():
    """Get evolution timeline."""
    days = request.args.get('days', 30, type=int)

    engine = get_evolution_engine()
    timeline = engine.tracker.get_timeline(days=days)

    return jsonify({
        'success': True,
        'timeline': timeline
    })
