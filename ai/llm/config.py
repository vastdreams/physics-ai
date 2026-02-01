"""
PATH: ai/llm/config.py
PURPOSE: Configuration for multi-layer LLM system

MODELS:
- Layer A (Gatekeeper): phi3.5:3.8b-mini-instruct-q4_K_M
- Layer B (Workhorse): qwen2.5:7b-instruct-q4_K_M  
- Layer C (Orchestrator): mistral:8b-instruct-q4_K_M (Ministral)

FALLBACK: DeepSeek API for when local models unavailable
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional
import os


class ModelTier(Enum):
    """Model tier in the DREAM agent stack."""
    GATEKEEPER = "gatekeeper"      # Layer A: Cheap, fast, always-on
    WORKHORSE = "workhorse"        # Layer B: Balanced cost/capability
    ORCHESTRATOR = "orchestrator"  # Layer C: Full capability


class ProviderType(Enum):
    """LLM provider types."""
    OLLAMA = "ollama"
    DEEPSEEK = "deepseek"
    OPENAI = "openai"


@dataclass
class ModelConfig:
    """Configuration for a specific model."""
    name: str
    provider: ProviderType
    tier: ModelTier
    
    # Model identifiers
    ollama_model: str = ""
    api_model: str = ""
    
    # Resource limits
    max_context: int = 8192
    max_output: int = 2048
    
    # Performance tuning
    temperature: float = 0.7
    top_p: float = 0.9
    
    # Cost estimation (relative units)
    cost_per_1k_tokens: float = 0.0
    
    # Capabilities
    supports_json: bool = True
    supports_tools: bool = True
    supports_vision: bool = False


@dataclass 
class LLMConfig:
    """Main configuration for the LLM system."""
    
    # DeepSeek API (fallback)
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"
    
    # Ollama settings
    ollama_host: str = "http://localhost:11434"
    ollama_timeout: int = 120
    
    # Model assignments
    models: Dict[ModelTier, ModelConfig] = field(default_factory=dict)
    
    # Routing settings
    auto_escalate: bool = True
    max_retries: int = 3
    fallback_to_api: bool = True
    
    # Cost optimization
    prefer_local: bool = True
    cache_responses: bool = True
    
    def __post_init__(self):
        """Initialize default models if not provided."""
        if not self.models:
            self.models = self._default_models()
    
    def _default_models(self) -> Dict[ModelTier, ModelConfig]:
        """Default DREAM-style model configuration."""
        return {
            # Layer A: Gatekeeper - Phi 3.5 Mini
            ModelTier.GATEKEEPER: ModelConfig(
                name="Phi 3.5 Mini",
                provider=ProviderType.OLLAMA,
                tier=ModelTier.GATEKEEPER,
                ollama_model="phi3.5:3.8b-mini-instruct-q4_K_M",
                api_model="deepseek-chat",  # Fallback
                max_context=8192,
                max_output=1024,
                temperature=0.3,  # Lower for consistent routing
                cost_per_1k_tokens=0.001,
                supports_tools=False,  # Keep it simple
            ),
            
            # Layer B: Workhorse - Qwen 2.5 7B
            ModelTier.WORKHORSE: ModelConfig(
                name="Qwen 2.5 7B",
                provider=ProviderType.OLLAMA,
                tier=ModelTier.WORKHORSE,
                ollama_model="qwen2.5:7b-instruct-q4_K_M",
                api_model="deepseek-chat",
                max_context=16384,
                max_output=2048,
                temperature=0.5,
                cost_per_1k_tokens=0.005,
                supports_tools=True,
            ),
            
            # Layer C: Orchestrator - Ministral/Mistral 8B
            ModelTier.ORCHESTRATOR: ModelConfig(
                name="Ministral 8B",
                provider=ProviderType.OLLAMA,
                tier=ModelTier.ORCHESTRATOR,
                ollama_model="mistral:8b-instruct-q4_K_M",
                api_model="deepseek-chat",
                max_context=32768,
                max_output=4096,
                temperature=0.7,
                cost_per_1k_tokens=0.01,
                supports_tools=True,
                supports_vision=False,
            ),
        }
    
    def get_model(self, tier: ModelTier) -> ModelConfig:
        """Get model config for a tier."""
        return self.models.get(tier, self.models[ModelTier.WORKHORSE])


# Global config instance
_config: Optional[LLMConfig] = None


def get_config() -> LLMConfig:
    """Get or create the global LLM config."""
    global _config
    if _config is None:
        _config = LLMConfig(
            deepseek_api_key=os.getenv("DEEPSEEK_API_KEY", "sk-6de05c4339ab41c4bbeb177c8cddc6a3"),
            ollama_host=os.getenv("OLLAMA_HOST", "http://localhost:11434"),
        )
    return _config


def set_config(config: LLMConfig):
    """Set the global LLM config."""
    global _config
    _config = config


# Task type classification for routing
TASK_ROUTING = {
    # Layer A tasks (Gatekeeper)
    "classify": ModelTier.GATEKEEPER,
    "validate": ModelTier.GATEKEEPER,
    "route": ModelTier.GATEKEEPER,
    "check_schema": ModelTier.GATEKEEPER,
    "detect_pii": ModelTier.GATEKEEPER,
    "simple_extract": ModelTier.GATEKEEPER,
    "yes_no": ModelTier.GATEKEEPER,
    "quick_check": ModelTier.GATEKEEPER,
    
    # Layer B tasks (Workhorse)
    "extract": ModelTier.WORKHORSE,
    "map_data": ModelTier.WORKHORSE,
    "generate_schema": ModelTier.WORKHORSE,
    "tool_call": ModelTier.WORKHORSE,
    "analyze": ModelTier.WORKHORSE,
    "transform": ModelTier.WORKHORSE,
    "summarize": ModelTier.WORKHORSE,
    "code_gen": ModelTier.WORKHORSE,
    
    # Layer C tasks (Orchestrator)
    "orchestrate": ModelTier.ORCHESTRATOR,
    "plan": ModelTier.ORCHESTRATOR,
    "reason": ModelTier.ORCHESTRATOR,
    "narrative": ModelTier.ORCHESTRATOR,
    "complex_analysis": ModelTier.ORCHESTRATOR,
    "multi_step": ModelTier.ORCHESTRATOR,
    "cross_check": ModelTier.ORCHESTRATOR,
    "synthesize": ModelTier.ORCHESTRATOR,
}


def get_tier_for_task(task_type: str) -> ModelTier:
    """Get the appropriate model tier for a task type."""
    return TASK_ROUTING.get(task_type.lower(), ModelTier.WORKHORSE)
