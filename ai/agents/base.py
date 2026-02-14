"""
PATH: ai/agents/base.py
PURPOSE: Base agent class for DREAM-style agents

SAFETY PRINCIPLE:
- LLMs should never be the source of truth for numbers
- All numeric claims must reference artefact IDs from deterministic code
- Agents reject any numeric claim without provenance
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
import re
import uuid

from ai.llm.config import ModelTier
from ai.llm.manager import LLMManager, get_manager_sync
from ai.llm.provider import LLMResponse, Message

_CONTENT_PREVIEW_MAX_LENGTH = 200


class AgentStatus(Enum):
    """Agent execution status."""
    SUCCESS = "success"
    PARTIAL = "partial"
    ESCALATED = "escalated"
    ERROR = "error"


@dataclass
class Artefact:
    """
    An artefact produced by deterministic computation.
    
    All numeric claims must reference artefact IDs.
    """
    id: str
    type: str  # "calculation", "simulation", "data", etc.
    content: Any
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    @classmethod
    def create(cls, type: str, content: Any, **metadata) -> "Artefact":
        return cls(
            id=f"art_{uuid.uuid4().hex[:8]}",
            type=type,
            content=content,
            metadata=metadata
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "content": self.content,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class AgentResponse:
    """Response from an agent."""
    status: AgentStatus
    content: str
    
    # Provenance
    artefacts: List[Artefact] = field(default_factory=list)
    artefact_references: List[str] = field(default_factory=list)
    
    # Metadata
    agent_name: str = ""
    tier: Optional[ModelTier] = None
    confidence: float = 1.0
    
    # For escalation
    should_escalate: bool = False
    escalation_reason: Optional[str] = None
    
    # Timing
    latency_ms: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Raw LLM response
    llm_response: Optional[LLMResponse] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "content": self.content,
            "artefacts": [a.to_dict() for a in self.artefacts],
            "artefact_references": self.artefact_references,
            "agent_name": self.agent_name,
            "tier": self.tier.value if self.tier else None,
            "confidence": self.confidence,
            "should_escalate": self.should_escalate,
            "escalation_reason": self.escalation_reason,
            "latency_ms": self.latency_ms,
        }
    
    def validate_numeric_claims(self) -> bool:
        """
        Validate that all numeric claims reference artefacts.
        
        This is a key safety feature to prevent hallucinated numbers.
        """
        # Find numbers in content
        numbers = re.findall(r'\b\d+\.?\d*\b', self.content)
        
        # Simple heuristic: if there are numbers but no artefact refs, suspicious
        if numbers and not self.artefact_references:
            return False
        
        return True


class BaseAgent(ABC):
    """
    Base class for DREAM-style agents.
    
    All agents follow these principles:
    1. LLM proposes structure, deterministic code produces numbers
    2. All numeric claims must have provenance (artefact IDs)
    3. Agents should know when to escalate
    """
    
    def __init__(self, manager: Optional[LLMManager] = None):
        """
        Initialize agent.
        
        Args:
            manager: LLM manager instance
        """
        self.manager = manager or get_manager_sync()
        self._artefacts: Dict[str, Artefact] = {}
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Agent name."""
        pass
    
    @property
    @abstractmethod
    def tier(self) -> ModelTier:
        """Model tier this agent uses."""
        pass
    
    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """System prompt for this agent."""
        pass
    
    def register_artefact(self, artefact: Artefact):
        """Register an artefact for reference."""
        self._artefacts[artefact.id] = artefact
    
    def get_artefact(self, artefact_id: str) -> Optional[Artefact]:
        """Get an artefact by ID."""
        return self._artefacts.get(artefact_id)
    
    def format_artefacts_for_prompt(self, artefact_ids: List[str]) -> str:
        """Format artefacts for inclusion in prompt."""
        lines = ["Available artefacts (use these IDs when citing data):"]
        for aid in artefact_ids:
            art = self.get_artefact(aid)
            if art:
                content_preview = str(art.content)[:_CONTENT_PREVIEW_MAX_LENGTH]
                lines.append(f"  [{art.id}] ({art.type}): {content_preview}")
        return "\n".join(lines)
    
    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> AgentResponse:
        """
        Process input and return response.
        
        Args:
            input_data: Input data for the agent
        
        Returns:
            AgentResponse with results
        """
        pass
    
    async def _generate(
        self,
        prompt: str,
        artefact_ids: Optional[List[str]] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Generate a response with artefact context.
        
        Args:
            prompt: User prompt
            artefact_ids: IDs of artefacts to include
        """
        messages = [Message.system(self.system_prompt)]
        
        # Add artefact context if provided
        if artefact_ids:
            artefact_context = self.format_artefacts_for_prompt(artefact_ids)
            messages.append(Message.system(artefact_context))
        
        messages.append(Message.user(prompt))
        
        return await self.manager.generate(
            messages=messages,
            force_tier=self.tier,
            **kwargs
        )
    
    def _extract_artefact_refs(self, content: str) -> List[str]:
        """Extract artefact references from content."""
        # Look for [art_XXXXXXXX] patterns
        return re.findall(r'\[art_[a-f0-9]{8}\]', content)
    
    def _build_response(
        self,
        llm_response: LLMResponse,
        artefacts: Optional[List[Artefact]] = None,
        should_escalate: bool = False,
        escalation_reason: Optional[str] = None,
    ) -> AgentResponse:
        """Build an AgentResponse from an LLM response."""
        if llm_response.is_error:
            return AgentResponse(
                status=AgentStatus.ERROR,
                content=llm_response.error or "Unknown error",
                agent_name=self.name,
                tier=self.tier,
                llm_response=llm_response,
                latency_ms=llm_response.latency_ms,
            )
        
        # Extract artefact references
        refs = self._extract_artefact_refs(llm_response.content)
        
        status = AgentStatus.SUCCESS
        if should_escalate:
            status = AgentStatus.ESCALATED
        
        return AgentResponse(
            status=status,
            content=llm_response.content,
            artefacts=artefacts or [],
            artefact_references=refs,
            agent_name=self.name,
            tier=self.tier,
            should_escalate=should_escalate,
            escalation_reason=escalation_reason,
            latency_ms=llm_response.latency_ms,
            llm_response=llm_response,
        )


# Provenance enforcement prompt
PROVENANCE_PROMPT = """CRITICAL SAFETY RULE:
You must NEVER generate or claim specific numeric values without citing an artefact ID.

When presenting calculations, measurements, or data:
- Always reference the artefact ID in brackets: [art_XXXXXXXX]
- If no artefact exists for a claim, state "requires calculation" instead of making up numbers
- Deterministic code produces numbers, you produce narrative and structure

Example:
WRONG: "The energy is 5.2 joules"
RIGHT: "The energy is 5.2 joules [art_a1b2c3d4]"
RIGHT: "The energy calculation requires running the simulation"
"""
