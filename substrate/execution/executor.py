# PATH: substrate/execution/executor.py
# PURPOSE:
#   - Execute formulas using symbolic (SymPy) or numeric (NumPy/SciPy) backends
# ROLE IN ARCHITECTURE:
#   - Replaces LLM math for formula execution with deterministic computation
# MAIN EXPORTS:
#   - FormulaExecutor
# NON-RESPONSIBILITIES:
#   - Does NOT plan derivations or manage graph state
# NOTES FOR FUTURE AI:
#   - Extend with ODE/PDE solvers and kernel accelerators
#   - Prefer stable numeric methods over ad-hoc evaluation

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import sympy as sp

from substrate.graph.formula import Formula


@dataclass
class FormulaExecutor:
    """Executes a Formula using symbolic/numeric backends.

    Tries SymPy first; falls back to simple evaluation.
    Returns a dict of outputs or None on failure.
    """

    def evaluate_formula(
        self, formula: Formula, variables: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Evaluate a formula with given variable assignments.

        Args:
            formula: The Formula to execute.
            variables: Mapping of symbol -> value for inputs/parameters.

        Returns:
            Dict of output symbol -> value, or None if evaluation fails.
        """
        try:
            expr_str = formula.sympy_expr or formula.symbolic_form
            if not expr_str:
                return None

            expr = sp.sympify(expr_str)

            if isinstance(expr, sp.Equality):
                left, right = expr.lhs, expr.rhs
                outputs: List[str] = (
                    [v.symbol for v in formula.outputs] or list(expr.free_symbols)
                )
                target = sp.Symbol(outputs[0])
                solution = sp.solve(sp.Eq(left, right), target)
                if not solution:
                    return None
                val = self._evaluate_expression(solution[0], variables)
                return {outputs[0]: val}

            outputs = [v.symbol for v in formula.outputs]
            if not outputs:
                return None

            result_val = self._evaluate_expression(expr, variables)
            return {outputs[0]: result_val}
        except Exception:
            return None

    def _evaluate_expression(self, expr: sp.Expr, variables: Dict[str, Any]) -> Any:
        """Evaluate a SymPy expression with given variables.

        Args:
            expr: SymPy expression to evaluate.
            variables: Mapping of symbol name -> value.

        Returns:
            Numeric result.

        Raises:
            ValueError: If required variables are missing.
        """
        symbols = list(expr.free_symbols)
        subs = {sp.Symbol(k): v for k, v in variables.items() if sp.Symbol(k) in symbols}
        missing = [s for s in symbols if s not in subs]
        if missing:
            raise ValueError(f"Missing variables for evaluation: {missing}")

        func = sp.lambdify(list(subs.keys()), expr, modules=["numpy", "math"])
        args = [subs[s] for s in subs]
        return func(*args)
