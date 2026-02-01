# api/v1/
"""
Rule management endpoints.
"""

from flask import request, jsonify
from api.v1 import api_v1
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from rules.enhanced_rule_engine import EnhancedRuleEngine, EnhancedRule, RulePriority
from utilities.cot_logging import ChainOfThoughtLogger, LogLevel
from loggers.system_logger import SystemLogger

logger = SystemLogger()
rule_engine = EnhancedRuleEngine()


@api_v1.route('/rules', methods=['GET'])
def list_rules():
    """List all rules."""
    cot = ChainOfThoughtLogger()
    step_id = cot.start_step(
        action="API_LIST_RULES",
        level=LogLevel.INFO
    )
    
    try:
        rules = rule_engine.list_rules()
        
        cot.end_step(step_id, output_data={'rule_count': len(rules)}, validation_passed=True)
        
        return jsonify({'rules': rules}), 200
    
    except Exception as e:
        cot.end_step(step_id, output_data={'error': str(e)}, validation_passed=False)
        logger.log(f"Error in list_rules endpoint: {str(e)}", level="ERROR")
        return jsonify({'error': str(e)}), 500


@api_v1.route('/rules', methods=['POST'])
def add_rule():
    """
    Add a new rule.
    
    Request body:
    {
        "name": "rule_name",
        "condition": "lambda function or description",
        "action": "lambda function or description",
        "physics_constraints": ["conservation_energy", ...],
        "priority": "MEDIUM",
        "description": "...",
        "tags": ["tag1", "tag2"]
    }
    """
    cot = ChainOfThoughtLogger()
    step_id = cot.start_step(
        action="API_ADD_RULE",
        level=LogLevel.INFO
    )
    
    try:
        data = request.get_json()
        
        if not data or 'name' not in data:
            cot.end_step(step_id, output_data={'error': 'Rule name required'}, validation_passed=False)
            return jsonify({'error': 'Rule name required'}), 400
        
        # Create rule (simplified - would need proper function deserialization)
        # For now, use placeholder functions
        def condition_func(ctx):
            return True
        
        def action_func(ctx):
            return {'result': 'placeholder'}
        
        rule = EnhancedRule(
            name=data['name'],
            condition=condition_func,
            action=action_func,
            physics_constraints=data.get('physics_constraints', []),
            priority=RulePriority[data.get('priority', 'MEDIUM')],
            description=data.get('description', ''),
            tags=set(data.get('tags', []))
        )
        
        success = rule_engine.add_enhanced_rule(rule)
        
        if success:
            cot.end_step(step_id, output_data={'rule_name': data['name']}, validation_passed=True)
            return jsonify({'success': True, 'rule': rule.to_dict()}), 201
        else:
            cot.end_step(step_id, output_data={'error': 'Failed to add rule'}, validation_passed=False)
            return jsonify({'error': 'Failed to add rule'}), 400
    
    except Exception as e:
        cot.end_step(step_id, output_data={'error': str(e)}, validation_passed=False)
        logger.log(f"Error in add_rule endpoint: {str(e)}", level="ERROR")
        return jsonify({'error': str(e)}), 500


@api_v1.route('/rules/<rule_name>', methods=['GET'])
def get_rule(rule_name):
    """Get a specific rule."""
    cot = ChainOfThoughtLogger()
    step_id = cot.start_step(
        action="API_GET_RULE",
        input_data={'rule_name': rule_name},
        level=LogLevel.INFO
    )
    
    try:
        rules = rule_engine.list_rules()
        rule = next((r for r in rules if r['name'] == rule_name), None)
        
        if not rule:
            cot.end_step(step_id, output_data={'error': 'Rule not found'}, validation_passed=False)
            return jsonify({'error': 'Rule not found'}), 404
        
        cot.end_step(step_id, output_data={'rule_name': rule_name}, validation_passed=True)
        
        return jsonify(rule), 200
    
    except Exception as e:
        cot.end_step(step_id, output_data={'error': str(e)}, validation_passed=False)
        logger.log(f"Error in get_rule endpoint: {str(e)}", level="ERROR")
        return jsonify({'error': str(e)}), 500


@api_v1.route('/rules/execute', methods=['POST'])
def execute_rules():
    """
    Execute rules on a context.
    
    Request body:
    {
        "context": {...},
        "validate_physics": true,
        "use_cot": true
    }
    """
    cot = ChainOfThoughtLogger()
    step_id = cot.start_step(
        action="API_EXECUTE_RULES",
        level=LogLevel.INFO
    )
    
    try:
        data = request.get_json()
        
        if not data or 'context' not in data:
            cot.end_step(step_id, output_data={'error': 'Context required'}, validation_passed=False)
            return jsonify({'error': 'Context required'}), 400
        
        context = data['context']
        validate_physics = data.get('validate_physics', True)
        use_cot = data.get('use_cot', True)
        
        results = rule_engine.execute_enhanced(
            context=context,
            validate_physics=validate_physics,
            use_cot=use_cot
        )
        
        cot.end_step(step_id, output_data={'results_count': len(results)}, validation_passed=True)
        
        return jsonify({'results': results}), 200
    
    except Exception as e:
        cot.end_step(step_id, output_data={'error': str(e)}, validation_passed=False)
        logger.log(f"Error in execute_rules endpoint: {str(e)}", level="ERROR")
        return jsonify({'error': str(e)}), 500


@api_v1.route('/rules/statistics', methods=['GET'])
def rule_statistics():
    """Get rule statistics."""
    cot = ChainOfThoughtLogger()
    step_id = cot.start_step(
        action="API_RULE_STATISTICS",
        level=LogLevel.INFO
    )
    
    try:
        stats = rule_engine.get_rule_statistics()
        
        cot.end_step(step_id, output_data={'statistics': stats}, validation_passed=True)
        
        return jsonify(stats), 200
    
    except Exception as e:
        cot.end_step(step_id, output_data={'error': str(e)}, validation_passed=False)
        logger.log(f"Error in rule_statistics endpoint: {str(e)}", level="ERROR")
        return jsonify({'error': str(e)}), 500

