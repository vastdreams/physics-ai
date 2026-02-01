"""
PATH: ai/agents/__init__.py
PURPOSE: DREAM-style multi-layer agent system for physics AI

AGENTS:
- GatekeeperAgent: Layer A - routing, validation, quick checks
- WorkhorseAgent: Layer B - extraction, calculation, tool calling  
- OrchestratorAgent: Layer C - complex reasoning, planning, synthesis

DESIGN PRINCIPLE:
- LLM proposes structure and narrative
- Deterministic code produces numbers and calculations
- Agents only write what they are given (no hallucinated numbers)
"""

from .gatekeeper import GatekeeperAgent
from .workhorse import WorkhorseAgent
from .orchestrator import OrchestratorAgent
from .base import BaseAgent, AgentResponse

__all__ = [
    'BaseAgent',
    'AgentResponse',
    'GatekeeperAgent',
    'WorkhorseAgent', 
    'OrchestratorAgent',
]
