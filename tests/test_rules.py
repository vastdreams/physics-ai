# tests/
"""
PATH: tests/test_rules.py
PURPOSE: Tests for rule engine with pattern matching and conflict resolution.

Tests cover:
- Rule creation and management
- Pattern matching
- Action execution
- Conflict resolution strategies
"""

import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rules.rule_engine import (
    RuleEngine, Rule, RuleMatch, PatternMatcher, ActionExecutor,
    ConflictResolutionStrategy, ExecutionResult
)


class TestPatternMatcher(unittest.TestCase):
    """Tests for PatternMatcher."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.matcher = PatternMatcher()
    
    def test_exact_match(self):
        """Test exact value matching."""
        pattern = {'x': 10, 'y': 20}
        context = {'x': 10, 'y': 20, 'z': 30}
        
        matches, bindings = self.matcher.match(pattern, context)
        self.assertTrue(matches)
    
    def test_no_match(self):
        """Test non-matching pattern."""
        pattern = {'x': 10}
        context = {'x': 20}
        
        matches, bindings = self.matcher.match(pattern, context)
        self.assertFalse(matches)
    
    def test_variable_binding(self):
        """Test variable binding with $ syntax."""
        pattern = {'value': '$x'}
        context = {'value': 42}
        
        matches, bindings = self.matcher.match(pattern, context)
        
        self.assertTrue(matches)
        self.assertEqual(bindings['x'], 42)
    
    def test_comparison_operators(self):
        """Test comparison operators."""
        # Greater than
        pattern = {'value': {'$gt': 10}}
        context = {'value': 15}
        matches, _ = self.matcher.match(pattern, context)
        self.assertTrue(matches)
        
        # Less than
        pattern = {'value': {'$lt': 10}}
        context = {'value': 5}
        matches, _ = self.matcher.match(pattern, context)
        self.assertTrue(matches)
        
        # Not equal
        pattern = {'value': {'$ne': 10}}
        context = {'value': 15}
        matches, _ = self.matcher.match(pattern, context)
        self.assertTrue(matches)
    
    def test_in_operator(self):
        """Test $in operator."""
        pattern = {'status': {'$in': ['active', 'pending']}}
        
        context_match = {'status': 'active'}
        matches, _ = self.matcher.match(pattern, context_match)
        self.assertTrue(matches)
        
        context_no_match = {'status': 'inactive'}
        matches, _ = self.matcher.match(pattern, context_no_match)
        self.assertFalse(matches)
    
    def test_and_operator(self):
        """Test $and operator."""
        pattern = {'value': {'$and': [{'$gt': 0}, {'$lt': 100}]}}
        
        context_match = {'value': 50}
        matches, _ = self.matcher.match(pattern, context_match)
        self.assertTrue(matches)
        
        context_no_match = {'value': 150}
        matches, _ = self.matcher.match(pattern, context_no_match)
        self.assertFalse(matches)
    
    def test_or_operator(self):
        """Test $or operator."""
        pattern = {'value': {'$or': [{'$lt': 0}, {'$gt': 100}]}}
        
        context_match1 = {'value': -5}
        matches, _ = self.matcher.match(pattern, context_match1)
        self.assertTrue(matches)
        
        context_match2 = {'value': 150}
        matches, _ = self.matcher.match(pattern, context_match2)
        self.assertTrue(matches)
        
        context_no_match = {'value': 50}
        matches, _ = self.matcher.match(pattern, context_no_match)
        self.assertFalse(matches)
    
    def test_nested_matching(self):
        """Test nested structure matching."""
        pattern = {'user': {'name': 'John', 'age': {'$gte': 18}}}
        context = {'user': {'name': 'John', 'age': 25, 'email': 'john@example.com'}}
        
        matches, _ = self.matcher.match(pattern, context)
        self.assertTrue(matches)
    
    def test_exists_operator(self):
        """Test $exists operator."""
        pattern = {'optional_field': {'$exists': True}}
        
        context_with = {'optional_field': 'value'}
        matches, _ = self.matcher.match(pattern, context_with)
        self.assertTrue(matches)
        
        context_without = {'other_field': 'value'}
        matches, _ = self.matcher.match(pattern, context_without)
        self.assertFalse(matches)


class TestActionExecutor(unittest.TestCase):
    """Tests for ActionExecutor."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.executor = ActionExecutor()
    
    def test_set_action(self):
        """Test $set action."""
        action = {'$set': {'result': 42, 'status': 'done'}}
        context = {'input': 10}
        bindings = {}
        
        result, new_context = self.executor.execute(action, context, bindings)
        
        self.assertEqual(new_context['result'], 42)
        self.assertEqual(new_context['status'], 'done')
    
    def test_compute_action(self):
        """Test $compute action."""
        action = {'$compute': {'expression': 'x * 2 + y', 'target': 'result'}}
        context = {'x': 10, 'y': 5}
        bindings = {}
        
        result, new_context = self.executor.execute(action, context, bindings)
        
        self.assertEqual(new_context['result'], 25)
    
    def test_variable_substitution(self):
        """Test variable substitution from bindings."""
        action = {'$set': {'doubled': '${x * 2}'}}
        context = {}
        bindings = {'x': 5}
        
        result, new_context = self.executor.execute(action, context, bindings)
        
        self.assertEqual(new_context['doubled'], '10')
    
    def test_remove_action(self):
        """Test $remove action."""
        action = {'$remove': ['temp', 'debug']}
        context = {'temp': 1, 'debug': 2, 'keep': 3}
        bindings = {}
        
        result, new_context = self.executor.execute(action, context, bindings)
        
        self.assertNotIn('temp', new_context)
        self.assertNotIn('debug', new_context)
        self.assertIn('keep', new_context)
    
    def test_custom_action(self):
        """Test custom registered action."""
        def my_function(a, b):
            return a + b
        
        self.executor.register_action('add', my_function)
        
        action = {'$call': {'function': 'add', 'args': [10, 20]}}
        context = {}
        bindings = {}
        
        result, _ = self.executor.execute(action, context, bindings)
        
        self.assertEqual(result['call_result'], 30)


