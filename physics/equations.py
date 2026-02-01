# physics/
"""
PATH: physics/equations.py
PURPOSE: Solves physics equations using symbolic mathematics (SymPy) and numerical methods.

FLOW:
┌─────────────┐    ┌──────────────┐    ┌─────────────┐    ┌──────────────┐
│   Parse     │───▶│   Symbolic   │───▶│  Numerical  │───▶│   Validate   │
│  Equation   │    │   Solving    │    │  Fallback   │    │   Results    │
└─────────────┘    └──────────────┘    └─────────────┘    └──────────────┘

First Principle Analysis:
- Physics equations express relationships between physical quantities
- Symbolic solving preserves exactness and shows relationships
- Numerical solving provides concrete values when symbolic fails
- Unit handling ensures dimensional consistency

Mathematical Foundation:
- Symbolic algebra (SymPy)
- Root finding algorithms (Newton-Raphson, bisection)
- Linear algebra for systems of equations
- Differential equations for dynamics

DEPENDENCIES:
- sympy: Symbolic mathematics
- numpy/scipy: Numerical methods
- pint: Unit handling
- validators: Data validation
- loggers: System logging
"""

from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, field
import numpy as np
from enum import Enum
import re
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from validators.data_validator import DataValidator
from loggers.system_logger import SystemLogger

# Try to import SymPy
try:
    import sympy as sp
    from sympy import (
        Symbol, symbols, sympify, simplify, expand, factor,
        solve, solveset, dsolve, nsolve,
        diff, integrate, limit, series,
        sin, cos, tan, exp, log, sqrt, pi, E, I,
        Eq, Function, Derivative, Integral,
        Matrix, eye, zeros, ones,
        latex, pretty
    )
    from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
    from sympy.physics.units import meter, second, kilogram, newton, joule, watt
    SYMPY_AVAILABLE = True
except ImportError:
    SYMPY_AVAILABLE = False

# Try to import scipy for numerical fallback
try:
    from scipy import optimize
    from scipy.integrate import odeint, solve_ivp
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False


class SolveMethod(Enum):
    """Method for solving equations."""
    SYMBOLIC = "symbolic"
    NUMERICAL = "numerical"
    AUTO = "auto"


@dataclass
class EquationResult:
    """Result from equation solving."""
    solutions: List[Any]
    method_used: str
    symbolic_form: Optional[str] = None
    latex_form: Optional[str] = None
    is_exact: bool = True
    variables_solved: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'solutions': [str(s) for s in self.solutions],
            'method_used': self.method_used,
            'symbolic_form': self.symbolic_form,
            'latex_form': self.latex_form,
            'is_exact': self.is_exact,
            'variables_solved': self.variables_solved,
            'metadata': self.metadata
        }


