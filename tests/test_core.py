# tests/
"""
PATH: tests/test_core.py
PURPOSE: Comprehensive tests for core module including engine and reasoning.

Tests cover:
- NeurosymboticEngine initialization and processing
- Neural component pattern matching
- Symbolic component rule application
- All 4 reasoning types
- Integration between components
"""

import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.engine import NeurosymboticEngine, NeuralComponent, SymbolicComponent, ProcessingMode
from core.reasoning import (
    ReasoningEngineImpl, ReasoningType,
    DeductiveReasoner, InductiveReasoner, AbductiveReasoner, AnalogicalReasoner
)


class TestNeuralComponent(unittest.TestCase):
    """Tests for NeuralComponent."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.neural = NeuralComponent(embedding_dim=64)
    
    def test_initialization(self):
        """Test neural component initialization."""
        self.assertIsNotNone(self.neural)
        self.assertEqual(self.neural.embedding_dim, 64)
        self.assertIsNotNone(self.neural.projection_matrix)
    
    def test_embedding(self):
        """Test embedding generation."""
        data = {"test": "data", "value": 42}
        embedding = self.neural.embed(data)
        
        self.assertEqual(len(embedding), 64)
        self.assertTrue(all(isinstance(x, float) for x in embedding))
    
    def test_similarity(self):
        """Test similarity computation."""
        data1 = {"x": 1, "y": 2}
        data2 = {"x": 1, "y": 2}
        data3 = {"a": 100, "b": 200}
        
        emb1 = self.neural.embed(data1)
        emb2 = self.neural.embed(data2)
        emb3 = self.neural.embed(data3)
        
        # Identical data should have similarity 1.0
        self.assertAlmostEqual(self.neural.similarity(emb1, emb2), 1.0, places=5)
        
        # Different data should have lower similarity
        sim_diff = self.neural.similarity(emb1, emb3)
        self.assertLess(sim_diff, 1.0)
    
    def test_pattern_learning(self):
        """Test pattern learning and recall."""
        input_data = {"mass": 10, "velocity": 5}
        output_data = {"kinetic_energy": 125}
        
        self.neural.learn_pattern("ke_pattern", input_data, output_data)
        
        self.assertIn("ke_pattern", self.neural.pattern_memory)
        self.assertEqual(self.neural.pattern_outputs["ke_pattern"], output_data)
    
    def test_process_with_patterns(self):
        """Test processing with learned patterns."""
        # Learn a pattern
        self.neural.learn_pattern("test", {"a": 1}, {"result": "success"})
        
        # Process similar input
        result = self.neural.process({"a": 1})
        
        self.assertIsNotNone(result)
        self.assertGreater(result.confidence, 0.5)


class TestSymbolicComponent(unittest.TestCase):
    """Tests for SymbolicComponent."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.symbolic = SymbolicComponent()
    
    def test_initialization(self):
        """Test symbolic component initialization."""
        self.assertIsNotNone(self.symbolic)
        self.assertIsInstance(self.symbolic.rules, list)
        self.assertIsInstance(self.symbolic.facts, dict)
    
    def test_add_rule(self):
        """Test adding rules."""
        self.symbolic.add_rule(
            name="test_rule",
            condition="'x' in context and context['x'] > 0",
            action="context['x'] * 2",
            priority=1
        )
        
        self.assertEqual(len(self.symbolic.rules), 1)
        self.assertEqual(self.symbolic.rules[0]['name'], "test_rule")
    
    def test_add_fact(self):
        """Test adding facts."""
        self.symbolic.add_fact("pi", 3.14159)
        
        self.assertIn("pi", self.symbolic.facts)
        self.assertAlmostEqual(self.symbolic.facts["pi"], 3.14159, places=5)
    
    def test_evaluate_condition(self):
        """Test condition evaluation."""
        context = {"x": 10, "y": 5}
        
        self.assertTrue(self.symbolic.evaluate_condition("'x' in context", context))
        self.assertTrue(self.symbolic.evaluate_condition("context['x'] > context['y']", context))
        self.assertFalse(self.symbolic.evaluate_condition("context['x'] < 0", context))
    
    def test_apply_rules(self):
        """Test rule application."""
        self.symbolic.add_rule(
            name="double",
            condition="'value' in context",
            action="context['value'] * 2"
        )
        
        results = self.symbolic.apply_rules({"value": 5})
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['result'], 10)
    
    def test_symbolic_math(self):
        """Test symbolic math operations."""
        # Test simplification
        result = self.symbolic.symbolic_math("x**2 + 2*x + 1", operation="simplify")
        self.assertIsNotNone(result)
        
        # Test differentiation
        result = self.symbolic.symbolic_math("x**2", operation="differentiate", variable="x")
        self.assertEqual(result, "2*x")


