"""Unit tests for Equational AI System."""

from __future__ import annotations

import unittest

from ai.equational import (
    EquationExtractor,
    EquationStore,
    EquationValidator,
    ResearchIngestion,
)
from physics.permanence import Precomputation, Retrieval, StateCache


class TestResearchIngestion(unittest.TestCase):
    """Test ResearchIngestion class."""

    def test_create_ingestion(self) -> None:
        """Test ingestion creation."""
        ingestion = ResearchIngestion()
        self.assertEqual(len(ingestion.papers), 0)

    def test_ingest_latex(self) -> None:
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

    def test_create_extractor(self) -> None:
        """Test extractor creation."""
        extractor = EquationExtractor()
        self.assertEqual(len(extractor.equations), 0)
        self.assertIn("display_math", extractor.patterns)

    def test_extract_inline_math(self) -> None:
        """Test inline math extraction (simplified - needs paper object for full test)."""
        extractor = EquationExtractor()
        # Placeholder for full extraction test
        self.assertIsNotNone(extractor)


class TestEquationStore(unittest.TestCase):
    """Test EquationStore class."""

    def test_create_store(self) -> None:
        """Test store creation."""
        store = EquationStore()
        self.assertEqual(len(store.equations), 0)
        self.assertIsNotNone(store.physics_graph)

    def test_query_equations(self) -> None:
        """Test querying equations."""
        store = EquationStore()
        results = store.query_equations(domain="quantum")
        self.assertIsInstance(results, list)


class TestEquationValidator(unittest.TestCase):
    """Test EquationValidator class."""

    def test_create_validator(self) -> None:
        """Test validator creation."""
        validator = EquationValidator()
        self.assertIsNotNone(validator.conservation)
        self.assertIsNotNone(validator.constraints)

    def test_check_syntax(self) -> None:
        """Test syntax checking."""
        validator = EquationValidator()
        self.assertTrue(validator._check_syntax("E = mc^2"))
        self.assertFalse(validator._check_syntax("E = (mc^2"))


class TestStateCache(unittest.TestCase):
    """Test StateCache class."""

    def test_create_cache(self) -> None:
        """Test cache creation."""
        cache = StateCache(max_size=1000)
        self.assertEqual(cache.max_size, 1000)
        self.assertEqual(len(cache.cache), 0)

    def test_store_and_retrieve(self) -> None:
        """Test storing and retrieving."""
        cache = StateCache()

        input_data = {"energy": 10.0, "velocity": 0.1}
        state = {"result": "computed"}

        cache.store(input_data, state)

        retrieved = cache.retrieve(input_data)

        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved, state)


class TestPrecomputation(unittest.TestCase):
    """Test Precomputation class."""

    def test_create_precomputation(self) -> None:
        """Test precomputation creation."""
        cache = StateCache()
        precomp = Precomputation(cache)
        self.assertIsNotNone(precomp.state_cache)
        self.assertIsNotNone(precomp.integrator)

    def test_generate_scenarios(self) -> None:
        """Test scenario generation."""
        cache = StateCache()
        precomp = Precomputation(cache)
        scenarios = precomp.generate_common_scenarios()
        self.assertIsInstance(scenarios, list)
        self.assertGreater(len(scenarios), 0)


class TestRetrieval(unittest.TestCase):
    """Test Retrieval class."""

    def test_create_retrieval(self) -> None:
        """Test retrieval creation."""
        cache = StateCache()
        retrieval = Retrieval(cache)
        self.assertIsNotNone(retrieval.state_cache)
        self.assertIsNotNone(retrieval.integrator)


if __name__ == "__main__":
    unittest.main()
