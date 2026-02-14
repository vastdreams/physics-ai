# api/v1/
"""
Brain Modal API endpoints.
"""

from flask import request, jsonify
from api.v1 import api_v1
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from ai.brain_modal import ExpertFeedbackSystem, AuditSystem, RecursiveBrain, FeedbackProcessor
from utilities.cot_logging import ChainOfThoughtLogger, LogLevel
from loggers.system_logger import SystemLogger

logger = SystemLogger()

# Global instances (in production, would use proper dependency injection)
expert_feedback = ExpertFeedbackSystem()
audit_system = AuditSystem()
recursive_brain = RecursiveBrain(expert_feedback, audit_system)
feedback_processor = FeedbackProcessor(expert_feedback)


@api_v1.route('/brain/feedback', methods=['POST'])
def submit_feedback():
    """
    Submit feedback for review.
    
    Request body:
    {
        "target_id": "cot_step_123",
        "feedback_type": "gap|inconsistency|improvement",
        "message": "Feedback message",
        "severity": "low|medium|high|critical",
        "suggestions": ["suggestion1", "suggestion2"]
    }
    """
    cot = ChainOfThoughtLogger()
    step_id = cot.start_step(action="API_SUBMIT_FEEDBACK", level=LogLevel.INFO)
    
    try:
        data = request.get_json()
        
        if not data or 'target_id' not in data or 'message' not in data:
            cot.end_step(step_id, output_data={'error': 'target_id and message required'}, validation_passed=False)
            return jsonify({'success': False, 'error': 'target_id and message required'}), 400
        
        from ai.brain_modal.expert_feedback import ExpertFeedback
        
        feedback = ExpertFeedback(
            feedback_id="",  # Auto-generated
            target_id=data['target_id'],
            feedback_type=data.get('feedback_type', 'improvement'),
            message=data['message'],
            severity=data.get('severity', 'medium'),
            suggestions=data.get('suggestions', [])
        )
        
        # Process feedback
        result = feedback_processor.process_feedback(feedback)
        
        cot.end_step(step_id, output_data={'feedback_id': feedback.feedback_id}, validation_passed=True)
        
        return jsonify(result), 201
    
    except Exception as e:
        cot.end_step(step_id, output_data={'error': str(e)}, validation_passed=False)
        logger.log(f"Error in submit_feedback: {str(e)}", level="ERROR")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_v1.route('/brain/audit', methods=['POST'])
def perform_audit():
    """
    Perform audit.
    
    Request body:
    {
        "audit_type": "performance|consistency|safety|compliance",
        "context": {...}
    }
    """
    cot = ChainOfThoughtLogger()
    step_id = cot.start_step(action="API_PERFORM_AUDIT", level=LogLevel.INFO)
    
    try:
        data = request.get_json()
        
        if not data or 'audit_type' not in data:
            cot.end_step(step_id, output_data={'error': 'audit_type required'}, validation_passed=False)
            return jsonify({'success': False, 'error': 'audit_type required'}), 400
        
        result = audit_system.perform_audit(
            audit_type=data['audit_type'],
            context=data.get('context')
        )
        
        cot.end_step(step_id, output_data={'audit_id': result.audit_id}, validation_passed=True)
        
        return jsonify({
            'audit_id': result.audit_id,
            'audit_type': result.audit_type,
            'findings': result.findings,
            'recommendations': result.recommendations,
            'severity': result.severity
        }), 200
    
    except Exception as e:
        cot.end_step(step_id, output_data={'error': str(e)}, validation_passed=False)
        logger.log(f"Error in perform_audit: {str(e)}", level="ERROR")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_v1.route('/brain/review', methods=['POST'])
def request_brain_review():
    """
    Request brain review.
    
    Request body:
    {
        "target": "target_id",
        "target_data": {...},
        "max_depth": 3
    }
    """
    cot = ChainOfThoughtLogger()
    step_id = cot.start_step(action="API_BRAIN_REVIEW", level=LogLevel.DECISION)
    
    try:
        data = request.get_json()
        
        if not data or 'target' not in data or 'target_data' not in data:
            cot.end_step(step_id, output_data={'error': 'target and target_data required'}, validation_passed=False)
            return jsonify({'success': False, 'error': 'target and target_data required'}), 400
        
        review = recursive_brain.recursive_review(
            target=data['target'],
            target_data=data['target_data'],
            depth=0
        )
        
        cot.end_step(step_id, output_data={'review_id': review.review_id}, validation_passed=True)
        
        return jsonify({
            'review_id': review.review_id,
            'target': review.target,
            'depth': review.depth,
            'feedback': review.feedback,
            'refinements': review.refinements
        }), 200
    
    except Exception as e:
        cot.end_step(step_id, output_data={'error': str(e)}, validation_passed=False)
        logger.log(f"Error in request_brain_review: {str(e)}", level="ERROR")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_v1.route('/brain/feedback-history', methods=['GET'])
def get_feedback_history():
    """Get feedback history."""
    cot = ChainOfThoughtLogger()
    step_id = cot.start_step(action="API_GET_FEEDBACK_HISTORY", level=LogLevel.INFO)
    
    try:
        history = expert_feedback.get_feedback_history()
        
        cot.end_step(step_id, output_data={'count': len(history)}, validation_passed=True)
        
        return jsonify({'feedback_history': history}), 200
    
    except Exception as e:
        cot.end_step(step_id, output_data={'error': str(e)}, validation_passed=False)
        logger.log(f"Error in get_feedback_history: {str(e)}", level="ERROR")
        return jsonify({'success': False, 'error': str(e)}), 500