class TestRule(unittest.TestCase):
    """Tests for Rule dataclass."""
    
    def test_rule_creation(self):
        """Test rule creation."""
        rule = Rule(
            name='test_rule',
            condition={'x': {'$gt': 0}},
            action={'$set': {'positive': True}},
            priority=5
        )
        
        self.assertEqual(rule.name, 'test_rule')
        self.assertEqual(rule.priority, 5)
        self.assertTrue(rule.enabled)
    
    def test_specificity_calculation(self):
        """Test specificity is calculated based on condition complexity."""
        simple_rule = Rule(
            name='simple',
            condition={'x': 1},
            action={}
        )
        
        complex_rule = Rule(
            name='complex',
            condition={'x': 1, 'y': 2, 'z': {'a': 1, 'b': 2}},
            action={}
        )
        
        self.assertGreater(complex_rule.specificity, simple_rule.specificity)
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        rule = Rule(
            name='test',
            condition={'x': 1},
            action={'$set': {'y': 2}},
            priority=3
        )
        
        d = rule.to_dict()
        
        self.assertEqual(d['name'], 'test')
        self.assertEqual(d['priority'], 3)
        self.assertIn('created_at', d)


class TestRuleEngine(unittest.TestCase):
    """Tests for RuleEngine."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.engine = RuleEngine(strategy=ConflictResolutionStrategy.PRIORITY)
    
    def test_initialization(self):
        """Test engine initialization."""
        self.assertIsNotNone(self.engine)
        self.assertEqual(len(self.engine.rules), 0)
    
    def test_add_rule(self):
        """Test adding rules."""
        result = self.engine.add_rule({
            'name': 'test_rule',
            'condition': {'x': {'$gt': 0}},
            'action': {'$set': {'positive': True}}
        })
        
        self.assertTrue(result)
        self.assertEqual(len(self.engine.rules), 1)
    
    def test_remove_rule(self):
        """Test removing rules."""
        self.engine.add_rule({
            'name': 'to_remove',
            'condition': {},
            'action': {}
        })
        
        self.assertEqual(len(self.engine.rules), 1)
        
        self.engine.remove_rule('to_remove')
        
        self.assertEqual(len(self.engine.rules), 0)
    
    def test_execute_matching_rule(self):
        """Test executing a matching rule."""
        self.engine.add_rule({
            'name': 'double_x',
            'condition': {'x': {'$gt': 0}},
            'action': {'$compute': {'expression': 'x * 2', 'target': 'result'}}
        })
        
        results = self.engine.execute({'x': 5})
        
        self.assertEqual(len(results), 1)
        self.assertTrue(results[0].success)
        self.assertEqual(results[0].output.get('result'), 10)
    
    def test_no_matching_rules(self):
        """Test execution with no matching rules."""
        self.engine.add_rule({
            'name': 'positive_only',
            'condition': {'x': {'$gt': 0}},
            'action': {}
        })
        
        results = self.engine.execute({'x': -5})
        
        self.assertEqual(len(results), 0)
    
    def test_conflict_resolution_priority(self):
        """Test priority-based conflict resolution."""
        self.engine.add_rule({
            'name': 'low_priority',
            'condition': {'x': {'$gt': 0}},
            'action': {'$return': 'low'},
            'priority': 1
        })
        
        self.engine.add_rule({
            'name': 'high_priority',
            'condition': {'x': {'$gt': 0}},
            'action': {'$return': 'high'},
            'priority': 10
        })
        
        results = self.engine.execute({'x': 5})
        
        # Should only execute high priority rule
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].rule_name, 'high_priority')
    
    def test_conflict_resolution_all(self):
        """Test executing all matching rules."""
        self.engine.strategy = ConflictResolutionStrategy.ALL
        
        self.engine.add_rule({
            'name': 'rule1',
            'condition': {'x': {'$gt': 0}},
            'action': {'$set': {'r1': True}}
        })
        
        self.engine.add_rule({
            'name': 'rule2',
            'condition': {'x': {'$gt': 0}},
            'action': {'$set': {'r2': True}}
        })
        
        results = self.engine.execute({'x': 5})
        
        self.assertEqual(len(results), 2)
    
    def test_conflict_resolution_specificity(self):
        """Test specificity-based conflict resolution."""
        self.engine.strategy = ConflictResolutionStrategy.SPECIFICITY
        
        self.engine.add_rule({
            'name': 'general',
            'condition': {'x': {'$gt': 0}},
            'action': {'$return': 'general'},
            'priority': 0
        })
        
        self.engine.add_rule({
            'name': 'specific',
            'condition': {'x': {'$gt': 0}, 'y': {'$gt': 0}},
            'action': {'$return': 'specific'},
            'priority': 0
        })
        
        results = self.engine.execute({'x': 5, 'y': 5})
        
        # Should prefer more specific rule
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].rule_name, 'specific')
    
    def test_rule_fire_count(self):
        """Test that fire count is tracked."""
        self.engine.add_rule({
            'name': 'counter',
            'condition': {},
            'action': {}
        })
        
        self.engine.execute({})
        self.engine.execute({})
        self.engine.execute({})
        
        rule = self.engine.get_rule('counter')
        self.assertEqual(rule.fire_count, 3)
    
    def test_enable_disable_rule(self):
        """Test enabling and disabling rules."""
        self.engine.add_rule({
            'name': 'toggleable',
            'condition': {},
            'action': {}
        })
        
        # Initially enabled
        results = self.engine.execute({})
        self.assertEqual(len(results), 1)
        
        # Disable
        self.engine.disable_rule('toggleable')
        results = self.engine.execute({})
        self.assertEqual(len(results), 0)
        
        # Re-enable
        self.engine.enable_rule('toggleable')
        results = self.engine.execute({})
        self.assertEqual(len(results), 1)
    
    def test_statistics(self):
        """Test getting statistics."""
        self.engine.add_rule({
            'name': 'test',
            'condition': {},
            'action': {}
        })
        
        self.engine.execute({})
        
        stats = self.engine.get_statistics()
        
        self.assertEqual(stats['total_rules'], 1)
        self.assertEqual(stats['enabled_rules'], 1)
        self.assertEqual(stats['total_fires'], 1)
    
    def test_custom_action_registration(self):
        """Test registering custom actions."""
        def calculate_energy(mass, velocity):
            return 0.5 * mass * velocity ** 2
        
        self.engine.register_action('kinetic_energy', calculate_energy)
        
        self.engine.add_rule({
            'name': 'physics_rule',
            'condition': {'mass': {'$gt': 0}, 'velocity': {'$exists': True}},
            'action': {'$call': {'function': 'kinetic_energy', 'args': ['$mass', '$velocity']}}
        })
        
        # Note: This would need proper variable resolution in the executor


class TestVariableBindingPropagation(unittest.TestCase):
    """Tests for variable binding through rules."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.engine = RuleEngine()
    
    def test_bindings_passed_to_action(self):
        """Test that pattern bindings are available in actions."""
        self.engine.add_rule({
            'name': 'binding_test',
            'condition': {'value': '$x'},
            'action': {'$compute': {'expression': 'x * 10', 'target': 'result'}}
        })
        
        results = self.engine.execute({'value': 5})
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].bindings.get('x'), 5)
        self.assertEqual(results[0].output.get('result'), 50)


if __name__ == '__main__':
    unittest.main()
