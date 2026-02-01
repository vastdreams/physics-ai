# tests/
"""
Unit tests for Context Memory System.
"""

import unittest
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai.context_memory import (
    ContextBubble, MicroAgent, ContextTree, TrafficAgent,
    PathOptimizer, UsageTracker
)


class TestContextBubble(unittest.TestCase):
    """Test ContextBubble class."""
    
    def test_create_bubble(self):
        """Test bubble creation."""
        bubble = ContextBubble(
            bubble_id="test_bubble",
            content={"data": "test"},
            metadata={"source": "test"}
        )
        
        self.assertEqual(bubble.bubble_id, "test_bubble")
        self.assertEqual(bubble.content, {"data": "test"})
        self.assertEqual(bubble.access_count, 0)
    
    def test_add_micro_agent(self):
        """Test adding micro-agent."""
        bubble = ContextBubble(bubble_id="test", content={})
        agent = MicroAgent(agent_id="agent_1", blueprint={})
        
        bubble.add_micro_agent(agent)
        
        self.assertEqual(len(bubble.micro_agents), 1)
        self.assertEqual(bubble.micro_agents[0].agent_id, "agent_1")
    
    def test_traffic_signal(self):
        """Test traffic signal management."""
        bubble = ContextBubble(bubble_id="test", content={})
        
        bubble.set_traffic_signal("pathway_1", 0.8)
        
        self.assertEqual(bubble.get_traffic_signal("pathway_1"), 0.8)
        self.assertEqual(bubble.get_traffic_signal("nonexistent"), 0.0)
    
    def test_process_with_agents(self):
        """Test processing with micro-agents."""
        bubble = ContextBubble(bubble_id="test", content={})
        agent = MicroAgent(agent_id="agent_1", blueprint={
            "instructions": {"type": "route"}
        })
        bubble.add_micro_agent(agent)
        
        result = bubble.process_with_agents({"query": "test"})
        
        self.assertEqual(result['bubble_id'], "test")
        self.assertIn('pathways', result)


class TestMicroAgent(unittest.TestCase):
    """Test MicroAgent class."""
    
    def test_create_agent(self):
        """Test agent creation."""
        agent = MicroAgent(
            agent_id="test_agent",
            blueprint={"instructions": {"type": "route"}}
        )
        
        self.assertEqual(agent.agent_id, "test_agent")
        self.assertEqual(agent.execution_count, 0)
    
    def test_process(self):
        """Test agent processing."""
        agent = MicroAgent(
            agent_id="test_agent",
            blueprint={"instructions": {"type": "route"}}
        )
        bubble = ContextBubble(bubble_id="test", content={})
        
        result = agent.process({"test": "data"}, bubble)
        
        self.assertIsNotNone(result)
        self.assertIn('agent_id', result)


class TestContextTree(unittest.TestCase):
    """Test ContextTree class."""
    
    def test_create_tree(self):
        """Test tree creation."""
        tree = ContextTree()
        
        self.assertEqual(len(tree.bubbles), 0)
        self.assertIsNone(tree.root_id)
    
    def test_add_bubble(self):
        """Test adding bubble to tree."""
        tree = ContextTree()
        bubble = ContextBubble(bubble_id="root", content={})
        
        success = tree.add_bubble(bubble, parent_id=None)
        
        self.assertTrue(success)
        self.assertEqual(tree.root_id, "root")
        self.assertEqual(len(tree.bubbles), 1)
    
    def test_get_bubble(self):
        """Test getting bubble."""
        tree = ContextTree()
        bubble = ContextBubble(bubble_id="test", content={})
        tree.add_bubble(bubble)
        
        retrieved = tree.get_bubble("test")
        
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.bubble_id, "test")
    
    def test_traverse(self):
        """Test tree traversal."""
        tree = ContextTree()
        root = ContextBubble(bubble_id="root", content={})
        child = ContextBubble(bubble_id="child", content={})
        
        tree.add_bubble(root)
        tree.add_bubble(child, parent_id="root")
        
        bubble_ids = tree.traverse_depth_first("root")
        
        self.assertIn("root", bubble_ids)
        self.assertIn("child", bubble_ids)


class TestTrafficAgent(unittest.TestCase):
    """Test TrafficAgent class."""
    
    def test_create_agent(self):
        """Test traffic agent creation."""
        tree = ContextTree()
        agent = TrafficAgent(tree)
        
        self.assertIsNotNone(agent.context_tree)
        self.assertEqual(len(agent.pathways), 0)
    
    def test_add_pathway(self):
        """Test adding pathway."""
        tree = ContextTree()
        agent = TrafficAgent(tree)
        
        agent.add_pathway("bubble_1", "bubble_2", weight=0.5)
        
        self.assertEqual(len(agent.pathways), 1)


class TestPathOptimizer(unittest.TestCase):
    """Test PathOptimizer class."""
    
    def test_create_optimizer(self):
        """Test optimizer creation."""
        tree = ContextTree()
        traffic_agent = TrafficAgent(tree)
        optimizer = PathOptimizer(traffic_agent)
        
        self.assertIsNotNone(optimizer.traffic_agent)


class TestUsageTracker(unittest.TestCase):
    """Test UsageTracker class."""
    
    def test_create_tracker(self):
        """Test tracker creation."""
        tracker = UsageTracker(retention_days=30)
        
        self.assertEqual(tracker.retention_days, 30)
        self.assertEqual(len(tracker.records), 0)
    
    def test_record_usage(self):
        """Test recording usage."""
        tracker = UsageTracker()
        
        tracker.record_usage("pathway_1", metadata={"source": "test"})
        
        self.assertEqual(len(tracker.records), 1)
        self.assertEqual(tracker.pathway_counts["pathway_1"], 1)
    
    def test_get_statistics(self):
        """Test getting statistics."""
        tracker = UsageTracker()
        tracker.record_usage("pathway_1")
        tracker.record_usage("pathway_1")
        tracker.record_usage("pathway_2")
        
        stats = tracker.get_pathway_statistics("pathway_1")
        
        self.assertEqual(stats['total_usage'], 2)


if __name__ == '__main__':
    unittest.main()

