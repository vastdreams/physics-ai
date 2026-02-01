# PATH: substrate/execution/__init__.py
# PURPOSE:
#   - Execution layer for evaluating formulas with symbolic/numeric backends
# ROLE IN ARCHITECTURE:
#   - Provides concrete computation for formulas (avoids LLM math)
# MAIN EXPORTS:
#   - FormulaExecutor: executes formulas using SymPy/SciPy where possible
# NON-RESPONSIBILITIES:
#   - Does NOT plan derivations
#   - Does NOT manage graph or critics
# NOTES FOR FUTURE AI:
#   - Extend with PDE/ODE solvers and kernel accelerators as needed

from substrate.execution.executor import FormulaExecutor

__all__ = ["FormulaExecutor"]

