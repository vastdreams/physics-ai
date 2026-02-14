"""
PATH: ai/llm/provider.py
PURPOSE: Base LLM provider interface and common types

WHY: Abstracts away the differences between local (Ollama) and API (DeepSeek)
     providers, allowing seamless fallback and routing.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
import json


class Role(Enum):
    """Message roles in a conversation."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


@dataclass
class Message:
    """A message in a conversation."""
    role: Role
    content: str
    name: Optional[str] = None
    tool_calls: Optional[List[Dict]] = None
    tool_call_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to API-compatible dict."""
        d = {"role": self.role.value, "content": self.content}
        if self.name:
            d["name"] = self.name
        if self.tool_calls:
            d["tool_calls"] = self.tool_calls
        if self.tool_call_id:
            d["tool_call_id"] = self.tool_call_id
        return d
    
    @classmethod
    def system(cls, content: str) -> "Message":
        return cls(Role.SYSTEM, content)
    
    @classmethod
    def user(cls, content: str) -> "Message":
        return cls(Role.USER, content)
    
    @classmethod
    def assistant(cls, content: str) -> "Message":
        return cls(Role.ASSISTANT, content)


@dataclass
class TokenUsage:
    """Token usage statistics."""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    
    @property
    def cost_estimate(self) -> float:
        """Rough cost estimate in USD (varies by provider)."""
        # Using DeepSeek pricing as baseline
        return (self.prompt_tokens * 0.14 + self.completion_tokens * 0.28) / 1_000_000


@dataclass
class LLMResponse:
    """Response from an LLM provider."""
    content: str
    model: str
    provider: str
    
    # Metadata
    finish_reason: str = "stop"
    usage: TokenUsage = field(default_factory=TokenUsage)
    
    # Timing
    latency_ms: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    
    # For tool calls
    tool_calls: Optional[List[Dict]] = None
    
    # Raw response for debugging
    raw: Optional[Dict] = None
    
    # Error info
    error: Optional[str] = None
    is_fallback: bool = False
    
    @property
    def is_error(self) -> bool:
        return self.error is not None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "model": self.model,
            "provider": self.provider,
            "finish_reason": self.finish_reason,
            "usage": {
                "prompt_tokens": self.usage.prompt_tokens,
                "completion_tokens": self.usage.completion_tokens,
                "total_tokens": self.usage.total_tokens,
            },
            "latency_ms": self.latency_ms,
            "is_fallback": self.is_fallback,
            "error": self.error,
        }
    
    def parse_json(self) -> Optional[Dict]:
        """Try to parse content as JSON."""
        try:
            # Handle markdown code blocks
            content = self.content.strip()
            if content.startswith("```"):
                lines = content.split("\n")
                # Remove first and last lines (code block markers)
                content = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])
            return json.loads(content)
        except json.JSONDecodeError:
            return None


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name."""
        pass
    
    @property
    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is available."""
        pass
    
    @abstractmethod
    async def generate(
        self,
        messages: List[Message],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        tools: Optional[List[Dict]] = None,
        json_mode: bool = False,
        **kwargs
    ) -> LLMResponse:
        """Generate a response from the model."""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the provider is healthy."""
        pass
    
    async def generate_with_retry(
        self,
        messages: List[Message],
        model: str,
        max_retries: int = 3,
        **kwargs
    ) -> LLMResponse:
        """Generate with automatic retries."""
        last_error = None
        for attempt in range(max_retries):
            try:
                response = await self.generate(messages, model, **kwargs)
                if not response.is_error:
                    return response
                last_error = response.error
            except Exception as e:
                last_error = str(e)
        
        return LLMResponse(
            content="",
            model=model,
            provider=self.name,
            error=f"Failed after {max_retries} attempts: {last_error}"
        )


@dataclass
class Tool:
    """Tool definition for function calling."""
    name: str
    description: str
    parameters: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to OpenAI-compatible tool format."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            }
        }


# Common tools for physics AI
PHYSICS_TOOLS = [
    Tool(
        name="solve_equation",
        description="Solve a physics equation symbolically or numerically",
        parameters={
            "type": "object",
            "properties": {
                "equation": {"type": "string", "description": "The equation to solve"},
                "solve_for": {"type": "string", "description": "Variable to solve for"},
                "known_values": {"type": "object", "description": "Known variable values"},
            },
            "required": ["equation", "solve_for"]
        }
    ),
    Tool(
        name="run_simulation",
        description="Run a physics simulation",
        parameters={
            "type": "object",
            "properties": {
                "simulation_type": {"type": "string", "description": "Type of simulation"},
                "parameters": {"type": "object", "description": "Simulation parameters"},
                "duration": {"type": "number", "description": "Simulation duration"},
            },
            "required": ["simulation_type", "parameters"]
        }
    ),
    Tool(
        name="search_knowledge",
        description="Search the physics knowledge base",
        parameters={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "domain": {"type": "string", "description": "Physics domain to search"},
                "limit": {"type": "integer", "description": "Max results"},
            },
            "required": ["query"]
        }
    ),
    Tool(
        name="validate_physics",
        description="Validate a physics claim or calculation",
        parameters={
            "type": "object",
            "properties": {
                "claim": {"type": "string", "description": "The claim to validate"},
                "context": {"type": "string", "description": "Additional context"},
            },
            "required": ["claim"]
        }
    ),
]
