# PATH: substrate/main.py
# PURPOSE:
#   - Main entry point for the Physics AI substrate
#   - Wires all components together
#   - Provides initialization and startup functions
#
# ROLE IN ARCHITECTURE:
#   - Bootstrap layer that creates and connects all systems
#
# MAIN EXPORTS:
#   - PhysicsAI: Main class that orchestrates everything
#   - create_physics_ai: Factory function
#
# NON-RESPONSIBILITIES:
#   - Does NOT implement component logic (that's in submodules)
#   - Does NOT handle HTTP (that's in api/)
#
# NOTES FOR FUTURE AI:
#   - This is where the system comes together
#   - Modify initialization here to change startup behavior
#   - Evolution loop starts automatically by default

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Optional, Any
import os
import json

from substrate.graph.formula import Formula
from substrate.graph.formula_graph import FormulaGraph, create_classical_mechanics_graph
from substrate.planner.formula_planner import FormulaPlanner
from substrate.memory.reasoning_trace import TraceStore
from substrate.critics.local_llm import (
    LocalLLMBackend, LLMConfig, LLMBackendType, 
    MockLLMBackend, create_llm_backend
)
from substrate.critics.logic_critic import LogicCritic
from substrate.critics.code_critic import CodeCritic
from substrate.critics.meta_critic import MetaCritic
from substrate.evolution.evolution_loop import EvolutionLoop, EvolutionConfig
from substrate.interface.chatbot import ChatbotInterface, ChatSession
from substrate.execution.executor import FormulaExecutor


@dataclass
class PhysicsAIConfig:
    """Configuration for the Physics AI system."""
    
    # Paths
    data_dir: str = ".physics_ai_data"
    graph_path: str = "formula_graph.json"
    
    # LLM configuration
    llm_backend_type: str = "throttled_openai"  # mock|subprocess|openai_compatible|throttled_openai
    llm_model_name: str = "lmstudio-deepseek"   # LM Studio model name
    llm_server_url: str = "http://127.0.0.1:8080"  # LM Studio / llama-server URL
    llm_model_path: Optional[str] = None
    llm_executable_path: Optional[str] = None
    
    # Evolution configuration
    evolution_enabled: bool = True
    evolution_interval_seconds: float = 300.0  # 5 minutes
    evolution_auto_apply: bool = True
    evolution_min_confidence: float = 0.3
    
    # Codebase
    codebase_root: str = "."
    
    # Initialize with classical mechanics
    seed_classical_mechanics: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "data_dir": self.data_dir,
            "graph_path": self.graph_path,
            "llm_backend_type": self.llm_backend_type,
            "llm_model_name": self.llm_model_name,
            "llm_server_url": self.llm_server_url,
            "evolution_enabled": self.evolution_enabled,
            "evolution_interval_seconds": self.evolution_interval_seconds,
            "evolution_auto_apply": self.evolution_auto_apply,
            "evolution_min_confidence": self.evolution_min_confidence,
            "codebase_root": self.codebase_root,
            "seed_classical_mechanics": self.seed_classical_mechanics,
        }


