# api/v1/
"""
Equational AI API endpoints.
"""

from flask import request, jsonify
from api.v1 import api_v1
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from ai.equational import ResearchIngestion, EquationExtractor, EquationStore, EquationValidator
from physics.permanence import StateCache, Precomputation, Retrieval
from utilities.cot_logging import ChainOfThoughtLogger, LogLevel
from loggers.system_logger import SystemLogger

logger = SystemLogger()

# Global instances (in production, would use proper dependency injection)
research_ingestion = ResearchIngestion()
equation_extractor = EquationExtractor()
equation_store = EquationStore()
equation_validator = EquationValidator()
state_cache = StateCache()
precomputation = Precomputation(state_cache)
retrieval = Retrieval(state_cache)


@api_v1.route('/equations/solve', methods=['POST'])
def solve_equation():
    """
    Solve an equation symbolically using SymPy.

    Request body:
    {
        "equation": "F = m * a",
        "variables": {"m": 10, "a": 9.8},
        "solve_for": "F"
    }
    """
    cot = ChainOfThoughtLogger()
    step_id = cot.start_step(action="API_SOLVE_EQUATION", level=LogLevel.INFO)

    try:
        data = request.get_json()
        if not data or 'equation' not in data:
            cot.end_step(step_id, output_data={'error': 'equation required'}, validation_passed=False)
            return jsonify({'success': False, 'error': 'equation required'}), 400

        equation_str = data['equation']
        solve_for = data.get('solve_for', '')
        variables = data.get('variables', {})

        import sympy
        from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application

        transformations = standard_transformations + (implicit_multiplication_application,)

        # Split on '=' to handle equations like "F = m * a"
        sides = equation_str.split('=')
        if len(sides) == 2:
            lhs = parse_expr(sides[0].strip(), transformations=transformations)
            rhs = parse_expr(sides[1].strip(), transformations=transformations)
            expr = sympy.Eq(lhs, rhs)
        else:
            expr = parse_expr(equation_str.strip(), transformations=transformations)

        # Substitute known variable values
        subs = {}
        for var_name, var_val in variables.items():
            sym = sympy.Symbol(var_name)
            subs[sym] = var_val

        # Solve
        if solve_for:
            target = sympy.Symbol(solve_for)
            solutions = sympy.solve(expr, target, dict=False)
        else:
            solutions = sympy.solve(expr, dict=True)

        # Evaluate numerically if substitutions available
        numeric_results = []
        for sol in (solutions if isinstance(solutions, list) else [solutions]):
            if subs:
                try:
                    numeric_results.append(str(sympy.nsimplify(sol).subs(subs).evalf()))
                except Exception:
                    numeric_results.append(str(sol))
            else:
                numeric_results.append(str(sol))

        simplified = str(sympy.simplify(expr))

        result = {
            'success': True,
            'equation': equation_str,
            'solve_for': solve_for,
            'solutions': [str(s) for s in (solutions if isinstance(solutions, list) else [solutions])],
            'numeric': numeric_results,
            'simplified': simplified,
            'steps': [
                f"Parse: {equation_str}",
                f"Target variable: {solve_for or 'all'}",
                f"Substitutions: {variables}",
                f"Solutions: {[str(s) for s in (solutions if isinstance(solutions, list) else [solutions])]}",
            ],
        }

        cot.end_step(step_id, output_data=result, validation_passed=True)
        return jsonify(result), 200

    except Exception as e:
        cot.end_step(step_id, output_data={'error': str(e)}, validation_passed=False)
        logger.log(f"Error in solve_equation: {str(e)}", level="ERROR")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_v1.route('/equational/ingest', methods=['POST'])
def ingest_research():
    """
    Ingest research paper.
    
    Request body:
    {
        "type": "pdf|arxiv|latex",
        "source": "file_path|arxiv_id|latex_content",
        "paper_id": "optional_id"
    }
    """
    cot = ChainOfThoughtLogger()
    step_id = cot.start_step(action="API_INGEST_RESEARCH", level=LogLevel.INFO)
    
    try:
        data = request.get_json()
        
        if not data or 'type' not in data or 'source' not in data:
            cot.end_step(step_id, output_data={'error': 'type and source required'}, validation_passed=False)
            return jsonify({'error': 'type and source required'}), 400
        
        paper = None
        ingest_type = data['type']
        source = data['source']
        
        if ingest_type == 'pdf':
            paper = research_ingestion.ingest_pdf(source)
        elif ingest_type == 'arxiv':
            paper = research_ingestion.ingest_arxiv(source)
        elif ingest_type == 'latex':
            paper = research_ingestion.ingest_latex(source, data.get('paper_id'))
        else:
            cot.end_step(step_id, output_data={'error': 'Invalid type'}, validation_passed=False)
            return jsonify({'error': 'Invalid type'}), 400
        
        if not paper:
            cot.end_step(step_id, output_data={'error': 'Failed to ingest'}, validation_passed=False)
            return jsonify({'error': 'Failed to ingest paper'}), 500
        
        # Extract equations
        equations = equation_extractor.extract_from_paper(paper)
        
        cot.end_step(step_id, output_data={'paper_id': paper.paper_id, 'num_equations': len(equations)}, validation_passed=True)
        
        return jsonify({
            'paper_id': paper.paper_id,
            'title': paper.title,
            'num_equations': len(equations),
            'equations': [eq.equation_id for eq in equations]
        }), 201
    
    except Exception as e:
        cot.end_step(step_id, output_data={'error': str(e)}, validation_passed=False)
        logger.log(f"Error in ingest_research: {str(e)}", level="ERROR")
        return jsonify({'error': str(e)}), 500


