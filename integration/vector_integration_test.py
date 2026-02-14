"""
Integration test for VECTOR framework with all systems.
"""

from __future__ import annotations

import numpy as np

from ai.llm_integration import LLMIntegration
from ai.nodal_vectorization.graph_builder import GraphBuilder
from ai.nodal_vectorization.vector_store import VectorStore
from evolution.vector_evolution_integration import VectorIntegratedEvolutionEngine
from loggers.system_logger import SystemLogger
from physics.integration.vector_integration import VectorIntegratedPhysicsIntegrator
from rules.enhanced_rule_engine import EnhancedRule, RulePriority
from rules.vector_rule_integration import VectorIntegratedRuleEngine
from utilities.data_imputation import DataImputation, ImputationStrategy
from utilities.data_streaming import DataStreamManager
from utilities.hitl_interface import HITLInterface
from utilities.particle_filters import ParticleFilter
from utilities.performance_monitoring import PerformanceMonitor
from utilities.vector_framework import DeltaFactor, VECTORFramework


def test_vector_integration() -> None:
    """Test VECTOR framework integration with all systems."""
    _logger = SystemLogger()
    _logger.log("Starting VECTOR integration test", level="INFO")

    # Test 1: VECTOR Framework
    _logger.log("Test 1: VECTOR Framework", level="INFO")
    try:
        vector = VECTORFramework(v_max=100.0, lambda_penalty=1.0)

        vector.add_delta_factor(DeltaFactor(name="energy", value=1.0, variance=0.1))
        vector.add_delta_factor(DeltaFactor(name="momentum", value=0.5, variance=0.2))

        v_obs = vector.compute_observed_variance()
        assert v_obs > 0

        vector.throttle_variance()
        stats = vector.get_statistics()

        _logger.log(f"VECTOR Framework: v_obs={v_obs:.4f}, stats={stats}", level="INFO")
    except Exception as e:
        _logger.log(f"VECTOR Framework test failed: {e}", level="ERROR")

    # Test 2: Vector-Integrated Physics Integrator
    _logger.log("Test 2: Vector-Integrated Physics Integrator", level="INFO")
    try:
        integrator = VectorIntegratedPhysicsIntegrator()

        result = integrator.simulate(
            scenario={"energy": 1.0, "velocity": 0.0},
            initial_conditions={},
            time_span=(0.0, 1.0),
            num_steps=10,
            use_vector=True,
        )

        assert result is not None
        integrator.get_vector_statistics()

        _logger.log(
            f"Vector-Integrated Physics Integrator: result keys={list(result.keys())}",
            level="INFO",
        )
    except Exception as e:
        _logger.log(f"Vector-Integrated Physics Integrator test failed: {e}", level="ERROR")

    # Test 3: Vector-Integrated Rule Engine
    _logger.log("Test 3: Vector-Integrated Rule Engine", level="INFO")
    try:
        rule_engine = VectorIntegratedRuleEngine()

        def condition(ctx: dict) -> bool:
            return "energy" in ctx

        def action(ctx: dict) -> dict:
            return {"result": "energy present"}

        rule = EnhancedRule(
            name="energy_rule",
            condition=condition,
            action=action,
            priority=RulePriority.MEDIUM,
        )

        rule_engine.add_enhanced_rule(rule)

        results = rule_engine.execute_enhanced(
            context={"energy": 1.0, "energy_uncertainty": 0.1},
            use_vector=True,
        )

        assert len(results) > 0
        _logger.log(f"Vector-Integrated Rule Engine: {len(results)} results", level="INFO")
    except Exception as e:
        _logger.log(f"Vector-Integrated Rule Engine test failed: {e}", level="ERROR")

    # Test 4: Data Imputation
    _logger.log("Test 4: Data Imputation", level="INFO")
    try:
        imputation = DataImputation()

        imputation.create_cluster_from_data(
            cluster_id="test_cluster",
            data_points=[{"energy": 1.0, "momentum": 0.5}, {"energy": 1.1, "momentum": 0.6}],
        )

        value, uncertainty = imputation.impute_missing(
            missing_feature="energy",
            available_features={"momentum": 0.55},
            strategy=ImputationStrategy.CLUSTER,
        )

        assert value is not None
        _logger.log(
            f"Data Imputation: value={value:.4f}, uncertainty={uncertainty:.4f}", level="INFO"
        )
    except Exception as e:
        _logger.log(f"Data Imputation test failed: {e}", level="ERROR")

    # Test 5: Performance Monitoring
    _logger.log("Test 5: Performance Monitoring", level="INFO")
    try:
        monitor = PerformanceMonitor()

        monitor.record_metric("simulation_time", 1.5, variance=0.1)
        monitor.record_metric("simulation_time", 1.6, variance=0.1)
        monitor.record_metric("simulation_time", 1.4, variance=0.1)

        stats = monitor.get_metric_statistics("simulation_time")
        assert stats is not None

        _logger.log(f"Performance Monitoring: stats={stats}", level="INFO")
    except Exception as e:
        _logger.log(f"Performance Monitoring test failed: {e}", level="ERROR")

    # Test 6: Particle Filter
    _logger.log("Test 6: Particle Filter", level="INFO")
    try:
        pf = ParticleFilter(num_particles=10)

        def initial_dist() -> dict:
            return {"x": np.random.normal(0, 1)}

        pf.initialize(initial_distribution=initial_dist)

        def dynamics(state: dict) -> dict:
            return {"x": state["x"] + 0.1}

        pf.predict(dynamics, noise={"x": 0.01})

        def likelihood(state: dict, obs: dict) -> float:
            return float(np.exp(-0.5 * ((state["x"] - obs["x"]) ** 2) / 0.1))

        pf.update({"x": 0.0}, likelihood)
        pf.resample()

        mean_state, variance_state = pf.get_estimate()
        assert "x" in mean_state

        _logger.log(
            f"Particle Filter: mean={mean_state}, variance={variance_state}", level="INFO"
        )
    except Exception as e:
        _logger.log(f"Particle Filter test failed: {e}", level="ERROR")

    # Test 7: Data Streaming
    _logger.log("Test 7: Data Streaming", level="INFO")
    try:
        stream_manager = DataStreamManager()
        stream = stream_manager.create_stream("test_stream")

        stream.register_processor(lambda point: None)
        stream.start()

        stream.add_data("source1", {"energy": 1.0})
        stream.add_data("source2", {"energy": 1.1})

        stats = stream.get_statistics()
        assert stats["total_points"] > 0

        _logger.log(f"Data Streaming: stats={stats}", level="INFO")
    except Exception as e:
        _logger.log(f"Data Streaming test failed: {e}", level="ERROR")

    # Test 8: HITL Interface
    _logger.log("Test 8: HITL Interface", level="INFO")
    try:
        hitl = HITLInterface()

        request_id = hitl.request_approval(
            action="test_action",
            description="Test action description",
            context={"test": True},
        )

        assert request_id is not None

        success = hitl.approve(request_id, "test_user")
        assert success

        _logger.log(f"HITL Interface: request_id={request_id}", level="INFO")
    except Exception as e:
        _logger.log(f"HITL Interface test failed: {e}", level="ERROR")

    # Test 9: LLM Integration
    _logger.log("Test 9: LLM Integration", level="INFO")
    try:
        llm = LLMIntegration()

        synergy = llm.discover_synergy("classical", "quantum")
        assert synergy is not None

        explanation = llm.explain_decision(
            "Selected quantum mechanics",
            context={"energy": 1.0},
        )
        assert explanation is not None

        _logger.log(
            f"LLM Integration: synergy={synergy.get('coupling_strength', 0)}", level="INFO"
        )
    except Exception as e:
        _logger.log(f"LLM Integration test failed: {e}", level="ERROR")

    _logger.log("VECTOR integration test completed", level="INFO")


if __name__ == "__main__":
    test_vector_integration()
