# PATH: ingestion/arxiv_ingestion.py
# PURPOSE:
#   - Crawl arXiv for papers, extract equations, convert to Formulas, insert into FormulaGraph
# ROLE IN ARCHITECTURE:
#   - Automated cold-knowledge expansion feeding the evolution loop
# MAIN FLOW:
#   arXiv search -> download PDFs -> ResearchIngestion -> EquationExtractor ->
#   create Formula objects -> add to graph -> trigger evolution

from __future__ import annotations

import hashlib
import os
import tempfile
from typing import Any, Dict

import arxiv

from ai.equational.equation_extractor import EquationExtractor
from ai.equational.research_ingestion import ResearchIngestion
from substrate.graph.formula import Formula, FormulaLayer, FormulaStatus
from substrate.graph.formula_graph import FormulaGraph
from substrate.main import PhysicsAI, PhysicsAIConfig

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
_HASH_PREFIX_LEN = 16
_DEFAULT_QUERY = "physics"
_DEFAULT_MAX_RESULTS = 3


def _hash_id(text: str) -> str:
    """Generate a short SHA-256 hash ID from *text*."""
    return hashlib.sha256(text.encode()).hexdigest()[:_HASH_PREFIX_LEN]


def equation_to_formula(eq: Any, paper_meta: Dict[str, Any]) -> Formula:
    """Convert an extracted equation to a Formula object.

    Args:
        eq: Extracted equation object with ``.equation`` and ``.domain`` attrs.
        paper_meta: Paper metadata dictionary.

    Returns:
        A ``Formula`` instance.
    """
    eq_text = eq.equation.strip()
    fid = _hash_id(eq_text)
    return Formula(
        id=fid,
        name=f"arxiv_eq_{fid}",
        symbolic_form=eq_text,
        domain=eq.domain or paper_meta.get("domain", "general"),
        assumptions=[],
        layer=FormulaLayer.FUNDAMENTAL,
        status=FormulaStatus.CANDIDATE,
        description=f"Extracted from arXiv paper {paper_meta.get('paper_id', '')}",
        tags={"arxiv", paper_meta.get("primary_category", "unknown")},
        source=f"arxiv:{paper_meta.get('paper_id', '')}",
    )


def ingest_arxiv_papers(
    ai: PhysicsAI,
    query: str = _DEFAULT_QUERY,
    max_results: int = _DEFAULT_MAX_RESULTS,
) -> Dict[str, int]:
    """Ingest papers from arXiv into the formula graph.

    Args:
        ai: Running ``PhysicsAI`` instance.
        query: arXiv search query.
        max_results: Maximum number of papers to fetch.

    Returns:
        Dict with keys ``equations_seen`` and ``formulas_added``.
    """
    graph: FormulaGraph = ai.graph
    ingestion = ResearchIngestion()
    extractor = EquationExtractor()

    added = 0
    seen = 0
    results = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate,
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        for result in results.results():
            paper_id = result.get_short_id()
            pdf_path = os.path.join(tmpdir, f"{paper_id}.pdf")
            try:
                result.download_pdf(dirpath=tmpdir, filename=f"{paper_id}.pdf")
            except Exception:
                continue

            paper = ingestion.ingest_pdf(pdf_path)
            if not paper:
                continue

            paper.metadata["paper_id"] = paper_id
            paper.metadata["primary_category"] = (
                result.primary_category if hasattr(result, "primary_category") else "unknown"
            )
            equations = extractor.extract_from_paper(paper)
            if not equations:
                continue

            for eq in equations:
                seen += 1
                formula = equation_to_formula(eq, paper.metadata)
                if graph.add_formula(formula, overwrite=False):
                    added += 1

    ai.force_evolution_cycle()

    return {"equations_seen": seen, "formulas_added": added}


if __name__ == "__main__":
    _query = os.getenv("ARXIV_QUERY", _DEFAULT_QUERY)
    _max = int(os.getenv("ARXIV_MAX_RESULTS", str(_DEFAULT_MAX_RESULTS)))

    config = PhysicsAIConfig(
        llm_backend_type=os.getenv("LLM_BACKEND", "throttled_openai"),
        llm_server_url=os.getenv("LM_STUDIO_URL", "http://127.0.0.1:8080"),
        llm_model_name=os.getenv("LM_STUDIO_MODEL", "lmstudio-deepseek"),
    )
    _ai = PhysicsAI(config)
    _ai.start()
    _stats = ingest_arxiv_papers(_ai, query=_query, max_results=_max)
    print(f"[arxiv ingestion] {_stats}")
    _ai.stop()
