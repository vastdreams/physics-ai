# api/v1/
"""
API v1 endpoints.

Includes:
- simulate: Physics simulation endpoints
- nodes: Code graph operations
- rules: Rule engine management
- evolution: Self-evolution control
- cot: Chain-of-thought logging
- vector: Uncertainty management
- state_graph: State machine operations
- context: Context memory
- equational: Equation solving
- brain: Brain modal
- substrate: PhysicsAI substrate
- knowledge: Physics knowledge base (constants, equations, relationships)
- reasoning: PageIndex-style reasoning-based retrieval
- logs: Real-time system logging
- agents: DREAM-style multi-layer agent system
"""

from flask import Blueprint

api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')

from . import simulate, nodes, rules, evolution, cot, vector, state_graph, context, equational, brain, substrate
# Import substrate blueprint for direct registration
from .substrate import substrate_bp
# Import knowledge blueprint
from .knowledge import knowledge_bp
# Import reasoning blueprint (PageIndex-inspired)
from .reasoning import reasoning_bp
# Import logs blueprint
from .logs import logs_bp
# Import agents blueprint (DREAM-style multi-layer agents)
from .agents import agents_bp
# Import evolution API blueprint
from .evolution_api import evolution_bp

# Register nested blueprints under api_v1
api_v1.register_blueprint(substrate_bp)
api_v1.register_blueprint(knowledge_bp, url_prefix='/knowledge')
api_v1.register_blueprint(reasoning_bp, url_prefix='/reasoning')
api_v1.register_blueprint(logs_bp)
api_v1.register_blueprint(agents_bp)
api_v1.register_blueprint(evolution_bp)