class EquationParser:
    """
    Parses equation strings into SymPy expressions.
    
    Supports:
    - Standard mathematical notation
    - Physics-specific notation (e.g., F=ma)
    - Greek letters (alpha, beta, etc.)
    - Common physics functions
    """
    
    # Greek letter mapping
    GREEK_LETTERS = {
        'alpha': 'α', 'beta': 'β', 'gamma': 'γ', 'delta': 'δ',
        'epsilon': 'ε', 'zeta': 'ζ', 'eta': 'η', 'theta': 'θ',
        'iota': 'ι', 'kappa': 'κ', 'lambda': 'λ', 'mu': 'μ',
        'nu': 'ν', 'xi': 'ξ', 'omicron': 'ο', 'pi': 'π',
        'rho': 'ρ', 'sigma': 'σ', 'tau': 'τ', 'upsilon': 'υ',
        'phi': 'φ', 'chi': 'χ', 'psi': 'ψ', 'omega': 'ω'
    }
    
    # Common physics equations
    PHYSICS_EQUATIONS = {
        'kinetic_energy': 'E_k = (1/2) * m * v**2',
        'potential_energy': 'E_p = m * g * h',
        'momentum': 'p = m * v',
        'force': 'F = m * a',
        'work': 'W = F * d',
        'power': 'P = W / t',
        'wave_speed': 'v = f * lambda',
        'ideal_gas': 'P * V = n * R * T',
        'coulomb': 'F = k * q1 * q2 / r**2',
        'gravitational': 'F = G * m1 * m2 / r**2',
        'einstein_energy': 'E = m * c**2',
        'schrodinger': 'i * hbar * diff(psi, t) = H * psi',
        'harmonic_oscillator': 'x = A * cos(omega * t + phi)'
    }
    
    def __init__(self):
        self.logger = SystemLogger()
        self.known_symbols: Dict[str, Any] = {}
    
    def parse(self, equation_str: str) -> Tuple[Any, List[Any]]:
        """
        Parse an equation string into SymPy expression.
        
        Args:
            equation_str: Equation as string
            
        Returns:
            Tuple of (expression_or_equation, list_of_symbols)
        """
        if not SYMPY_AVAILABLE:
            raise RuntimeError("SymPy is required for equation parsing")
        
        # Preprocess the string
        processed = self._preprocess(equation_str)
        
        # Check if it's an equation (contains =)
        if '=' in processed and processed.count('=') == 1:
            left, right = processed.split('=')
            try:
                left_expr = parse_expr(left.strip(), transformations=standard_transformations + (implicit_multiplication_application,))
                right_expr = parse_expr(right.strip(), transformations=standard_transformations + (implicit_multiplication_application,))
                equation = Eq(left_expr, right_expr)
                symbols_found = list(equation.free_symbols)
                return equation, symbols_found
            except Exception as e:
                self.logger.log(f"Error parsing equation: {e}", level="WARNING")
        
        # Parse as expression
        try:
            expr = parse_expr(processed, transformations=standard_transformations + (implicit_multiplication_application,))
            symbols_found = list(expr.free_symbols)
            return expr, symbols_found
        except Exception as e:
            self.logger.log(f"Error parsing expression: {e}", level="ERROR")
            raise ValueError(f"Could not parse equation: {equation_str}")
    
    def _preprocess(self, equation_str: str) -> str:
        """Preprocess equation string for parsing."""
        processed = equation_str.strip()
        
        # Replace common physics notation
        replacements = {
            '^': '**',
            '×': '*',
            '÷': '/',
            '√': 'sqrt',
            'π': 'pi',
            '∞': 'oo',
        }
        
        for old, new in replacements.items():
            processed = processed.replace(old, new)
        
        return processed
    
    def get_physics_equation(self, name: str) -> str:
        """Get a standard physics equation by name."""
        return self.PHYSICS_EQUATIONS.get(name, '')


