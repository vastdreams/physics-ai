# api/v1/
"""
Evolution endpoints.
"""

from flask import request, jsonify
from api.v1 import api_v1
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from evolution.self_evolution import SelfEvolutionEngine
from ai.nodal_vectorization.graph_builder import GraphBuilder
from ai.nodal_vectorization.vector_store import VectorStore
from utilities.cot_logging import ChainOfThoughtLogger, LogLevel
from loggers.system_logger import SystemLogger

logger = SystemLogger()
vector_store = VectorStore()
graph_builder = GraphBuilder(vector_store)
evolution_engine = SelfEvolutionEngine(graph_builder)


@api_v1.route('/evolution/analyze', methods=['POST'])
def analyze_codebase():
    """
    Analyze codebase for evolution opportunities.
    
    Request body:
    {
        "directory": "/path/to/directory"
    }
    """
    cot = ChainOfThoughtLogger()
    step_id = cot.start_step(
        action="API_ANALYZE_CODEBASE",
        level=LogLevel.INFO
    )
    
    try:
        data = request.get_json()
        
        if not data or 'directory' not in data:
            cot.end_step(step_id, output_data={'error': 'Directory required'}, validation_passed=False)
            return jsonify({'error': 'Directory required'}), 400
        
        directory = data['directory']
        
        result = evolution_engine.analyze_codebase(directory)
        
        cot.end_step(step_id, output_data={'opportunities': len(result.get('opportunities', []))}, validation_passed=True)
        
        return jsonify(result), 200
    
    except Exception as e:
        cot.end_step(step_id, output_data={'error': str(e)}, validation_passed=False)
        logger.log(f"Error in analyze_codebase endpoint: {str(e)}", level="ERROR")
        return jsonify({'error': str(e)}), 500


@api_v1.route('/evolution/evolve', methods=['POST'])
def evolve_function():
    """
    Evolve a function.
    
    Request body:
    {
        "file_path": "/path/to/file.py",
        "function_name": "function_name",
        "improvement_spec": {...}
    }
    """
    cot = ChainOfThoughtLogger()
    step_id = cot.start_step(
        action="API_EVOLVE_FUNCTION",
        level=LogLevel.INFO
    )
    
    try:
        data = request.get_json()
        
        if not data or 'file_path' not in data or 'function_name' not in data:
            cot.end_step(step_id, output_data={'error': 'file_path and function_name required'}, validation_passed=False)
            return jsonify({'error': 'file_path and function_name required'}), 400
        
        file_path = data['file_path']
        function_name = data['function_name']
        improvement_spec = data.get('improvement_spec', {})
        
        success, new_code = evolution_engine.evolve_function(
            file_path=file_path,
            function_name=function_name,
            improvement_spec=improvement_spec
        )
        
        if success:
            cot.end_step(step_id, output_data={'success': True}, validation_passed=True)
            return jsonify({
                'success': True,
                'new_code': new_code
            }), 200
        else:
            cot.end_step(step_id, output_data={'error': 'Evolution failed'}, validation_passed=False)
            return jsonify({'error': 'Evolution failed'}), 400
    
    except Exception as e:
        cot.end_step(step_id, output_data={'error': str(e)}, validation_passed=False)
        logger.log(f"Error in evolve_function endpoint: {str(e)}", level="ERROR")
        return jsonify({'error': str(e)}), 500


@api_v1.route('/evolution/history', methods=['GET'])
def evolution_history():
    """Get evolution history."""
    cot = ChainOfThoughtLogger()
    step_id = cot.start_step(
        action="API_EVOLUTION_HISTORY",
        level=LogLevel.INFO
    )
    
    try:
        history = evolution_engine.get_evolution_history()
        
        cot.end_step(step_id, output_data={'history_count': len(history)}, validation_passed=True)
        
        return jsonify({'history': history}), 200
    
    except Exception as e:
        cot.end_step(step_id, output_data={'error': str(e)}, validation_passed=False)
        logger.log(f"Error in evolution_history endpoint: {str(e)}", level="ERROR")
        return jsonify({'error': str(e)}), 500


@api_v1.route('/evolution/rollback', methods=['POST'])
def rollback():
    """
    Rollback last evolution.
    
    Request body:
    {
        "file_path": "/path/to/file.py"  # Optional, rollback most recent if not provided
    }
    """
    cot = ChainOfThoughtLogger()
    step_id = cot.start_step(
        action="API_ROLLBACK",
        level=LogLevel.INFO
    )
    
    try:
        data = request.get_json() or {}
        file_path = data.get('file_path')
        
        success = evolution_engine.rollback(file_path)
        
        if success:
            cot.end_step(step_id, output_data={'success': True}, validation_passed=True)
            return jsonify({'success': True}), 200
        else:
            cot.end_step(step_id, output_data={'error': 'Rollback failed'}, validation_passed=False)
            return jsonify({'error': 'Rollback failed'}), 400
    
    except Exception as e:
        cot.end_step(step_id, output_data={'error': str(e)}, validation_passed=False)
        logger.log(f"Error in rollback endpoint: {str(e)}", level="ERROR")
        return jsonify({'error': str(e)}), 500

