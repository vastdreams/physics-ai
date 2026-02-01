# ai/context_memory/
"""
Context Bubble - Atomic context unit with micro-agents.

Inspired by DREAM architecture - context bubbles acting as traffic signals.

First Principle Analysis:
- Bubble: B = {content, metadata, micro_agents, traffic_signals}
- Traffic signals: T = {pathway: weight} for routing decisions
- Micro-agents: Embedded sub-agentic structures
- Mathematical foundation: Graph nodes, weighted edges, attention mechanisms
- Architecture: Atomic unit in hierarchical context tree
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from loggers.system_logger import SystemLogger
from utilities.cot_logging import ChainOfThoughtLogger, LogLevel
from .micro_agent import MicroAgent


@dataclass
class ContextBubble:
    """
    Atomic context unit with embedded micro-agents.
    
    Acts as a traffic signal in the context memory tree,
    directing attention to relevant pathways.
    """
    bubble_id: str
    content: Any
    metadata: Dict[str, Any] = field(default_factory=dict)
    micro_agents: List[MicroAgent] = field(default_factory=list)
    traffic_signals: Dict[str, float] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    
    def __post_init__(self):
        """Initialize context bubble."""
        if not self.bubble_id:
            self.bubble_id = f"bubble_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    
    def add_micro_agent(self, agent: MicroAgent) -> None:
        """
        Add micro-agent to bubble.
        
        Args:
            agent: MicroAgent instance
        """
        if agent not in self.micro_agents:
            self.micro_agents.append(agent)
            self.updated_at = datetime.now()
    
    def remove_micro_agent(self, agent_id: str) -> bool:
        """
        Remove micro-agent by ID.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            True if removed successfully
        """
        original_count = len(self.micro_agents)
        self.micro_agents = [a for a in self.micro_agents if a.agent_id != agent_id]
        removed = len(self.micro_agents) < original_count
        if removed:
            self.updated_at = datetime.now()
        return removed
    
    def get_traffic_signal(self, pathway: str, default: float = 0.0) -> float:
        """
        Get traffic signal weight for pathway.
        
        Mathematical: w(pathway) ∈ [0, 1] where higher = more relevant
        
        Args:
            pathway: Pathway identifier
            default: Default weight if pathway not found
            
        Returns:
            Traffic signal weight
        """
        return self.traffic_signals.get(pathway, default)
    
    def set_traffic_signal(self, pathway: str, weight: float) -> None:
        """
        Set traffic signal weight for pathway.
        
        Args:
            pathway: Pathway identifier
            weight: Weight value (clamped to [0, 1])
        """
        self.traffic_signals[pathway] = max(0.0, min(1.0, weight))
        self.updated_at = datetime.now()
    
    def update_traffic_signals(self, usage_data: Dict[str, int]) -> None:
        """
        Update traffic signals based on usage data.
        
        Mathematical: w_i = usage_i / max(usage) (normalized)
        
        Args:
            usage_data: Dictionary of pathway -> usage count
        """
        if not usage_data:
            return
        
        max_usage = max(usage_data.values())
        if max_usage > 0:
            for pathway, usage in usage_data.items():
                weight = usage / max_usage
                self.set_traffic_signal(pathway, weight)
        
        self.updated_at = datetime.now()
    
    def process_with_agents(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process query through micro-agents.
        
        Args:
            query: Query dictionary
            
        Returns:
            Processed result
        """
        self.access_count += 1
        self.last_accessed = datetime.now()
        
        result = {
            'bubble_id': self.bubble_id,
            'content': self.content,
            'pathways': []
        }
        
        # Process through each micro-agent
        for agent in self.micro_agents:
            agent_result = agent.process(query, self)
            if agent_result:
                result['pathways'].append(agent_result)
        
        return result
    
    def get_next_pathway(self) -> Optional[str]:
        """
        Get next pathway based on traffic signals.
        
        Returns:
            Pathway identifier with highest weight, or None
        """
        if not self.traffic_signals:
            return None
        
        # Return pathway with highest weight
        return max(self.traffic_signals.items(), key=lambda x: x[1])[0]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get bubble statistics."""
        return {
            'bubble_id': self.bubble_id,
            'num_micro_agents': len(self.micro_agents),
            'num_pathways': len(self.traffic_signals),
            'access_count': self.access_count,
            'avg_traffic_signal': sum(self.traffic_signals.values()) / len(self.traffic_signals) if self.traffic_signals else 0.0,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'last_accessed': self.last_accessed.isoformat() if self.last_accessed else None
        }

