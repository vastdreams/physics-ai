# api/v1/
"""
Simulation endpoints.
"""

from flask import request, jsonify
from api.v1 import api_v1
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from physics.integration.physics_integrator import PhysicsIntegrator
from utilities.enhanced_registry import EnhancedRegistry
from utilities.cot_logging import ChainOfThoughtLogger, LogLevel
from loggers.system_logger import SystemLogger

logger = SystemLogger()
integrator = PhysicsIntegrator()
registry = EnhancedRegistry()


@api_v1.route('/simulate', methods=['POST'])
def simulate():
    """
    Run physics simulation.
    
    Request body:
    {
        "scenario": {...},
        "initial_conditions": {...},
        "time_span": [t_start, t_end],
        "num_steps": 100
    }
    """
    cot = ChainOfThoughtLogger()
    step_id = cot.start_step(
        action="API_SIMULATE",
        input_data={'endpoint': '/api/v1/simulate'},
        level=LogLevel.INFO
    )
    
    try:
        data = request.get_json()
        
        if not data:
            cot.end_step(step_id, output_data={'error': 'No data provided'}, validation_passed=False)
            return jsonify({'error': 'No data provided'}), 400
        
        scenario = data.get('scenario', {})
        initial_conditions = data.get('initial_conditions', {})
        time_span = data.get('time_span', [0.0, 1.0])
        num_steps = data.get('num_steps', 100)
        
        # Run simulation
        result = integrator.simulate(
            scenario=scenario,
            initial_conditions=initial_conditions,
            time_span=tuple(time_span),
            num_steps=num_steps
        )
        
        cot.end_step(step_id, output_data={'success': True, 'result_keys': list(result.keys())}, validation_passed=True)
        
        return jsonify({
            'success': True,
            'result': result
        }), 200
    
    except Exception as e:
        cot.end_step(step_id, output_data={'error': str(e)}, validation_passed=False)
        logger.log(f"Error in simulate endpoint: {str(e)}", level="ERROR")
        return jsonify({'error': str(e)}), 500

