"""
PATH: ai/llm/router.py
PURPOSE: Multi-layer agent router implementing DREAM pattern

ARCHITECTURE:
┌────────────────────────────────────────────────────────────────────┐
│                         Request Router                             │
│                                                                    │
│  Input -> Layer A (Gate) -> [Pass/Escalate] -> Layer B -> Layer C │
│                   |                                                │
│                   v                                                │
│           Quick Response (if simple)                               │
└────────────────────────────────────────────────────────────────────┘

WHY: Most requests can be handled by cheap Layer A, reducing GPU time
     and costs. Only complex tasks escalate to higher layers.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple
import json
import re

from .config import ModelTier, get_config, get_tier_for_task, TASK_ROUTING
from .provider import LLMResponse, Message


class EscalationReason(Enum):
    """Reasons for escalating to a higher tier."""
    COMPLEXITY = "complexity"           # Task too complex for current tier
    CONFIDENCE = "confidence"           # Low confidence in response
    TOOL_REQUIRED = "tool_required"     # Need tool calling capability
    CONTEXT_SIZE = "context_size"       # Context too large
    EXPLICIT = "explicit"               # User/system requested higher tier
    ERROR = "error"                     # Error at current tier
    QUALITY = "quality"                 # Quality check failed


@dataclass
class RouteDecision:
    """Decision about how to route a request."""
    tier: ModelTier
    task_type: str
    confidence: float
    
    # Escalation info
    escalated_from: Optional[ModelTier] = None
    escalation_reason: Optional[EscalationReason] = None
    
    # Metadata
    context_tokens: int = 0
    estimated_cost: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "tier": self.tier.value,
            "task_type": self.task_type,
            "confidence": self.confidence,
            "escalated_from": self.escalated_from.value if self.escalated_from else None,
            "escalation_reason": self.escalation_reason.value if self.escalation_reason else None,
            "context_tokens": self.context_tokens,
            "estimated_cost": self.estimated_cost,
        }


class AgentRouter:
    """
    Routes requests to appropriate model tier.
    
    Implements the DREAM 3-layer pattern:
    - Layer A: Gatekeeper (Phi 3.5 Mini) - routing, validation, quick checks
    - Layer B: Workhorse (Qwen 2.5 7B) - extraction, tool calling, analysis
    - Layer C: Orchestrator (Ministral 8B) - complex reasoning, orchestration
    """
    
    # Keywords that suggest task complexity
    COMPLEXITY_KEYWORDS = {
        # Layer A keywords (simple)
        "simple": ["check", "validate", "is", "does", "yes", "no", "classify", "route"],
        # Layer B keywords (moderate)  
        "moderate": ["extract", "analyze", "summarize", "map", "transform", "generate"],
        # Layer C keywords (complex)
        "complex": ["explain", "reason", "why", "plan", "orchestrate", "synthesize", "compare"],
    }
    
    # Physics-specific routing hints
    PHYSICS_ROUTING = {
        # Quick lookups -> Layer A
        "constant": ModelTier.GATEKEEPER,
        "unit": ModelTier.GATEKEEPER,
        "definition": ModelTier.GATEKEEPER,
        
        # Calculations -> Layer B
        "calculate": ModelTier.WORKHORSE,
        "solve": ModelTier.WORKHORSE,
        "equation": ModelTier.WORKHORSE,
        "simulate": ModelTier.WORKHORSE,
        
        # Deep analysis -> Layer C
        "derive": ModelTier.ORCHESTRATOR,
        "prove": ModelTier.ORCHESTRATOR,
        "unify": ModelTier.ORCHESTRATOR,
        "theory": ModelTier.ORCHESTRATOR,
    }
    
    def __init__(self):
        self.config = get_config()
        self._route_history: List[RouteDecision] = []
    
    def classify_task(self, prompt: str) -> Tuple[str, float]:
        """
        Classify the task type from a prompt.
        
        Returns (task_type, confidence).
        """
        prompt_lower = prompt.lower()
        
        # Check explicit task markers
        for task_type in TASK_ROUTING.keys():
            if task_type in prompt_lower:
                return task_type, 0.9
        
        # Check physics-specific keywords
        for keyword, tier in self.PHYSICS_ROUTING.items():
            if keyword in prompt_lower:
                # Map tier back to task type
                if tier == ModelTier.GATEKEEPER:
                    return "classify", 0.8
                elif tier == ModelTier.WORKHORSE:
                    return "analyze", 0.8
                else:
                    return "reason", 0.8
        
        # Check complexity keywords
        for keyword in self.COMPLEXITY_KEYWORDS["simple"]:
            if keyword in prompt_lower:
                return "quick_check", 0.7
        
        for keyword in self.COMPLEXITY_KEYWORDS["moderate"]:
            if keyword in prompt_lower:
                return "analyze", 0.7
        
        for keyword in self.COMPLEXITY_KEYWORDS["complex"]:
            if keyword in prompt_lower:
                return "reason", 0.7
        
        # Default to workhorse for unknown tasks
        return "analyze", 0.5
    
    def estimate_context_size(self, messages: List[Message]) -> int:
        """Estimate token count for messages."""
        # Rough estimation: ~4 chars per token
        total_chars = sum(len(m.content) for m in messages)
        return total_chars // 4
    
    def route(
        self,
        messages: List[Message],
        task_type: Optional[str] = None,
        force_tier: Optional[ModelTier] = None,
    ) -> RouteDecision:
        """
        Determine the appropriate tier for a request.
        
        Args:
            messages: The conversation messages
            task_type: Explicit task type (optional)
            force_tier: Force a specific tier (optional)
        
        Returns:
            RouteDecision with routing information
        """
        # If tier forced, use it directly
        if force_tier:
            return RouteDecision(
                tier=force_tier,
                task_type=task_type or "forced",
                confidence=1.0,
            )
        
        # Get last user message for classification
        user_messages = [m for m in messages if m.role.value == "user"]
        if not user_messages:
            # No user message, default to workhorse
            return RouteDecision(
                tier=ModelTier.WORKHORSE,
                task_type="unknown",
                confidence=0.5,
            )
        
        last_prompt = user_messages[-1].content
        
        # Classify task if not provided
        if task_type:
            confidence = 0.9
        else:
            task_type, confidence = self.classify_task(last_prompt)
        
        # Get base tier for task type
        base_tier = get_tier_for_task(task_type)
        
        # Check context size - escalate if too large for tier
        context_tokens = self.estimate_context_size(messages)
        model_config = self.config.get_model(base_tier)
        
        escalated_from = None
        escalation_reason = None
        
        if context_tokens > model_config.max_context:
            # Need to escalate for context size
            if base_tier == ModelTier.GATEKEEPER:
                base_tier = ModelTier.WORKHORSE
                escalated_from = ModelTier.GATEKEEPER
                escalation_reason = EscalationReason.CONTEXT_SIZE
            elif base_tier == ModelTier.WORKHORSE:
                base_tier = ModelTier.ORCHESTRATOR
                escalated_from = ModelTier.WORKHORSE
                escalation_reason = EscalationReason.CONTEXT_SIZE
        
        decision = RouteDecision(
            tier=base_tier,
            task_type=task_type,
            confidence=confidence,
            context_tokens=context_tokens,
            escalated_from=escalated_from,
            escalation_reason=escalation_reason,
        )
        
        self._route_history.append(decision)
        return decision
    
    def should_escalate(
        self,
        response: LLMResponse,
        current_tier: ModelTier,
    ) -> Tuple[bool, Optional[EscalationReason]]:
        """
        Determine if a response should trigger escalation.
        
        Checks for:
        - Errors
        - Low confidence indicators
        - Quality issues
        """
        # Error -> escalate
        if response.is_error:
            return True, EscalationReason.ERROR
        
        # Check for low confidence phrases
        low_confidence_phrases = [
            "i'm not sure",
            "i don't know",
            "unclear",
            "cannot determine",
            "need more information",
            "too complex",
            "escalate",
        ]
        
        content_lower = response.content.lower()
        for phrase in low_confidence_phrases:
            if phrase in content_lower:
                return True, EscalationReason.CONFIDENCE
        
        # Check if response is asking for clarification (might need higher tier)
        if "?" in response.content and current_tier == ModelTier.GATEKEEPER:
            # Gatekeeper shouldn't be asking questions for most tasks
            return True, EscalationReason.COMPLEXITY
        
        return False, None
    
    def get_next_tier(self, current: ModelTier) -> Optional[ModelTier]:
        """Get the next tier up from current."""
        if current == ModelTier.GATEKEEPER:
            return ModelTier.WORKHORSE
        elif current == ModelTier.WORKHORSE:
            return ModelTier.ORCHESTRATOR
        return None
    
    def get_route_stats(self) -> Dict[str, Any]:
        """Get routing statistics."""
        if not self._route_history:
            return {"total_routes": 0}
        
        tier_counts = {}
        task_counts = {}
        escalation_counts = {}
        
        for decision in self._route_history:
            tier = decision.tier.value
            tier_counts[tier] = tier_counts.get(tier, 0) + 1
            
            task = decision.task_type
            task_counts[task] = task_counts.get(task, 0) + 1
            
            if decision.escalation_reason:
                reason = decision.escalation_reason.value
                escalation_counts[reason] = escalation_counts.get(reason, 0) + 1
        
        return {
            "total_routes": len(self._route_history),
            "by_tier": tier_counts,
            "by_task": task_counts,
            "escalations": escalation_counts,
            "avg_context_tokens": sum(d.context_tokens for d in self._route_history) / len(self._route_history),
        }


# Gate prompts for Layer A decisions
GATE_PROMPTS = {
    "classify_task": """Classify this task into one category:
- SIMPLE: Quick lookups, yes/no questions, validations
- MODERATE: Data extraction, calculations, transformations
- COMPLEX: Multi-step reasoning, planning, synthesis

Task: {task}

Respond with only: SIMPLE, MODERATE, or COMPLEX""",

    "validate_output": """Check if this output is valid and complete:

Output: {output}

Requirements: {requirements}

Respond with JSON: {{"valid": true/false, "reason": "..."}}""",

    "detect_escalation": """Should this be escalated to a more capable model?

Request: {request}
Current response: {response}

Respond with JSON: {{"escalate": true/false, "reason": "..."}}""",
}
