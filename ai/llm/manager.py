"""
PATH: ai/llm/manager.py
PURPOSE: Central LLM manager with automatic fallback and routing

FLOW:
┌─────────────────────────────────────────────────────────────────────┐
│                         LLM Manager                                 │
│                                                                     │
│  Request -> Router -> Select Tier -> Try Local -> Fallback API     │
│                           |              |              |           │
│                           v              v              v           │
│                     Gatekeeper      Ollama        DeepSeek         │
│                     Workhorse                                       │
│                     Orchestrator                                    │
└─────────────────────────────────────────────────────────────────────┘

WHY: Provides unified interface for multi-tier LLM access with
     automatic failover from local to cloud when needed.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
import json

from .config import LLMConfig, ModelTier, get_config
from .provider import LLMProvider, LLMResponse, Message, Tool
from .local_provider import OllamaProvider
from .deepseek_provider import DeepSeekProvider
from .router import AgentRouter, RouteDecision, EscalationReason

logger = logging.getLogger("PhysicsAI.LLM")


@dataclass
class RequestStats:
    """Statistics for a request."""
    tier: ModelTier
    provider_used: str
    is_fallback: bool
    latency_ms: float
    tokens_used: int
    escalations: int
    timestamp: datetime = field(default_factory=datetime.now)


class LLMManager:
    """
    Central manager for LLM operations.
    
    Handles:
    - Multi-tier routing (Gatekeeper -> Workhorse -> Orchestrator)
    - Automatic fallback (Local -> DeepSeek API)
    - Request tracking and statistics
    - Model health monitoring
    """
    
    def __init__(self, config: Optional[LLMConfig] = None):
        """
        Initialize LLM manager.
        
        Args:
            config: LLM configuration (default from global config)
        """
        self.config = config or get_config()
        
        # Initialize providers
        self.local_provider = OllamaProvider(
            host=self.config.ollama_host,
            timeout=self.config.ollama_timeout
        )
        self.api_provider = DeepSeekProvider(
            api_key=self.config.deepseek_api_key,
            base_url=self.config.deepseek_base_url
        )
        
        # Router for tier selection
        self.router = AgentRouter()
        
        # Statistics
        self._request_history: List[RequestStats] = []
        self._provider_status: Dict[str, bool] = {}
    
    async def initialize(self):
        """Initialize the manager and check provider health."""
        # Check local provider
        local_healthy = await self.local_provider.health_check()
        self._provider_status["ollama"] = local_healthy
        
        if local_healthy:
            logger.info("Ollama local provider is healthy")
            models = await self.local_provider.list_models()
            logger.info(f"Available local models: {models}")
        else:
            logger.warning("Ollama not available, will use API fallback")
        
        # Check API provider
        if self.config.fallback_to_api:
            api_healthy = await self.api_provider.health_check()
            self._provider_status["deepseek"] = api_healthy
            if api_healthy:
                logger.info("DeepSeek API fallback is available")
            else:
                logger.warning("DeepSeek API not available")
        
        return self._provider_status
    
    def _get_model_name(self, tier: ModelTier, provider: str) -> str:
        """Get the model name for a tier and provider."""
        model_config = self.config.get_model(tier)
        
        if provider == "ollama":
            return model_config.ollama_model
        else:
            return model_config.api_model
    
    async def _try_provider(
        self,
        provider: LLMProvider,
        messages: List[Message],
        tier: ModelTier,
        **kwargs
    ) -> Optional[LLMResponse]:
        """Try to get a response from a provider."""
        model = self._get_model_name(tier, provider.name)
        model_config = self.config.get_model(tier)
        
        try:
            response = await provider.generate(
                messages=messages,
                model=model,
                temperature=kwargs.get("temperature", model_config.temperature),
                max_tokens=kwargs.get("max_tokens", model_config.max_output),
                tools=kwargs.get("tools"),
                json_mode=kwargs.get("json_mode", False),
            )
            
            if not response.is_error:
                return response
            
            logger.warning(f"Provider {provider.name} error: {response.error}")
            return None
            
        except Exception as e:
            logger.error(f"Provider {provider.name} exception: {e}")
            return None
    
    async def generate(
        self,
        messages: List[Message],
        task_type: Optional[str] = None,
        force_tier: Optional[ModelTier] = None,
        auto_escalate: bool = True,
        max_escalations: int = 2,
        **kwargs
    ) -> LLMResponse:
        """
        Generate a response using the appropriate tier and provider.
        
        Args:
            messages: Conversation messages
            task_type: Explicit task type for routing
            force_tier: Force a specific tier
            auto_escalate: Automatically escalate on failure/low confidence
            max_escalations: Maximum number of escalation attempts
            **kwargs: Additional generation parameters
        
        Returns:
            LLMResponse from the best available provider
        """
        # Route the request
        decision = self.router.route(
            messages=messages,
            task_type=task_type,
            force_tier=force_tier
        )
        
        current_tier = decision.tier
        escalation_count = 0
        
        while True:
            # Try local provider first (if available and preferred)
            response = None
            provider_used = None
            
            if self.config.prefer_local and self._provider_status.get("ollama"):
                response = await self._try_provider(
                    self.local_provider,
                    messages,
                    current_tier,
                    **kwargs
                )
                if response:
                    provider_used = "ollama"
            
            # Fall back to API if local failed
            if response is None and self.config.fallback_to_api:
                response = await self._try_provider(
                    self.api_provider,
                    messages,
                    current_tier,
                    **kwargs
                )
                if response:
                    provider_used = "deepseek"
                    response.is_fallback = True
            
            # If still no response, return error
            if response is None:
                return LLMResponse(
                    content="",
                    model="",
                    provider="none",
                    error="All providers failed"
                )
            
            # Check if we should escalate
            if auto_escalate and escalation_count < max_escalations:
                should_escalate, reason = self.router.should_escalate(response, current_tier)
                
                if should_escalate:
                    next_tier = self.router.get_next_tier(current_tier)
                    if next_tier:
                        logger.info(f"Escalating from {current_tier.value} to {next_tier.value}: {reason}")
                        current_tier = next_tier
                        escalation_count += 1
                        continue
            
            # Record stats
            self._request_history.append(RequestStats(
                tier=current_tier,
                provider_used=provider_used or "unknown",
                is_fallback=response.is_fallback,
                latency_ms=response.latency_ms,
                tokens_used=response.usage.total_tokens,
                escalations=escalation_count
            ))
            
            return response
    
    async def generate_simple(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Simple generation interface.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
        
        Returns:
            Generated text content
        """
        messages = []
        if system_prompt:
            messages.append(Message.system(system_prompt))
        messages.append(Message.user(prompt))
        
        response = await self.generate(messages, **kwargs)
        return response.content
    
    async def classify(self, text: str, categories: List[str]) -> str:
        """
        Classify text into one of the given categories.
        Uses Layer A (Gatekeeper) for efficiency.
        """
        prompt = f"""Classify the following text into exactly one of these categories: {', '.join(categories)}

Text: {text}

Respond with only the category name, nothing else."""
        
        response = await self.generate(
            messages=[Message.user(prompt)],
            force_tier=ModelTier.GATEKEEPER,
            temperature=0.1,  # Low temperature for consistency
        )
        
        # Find matching category
        content = response.content.strip().lower()
        for cat in categories:
            if cat.lower() in content:
                return cat
        
        return categories[0]  # Default to first category
    
    async def validate(self, data: Any, schema: Dict) -> Dict[str, Any]:
        """
        Validate data against a schema.
        Uses Layer A (Gatekeeper) for efficiency.
        """
        prompt = f"""Validate this data against the schema.

Data: {json.dumps(data) if isinstance(data, (dict, list)) else str(data)}

Schema: {json.dumps(schema)}

Respond with JSON: {{"valid": true/false, "errors": ["list of errors if any"]}}"""
        
        response = await self.generate(
            messages=[Message.user(prompt)],
            force_tier=ModelTier.GATEKEEPER,
            json_mode=True,
        )
        
        result = response.parse_json()
        return result or {"valid": False, "errors": ["Failed to parse validation response"]}
    
    async def analyze(self, content: str, analysis_type: str = "general") -> str:
        """
        Analyze content using Layer B (Workhorse).
        """
        prompt = f"""Perform a {analysis_type} analysis of the following content:

{content}

Provide a structured analysis."""
        
        return await self.generate_simple(
            prompt,
            force_tier=ModelTier.WORKHORSE
        )
    
    async def orchestrate(
        self,
        task: str,
        context: str = "",
        tools: Optional[List[Tool]] = None
    ) -> str:
        """
        Complex orchestration using Layer C (Orchestrator).
        """
        system_prompt = """You are an AI orchestrator for a physics research system.
Your role is to:
1. Break down complex tasks into steps
2. Call appropriate tools when needed
3. Synthesize results into coherent responses
4. Maintain scientific rigor and cite sources

Always structure your response with clear reasoning steps."""
        
        prompt = task
        if context:
            prompt = f"Context:\n{context}\n\nTask:\n{task}"
        
        tool_dicts = [t.to_dict() for t in tools] if tools else None
        
        response = await self.generate(
            messages=[
                Message.system(system_prompt),
                Message.user(prompt)
            ],
            force_tier=ModelTier.ORCHESTRATOR,
            tools=tool_dicts,
        )
        
        return response.content
    
    def get_stats(self) -> Dict[str, Any]:
        """Get manager statistics."""
        if not self._request_history:
            return {"total_requests": 0}
        
        tier_counts = {}
        provider_counts = {}
        total_latency = 0
        total_tokens = 0
        fallback_count = 0
        escalation_total = 0
        
        for stat in self._request_history:
            tier = stat.tier.value
            tier_counts[tier] = tier_counts.get(tier, 0) + 1
            
            provider = stat.provider_used
            provider_counts[provider] = provider_counts.get(provider, 0) + 1
            
            total_latency += stat.latency_ms
            total_tokens += stat.tokens_used
            
            if stat.is_fallback:
                fallback_count += 1
            
            escalation_total += stat.escalations
        
        return {
            "total_requests": len(self._request_history),
            "by_tier": tier_counts,
            "by_provider": provider_counts,
            "avg_latency_ms": total_latency / len(self._request_history),
            "total_tokens": total_tokens,
            "fallback_rate": fallback_count / len(self._request_history),
            "avg_escalations": escalation_total / len(self._request_history),
            "provider_status": self._provider_status,
            "router_stats": self.router.get_route_stats(),
        }


# Global manager instance
_manager: Optional[LLMManager] = None


async def get_manager() -> LLMManager:
    """Get or create the global LLM manager."""
    global _manager
    if _manager is None:
        _manager = LLMManager()
        await _manager.initialize()
    return _manager


def get_manager_sync() -> LLMManager:
    """Get the global manager (sync version, must be initialized first)."""
    global _manager
    if _manager is None:
        _manager = LLMManager()
    return _manager
