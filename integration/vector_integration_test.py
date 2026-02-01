# integration/
"""
Integration test for VECTOR framework with all systems.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from physics.integration.vector_integration import VectorIntegratedPhysicsIntegrator
from rules.vector_rule_integration import VectorIntegratedRuleEngine
from evolution.vector_evolution_integration import VectorIntegratedEvolutionEngine
from ai.nodal_vectorization.graph_builder import GraphBuilder
from ai.nodal_vectorization.vector_store import VectorStore
from utilities.vector_framework import VECTORFramework, DeltaFactor
from utilities.data_imputation import DataImputation, ImputationStrategy
from utilities.performance_monitoring import PerformanceMonitor
from utilities.particle_filters import ParticleFilter
from utilities.data_streaming import DataStreamManager
from utilities.hitl_interface import HITLInterface
from ai.llm_integration import LLMIntegration
from loggers.system_logger import SystemLogger


def test_vector_integration():
    """Test VECTOR framework integration with all systems."""
    logger = SystemLogger()
    logger.log("Starting VECTOR integration test", level="INFO")
    
    # Test 1: VECTOR Framework
    logger.log("Test 1: VECTOR Framework", level="INFO")
    try:
        vector = VECTORFramework(v_max=100.0, lambda_penalty=1.0)
        
        vector.add_delta_factor(DeltaFactor(name="energy", value=1.0, variance=0.1))
        vector.add_delta_factor(DeltaFactor(name="momentum", value=0.5, variance=0.2))
        
        v_obs = vector.compute_observed_variance()
        assert v_obs > 0
        
        throttled = vector.throttle_variance()
        stats = vector.get_statistics()
        
        logger.log(f"✓ VECTOR Framework: v_obs={v_obs:.4f}, stats={stats}", level="INFO")
    except Exception as e:
        logger.log(f"✗ VECTOR Framework test failed: {str(e)}", level="ERROR")
    
    # Test 2: Vector-Integrated Physics Integrator
    logger.log("Test 2: Vector-Integrated Physics Integrator", level="INFO")
    try:
        integrator = VectorIntegratedPhysicsIntegrator()
        
        result = integrator.simulate(
            scenario={'energy': 1.0, 'velocity': 0.0},
            initial_conditions={},
            time_span=(0.0, 1.0),
            num_steps=10,
            use_vector=True
        )
        
        assert result is not None
        vector_stats = integrator.get_vector_statistics()
        
        logger.log(f"✓ Vector-Integrated Physics Integrator: result keys={list(result.keys())}", level="INFO")
    except Exception as e:
        logger.log(f"✗ Vector-Integrated Physics Integrator test failed: {str(e)}", level="ERROR")
    
    # Test 3: Vector-Integrated Rule Engine
    logger.log("Test 3: Vector-Integrated Rule Engine", level="INFO")
    try:
        rule_engine = VectorIntegratedRuleEngine()
        
        from rules.enhanced_rule_engine import EnhancedRule, RulePriority
        
        def condition(ctx):
            return 'energy' in ctx
        
        def action(ctx):
            return {'result': 'energy present'}
        
        rule = EnhancedRule(
            name="energy_rule",
            condition=condition,
            action=action,
            priority=RulePriority.MEDIUM
        )
        
        rule_engine.add_enhanced_rule(rule)
        
        results = rule_engine.execute_enhanced(
            context={'energy': 1.0, 'energy_uncertainty': 0.1},
            use_vector=True
        )
        
        assert len(results) > 0
        logger.log(f"✓ Vector-Integrated Rule Engine: {len(results)} results", level="INFO")
    except Exception as e:
        logger.log(f"✗ Vector-Integrated Rule Engine test failed: {str(e)}", level="ERROR")
    
    # Test 4: Data Imputation
    logger.log("Test 4: Data Imputation", level="INFO")
    try:
        imputation = DataImputation()
        
        cluster = imputation.create_cluster_from_data(
            cluster_id="test_cluster",
            data_points=[{'energy': 1.0, 'momentum': 0.5}, {'energy': 1.1, 'momentum': 0.6}]
        )
        
        value, uncertainty = imputation.impute_missing(
            missing_feature="energy",
            available_features={'momentum': 0.55},
            strategy=ImputationStrategy.CLUSTER
        )
        
        assert value is not None
        logger.log(f"✓ Data Imputation: value={value:.4f}, uncertainty={uncertainty:.4f}", level="INFO")
    except Exception as e:
        logger.log(f"✗ Data Imputation test failed: {str(e)}", level="ERROR")
    
    # Test 5: Performance Monitoring
    logger.log("Test 5: Performance Monitoring", level="INFO")
    try:
        monitor = PerformanceMonitor()
        
        monitor.record_metric("simulation_time", 1.5, variance=0.1)
        monitor.record_metric("simulation_time", 1.6, variance=0.1)
        monitor.record_metric("simulation_time", 1.4, variance=0.1)
        
        stats = monitor.get_metric_statistics("simulation_time")
        assert stats is not None
        
        logger.log(f"✓ Performance Monitoring: stats={stats}", level="INFO")
    except Exception as e:
        logger.log(f"✗ Performance Monitoring test failed: {str(e)}", level="ERROR")
    
    # Test 6: Particle Filter
    logger.log("Test 6: Particle Filter", level="INFO")
    try:
        pf = ParticleFilter(num_particles=10)
        
        def initial_dist():
            return {'x': np.random.normal(0, 1)}
        
        pf.initialize(initial_distribution=initial_dist)
        
        def dynamics(state):
            return {'x': state['x'] + 0.1}
        
        pf.predict(dynamics, noise={'x': 0.01})
        
        def likelihood(state, obs):
            return np.exp(-0.5 * ((state['x'] - obs['x'])**2) / 0.1)
        
        pf.update({'x': 0.0}, likelihood)
        pf.resample()
        
        mean_state, variance_state = pf.get_estimate()
        assert 'x' in mean_state
        
        logger.log(f"✓ Particle Filter: mean={mean_state}, variance={variance_state}", level="INFO")
    except Exception as e:
        logger.log(f"✗ Particle Filter test failed: {str(e)}", level="ERROR")
    
    # Test 7: Data Streaming
    logger.log("Test 7: Data Streaming", level="INFO")
    try:
        stream_manager = DataStreamManager()
        stream = stream_manager.create_stream("test_stream")
        
        stream.register_processor(lambda point: None)  # Dummy processor
        stream.start()
        
        stream.add_data("source1", {'energy': 1.0})
        stream.add_data("source2", {'energy': 1.1})
        
        stats = stream.get_statistics()
        assert stats['total_points'] > 0
        
        logger.log(f"✓ Data Streaming: stats={stats}", level="INFO")
    except Exception as e:
        logger.log(f"✗ Data Streaming test failed: {str(e)}", level="ERROR")
    
    # Test 8: HITL Interface
    logger.log("Test 8: HITL Interface", level="INFO")
    try:
        hitl = HITLInterface()
        
        request_id = hitl.request_approval(
            action="test_action",
            description="Test action description",
            context={'test': True}
        )
        
        assert request_id is not None
        
        success = hitl.approve(request_id, "test_user")
        assert success
        
        logger.log(f"✓ HITL Interface: request_id={request_id}", level="INFO")
    except Exception as e:
        logger.log(f"✗ HITL Interface test failed: {str(e)}", level="ERROR")
    
    # Test 9: LLM Integration
    logger.log("Test 9: LLM Integration", level="INFO")
    try:
        llm = LLMIntegration()
        
        synergy = llm.discover_synergy("classical", "quantum")
        assert synergy is not None
        
        explanation = llm.explain_decision(
            "Selected quantum mechanics",
            context={'energy': 1.0}
        )
        assert explanation is not None
        
        logger.log(f"✓ LLM Integration: synergy={synergy.get('coupling_strength', 0)}", level="INFO")
    except Exception as e:
        logger.log(f"✗ LLM Integration test failed: {str(e)}", level="ERROR")
    
    logger.log("VECTOR integration test completed", level="INFO")


if __name__ == '__main__':
    import numpy as np
    test_vector_integration()

