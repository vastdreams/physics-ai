# api/v1/
"""
State Graph API endpoints.
"""

from flask import request, jsonify
from api.v1 import api_v1
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from utilities.state_graph import StateGraph, State, Transition, TransitionType
from utilities.cot_logging import ChainOfThoughtLogger, LogLevel
from loggers.system_logger import SystemLogger

logger = SystemLogger()
state_graph = StateGraph()


@api_v1.route('/state-graph/states', methods=['POST'])
def add_state():
    """
    Add a state to the graph.
    
    Request body:
    {
        "state_id": "state1",
        "name": "State Name",
        "properties": {...},
        "constraints": [...]
    }
    """
    cot = ChainOfThoughtLogger()
    step_id = cot.start_step(action="API_ADD_STATE", level=LogLevel.INFO)
    
    try:
        data = request.get_json()
        
        if not data or 'state_id' not in data:
            cot.end_step(step_id, output_data={'error': 'state_id required'}, validation_passed=False)
            return jsonify({'success': False, 'error': 'state_id required'}), 400
        
        state = State(
            state_id=data['state_id'],
            name=data.get('name', data['state_id']),
            properties=data.get('properties', {}),
            constraints=data.get('constraints', [])
        )
        
        state_graph.add_state(state)
        
        cot.end_step(step_id, output_data={'state_id': data['state_id']}, validation_passed=True)
        
        return jsonify({'success': True, 'state_id': data['state_id']}), 200
    
    except Exception as e:
        cot.end_step(step_id, output_data={'error': str(e)}, validation_passed=False)
        logger.log(f"Error in add_state endpoint: {str(e)}", level="ERROR")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_v1.route('/state-graph/paths', methods=['POST'])
def find_paths():
    """
    Find paths between states.
    
    Request body:
    {
        "from_state": "state1",
        "to_state": "state2",
        "max_depth": 10,
        "context": {...}
    }
    """
    cot = ChainOfThoughtLogger()
    step_id = cot.start_step(action="API_FIND_PATHS", level=LogLevel.INFO)
    
    try:
        data = request.get_json()
        
        if not data or 'from_state' not in data or 'to_state' not in data:
            cot.end_step(step_id, output_data={'error': 'from_state and to_state required'}, validation_passed=False)
            return jsonify({'success': False, 'error': 'from_state and to_state required'}), 400
        
        paths = state_graph.find_paths(
            from_state=data['from_state'],
            to_state=data['to_state'],
            max_depth=data.get('max_depth', 10),
            context=data.get('context')
        )
        
        cot.end_step(step_id, output_data={'paths_count': len(paths)}, validation_passed=True)
        
        return jsonify({'paths': paths}), 200
    
    except Exception as e:
        cot.end_step(step_id, output_data={'error': str(e)}, validation_passed=False)
        logger.log(f"Error in find_paths endpoint: {str(e)}", level="ERROR")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_v1.route('/state-graph/scenarios', methods=['POST'])
def explore_scenarios():
    """
    Explore scenarios.
    
    Request body:
    {
        "initial_state": "state1",
        "target_properties": {...},
        "max_steps": 10,
        "context": {...}
    }
    """
    cot = ChainOfThoughtLogger()
    step_id = cot.start_step(action="API_EXPLORE_SCENARIOS", level=LogLevel.INFO)
    
    try:
        data = request.get_json()
        
        if not data or 'initial_state' not in data:
            cot.end_step(step_id, output_data={'error': 'initial_state required'}, validation_passed=False)
            return jsonify({'success': False, 'error': 'initial_state required'}), 400
        
        scenarios = state_graph.explore_scenarios(
            initial_state=data['initial_state'],
            target_properties=data.get('target_properties', {}),
            max_steps=data.get('max_steps', 10),
            context=data.get('context')
        )
        
        cot.end_step(step_id, output_data={'scenarios_count': len(scenarios)}, validation_passed=True)
        
        return jsonify({'scenarios': scenarios}), 200
    
    except Exception as e:
        cot.end_step(step_id, output_data={'error': str(e)}, validation_passed=False)
        logger.log(f"Error in explore_scenarios endpoint: {str(e)}", level="ERROR")
        return jsonify({'success': False, 'error': str(e)}), 500

