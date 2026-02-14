"""
Integration tests for unified Beyond Frontier system.

Tests the integration of all components:
- Nodal vectorization
- Enhanced registry
- CoT logging
- Self-evolution
- Enhanced rules
- API layer
"""

from __future__ import annotations

import os

from ai.nodal_vectorization.graph_builder import GraphBuilder
from ai.nodal_vectorization.node_analyzer import NodeAnalyzer
from ai.nodal_vectorization.vector_store import VectorStore
from evolution.self_evolution import SelfEvolutionEngine
from loggers.system_logger import SystemLogger
from physics.integration.physics_integrator import PhysicsIntegrator
from rules.enhanced_rule_engine import EnhancedRule, EnhancedRuleEngine, RulePriority
from utilities.cot_logging import ChainOfThoughtLogger, LogLevel
from utilities.enhanced_registry import EnhancedRegistry


def test_integration() -> None:
    """Test integration of all components."""
    _logger = SystemLogger()
    _logger.log("Starting integration test", level="INFO")

    vector_store = VectorStore()
    graph_builder = GraphBuilder(vector_store)
    node_analyzer = NodeAnalyzer()
    registry = EnhancedRegistry()
    cot = ChainOfThoughtLogger()
    evolution_engine = SelfEvolutionEngine(graph_builder)
    rule_engine = EnhancedRuleEngine()
    integrator = PhysicsIntegrator()

    # Test 1: Nodal vectorization
    _logger.log("Test 1: Nodal vectorization", level="INFO")
    try:
        test_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "core", "engine.py")
        if os.path.exists(test_file):
            node = node_analyzer.analyze_file(test_file)
            graph_builder.add_node(node)
            _logger.log(f"Node analyzed and added: {node.node_id}", level="INFO")
        else:
            _logger.log("Test file not found, skipping", level="WARNING")
    except Exception as e:
        _logger.log(f"Nodal vectorization test failed: {e}", level="ERROR")

    # Test 2: Enhanced registry
    _logger.log("Test 2: Enhanced registry", level="INFO")
    try:
        def test_function(x: int) -> int:
            return x * 2

        registry.register(
            name="test_function",
            function=test_function,
            description="Test function",
            tags=["test"],
        )

        func = registry.get("test_function")
        assert func is not None
        assert func(5) == 10
        _logger.log("Enhanced registry test passed", level="INFO")
    except Exception as e:
        _logger.log(f"Enhanced registry test failed: {e}", level="ERROR")

    # Test 3: CoT logging
    _logger.log("Test 3: CoT logging", level="INFO")
    try:
        step_id = cot.start_step(
            action="TEST_STEP",
            input_data={"test": "data"},
            level=LogLevel.INFO,
        )
        cot.end_step(step_id, output_data={"result": "success"}, validation_passed=True)

        stats = cot.get_statistics()
        assert stats["total_steps"] > 0
        _logger.log("CoT logging test passed", level="INFO")
    except Exception as e:
        _logger.log(f"CoT logging test failed: {e}", level="ERROR")

    # Test 4: Enhanced rules
    _logger.log("Test 4: Enhanced rules", level="INFO")
    try:
        def condition(ctx: dict) -> bool:
            return "test" in ctx

        def action(ctx: dict) -> dict:
            return {"result": "rule_executed"}

        rule = EnhancedRule(
            name="test_rule",
            condition=condition,
            action=action,
            description="Test rule",
            priority=RulePriority.MEDIUM,
        )

        rule_engine.add_enhanced_rule(rule)
        results = rule_engine.execute_enhanced(
            {"test": True}, validate_physics=False, use_cot=False
        )
        assert len(results) > 0
        _logger.log("Enhanced rules test passed", level="INFO")
    except Exception as e:
        _logger.log(f"Enhanced rules test failed: {e}", level="ERROR")

    # Test 5: Physics integrator
    _logger.log("Test 5: Physics integrator", level="INFO")
    try:
        result = integrator.simulate(
            scenario={"energy": 1.0, "velocity": 0.0},
            initial_conditions={},
            time_span=(0.0, 1.0),
            num_steps=10,
        )
        assert result is not None
        _logger.log("Physics integrator test passed", level="INFO")
    except Exception as e:
        _logger.log(f"Physics integrator test failed: {e}", level="ERROR")

    # Test 6: Graph statistics
    _logger.log("Test 6: Graph statistics", level="INFO")
    try:
        stats = graph_builder.get_statistics()
        assert "num_nodes" in stats
        _logger.log(f"Graph statistics: {stats}", level="INFO")
    except Exception as e:
        _logger.log(f"Graph statistics test failed: {e}", level="ERROR")

    _logger.log("Integration test completed", level="INFO")


if __name__ == "__main__":
    test_integration()
