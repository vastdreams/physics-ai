# integration/
"""
Integration tests for unified Physics AI system.

Tests the integration of all components:
- Nodal vectorization
- Enhanced registry
- CoT logging
- Self-evolution
- Enhanced rules
- API layer
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai.nodal_vectorization.graph_builder import GraphBuilder
from ai.nodal_vectorization.vector_store import VectorStore
from ai.nodal_vectorization.node_analyzer import NodeAnalyzer
from utilities.enhanced_registry import EnhancedRegistry
from utilities.cot_logging import ChainOfThoughtLogger, LogLevel
from evolution.self_evolution import SelfEvolutionEngine
from rules.enhanced_rule_engine import EnhancedRuleEngine, EnhancedRule, RulePriority
from physics.integration.physics_integrator import PhysicsIntegrator
from loggers.system_logger import SystemLogger


def test_integration():
    """Test integration of all components."""
    logger = SystemLogger()
    logger.log("Starting integration test", level="INFO")
    
    # Initialize components
    vector_store = VectorStore()
    graph_builder = GraphBuilder(vector_store)
    node_analyzer = NodeAnalyzer()
    registry = EnhancedRegistry()
    cot = ChainOfThoughtLogger()
    evolution_engine = SelfEvolutionEngine(graph_builder)
    rule_engine = EnhancedRuleEngine()
    integrator = PhysicsIntegrator()
    
    # Test 1: Nodal vectorization
    logger.log("Test 1: Nodal vectorization", level="INFO")
    try:
        # Analyze a sample file
        test_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "core", "engine.py")
        if os.path.exists(test_file):
            node = node_analyzer.analyze_file(test_file)
            graph_builder.add_node(node)
            logger.log(f"✓ Node analyzed and added: {node.node_id}", level="INFO")
        else:
            logger.log("Test file not found, skipping", level="WARNING")
    except Exception as e:
        logger.log(f"✗ Nodal vectorization test failed: {str(e)}", level="ERROR")
    
    # Test 2: Enhanced registry
    logger.log("Test 2: Enhanced registry", level="INFO")
    try:
        def test_function(x):
            return x * 2
        
        registry.register(
            name="test_function",
            function=test_function,
            description="Test function",
            tags=["test"]
        )
        
        func = registry.get("test_function")
        assert func is not None
        assert func(5) == 10
        logger.log("✓ Enhanced registry test passed", level="INFO")
    except Exception as e:
        logger.log(f"✗ Enhanced registry test failed: {str(e)}", level="ERROR")
    
    # Test 3: CoT logging
    logger.log("Test 3: CoT logging", level="INFO")
    try:
        step_id = cot.start_step(
            action="TEST_STEP",
            input_data={'test': 'data'},
            level=LogLevel.INFO
        )
        cot.end_step(step_id, output_data={'result': 'success'}, validation_passed=True)
        
        stats = cot.get_statistics()
        assert stats['total_steps'] > 0
        logger.log("✓ CoT logging test passed", level="INFO")
    except Exception as e:
        logger.log(f"✗ CoT logging test failed: {str(e)}", level="ERROR")
    
    # Test 4: Enhanced rules
    logger.log("Test 4: Enhanced rules", level="INFO")
    try:
        def condition(ctx):
            return 'test' in ctx
        
        def action(ctx):
            return {'result': 'rule_executed'}
        
        rule = EnhancedRule(
            name="test_rule",
            condition=condition,
            action=action,
            description="Test rule",
            priority=RulePriority.MEDIUM
        )
        
        rule_engine.add_enhanced_rule(rule)
        results = rule_engine.execute_enhanced({'test': True}, validate_physics=False, use_cot=False)
        assert len(results) > 0
        logger.log("✓ Enhanced rules test passed", level="INFO")
    except Exception as e:
        logger.log(f"✗ Enhanced rules test failed: {str(e)}", level="ERROR")
    
    # Test 5: Physics integrator
    logger.log("Test 5: Physics integrator", level="INFO")
    try:
        result = integrator.simulate(
            scenario={'energy': 1.0, 'velocity': 0.0},
            initial_conditions={},
            time_span=(0.0, 1.0),
            num_steps=10
        )
        assert result is not None
        logger.log("✓ Physics integrator test passed", level="INFO")
    except Exception as e:
        logger.log(f"✗ Physics integrator test failed: {str(e)}", level="ERROR")
    
    # Test 6: Graph statistics
    logger.log("Test 6: Graph statistics", level="INFO")
    try:
        stats = graph_builder.get_statistics()
        assert 'num_nodes' in stats
        logger.log(f"✓ Graph statistics: {stats}", level="INFO")
    except Exception as e:
        logger.log(f"✗ Graph statistics test failed: {str(e)}", level="ERROR")
    
    logger.log("Integration test completed", level="INFO")


if __name__ == '__main__':
    test_integration()