class TestNeurosymboticEngine(unittest.TestCase):
    """Tests for NeurosymboticEngine."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.engine = NeurosymboticEngine()
    
    def test_initialization(self):
        """Test engine initialization."""
        self.assertIsNotNone(self.engine)
        self.assertIsNotNone(self.engine.neural_component)
        self.assertIsNotNone(self.engine.symbolic_component)
        self.assertIsNotNone(self.engine.validator)
        self.assertIsNotNone(self.engine.logger)
    
    def test_process_dict(self):
        """Test processing dictionary input."""
        input_data = {"test": "data", "value": 42}
        result = self.engine.process(input_data)
        
        self.assertIsNotNone(result)
        self.assertIn("neural", result)
        self.assertIn("symbolic", result)
        self.assertIn("confidence", result)
    
    def test_process_physics_context(self):
        """Test processing physics context."""
        input_data = {"mass": 10, "velocity": 5}
        result = self.engine.process(input_data)
        
        self.assertIsNotNone(result)
        # Should trigger physics rules
        self.assertIn("symbolic", result)
    
    def test_hybrid_mode(self):
        """Test hybrid processing mode."""
        self.engine.mode = ProcessingMode.HYBRID
        result = self.engine.process({"x": 1})
        
        self.assertIn("weights", result)
        self.assertIn("neural", result["weights"])
        self.assertIn("symbolic", result["weights"])
    
    def test_learning(self):
        """Test pattern learning."""
        self.engine.learn({"input": "test"}, {"output": "result"}, "test_pattern")
        
        self.assertIn("test_pattern", self.engine.neural_component.pattern_memory)
    
    def test_add_rule(self):
        """Test adding rules to engine."""
        self.engine.add_rule(
            name="custom_rule",
            condition="True",
            action="'executed'",
            priority=10
        )
        
        self.assertEqual(len(self.engine.symbolic_component.rules), 4)  # 3 default + 1 custom
    
    def test_evolution(self):
        """Test evolution with feedback."""
        initial_alpha = self.engine.alpha
        
        self.engine.evolve({
            'neural_accuracy': 0.9,
            'symbolic_accuracy': 0.5
        })
        
        # Alpha should increase (shift towards neural)
        self.assertGreater(self.engine.alpha, initial_alpha)
    
    def test_statistics(self):
        """Test getting statistics."""
        stats = self.engine.get_statistics()
        
        self.assertIn("mode", stats)
        self.assertIn("alpha", stats)
        self.assertIn("neural_patterns", stats)
        self.assertIn("symbolic_rules", stats)


class TestDeductiveReasoner(unittest.TestCase):
    """Tests for DeductiveReasoner."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.reasoner = DeductiveReasoner()
    
    def test_modus_ponens(self):
        """Test modus ponens reasoning."""
        # Add implication: P -> Q
        self.reasoner.add_implication("P", "Q")
        self.reasoner.add_fact("P", True)
        
        result = self.reasoner.reason(["P", "P -> Q"])
        
        self.assertIn("Q", [str(c) for c in result.conclusion])
    
    def test_hypothetical_syllogism(self):
        """Test hypothetical syllogism."""
        self.reasoner.add_implication("A", "B")
        self.reasoner.add_implication("B", "C")
        
        new_impls = self.reasoner.hypothetical_syllogism(self.reasoner.implications)
        
        # Should derive A -> C
        self.assertTrue(any(i.antecedent == "A" and i.consequent == "C" for i in new_impls))
    
    def test_complex_reasoning(self):
        """Test complex deductive chain."""
        premises = [
            "is_human -> is_mortal",
            "socrates -> is_human",
            "socrates"
        ]
        
        result = self.reasoner.reason(premises)
        
        self.assertTrue(result.confidence > 0)
        self.assertEqual(result.reasoning_type, ReasoningType.DEDUCTIVE)


