# ai/brain_modal/
"""
Expert Feedback System.

Inspired by DREAM architecture - Brain LLM trained on expert thought processes.

First Principle Analysis:
- Feedback: Review CoT → Identify gaps → Provide expert feedback
- Expert model: Trained on surgeon/researcher thought processes
- Mathematical foundation: Pattern recognition, gap analysis, feedback loops
- Architecture: Feedback system with expert knowledge integration
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from loggers.system_logger import SystemLogger
from utilities.cot_logging import ChainOfThoughtLogger, LogLevel
from ai.llm_integration import LLMIntegration


@dataclass
class ExpertFeedback:
    """Represents expert feedback."""
    feedback_id: str
    target_id: str  # CoT step ID, equation ID, etc.
    feedback_type: str  # 'gap', 'inconsistency', 'improvement', 'validation'
    message: str
    severity: str = 'medium'  # 'low', 'medium', 'high', 'critical'
    suggestions: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ExpertFeedbackSystem:
    """
    Expert feedback system.
    
    Features:
    - CoT log review
    - Gap identification
    - Inconsistency detection
    - Improvement suggestions
    - Expert-level validation
    """
    
    def __init__(self, llm: Optional[LLMIntegration] = None):
        """
        Initialize expert feedback system.
        
        Args:
            llm: Optional LLM integration instance
        """
        self.logger = SystemLogger()
        self.llm = llm or LLMIntegration()
        self.feedback_history: List[ExpertFeedback] = []
        
        self.logger.log("ExpertFeedbackSystem initialized", level="INFO")
    
    def review_cot_log(self, cot_log: Dict[str, Any]) -> List[ExpertFeedback]:
        """
        Review chain-of-thought log and provide feedback.
        
        Args:
            cot_log: CoT log dictionary
            
        Returns:
            List of expert feedback
        """
        cot = ChainOfThoughtLogger()
        step_id = cot.start_step(
            action="EXPERT_REVIEW_COT",
            level=LogLevel.DECISION
        )
        
        try:
            feedback_list = []
            
            # Analyze CoT structure
            gaps = self._identify_gaps(cot_log)
            inconsistencies = self._identify_inconsistencies(cot_log)
            improvements = self._suggest_improvements(cot_log)
            
            # Create feedback for gaps
            for gap in gaps:
                feedback = ExpertFeedback(
                    feedback_id=f"fb_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
                    target_id=gap.get('target_id', 'unknown'),
                    feedback_type='gap',
                    message=gap.get('message', ''),
                    severity=gap.get('severity', 'medium'),
                    suggestions=gap.get('suggestions', [])
                )
                feedback_list.append(feedback)
            
            # Create feedback for inconsistencies
            for inconsistency in inconsistencies:
                feedback = ExpertFeedback(
                    feedback_id=f"fb_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
                    target_id=inconsistency.get('target_id', 'unknown'),
                    feedback_type='inconsistency',
                    message=inconsistency.get('message', ''),
                    severity=inconsistency.get('severity', 'high'),
                    suggestions=inconsistency.get('suggestions', [])
                )
                feedback_list.append(feedback)
            
            # Create feedback for improvements
            for improvement in improvements:
                feedback = ExpertFeedback(
                    feedback_id=f"fb_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
                    target_id=improvement.get('target_id', 'unknown'),
                    feedback_type='improvement',
                    message=improvement.get('message', ''),
                    severity=improvement.get('severity', 'low'),
                    suggestions=improvement.get('suggestions', [])
                )
                feedback_list.append(feedback)
            
            # Store feedback
            self.feedback_history.extend(feedback_list)
            
            cot.end_step(
                step_id,
                output_data={'num_feedback': len(feedback_list)},
                validation_passed=True
            )
            
            self.logger.log(f"Expert review completed: {len(feedback_list)} feedback items", level="INFO")
            
            return feedback_list
        
        except Exception as e:
            cot.end_step(step_id, output_data={'error': str(e)}, validation_passed=False)
            self.logger.log(f"Error in expert review: {str(e)}", level="ERROR")
            return []
    
    def _identify_gaps(self, cot_log: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify gaps in CoT log."""
        gaps = []
        
        # Check for missing validation steps
        steps = cot_log.get('steps', {})
        for step_id, step in steps.items():
            if not step.get('validation_passed') and 'validation' not in step.get('action', '').lower():
                gaps.append({
                    'target_id': step_id,
                    'message': f"Step {step_id} lacks validation",
                    'severity': 'medium',
                    'suggestions': ['Add validation step', 'Check physics constraints']
                })
        
        return gaps
    
    def _identify_inconsistencies(self, cot_log: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify inconsistencies in CoT log."""
        inconsistencies = []
        
        # Check for contradictory outputs
        steps = cot_log.get('steps', {})
        outputs = {}
        
        for step_id, step in steps.items():
            output = step.get('output_data', {})
            for key, value in output.items():
                if key in outputs and outputs[key] != value:
                    inconsistencies.append({
                        'target_id': step_id,
                        'message': f"Inconsistent value for {key}: {outputs[key]} vs {value}",
                        'severity': 'high',
                        'suggestions': ['Review previous steps', 'Check data consistency']
                    })
                outputs[key] = value
        
        return inconsistencies
    
    def _suggest_improvements(self, cot_log: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Suggest improvements to CoT log."""
        improvements = []
        
        # Check for optimization opportunities
        steps = cot_log.get('steps', {})
        if len(steps) > 10:
            improvements.append({
                'target_id': 'overall',
                'message': 'CoT log has many steps - consider consolidation',
                'severity': 'low',
                'suggestions': ['Group related steps', 'Use hierarchical structure']
            })
        
        return improvements
    
    def get_feedback_history(self) -> List[Dict[str, Any]]:
        """Get feedback history."""
        return [
            {
                'feedback_id': fb.feedback_id,
                'target_id': fb.target_id,
                'feedback_type': fb.feedback_type,
                'message': fb.message,
                'severity': fb.severity,
                'suggestions': fb.suggestions,
                'created_at': fb.created_at.isoformat()
            }
            for fb in self.feedback_history
        ]

