"""
PATH: ai/llm/__init__.py
PURPOSE: Multi-layer LLM infrastructure for DREAM-style agent system

ARCHITECTURE:
┌─────────────────────────────────────────────────────────────────────┐
│                        DREAM Agent Stack                            │
├─────────────────────────────────────────────────────────────────────┤
│  Layer C: Orchestrator (Ministral 8B)                               │
│  - End-to-end orchestration, narrative generation                   │
│  - Complex reasoning, cross-checking                                │
├─────────────────────────────────────────────────────────────────────┤
│  Layer B: Workhorse (Qwen2.5 7B)                                    │
│  - Data mapping, tool calling, extraction                           │
│  - Schema generation, analysis plans                                │
├─────────────────────────────────────────────────────────────────────┤
│  Layer A: Gatekeeper (Phi 3.5 Mini 3.8B)                            │
│  - Input classification, routing                                    │
│  - Validation, schema checks, quick decisions                       │
└─────────────────────────────────────────────────────────────────────┘

FALLBACK CHAIN:
  Local (Ollama) -> DeepSeek API -> Error

WHY: Cost optimization by routing requests to appropriate model tier.
     Most requests handled by cheap Layer A, escalated only when needed.
"""

from .config import LLMConfig, ModelTier, get_config
from .provider import LLMProvider, LLMResponse, Message
from .local_provider import OllamaProvider
from .deepseek_provider import DeepSeekProvider
from .router import AgentRouter, RouteDecision
from .manager import LLMManager

__all__ = [
    'LLMConfig',
    'ModelTier', 
    'get_config',
    'LLMProvider',
    'LLMResponse',
    'Message',
    'OllamaProvider',
    'DeepSeekProvider',
    'AgentRouter',
    'RouteDecision',
    'LLMManager',
]
