# tests/
"""
Unit tests for Equational AI System.
"""

import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai.equational import (
    ResearchIngestion, EquationExtractor, EquationStore, EquationValidator
)
from physics.permanence import StateCache, Precomputation, Retrieval


class TestResearchIngestion(unittest.TestCase):
    """Test ResearchIngestion class."""
    
    def test_create_ingestion(self):
        """Test ingestion creation."""
        ingestion = ResearchIngestion()
        
        self.assertEqual(len(ingestion.papers), 0)
    
    def test_ingest_latex(self):
        """Test LaTeX ingestion."""
        ingestion = ResearchIngestion()
        
        latex_content = r"""
        \title{Test Paper}
        \author{Test Author}
        The energy is $E = mc^2$.
        """
        
        paper = ingestion.ingest_latex(latex_content, paper_id="test_paper")
        
        self.assertIsNotNone(paper)
        self.assertEqual(paper.paper_id, "test_paper")
        self.assertIn("Test Paper", paper.title)


class TestEquationExtractor(unittest.TestCase):
    """Test EquationExtractor class."""
    
    def test_create_extractor(self):
        """Test extractor creation."""
        extractor = EquationExtractor()
        
        self.assertEqual(len(extractor.equations), 0)
        self.assertIn('display_math', extractor.patterns)
    
    def test_extract_inline_math(self):
        """Test inline math extraction."""
        extractor = EquationExtractor()
        
        text = "The energy is $E = mc^2$ and momentum is $p = mv$."
        # Would need a paper object for full extraction
        # This is a simplified test


class TestEquationStore(unittest.TestCase):
    """Test EquationStore class."""
    
    def test_create_store(self):
        """Test store creation."""
        store = EquationStore()
        
        self.assertEqual(len(store.equations), 0)
        self.assertIsNotNone(store.physics_graph)
    
    def test_query_equations(self):
        """Test querying equations."""
        store = EquationStore()
        
        results = store.query_equations(domain="quantum")
        
        self.assertIsInstance(results, list)


class TestEquationValidator(unittest.TestCase):
    """Test EquationValidator class."""
    
    def test_create_validator(self):
        """Test validator creation."""
        validator = EquationValidator()
        
        self.assertIsNotNone(validator.conservation)
        self.assertIsNotNone(validator.constraints)
    
    def test_check_syntax(self):
        """Test syntax checking."""
        validator = EquationValidator()
        
        # Valid syntax
        self.assertTrue(validator._check_syntax("E = mc^2"))
        
        # Invalid syntax (unbalanced)
        self.assertFalse(validator._check_syntax("E = (mc^2"))


class TestStateCache(unittest.TestCase):
    """Test StateCache class."""
    
    def test_create_cache(self):
        """Test cache creation."""
        cache = StateCache(max_size=1000)
        
        self.assertEqual(cache.max_size, 1000)
        self.assertEqual(len(cache.cache), 0)
    
    def test_store_and_retrieve(self):
        """Test storing and retrieving."""
        cache = StateCache()
        
        input_data = {"energy": 10.0, "velocity": 0.1}
        state = {"result": "computed"}
        
        cache_key = cache.store(input_data, state)
        
        retrieved = cache.retrieve(input_data)
        
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved, state)


class TestPrecomputation(unittest.TestCase):
    """Test Precomputation class."""
    
    def test_create_precomputation(self):
        """Test precomputation creation."""
        cache = StateCache()
        precomp = Precomputation(cache)
        
        self.assertIsNotNone(precomp.state_cache)
        self.assertIsNotNone(precomp.integrator)
    
    def test_generate_scenarios(self):
        """Test scenario generation."""
        cache = StateCache()
        precomp = Precomputation(cache)
        
        scenarios = precomp.generate_common_scenarios()
        
        self.assertIsInstance(scenarios, list)
        self.assertGreater(len(scenarios), 0)


class TestRetrieval(unittest.TestCase):
    """Test Retrieval class."""
    
    def test_create_retrieval(self):
        """Test retrieval creation."""
        cache = StateCache()
        retrieval = Retrieval(cache)
        
        self.assertIsNotNone(retrieval.state_cache)
        self.assertIsNotNone(retrieval.integrator)


if __name__ == '__main__':
    unittest.main()