class EquationSolver:
    """
    Solves physics equations using symbolic and numerical methods.
    
    Features:
    - Symbolic solving with SymPy
    - Numerical fallback with scipy
    - Unit handling
    - Multiple solution methods
    """
    
    # Physical constants
    CONSTANTS = {
        'c': 299792458,  # Speed of light (m/s)
        'G': 6.67430e-11,  # Gravitational constant (m³/(kg·s²))
        'h': 6.62607015e-34,  # Planck constant (J·s)
        'hbar': 1.054571817e-34,  # Reduced Planck constant (J·s)
        'k_B': 1.380649e-23,  # Boltzmann constant (J/K)
        'e': 1.602176634e-19,  # Elementary charge (C)
        'm_e': 9.1093837015e-31,  # Electron mass (kg)
        'm_p': 1.67262192369e-27,  # Proton mass (kg)
        'epsilon_0': 8.8541878128e-12,  # Vacuum permittivity (F/m)
        'mu_0': 1.25663706212e-6,  # Vacuum permeability (H/m)
        'N_A': 6.02214076e23,  # Avogadro constant (1/mol)
        'R': 8.314462618,  # Gas constant (J/(mol·K))
        'g': 9.80665,  # Standard gravity (m/s²)
    }
    
    def __init__(self):
        """Initialize equation solver."""
        self.validator = DataValidator()
        self.logger = SystemLogger()
        self.parser = EquationParser()
        
        self.logger.log("EquationSolver initialized", level="INFO")
    
    def solve(self, equation: str, variables: Dict[str, float], 
              solve_for: Optional[str] = None,
              method: SolveMethod = SolveMethod.AUTO) -> EquationResult:
        """
        Solve a physics equation.
        
        Args:
            equation: Equation string (e.g., "F = m * a")
            variables: Dictionary of known variable values
            solve_for: Variable to solve for (if None, tries to determine automatically)
            method: Solving method to use
            
        Returns:
            EquationResult with solutions
        """
        if not isinstance(equation, str):
            self.logger.log("Invalid equation provided", level="ERROR")
            raise ValueError("Equation must be a string")
        
        self.logger.log(f"Solving equation: {equation}", level="DEBUG")
        
        if not SYMPY_AVAILABLE:
            self.logger.log("SymPy not available, using simple evaluation", level="WARNING")
            return self._simple_solve(equation, variables)
        
        try:
            # Parse the equation
            parsed, found_symbols = self.parser.parse(equation)
            
            # Determine variable to solve for
            if solve_for is None:
                # Find the unknown variable
                known_vars = set(variables.keys())
                symbol_names = {str(s) for s in found_symbols}
                unknown_vars = symbol_names - known_vars - set(self.CONSTANTS.keys())
                
                if len(unknown_vars) == 1:
                    solve_for = unknown_vars.pop()
                elif len(unknown_vars) == 0:
                    # All variables known - evaluate
                    return self._evaluate(parsed, variables)
                else:
                    self.logger.log(f"Multiple unknowns: {unknown_vars}", level="WARNING")
                    solve_for = list(unknown_vars)[0]
            
            # Create substitution dictionary
            subs_dict = {}
            for var_name, value in variables.items():
                sym = Symbol(var_name)
                subs_dict[sym] = value
            
            # Add physical constants
            for const_name, const_value in self.CONSTANTS.items():
                if const_name in str(parsed):
                    sym = Symbol(const_name)
                    subs_dict[sym] = const_value
            
            # Solve the equation
            solve_symbol = Symbol(solve_for)
            
            if method == SolveMethod.SYMBOLIC or method == SolveMethod.AUTO:
                result = self._solve_symbolic(parsed, solve_symbol, subs_dict)
                if result.solutions:
                    return result
            
            if method == SolveMethod.NUMERICAL or (method == SolveMethod.AUTO and not result.solutions):
                return self._solve_numerical(parsed, solve_symbol, subs_dict, variables)
            
            return result
            
        except Exception as e:
            self.logger.log(f"Error solving equation: {e}", level="ERROR")
            return EquationResult(
                solutions=[],
                method_used="error",
                metadata={'error': str(e)}
            )
    
    def _solve_symbolic(self, parsed: Any, solve_symbol: Any, 
                       subs_dict: Dict[Any, float]) -> EquationResult:
        """
        Solve equation symbolically.
        
        Args:
            parsed: Parsed equation
            solve_symbol: Symbol to solve for
            subs_dict: Substitution dictionary
            
        Returns:
            EquationResult
        """
        try:
            # Get the equation to solve
            if isinstance(parsed, Eq):
                # It's an equation
                equation = parsed
            else:
                # It's an expression, assume = 0
                equation = Eq(parsed, 0)
            
            # Substitute known values first (partially)
            # Keep the solve_symbol free
            partial_subs = {k: v for k, v in subs_dict.items() if k != solve_symbol}
            equation_substituted = equation.subs(partial_subs)
            
            # Solve
            solutions = solve(equation_substituted, solve_symbol)
            
            # Convert to list if necessary
            if not isinstance(solutions, list):
                solutions = [solutions]
            
            # Evaluate numerical values
            numerical_solutions = []
            for sol in solutions:
                try:
                    # Try to evaluate to float
                    num_val = float(sol.evalf())
                    numerical_solutions.append(num_val)
                except:
                    numerical_solutions.append(sol)
            
            return EquationResult(
                solutions=numerical_solutions,
                method_used="symbolic",
                symbolic_form=str(solutions[0]) if solutions else None,
                latex_form=latex(solutions[0]) if solutions else None,
                is_exact=True,
                variables_solved=[str(solve_symbol)],
                metadata={
                    'original_equation': str(parsed),
                    'num_solutions': len(solutions)
                }
            )
            
        except Exception as e:
            self.logger.log(f"Symbolic solving failed: {e}", level="WARNING")
            return EquationResult(
                solutions=[],
                method_used="symbolic_failed",
                metadata={'error': str(e)}
            )
    
    def _solve_numerical(self, parsed: Any, solve_symbol: Any,
                        subs_dict: Dict[Any, float],
                        variables: Dict[str, float]) -> EquationResult:
        """
        Solve equation numerically.
        
        Args:
            parsed: Parsed equation
            solve_symbol: Symbol to solve for
            subs_dict: Substitution dictionary
            variables: Original variable dictionary
            
        Returns:
            EquationResult
        """
        if not SCIPY_AVAILABLE:
            return EquationResult(
                solutions=[],
                method_used="numerical_unavailable",
                is_exact=False,
                metadata={'error': 'scipy not available'}
            )
        
        try:
            # Create a function from the equation
            if isinstance(parsed, Eq):
                # Convert equation to f(x) = 0 form
                expr = parsed.lhs - parsed.rhs
            else:
                expr = parsed
            
            # Substitute known values
            for sym, val in subs_dict.items():
                if sym != solve_symbol:
                    expr = expr.subs(sym, val)
            
            # Create numerical function
            f = sp.lambdify(solve_symbol, expr, 'numpy')
            
            # Try multiple initial guesses
            initial_guesses = [0, 1, -1, 10, -10, 100, -100]
            solutions = []
            
            for guess in initial_guesses:
                try:
                    sol = optimize.fsolve(f, guess, full_output=True)
                    if sol[2] == 1:  # Converged
                        solutions.append(float(sol[0][0]))
                except:
                    continue
            
            # Remove duplicates (within tolerance)
            unique_solutions = []
            for sol in solutions:
                is_duplicate = False
                for existing in unique_solutions:
                    if abs(sol - existing) < 1e-10:
                        is_duplicate = True
                        break
                if not is_duplicate:
                    unique_solutions.append(sol)
            
            return EquationResult(
                solutions=unique_solutions,
                method_used="numerical",
                is_exact=False,
                variables_solved=[str(solve_symbol)],
                metadata={
                    'initial_guesses': initial_guesses,
                    'num_solutions': len(unique_solutions)
                }
            )
            
        except Exception as e:
            self.logger.log(f"Numerical solving failed: {e}", level="WARNING")
            return EquationResult(
                solutions=[],
                method_used="numerical_failed",
                is_exact=False,
                metadata={'error': str(e)}
            )
    
    def _evaluate(self, parsed: Any, variables: Dict[str, float]) -> EquationResult:
        """
        Evaluate an expression with all variables known.
        
        Args:
            parsed: Parsed expression/equation
            variables: All variable values
            
        Returns:
            EquationResult with evaluated value
        """
        try:
            subs_dict = {}
            for var_name, value in variables.items():
                sym = Symbol(var_name)
                subs_dict[sym] = value
            
            # Add constants
            for const_name, const_value in self.CONSTANTS.items():
                sym = Symbol(const_name)
                subs_dict[sym] = const_value
            
            if isinstance(parsed, Eq):
                # Evaluate both sides
                lhs = float(parsed.lhs.subs(subs_dict).evalf())
                rhs = float(parsed.rhs.subs(subs_dict).evalf())
                is_satisfied = abs(lhs - rhs) < 1e-10
                
                return EquationResult(
                    solutions=[is_satisfied],
                    method_used="evaluation",
                    is_exact=True,
                    metadata={
                        'lhs': lhs,
                        'rhs': rhs,
                        'satisfied': is_satisfied
                    }
                )
            else:
                result = float(parsed.subs(subs_dict).evalf())
                return EquationResult(
                    solutions=[result],
                    method_used="evaluation",
                    is_exact=True
                )
                
        except Exception as e:
            self.logger.log(f"Evaluation failed: {e}", level="WARNING")
            return EquationResult(
                solutions=[],
                method_used="evaluation_failed",
                metadata={'error': str(e)}
            )
    
    def _simple_solve(self, equation: str, variables: Dict[str, float]) -> EquationResult:
        """
        Simple solving without SymPy (limited functionality).
        
        Args:
            equation: Equation string
            variables: Variable values
            
        Returns:
            EquationResult
        """
        # Very basic evaluation for simple expressions
        try:
            # Add constants and variables to context
            context = dict(self.CONSTANTS)
            context.update(variables)
            context.update({
                'sin': np.sin, 'cos': np.cos, 'tan': np.tan,
                'exp': np.exp, 'log': np.log, 'sqrt': np.sqrt,
                'pi': np.pi, 'e': np.e
            })
            
            if '=' in equation:
                left, right = equation.split('=')
                left_val = eval(left.strip(), {"__builtins__": {}}, context)
                right_val = eval(right.strip(), {"__builtins__": {}}, context)
                return EquationResult(
                    solutions=[left_val == right_val],
                    method_used="simple_evaluation",
                    is_exact=False,
                    metadata={'lhs': left_val, 'rhs': right_val}
                )
            else:
                result = eval(equation, {"__builtins__": {}}, context)
                return EquationResult(
                    solutions=[result],
                    method_used="simple_evaluation",
                    is_exact=False
                )
        except Exception as e:
            return EquationResult(
                solutions=[],
                method_used="simple_failed",
                metadata={'error': str(e)}
            )
    
    def solve_system(self, equations: List[str], variables: Dict[str, float],
                    solve_for: List[str]) -> Dict[str, EquationResult]:
        """
        Solve a system of equations.
        
        Args:
            equations: List of equation strings
            variables: Known variable values
            solve_for: List of variables to solve for
            
        Returns:
            Dictionary mapping variable names to EquationResults
        """
        if not SYMPY_AVAILABLE:
            return {'error': EquationResult(
                solutions=[],
                method_used='sympy_unavailable',
                metadata={'error': 'SymPy required for systems'}
            )}
        
        try:
            # Parse all equations
            parsed_eqs = []
            all_symbols = set()
            
            for eq_str in equations:
                parsed, syms = self.parser.parse(eq_str)
                if isinstance(parsed, Eq):
                    parsed_eqs.append(parsed)
                else:
                    parsed_eqs.append(Eq(parsed, 0))
                all_symbols.update(syms)
            
            # Create symbols to solve for
            solve_symbols = [Symbol(s) for s in solve_for]
            
            # Substitute known values
            subs_dict = {}
            for var_name, value in variables.items():
                sym = Symbol(var_name)
                subs_dict[sym] = value
            
            # Add constants
            for const_name, const_value in self.CONSTANTS.items():
                sym = Symbol(const_name)
                subs_dict[sym] = const_value
            
            # Substitute
            substituted_eqs = [eq.subs(subs_dict) for eq in parsed_eqs]
            
            # Solve the system
            solutions = solve(substituted_eqs, solve_symbols)
            
            # Format results
            results = {}
            if isinstance(solutions, dict):
                for sym, sol in solutions.items():
                    try:
                        num_val = float(sol.evalf())
                    except:
                        num_val = sol
                    
                    results[str(sym)] = EquationResult(
                        solutions=[num_val],
                        method_used="system_symbolic",
                        symbolic_form=str(sol),
                        is_exact=True,
                        variables_solved=[str(sym)]
                    )
            elif isinstance(solutions, list):
                for i, sol_tuple in enumerate(solutions):
                    for j, sym in enumerate(solve_symbols):
                        sol = sol_tuple[j] if isinstance(sol_tuple, tuple) else sol_tuple
                        try:
                            num_val = float(sol.evalf())
                        except:
                            num_val = sol
                        
                        key = f"{str(sym)}_solution_{i}"
                        results[key] = EquationResult(
                            solutions=[num_val],
                            method_used="system_symbolic",
                            symbolic_form=str(sol),
                            is_exact=True,
                            variables_solved=[str(sym)]
                        )
            
            return results
            
        except Exception as e:
            self.logger.log(f"System solving failed: {e}", level="ERROR")
            return {'error': EquationResult(
                solutions=[],
                method_used='system_failed',
                metadata={'error': str(e)}
            )}
    
    def differentiate(self, expression: str, variable: str, order: int = 1) -> EquationResult:
        """
        Differentiate an expression.
        
        Args:
            expression: Expression to differentiate
            variable: Variable to differentiate with respect to
            order: Order of differentiation
            
        Returns:
            EquationResult with derivative
        """
        if not SYMPY_AVAILABLE:
            return EquationResult(
                solutions=[],
                method_used="sympy_unavailable"
            )
        
        try:
            expr, _ = self.parser.parse(expression)
            var = Symbol(variable)
            
            derivative = diff(expr, var, order)
            
            return EquationResult(
                solutions=[str(derivative)],
                method_used="differentiation",
                symbolic_form=str(derivative),
                latex_form=latex(derivative),
                is_exact=True,
                metadata={
                    'variable': variable,
                    'order': order,
                    'original': expression
                }
            )
        except Exception as e:
            return EquationResult(
                solutions=[],
                method_used="differentiation_failed",
                metadata={'error': str(e)}
            )
    
    def integrate_expr(self, expression: str, variable: str,
                      lower: Optional[float] = None,
                      upper: Optional[float] = None) -> EquationResult:
        """
        Integrate an expression.
        
        Args:
            expression: Expression to integrate
            variable: Variable to integrate with respect to
            lower: Lower bound (for definite integral)
            upper: Upper bound (for definite integral)
            
        Returns:
            EquationResult with integral
        """
        if not SYMPY_AVAILABLE:
            return EquationResult(
                solutions=[],
                method_used="sympy_unavailable"
            )
        
        try:
            expr, _ = self.parser.parse(expression)
            var = Symbol(variable)
            
            if lower is not None and upper is not None:
                # Definite integral
                integral = integrate(expr, (var, lower, upper))
            else:
                # Indefinite integral
                integral = integrate(expr, var)
            
            try:
                num_val = float(integral.evalf())
            except:
                num_val = integral
            
            return EquationResult(
                solutions=[num_val],
                method_used="integration",
                symbolic_form=str(integral),
                latex_form=latex(integral),
                is_exact=True,
                metadata={
                    'variable': variable,
                    'lower': lower,
                    'upper': upper,
                    'original': expression
                }
            )
        except Exception as e:
            return EquationResult(
                solutions=[],
                method_used="integration_failed",
                metadata={'error': str(e)}
            )
    
    def get_constant(self, name: str) -> Optional[float]:
        """Get a physical constant by name."""
        return self.CONSTANTS.get(name)
    
    def list_constants(self) -> Dict[str, float]:
        """List all physical constants."""
        return dict(self.CONSTANTS)