@api_v1.route('/equational/equations', methods=['GET'])
def list_equations():
    """List all equations."""
    cot = ChainOfThoughtLogger()
    step_id = cot.start_step(action="API_LIST_EQUATIONS", level=LogLevel.INFO)
    
    try:
        equations = equation_store.equations
        equation_list = [
            {
                'equation_id': stored.equation.equation_id,
                'equation': stored.equation.equation,
                'domain': stored.equation.domain,
                'variables': stored.equation.variables,
                'validated': stored.validated
            }
            for stored in equations.values()
        ]
        
        cot.end_step(step_id, output_data={'count': len(equation_list)}, validation_passed=True)
        
        return jsonify({'equations': equation_list}), 200
    
    except Exception as e:
        cot.end_step(step_id, output_data={'error': str(e)}, validation_passed=False)
        logger.log(f"Error in list_equations: {str(e)}", level="ERROR")
        return jsonify({'error': str(e)}), 500


@api_v1.route('/equational/equations/<eq_id>', methods=['GET'])
def get_equation(eq_id):
    """Get equation details."""
    cot = ChainOfThoughtLogger()
    step_id = cot.start_step(action="API_GET_EQUATION", level=LogLevel.INFO)
    
    try:
        stored = equation_store.get_equation(eq_id)
        
        if not stored:
            cot.end_step(step_id, output_data={'error': 'Equation not found'}, validation_passed=False)
            return jsonify({'error': 'Equation not found'}), 404
        
        eq = stored.equation
        
        cot.end_step(step_id, output_data={'equation_id': eq_id}, validation_passed=True)
        
        return jsonify({
            'equation_id': eq.equation_id,
            'equation': eq.equation,
            'equation_type': eq.equation_type,
            'domain': eq.domain,
            'variables': eq.variables,
            'context': eq.context,
            'theory_links': stored.theory_links,
            'domain_links': stored.domain_links,
            'related_equations': stored.related_equations,
            'validated': stored.validated
        }), 200
    
    except Exception as e:
        cot.end_step(step_id, output_data={'error': str(e)}, validation_passed=False)
        logger.log(f"Error in get_equation: {str(e)}", level="ERROR")
        return jsonify({'error': str(e)}), 500


@api_v1.route('/equational/validate', methods=['POST'])
def validate_equation():
    """
    Validate equation.
    
    Request body:
    {
        "equation_id": "eq_123"
    }
    """
    cot = ChainOfThoughtLogger()
    step_id = cot.start_step(action="API_VALIDATE_EQUATION", level=LogLevel.VALIDATION)
    
    try:
        data = request.get_json()
        
        if not data or 'equation_id' not in data:
            cot.end_step(step_id, output_data={'error': 'equation_id required'}, validation_passed=False)
            return jsonify({'error': 'equation_id required'}), 400
        
        stored = equation_store.get_equation(data['equation_id'])
        
        if not stored:
            cot.end_step(step_id, output_data={'error': 'Equation not found'}, validation_passed=False)
            return jsonify({'error': 'Equation not found'}), 404
        
        is_valid, violations = equation_validator.validate(stored.equation)
        
        # Update stored equation
        stored.validated = is_valid
        
        cot.end_step(step_id, output_data={'is_valid': is_valid, 'violations': violations}, validation_passed=is_valid)
        
        return jsonify({
            'equation_id': data['equation_id'],
            'is_valid': is_valid,
            'violations': violations
        }), 200
    
    except Exception as e:
        cot.end_step(step_id, output_data={'error': str(e)}, validation_passed=False)
        logger.log(f"Error in validate_equation: {str(e)}", level="ERROR")
        return jsonify({'error': str(e)}), 500


@api_v1.route('/equational/permanence', methods=['GET'])
def get_permanence_states():
    """Get permanence state cache statistics."""
    cot = ChainOfThoughtLogger()
    step_id = cot.start_step(action="API_GET_PERMANENCE", level=LogLevel.INFO)
    
    try:
        cache_stats = state_cache.get_statistics()
        precomp_stats = precomputation.get_statistics()
        
        combined = {
            'cache': cache_stats,
            'precomputation': precomp_stats
        }
        
        cot.end_step(step_id, output_data={'stats': combined}, validation_passed=True)
        
        return jsonify(combined), 200
    
    except Exception as e:
        cot.end_step(step_id, output_data={'error': str(e)}, validation_passed=False)
        logger.log(f"Error in get_permanence_states: {str(e)}", level="ERROR")
        return jsonify({'error': str(e)}), 500

