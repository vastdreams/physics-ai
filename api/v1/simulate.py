"""Simulation endpoints."""

from flask import jsonify, request

from api.v1 import api_v1
from loggers.system_logger import SystemLogger
from physics.integration.physics_integrator import PhysicsIntegrator
from utilities.cot_logging import ChainOfThoughtLogger, LogLevel
from utilities.enhanced_registry import EnhancedRegistry

_logger = SystemLogger()
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
    step_id = cot.start_step(action="API_SIMULATE", input_data={'endpoint': '/api/v1/simulate'}, level=LogLevel.INFO)

    try:
        data = request.get_json()

        if not data:
            cot.end_step(step_id, output_data={'error': 'No data provided'}, validation_passed=False)
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        # Accept BOTH frontend format (model/parameters/t_end/dt) and
        # canonical backend format (scenario/time_span/num_steps)
        if 'model' in data and 'scenario' not in data:
            # Frontend format — translate
            scenario = {
                'type': data.get('model', 'generic'),
                'parameters': data.get('parameters', {}),
                'method': data.get('method', 'rk4'),
            }
            initial_conditions = data.get('initial_conditions', {})
            t_end = float(data.get('t_end', 10.0))
            dt = float(data.get('dt', 0.01))
            time_span = [0.0, t_end]
            num_steps = max(10, int(t_end / dt))
        else:
            scenario = data.get('scenario', {})
            initial_conditions = data.get('initial_conditions', {})
            time_span = data.get('time_span', [0.0, 1.0])
            num_steps = data.get('num_steps', 100)

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
        _logger.log(f"Error in simulate endpoint: {str(e)}", level="ERROR")
        return jsonify({'success': False, 'error': str(e)}), 500
