# PATH: substrate/critics/__init__.py
# PURPOSE:
#   - Package for the multi-LLM audit stack
#   - Contains LocalLLMBackend and specialized critics

from substrate.critics.local_llm import LocalLLMBackend, LLMConfig
from substrate.critics.logic_critic import LogicCritic
from substrate.critics.code_critic import CodeCritic
from substrate.critics.meta_critic import MetaCritic

__all__ = [
    "LocalLLMBackend",
    "LLMConfig",
    "LogicCritic",
    "CodeCritic",
    "MetaCritic",
]