class PhysicsAI:
    """
    Main Physics AI system.
    
    This class orchestrates all components:
    - FormulaGraph (reality substrate)
    - FormulaPlanner (derivation planning)
    - TraceStore (hot memory)
    - Critics (logic, code, meta)
    - EvolutionLoop (self-modification)
    - ChatbotInterface (user interaction)
    
    Example usage:
        ai = PhysicsAI.create()
        ai.start()
        response = ai.chat("What is the kinetic energy of a 10kg object moving at 5m/s?")
        print(response.content)
    """
    
    def __init__(self, config: PhysicsAIConfig):
        self.config = config
        
        # Create data directory
        os.makedirs(config.data_dir, exist_ok=True)
        
        # Initialize components
        self._init_llm()
        self._init_graph()
        self._init_memory()
        self._init_critics()
        self._init_planner()
        self._init_executor()
        self._init_evolution()
        self._init_chatbot()
        
        self._running = False
    
    def _init_llm(self):
        """Initialize LLM backend."""
        backend_type = {
            "mock": LLMBackendType.MOCK,
            "subprocess": LLMBackendType.SUBPROCESS,
            "openai_compatible": LLMBackendType.OPENAI_COMPATIBLE,
            "throttled_openai": LLMBackendType.THROTTLED_OPENAI,
        }.get(self.config.llm_backend_type, LLMBackendType.MOCK)
        
        llm_config = LLMConfig(
            backend_type=backend_type,
            model_name=self.config.llm_model_name,
            server_url=self.config.llm_server_url,
            model_path=self.config.llm_model_path,
            executable_path=self.config.llm_executable_path,
            throttle_max_concurrent=int(os.getenv("LM_STUDIO_MAX_CONCURRENT", "1")),
            throttle_min_delay=float(os.getenv("LM_STUDIO_MIN_DELAY", "0.5")),
            throttle_default_max_tokens=int(os.getenv("LM_STUDIO_MAX_TOKENS", "512")),
        )
        
        self.llm = create_llm_backend(llm_config)
    
    def _init_graph(self):
        """Initialize FormulaGraph."""
        graph_path = os.path.join(self.config.data_dir, self.config.graph_path)
        
        if os.path.exists(graph_path):
            # Load existing graph
            self.graph = FormulaGraph(persist_path=graph_path)
        elif self.config.seed_classical_mechanics:
            # Create with classical mechanics seed
            self.graph = create_classical_mechanics_graph()
            self.graph._persist_path = graph_path
        else:
            # Empty graph
            self.graph = FormulaGraph(persist_path=graph_path)
    
    def _init_memory(self):
        """Initialize memory systems."""
        self.trace_store = TraceStore(max_buffer_size=1000)
    
    def _init_critics(self):
        """Initialize critic systems."""
        self.logic_critic = LogicCritic(self.llm, self.graph)
        self.code_critic = CodeCritic(self.llm, self.config.codebase_root)
        self.meta_critic = MetaCritic(self.llm)
        
        # Register critics
        self.meta_critic.register_critic(self.logic_critic.critic_id, "logic")
        self.meta_critic.register_critic(self.code_critic.critic_id, "code")
    
    def _init_planner(self):
        """Initialize planner."""
        self.planner = FormulaPlanner(self.graph)

    def _init_executor(self):
        """Initialize formula executor."""
        self.executor = FormulaExecutor()
    
    def _init_evolution(self):
        """Initialize evolution loop."""
        evolution_config = EvolutionConfig(
            cycle_interval_seconds=self.config.evolution_interval_seconds,
            min_confidence_for_action=self.config.evolution_min_confidence,
            auto_apply_patches=self.config.evolution_auto_apply,
            codebase_root=self.config.codebase_root,
            backup_dir=os.path.join(self.config.data_dir, "backups"),
            log_dir=os.path.join(self.config.data_dir, "evolution_logs"),
        )
        
        self.evolution = EvolutionLoop(
            config=evolution_config,
            formula_graph=self.graph,
            llm_backend=self.llm,
            trace_store=self.trace_store,
            logic_critic=self.logic_critic,
            code_critic=self.code_critic,
            meta_critic=self.meta_critic,
        )
    
    def _init_chatbot(self):
        """Initialize chatbot interface."""
        self.chatbot = ChatbotInterface(
            formula_graph=self.graph,
            llm_backend=self.llm,
            trace_store=self.trace_store,
            planner=self.planner,
            logic_critic=self.logic_critic,
            executor=self.executor,
        )
    
    # =========================================================================
    # Lifecycle
    # =========================================================================
    
    def start(self):
        """Start the Physics AI system."""
        if self._running:
            return
        
        self._running = True
        
        # Start evolution loop if enabled
        if self.config.evolution_enabled:
            self.evolution.start()
        
        print("Physics AI started")
        print(f"  - Graph has {len(self.graph)} formulas")
        print(f"  - Evolution: {'enabled' if self.config.evolution_enabled else 'disabled'}")
        print(f"  - LLM backend: {self.config.llm_backend_type}")
    
    def stop(self):
        """Stop the Physics AI system."""
        if not self._running:
            return
        
        self._running = False
        
        # Stop evolution
        self.evolution.stop()
        
        # Save graph
        self.graph.save()
        
        print("Physics AI stopped")
    
    # =========================================================================
    # Main interface
    # =========================================================================
    
    def chat(
        self,
        message: str,
        session_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Send a message to the Physics AI.
        
        Args:
            message: Natural language message
            session_id: Optional session ID for conversation context
            context: Optional additional context
            
        Returns:
            ChatMessage with response
        """
        return self.chatbot.chat(message, session_id, context)
    
    def create_session(self, context: Optional[Dict[str, Any]] = None) -> ChatSession:
        """Create a new chat session."""
        return self.chatbot.create_session(context)
    
    # =========================================================================
    # Direct access to components
    # =========================================================================
    
    def get_formula(self, formula_id: str) -> Optional[Formula]:
        """Get a formula by ID."""
        return self.graph.get_formula(formula_id)
    
    def add_formula(self, formula: Formula) -> bool:
        """Add a formula to the graph."""
        return self.graph.add_formula(formula)
    
    def search_formulas(self, query: str, domain: Optional[str] = None, limit: int = 10):
        """Search for formulas."""
        return self.chatbot.search_formulas(query, domain, limit)
    
    def get_trace(self, trace_id: str):
        """Get a reasoning trace."""
        return self.chatbot.get_trace(trace_id)
    
    def force_evolution_cycle(self):
        """Force an immediate evolution cycle."""
        return self.evolution.force_cycle()
    
    # =========================================================================
    # Statistics
    # =========================================================================
    
    def stats(self) -> Dict[str, Any]:
        """Get system statistics."""
        return {
            "running": self._running,
            "graph": self.graph.stats(),
            "evolution": self.evolution.get_statistics(),
            "traces": self.trace_store.statistics(),
            "llm": self.llm.statistics(),
            "meta_critic": self.meta_critic.statistics(),
        }

    # -------------------------------------------------------------------------
    # Planner / Executor helpers
    # -------------------------------------------------------------------------
    def dry_run_plan(
        self,
        inputs: Dict[str, Any],
        outputs: List[str],
        context: Optional[Dict[str, Any]] = None,
        max_plans: int = 3,
    ) -> List[Dict[str, Any]]:
        """Run planner without execution; return plan dicts."""
        plans = self.planner.plan(
            inputs=inputs,
            outputs=outputs,
            context=context or {},
            max_plans=max_plans,
        )
        return [p.to_dict() for p in plans]

    def execute_formula(
        self,
        formula_id: str,
        inputs: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute a single formula via executor."""
        formula = self.graph.get_formula(formula_id)
        if not formula:
            raise ValueError(f"Formula not found: {formula_id}")
        outputs = self.executor.evaluate_formula(formula, inputs)
        if outputs is None:
            raise ValueError("Execution failed")
        return outputs
    
    # =========================================================================
    # Factory
    # =========================================================================
    
    @classmethod
    def create(cls, config: Optional[PhysicsAIConfig] = None) -> PhysicsAI:
        """Create a new Physics AI instance."""
        config = config or PhysicsAIConfig()
        return cls(config)
    
    @classmethod
    def from_config_file(cls, path: str) -> PhysicsAI:
        """Create from a config file."""
        with open(path) as f:
            data = json.load(f)
        config = PhysicsAIConfig(**data)
        return cls(config)


def create_physics_ai(
    llm_backend: str = "mock",
    evolution_enabled: bool = True,
    **kwargs
) -> PhysicsAI:
    """
    Factory function to create a Physics AI instance.
    
    Args:
        llm_backend: "mock", "subprocess", or "openai_compatible"
        evolution_enabled: Whether to enable self-evolution
        **kwargs: Additional config options
        
    Returns:
        PhysicsAI instance
    """
    config = PhysicsAIConfig(
        llm_backend_type=llm_backend,
        evolution_enabled=evolution_enabled,
        **kwargs
    )
    return PhysicsAI(config)


# =========================================================================
# CLI entry point
# =========================================================================

def main():
    """Command-line entry point for Physics AI."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Physics AI - Self-evolving physics reasoning system")
    parser.add_argument("--config", type=str, help="Path to config file")
    parser.add_argument("--llm-backend", type=str, default="mock", 
                       choices=["mock", "subprocess", "openai_compatible"],
                       help="LLM backend type")
    parser.add_argument("--llm-server", type=str, default="http://localhost:8000",
                       help="LLM server URL (for openai_compatible)")
    parser.add_argument("--no-evolution", action="store_true",
                       help="Disable self-evolution")
    parser.add_argument("--interactive", action="store_true",
                       help="Start interactive chat mode")
    
    args = parser.parse_args()
    
    # Create config
    if args.config:
        ai = PhysicsAI.from_config_file(args.config)
    else:
        config = PhysicsAIConfig(
            llm_backend_type=args.llm_backend,
            llm_server_url=args.llm_server,
            evolution_enabled=not args.no_evolution,
        )
        ai = PhysicsAI(config)
    
    # Start
    ai.start()
    
    if args.interactive:
        print("\n" + "=" * 60)
        print("Physics AI Interactive Mode")
        print("Type 'quit' to exit, 'stats' for statistics")
        print("=" * 60 + "\n")
        
        session = ai.create_session()
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() == "quit":
                    break
                
                if user_input.lower() == "stats":
                    print(json.dumps(ai.stats(), indent=2, default=str))
                    continue
                
                if user_input.lower() == "evolve":
                    result = ai.force_evolution_cycle()
                    print(f"Evolution cycle complete: {result.actions_succeeded}/{result.actions_applied} actions succeeded")
                    continue
                
                response = ai.chat(user_input, session_id=session.id)
                print(f"\nAI: {response.content}")
                
                if response.confidence < 1.0:
                    print(f"   (Confidence: {response.confidence:.2f})")
                
                print()
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")
    
    ai.stop()


if __name__ == "__main__":
    main()

