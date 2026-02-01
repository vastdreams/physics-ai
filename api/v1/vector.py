# api/v1/
"""
VECTOR Framework API endpoints.
"""

from flask import request, jsonify
from api.v1 import api_v1
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from utilities.vector_framework import VECTORFramework, DeltaFactor
from utilities.cot_logging import ChainOfThoughtLogger, LogLevel
from loggers.system_logger import SystemLogger

logger = SystemLogger()
vector_framework = VECTORFramework()


@api_v1.route('/vector/delta-factors', methods=['POST'])
def add_delta_factor():
    """
    Add a delta factor.
    
    Request body:
    {
        "name": "energy",
        "value": 1.0,
        "variance": 0.1,
        "confidence": 1.0
    }
    """
    cot = ChainOfThoughtLogger()
    step_id = cot.start_step(
        action="API_ADD_DELTA_FACTOR",
        level=LogLevel.INFO
    )
    
    try:
        data = request.get_json()
        
        if not data or 'name' not in data or 'value' not in data:
            cot.end_step(step_id, output_data={'error': 'name and value required'}, validation_passed=False)
            return jsonify({'error': 'name and value required'}), 400
        
        delta = DeltaFactor(
            name=data['name'],
            value=data['value'],
            variance=data.get('variance', 0.0),
            confidence=data.get('confidence', 1.0),
            metadata=data.get('metadata', {})
        )
        
        vector_framework.add_delta_factor(delta)
        
        cot.end_step(step_id, output_data={'delta_name': data['name']}, validation_passed=True)
        
        return jsonify({'success': True, 'delta': {'name': delta.name, 'value': delta.value}}), 200
    
    except Exception as e:
        cot.end_step(step_id, output_data={'error': str(e)}, validation_passed=False)
        logger.log(f"Error in add_delta_factor endpoint: {str(e)}", level="ERROR")
        return jsonify({'error': str(e)}), 500


@api_v1.route('/vector/throttle', methods=['POST'])
def throttle_variance():
    """Throttle variance if needed."""
    cot = ChainOfThoughtLogger()
    step_id = cot.start_step(
        action="API_THROTTLE_VARIANCE",
        level=LogLevel.INFO
    )
    
    try:
        throttled = vector_framework.throttle_variance()
        v_obs = vector_framework.compute_observed_variance()
        
        cot.end_step(
            step_id,
            output_data={'throttled': len(throttled) > 0, 'v_obs': v_obs},
            validation_passed=True
        )
        
        return jsonify({
            'throttled': throttled,
            'observed_variance': v_obs,
            'max_variance': vector_framework.v_max
        }), 200
    
    except Exception as e:
        cot.end_step(step_id, output_data={'error': str(e)}, validation_passed=False)
        logger.log(f"Error in throttle_variance endpoint: {str(e)}", level="ERROR")
        return jsonify({'error': str(e)}), 500


@api_v1.route('/vector/bayesian-update', methods=['POST'])
def bayesian_update():
    """
    Perform Bayesian parameter update.
    
    Request body:
    {
        "parameter_name": "energy",
        "new_data_value": 1.05,
        "new_data_variance": 0.05
    }
    """
    cot = ChainOfThoughtLogger()
    step_id = cot.start_step(
        action="API_BAYESIAN_UPDATE",
        level=LogLevel.INFO
    )
    
    try:
        data = request.get_json()
        
        if not data or 'parameter_name' not in data:
            cot.end_step(step_id, output_data={'error': 'parameter_name required'}, validation_passed=False)
            return jsonify({'error': 'parameter_name required'}), 400
        
        vector_framework.update_delta_with_bayesian(
            data['parameter_name'],
            data.get('new_data_value', 0.0),
            data.get('new_data_variance', 0.1)
        )
        
        cot.end_step(step_id, output_data={'parameter_name': data['parameter_name']}, validation_passed=True)
        
        return jsonify({'success': True}), 200
    
    except Exception as e:
        cot.end_step(step_id, output_data={'error': str(e)}, validation_passed=False)
        logger.log(f"Error in bayesian_update endpoint: {str(e)}", level="ERROR")
        return jsonify({'error': str(e)}), 500


@api_v1.route('/vector/overlay-validation', methods=['POST'])
def overlay_validation():
    """
    Perform overlay validation.
    
    Request body:
    {
        "simple_output": {...},
        "complex_output": {...},
        "epsilon_limit": 0.1
    }
    """
    cot = ChainOfThoughtLogger()
    step_id = cot.start_step(
        action="API_OVERLAY_VALIDATION",
        level=LogLevel.INFO
    )
    
    try:
        data = request.get_json()
        
        if not data or 'simple_output' not in data or 'complex_output' not in data:
            cot.end_step(step_id, output_data={'error': 'simple_output and complex_output required'}, validation_passed=False)
            return jsonify({'error': 'simple_output and complex_output required'}), 400
        
        is_valid, deviation = vector_framework.overlay_validation(
            data['simple_output'],
            data['complex_output'],
            data.get('epsilon_limit', 0.1)
        )
        
        cot.end_step(
            step_id,
            output_data={'is_valid': is_valid, 'deviation': deviation},
            validation_passed=is_valid
        )
        
        return jsonify({
            'is_valid': is_valid,
            'deviation': deviation,
            'epsilon_limit': data.get('epsilon_limit', 0.1)
        }), 200
    
    except Exception as e:
        cot.end_step(step_id, output_data={'error': str(e)}, validation_passed=False)
        logger.log(f"Error in overlay_validation endpoint: {str(e)}", level="ERROR")
        return jsonify({'error': str(e)}), 500


@api_v1.route('/vector/statistics', methods=['GET'])
def vector_statistics():
    """Get VECTOR framework statistics."""
    cot = ChainOfThoughtLogger()
    step_id = cot.start_step(
        action="API_VECTOR_STATISTICS",
        level=LogLevel.INFO
    )
    
    try:
        stats = vector_framework.get_statistics()
        
        cot.end_step(step_id, output_data={'statistics': stats}, validation_passed=True)
        
        return jsonify(stats), 200
    
    except Exception as e:
        cot.end_step(step_id, output_data={'error': str(e)}, validation_passed=False)
        logger.log(f"Error in vector_statistics endpoint: {str(e)}", level="ERROR")
        return jsonify({'error': str(e)}), 500

