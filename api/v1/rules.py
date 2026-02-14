"""Rule management endpoints."""

from flask import jsonify, request

from api.v1 import api_v1
from loggers.system_logger import SystemLogger
from rules.enhanced_rule_engine import EnhancedRule, EnhancedRuleEngine, RulePriority
from utilities.cot_logging import ChainOfThoughtLogger, LogLevel

_logger = SystemLogger()
rule_engine = EnhancedRuleEngine()


@api_v1.route('/rules', methods=['GET'])
def list_rules():
    """List all rules."""
    cot = ChainOfThoughtLogger()
    step_id = cot.start_step(action="API_LIST_RULES", level=LogLevel.INFO)

    try:
        rules = rule_engine.list_rules()
        cot.end_step(step_id, output_data={'rule_count': len(rules)}, validation_passed=True)
        return jsonify({'rules': rules}), 200

    except Exception as e:
        cot.end_step(step_id, output_data={'error': str(e)}, validation_passed=False)
        _logger.log(f"Error in list_rules endpoint: {str(e)}", level="ERROR")
        return jsonify({'success': False, 'error': str(e)}), 500


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
    step_id = cot.start_step(action="API_ADD_RULE", level=LogLevel.INFO)

    try:
        data = request.get_json()

        if not data or 'name' not in data:
            cot.end_step(step_id, output_data={'error': 'Rule name required'}, validation_passed=False)
            return jsonify({'success': False, 'error': 'Rule name required'}), 400

        # Build condition / action functions from the provided strings.
        # The string is stored alongside a closure that evaluates it
        # with the safe expression evaluator from core.engine.
        condition_str = data.get('condition', 'True')
        action_str = data.get('action', "{'result': 'applied'}")

        def _make_condition(expr):
            def condition_func(ctx):
                try:
                    from core.engine import NeurosymbolicEngine
                    return bool(NeurosymbolicEngine._safe_eval(expr, ctx))
                except Exception:
                    return True
            return condition_func

        def _make_action(expr):
            def action_func(ctx):
                try:
                    from core.engine import NeurosymbolicEngine
                    return NeurosymbolicEngine._safe_eval(expr, ctx)
                except Exception:
                    return {'result': 'executed', 'expression': expr}
            return action_func

        condition_func = _make_condition(condition_str)
        action_func = _make_action(action_str)

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
            return jsonify({'success': False, 'error': 'Failed to add rule'}), 400

    except Exception as e:
        cot.end_step(step_id, output_data={'error': str(e)}, validation_passed=False)
        _logger.log(f"Error in add_rule endpoint: {str(e)}", level="ERROR")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_v1.route('/rules/<rule_name>', methods=['DELETE'])
def delete_rule(rule_name: str):
    """Delete a rule by name."""
    cot = ChainOfThoughtLogger()
    step_id = cot.start_step(action="API_DELETE_RULE", input_data={'rule_name': rule_name}, level=LogLevel.INFO)

    try:
        removed = rule_engine.remove_rule(rule_name) if hasattr(rule_engine, 'remove_rule') else False
        if not removed:
            # Fallback: try removing from internal list
            before = len(rule_engine.rules) if hasattr(rule_engine, 'rules') else 0
            if hasattr(rule_engine, 'rules'):
                rule_engine.rules = [r for r in rule_engine.rules if r.get('name') != rule_name and getattr(r, 'name', None) != rule_name]
                removed = len(rule_engine.rules) < before

        if removed:
            cot.end_step(step_id, output_data={'deleted': rule_name}, validation_passed=True)
            return jsonify({'success': True, 'deleted': rule_name}), 200
        else:
            cot.end_step(step_id, output_data={'error': 'Rule not found'}, validation_passed=False)
            return jsonify({'success': False, 'error': 'Rule not found'}), 404

    except Exception as e:
        cot.end_step(step_id, output_data={'error': str(e)}, validation_passed=False)
        _logger.log(f"Error in delete_rule endpoint: {str(e)}", level="ERROR")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_v1.route('/rules/<rule_name>', methods=['GET'])
def get_rule(rule_name: str):
    """Get a specific rule."""
    cot = ChainOfThoughtLogger()
    step_id = cot.start_step(action="API_GET_RULE", input_data={'rule_name': rule_name}, level=LogLevel.INFO)

    try:
        rules = rule_engine.list_rules()
        rule = next((r for r in rules if r['name'] == rule_name), None)

        if not rule:
            cot.end_step(step_id, output_data={'error': 'Rule not found'}, validation_passed=False)
            return jsonify({'success': False, 'error': 'Rule not found'}), 404

        cot.end_step(step_id, output_data={'rule_name': rule_name}, validation_passed=True)
        return jsonify(rule), 200

    except Exception as e:
        cot.end_step(step_id, output_data={'error': str(e)}, validation_passed=False)
        _logger.log(f"Error in get_rule endpoint: {str(e)}", level="ERROR")
        return jsonify({'success': False, 'error': str(e)}), 500


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
    step_id = cot.start_step(action="API_EXECUTE_RULES", level=LogLevel.INFO)

    try:
        data = request.get_json()

        if not data or 'context' not in data:
            cot.end_step(step_id, output_data={'error': 'Context required'}, validation_passed=False)
            return jsonify({'success': False, 'error': 'Context required'}), 400

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
        _logger.log(f"Error in execute_rules endpoint: {str(e)}", level="ERROR")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_v1.route('/rules/statistics', methods=['GET'])
def rule_statistics():
    """Get rule statistics."""
    cot = ChainOfThoughtLogger()
    step_id = cot.start_step(action="API_RULE_STATISTICS", level=LogLevel.INFO)

    try:
        stats = rule_engine.get_rule_statistics()
        cot.end_step(step_id, output_data={'statistics': stats}, validation_passed=True)
        return jsonify(stats), 200

    except Exception as e:
        cot.end_step(step_id, output_data={'error': str(e)}, validation_passed=False)
        _logger.log(f"Error in rule_statistics endpoint: {str(e)}", level="ERROR")
        return jsonify({'success': False, 'error': str(e)}), 500