class TestInductiveReasoner(unittest.TestCase):
    """Tests for InductiveReasoner."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.reasoner = InductiveReasoner()
    
    def test_find_patterns_constant(self):
        """Test finding constant patterns."""
        observations = [
            {"color": "red", "size": 10},
            {"color": "red", "size": 20},
            {"color": "red", "size": 30}
        ]
        
        patterns = self.reasoner.find_patterns(observations)
        
        # Should find that color is always "red"
        constant_patterns = [p for p in patterns if p['type'] == 'constant']
        self.assertTrue(any(p['key'] == 'color' and p['value'] == 'red' for p in constant_patterns))
    
    def test_find_patterns_monotonic(self):
        """Test finding monotonic patterns."""
        observations = [
            {"value": 1},
            {"value": 2},
            {"value": 3},
            {"value": 4}
        ]
        
        patterns = self.reasoner.find_patterns(observations)
        
        # Should find monotonic increase
        monotonic = [p for p in patterns if p['type'] == 'monotonic_increase']
        self.assertTrue(len(monotonic) > 0)
    
    def test_generalize(self):
        """Test pattern generalization."""
        patterns = [
            {'type': 'constant', 'key': 'status', 'value': 'active', 'confidence': 1.0}
        ]
        
        hypothesis = self.reasoner.generalize(patterns)
        
        self.assertIn('rules', hypothesis)
        self.assertEqual(len(hypothesis['rules']), 1)
    
    def test_reasoning(self):
        """Test full inductive reasoning."""
        premises = [
            {"x": 1, "y": 2},
            {"x": 2, "y": 4},
            {"x": 3, "y": 6}
        ]
        
        result = self.reasoner.reason(premises)
        
        self.assertEqual(result.reasoning_type, ReasoningType.INDUCTIVE)
        self.assertTrue(result.confidence > 0)


class TestAbductiveReasoner(unittest.TestCase):
    """Tests for AbductiveReasoner."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.reasoner = AbductiveReasoner()
    
    def test_add_hypothesis(self):
        """Test adding hypotheses."""
        self.reasoner.add_hypothesis(
            name="Hypothesis A",
            explains=["obs1", "obs2"],
            complexity=1,
            prior=0.6
        )
        
        self.assertEqual(len(self.reasoner.hypotheses), 1)
    
    def test_score_hypothesis(self):
        """Test hypothesis scoring."""
        hypothesis = {
            'name': 'Test',
            'explains': {'obs1', 'obs2'},
            'complexity': 1,
            'prior': 0.5
        }
        
        observations = {'obs1', 'obs2', 'obs3'}
        score = self.reasoner.score_hypothesis(hypothesis, observations)
        
        # Coverage is 2/3, so score should reflect that
        self.assertTrue(0 < score < 1)
    
    def test_reasoning(self):
        """Test abductive reasoning."""
        # Add some hypotheses
        self.reasoner.add_hypothesis("Theory1", ["effect1", "effect2"], 1, 0.7)
        self.reasoner.add_hypothesis("Theory2", ["effect1"], 2, 0.3)
        
        result = self.reasoner.reason(["effect1", "effect2"])
        
        self.assertEqual(result.reasoning_type, ReasoningType.ABDUCTIVE)
        # Theory1 should be preferred (explains more, simpler, higher prior)
        self.assertIn("best_explanation", result.conclusion)


class TestAnalogicalReasoner(unittest.TestCase):
    """Tests for AnalogicalReasoner."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.reasoner = AnalogicalReasoner()
    
    def test_structural_similarity(self):
        """Test structural similarity computation."""
        domain1 = {"a": 1, "b": 2, "c": 3}
        domain2 = {"a": 10, "b": 20, "c": 30}
        domain3 = {"x": 1, "y": 2}
        
        # Same structure should have high similarity
        sim_same = self.reasoner.compute_structural_similarity(domain1, domain2)
        self.assertGreater(sim_same, 0.8)
        
        # Different structure should have lower similarity
        sim_diff = self.reasoner.compute_structural_similarity(domain1, domain3)
        self.assertLess(sim_diff, 0.5)
    
    def test_find_mapping(self):
        """Test mapping discovery."""
        source = {"mass": 10, "velocity": 5}
        target = {"mass": 20, "velocity": 10}
        
        mapping = self.reasoner.find_mapping(source, target)
        
        # Should map same keys to same keys
        self.assertEqual(mapping.get("mass"), "mass")
        self.assertEqual(mapping.get("velocity"), "velocity")
    
    def test_reasoning(self):
        """Test analogical reasoning."""
        premises = [
            {"source": {"mass": 10, "velocity": 5, "energy": 125}},
            {"target": {"mass": 20, "velocity": 10}},
            {"query": "energy"}
        ]
        
        result = self.reasoner.reason(premises)
        
        self.assertEqual(result.reasoning_type, ReasoningType.ANALOGICAL)
        self.assertIn("transferred_knowledge", result.conclusion)


class TestReasoningEngineImpl(unittest.TestCase):
    """Tests for ReasoningEngineImpl."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.engine = ReasoningEngineImpl()
    
    def test_initialization(self):
        """Test reasoning engine initialization."""
        self.assertIsNotNone(self.engine)
        self.assertIsNotNone(self.engine.deductive)
        self.assertIsNotNone(self.engine.inductive)
        self.assertIsNotNone(self.engine.abductive)
        self.assertIsNotNone(self.engine.analogical)
    
    def test_reason_deductive(self):
        """Test deductive reasoning through engine."""
        self.engine.reasoning_type = ReasoningType.DEDUCTIVE
        result = self.engine.reason(["A -> B", "A"])
        
        self.assertIsNotNone(result)
        self.assertEqual(result['reasoning_type'], 'deductive')
    
    def test_reason_inductive(self):
        """Test inductive reasoning through engine."""
        self.engine.reasoning_type = ReasoningType.INDUCTIVE
        result = self.engine.reason([{"x": i} for i in range(5)])
        
        self.assertIsNotNone(result)
        self.assertEqual(result['reasoning_type'], 'inductive')
    
    def test_reason_all(self):
        """Test applying all reasoning types."""
        results = self.engine.reason_all([{"data": 1}, {"data": 2}])
        
        self.assertIn("deductive", results)
        self.assertIn("inductive", results)
        self.assertIn("abductive", results)
        self.assertIn("analogical", results)


if __name__ == '__main__':
    unittest.main()
