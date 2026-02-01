# api/v1/
"""
API v1 endpoints.
"""

from flask import Blueprint

api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')

from . import simulate, nodes, rules, evolution, cot, vector, state_graph, context, equational, brain, substrate
# Import substrate blueprint for direct registration
from .substrate import substrate_bp

# Register nested blueprint for substrate under api_v1
api_v1.register_blueprint(substrate_bp)

