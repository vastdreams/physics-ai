# PATH: substrate/__init__.py
# PURPOSE:
#   - Root package for the Beyond Frontier reality substrate
#   - Contains the Formula Graph, Planner, Memory, Critics, and Evolution systems
#
# ROLE IN ARCHITECTURE:
#   - Core layer that grounds all reasoning in physical reality
#   - Everything else (LLM, chatbot, API) sits on top of this substrate
#
# MAIN EXPORTS:
#   - Formula: First-class representation of a physical law/equation
#   - FormulaGraph: Graph of formulas with derivation/limit relationships
#   - FormulaPlanner: Plans derivation paths through the graph
#   - ReasoningTrace: Hot memory for per-query reasoning
#   - LocalLLMBackend: Interface to local DeepSeek model
#   - LogicCritic, CodeCritic, MetaCritic: Audit stack
#   - EvolutionLoop: Unconstrained self-modification engine
#   - ChatbotInterface: Final user-facing layer
#
# NON-RESPONSIBILITIES:
#   - Does NOT handle HTTP/API concerns (that's in api/)
#   - Does NOT handle visualization (that's in dashboard/)
#
# NOTES FOR FUTURE AI:
#   - This is the "reality fabric" - all reasoning should trace back here
#   - Evolution happens at this layer, not above it
#   - No safety gating - only technical validators

from substrate.critics.code_critic import CodeCritic
from substrate.critics.local_llm import LocalLLMBackend
from substrate.critics.logic_critic import LogicCritic
from substrate.critics.meta_critic import MetaCritic
from substrate.evolution.evolution_loop import EvolutionLoop
from substrate.execution.executor import FormulaExecutor
from substrate.graph.formula import Formula, FormulaLayer, FormulaStatus
from substrate.graph.formula_graph import EdgeType, FormulaGraph
from substrate.interface.chatbot import ChatbotInterface
from substrate.memory.reasoning_trace import ReasoningTrace, TraceStep
from substrate.planner.formula_planner import DerivationPlan, FormulaPlanner

__all__ = [
    "Formula",
    "FormulaStatus",
    "FormulaLayer",
    "FormulaGraph",
    "EdgeType",
    "FormulaPlanner",
    "DerivationPlan",
    "ReasoningTrace",
    "TraceStep",
    "FormulaExecutor",
    "LocalLLMBackend",
    "LogicCritic",
    "CodeCritic",
    "MetaCritic",
    "EvolutionLoop",
    "ChatbotInterface",
]
