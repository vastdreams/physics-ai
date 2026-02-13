# PATH: substrate/critics/local_llm.py
# PURPOSE:
#   - Interface to local LLM (DeepSeek or similar)
#   - Abstracts the local inference process
#   - Supports multiple backends (llama.cpp, vLLM, transformers, etc.)
#
# ROLE IN ARCHITECTURE:
#   - Foundation for all critic operations
#   - Provides structured generation and validation
#
# MAIN EXPORTS:
#   - LocalLLMBackend: Main interface class
#   - LLMConfig: Configuration dataclass
#
# NON-RESPONSIBILITIES:
#   - Does NOT implement specific critic logic (that's in critic classes)
#   - Does NOT handle training (inference only)
#
# NOTES FOR FUTURE AI:
#   - Add new backends by implementing generate() method
#   - Keep prompts structured and parseable
#   - Log all generations for audit

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Union
from datetime import datetime
from enum import Enum, auto
import json
import subprocess
import os
import time
import logging
from abc import ABC, abstractmethod
from utilities.throttled_llm import ThrottledLLMClient

logger = logging.getLogger(__name__)


class LLMBackendType(Enum):
    """Supported LLM backends."""
    MOCK = auto()           # For testing
    SUBPROCESS = auto()     # Call external process (llama.cpp, ollama, etc.)
    TRANSFORMERS = auto()   # HuggingFace transformers
    VLLM = auto()           # vLLM server
    OPENAI_COMPATIBLE = auto()  # OpenAI-compatible API (local or remote)
    THROTTLED_OPENAI = auto()   # OpenAI-compatible with throttling wrapper


@dataclass
class LLMConfig:
    """Configuration for local LLM."""
    
    # Backend selection
    backend_type: LLMBackendType = LLMBackendType.MOCK
    
    # Model specification
    model_path: Optional[str] = None  # Path to model weights
    model_name: str = "deepseek-coder"  # Model identifier
    
    # Generation parameters
    max_tokens: int = 2048
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 40
    repeat_penalty: float = 1.1
    
    # Server settings (for VLLM/OpenAI-compatible)
    server_url: str = os.getenv("LLM_SERVER_URL", "http://localhost:8000")
    api_key: Optional[str] = os.getenv("LLM_API_KEY")
    
    # Subprocess settings
    executable_path: Optional[str] = None  # Path to llama.cpp main, ollama, etc.
    extra_args: List[str] = field(default_factory=list)
    
    # Resource limits
    n_gpu_layers: int = -1  # -1 = all layers on GPU
    n_ctx: int = 4096       # Context window size
    n_batch: int = 512      # Batch size for prompt processing
    
    # Timeouts
    generation_timeout: float = 120.0  # seconds

    # Throttling (for THROTTLED_OPENAI)
    throttle_max_concurrent: int = 1
    throttle_min_delay: float = 0.5
    throttle_default_max_tokens: int = 512
    
    def to_dict(self) -> Dict[str, Any]:
        d = {
            "backend_type": self.backend_type.name,
            "model_path": self.model_path,
            "model_name": self.model_name,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "top_k": self.top_k,
            "repeat_penalty": self.repeat_penalty,
            "server_url": self.server_url,
            "n_gpu_layers": self.n_gpu_layers,
            "n_ctx": self.n_ctx,
            "n_batch": self.n_batch,
            "generation_timeout": self.generation_timeout,
        }
        return d


@dataclass
class LLMResponse:
    """Response from LLM generation."""
    
    text: str
    finish_reason: str = "stop"  # "stop", "length", "error"
    
    # Token counts
    prompt_tokens: int = 0
    completion_tokens: int = 0
    
    # Timing
    generation_time_ms: float = 0.0
    
    # Metadata
    model_name: str = ""
    raw_response: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "finish_reason": self.finish_reason,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "generation_time_ms": self.generation_time_ms,
            "model_name": self.model_name,
        }


class LocalLLMBackend(ABC):
    """
    Abstract base class for local LLM backends.
    
    Provides a unified interface for generating text from local LLMs.
    Subclasses implement specific backends (subprocess, transformers, etc.).
    """
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self._generation_count = 0
        self._total_tokens = 0
        self._total_time_ms = 0.0
        self._history: List[Dict[str, Any]] = []
    
    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        stop_sequences: Optional[List[str]] = None,
    ) -> LLMResponse:
        """
        Generate text from the LLM.
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt
            max_tokens: Override max tokens
            temperature: Override temperature
            stop_sequences: Sequences that stop generation
            
        Returns:
            LLMResponse with generated text
        """
        pass
    
    def generate_structured(
        self,
        prompt: str,
        schema: Dict[str, Any],
        system_prompt: Optional[str] = None,
        max_retries: int = 3,
    ) -> Optional[Dict[str, Any]]:
        """
        Generate structured output matching a JSON schema.
        
        Args:
            prompt: The user prompt
            schema: JSON schema for expected output
            system_prompt: Optional system prompt
            max_retries: Number of retries on parse failure
            
        Returns:
            Parsed JSON dict or None on failure
        """
        schema_str = json.dumps(schema, indent=2)
        full_prompt = f"""{prompt}

Respond with valid JSON matching this schema:
{schema_str}

JSON response:"""
        
        for attempt in range(max_retries):
            response = self.generate(
                prompt=full_prompt,
                system_prompt=system_prompt,
                stop_sequences=["```", "\n\n\n"],
            )
            
            try:
                # Try to extract JSON from response
                text = response.text.strip()
                
                # Handle markdown code blocks
                if text.startswith("```json"):
                    text = text[7:]
                if text.startswith("```"):
                    text = text[3:]
                if text.endswith("```"):
                    text = text[:-3]
                
                result = json.loads(text.strip())
                return result
            except json.JSONDecodeError as e:
                logger.warning(f"JSON parse failed (attempt {attempt + 1}): {e}")
                continue
        
        return None
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> LLMResponse:
        """
        Chat-style generation with message history.
        
        Args:
            messages: List of {"role": "user"|"assistant"|"system", "content": str}
            max_tokens: Override max tokens
            temperature: Override temperature
            
        Returns:
            LLMResponse with assistant's reply
        """
        # Build prompt from messages
        prompt_parts = []
        system_prompt = None
        
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            if role == "system":
                system_prompt = content
            elif role == "user":
                prompt_parts.append(f"User: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
        
        prompt_parts.append("Assistant:")
        prompt = "\n\n".join(prompt_parts)
        
        return self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
        )
    
    def _record_generation(self, prompt: str, response: LLMResponse):
        """Record generation for statistics and audit."""
        self._generation_count += 1
        self._total_tokens += response.prompt_tokens + response.completion_tokens
        self._total_time_ms += response.generation_time_ms
        
        self._history.append({
            "timestamp": datetime.now().isoformat(),
            "prompt_preview": prompt[:200] + "..." if len(prompt) > 200 else prompt,
            "response_preview": response.text[:200] + "..." if len(response.text) > 200 else response.text,
            "tokens": response.prompt_tokens + response.completion_tokens,
            "time_ms": response.generation_time_ms,
        })
        
        # Keep history bounded
        if len(self._history) > 1000:
            self._history = self._history[-500:]
    
    def statistics(self) -> Dict[str, Any]:
        """Get generation statistics."""
        return {
            "generation_count": self._generation_count,
            "total_tokens": self._total_tokens,
            "total_time_ms": self._total_time_ms,
            "avg_tokens_per_gen": self._total_tokens / max(1, self._generation_count),
            "avg_time_per_gen_ms": self._total_time_ms / max(1, self._generation_count),
        }


class MockLLMBackend(LocalLLMBackend):
    """
    Mock LLM backend for testing.
    
    Returns predefined responses or simple transformations of input.
    """
    
    def __init__(self, config: LLMConfig, responses: Optional[Dict[str, str]] = None):
        super().__init__(config)
        self._responses = responses or {}
        self._default_response = "This is a mock response."
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        stop_sequences: Optional[List[str]] = None,
    ) -> LLMResponse:
        start_time = time.time()
        
        # Check for predefined response
        for key, response_text in self._responses.items():
            if key.lower() in prompt.lower():
                text = response_text
                break
        else:
            # Generate a simple mock response
            text = self._generate_mock(prompt, system_prompt)
        
        # Simulate some latency
        time.sleep(0.01)
        
        elapsed_ms = (time.time() - start_time) * 1000
        
        response = LLMResponse(
            text=text,
            finish_reason="stop",
            prompt_tokens=len(prompt.split()),
            completion_tokens=len(text.split()),
            generation_time_ms=elapsed_ms,
            model_name="mock",
        )
        
        self._record_generation(prompt, response)
        return response
    
    def _generate_mock(self, prompt: str, system_prompt: Optional[str]) -> str:
        """Generate a mock response based on prompt content."""
        prompt_lower = prompt.lower()
        
        if "error" in prompt_lower or "issue" in prompt_lower:
            return json.dumps({
                "issues": [
                    {"type": "mock_issue", "severity": "warning", "message": "Mock issue detected"}
                ],
                "suggestions": ["Consider reviewing the implementation"]
            })
        
        if "validate" in prompt_lower or "check" in prompt_lower:
            return json.dumps({
                "valid": True,
                "confidence": 0.95,
                "notes": "Mock validation passed"
            })
        
        if "analyze" in prompt_lower or "review" in prompt_lower:
            return json.dumps({
                "analysis": "Mock analysis complete",
                "findings": [],
                "recommendations": []
            })
        
        return self._default_response
    
    def set_response(self, key: str, response: str):
        """Set a predefined response for a key."""
        self._responses[key] = response


class SubprocessLLMBackend(LocalLLMBackend):
    """
    LLM backend using subprocess calls.
    
    Supports llama.cpp, ollama, and other CLI-based inference tools.
    """
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        if not config.executable_path:
            raise ValueError("executable_path required for subprocess backend")
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        stop_sequences: Optional[List[str]] = None,
    ) -> LLMResponse:
        max_tokens = max_tokens or self.config.max_tokens
        temperature = temperature or self.config.temperature
        
        # Build command
        cmd = [
            self.config.executable_path,
            "-m", self.config.model_path,
            "-n", str(max_tokens),
            "--temp", str(temperature),
            "-c", str(self.config.n_ctx),
            "-ngl", str(self.config.n_gpu_layers),
        ]
        
        # Add prompt
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"System: {system_prompt}\n\n{prompt}"
        
        cmd.extend(["-p", full_prompt])
        cmd.extend(self.config.extra_args)
        
        start_time = time.time()
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.config.generation_timeout,
            )
            text = result.stdout
            finish_reason = "stop"
        except subprocess.TimeoutExpired:
            text = ""
            finish_reason = "timeout"
        except Exception as e:
            text = f"Error: {str(e)}"
            finish_reason = "error"
        
        elapsed_ms = (time.time() - start_time) * 1000
        
        response = LLMResponse(
            text=text,
            finish_reason=finish_reason,
            generation_time_ms=elapsed_ms,
            model_name=self.config.model_name,
        )
        
        self._record_generation(prompt, response)
        return response


class OpenAICompatibleBackend(LocalLLMBackend):
    """
    LLM backend using OpenAI-compatible API.
    
    Works with local servers (vLLM, LocalAI, text-generation-webui)
    or remote APIs that follow the OpenAI format.
    """
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        try:
            import requests
            self._requests = requests
        except ImportError:
            raise ImportError("requests package required for OpenAI-compatible backend")
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        stop_sequences: Optional[List[str]] = None,
    ) -> LLMResponse:
        max_tokens = max_tokens or self.config.max_tokens
        temperature = temperature or self.config.temperature
        
        # Build messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        # Build request
        payload = {
            "model": self.config.model_name,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": self.config.top_p,
        }
        
        if stop_sequences:
            payload["stop"] = stop_sequences
        
        headers = {"Content-Type": "application/json"}
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"
        
        start_time = time.time()
        
        try:
            response = self._requests.post(
                f"{self.config.server_url}/v1/chat/completions",
                json=payload,
                headers=headers,
                timeout=self.config.generation_timeout,
            )
            response.raise_for_status()
            data = response.json()
            
            text = data["choices"][0]["message"]["content"]
            finish_reason = data["choices"][0].get("finish_reason", "stop")
            prompt_tokens = data.get("usage", {}).get("prompt_tokens", 0)
            completion_tokens = data.get("usage", {}).get("completion_tokens", 0)
            
        except Exception as e:
            text = f"Error: {str(e)}"
            finish_reason = "error"
            prompt_tokens = 0
            completion_tokens = 0
            data = None
        
        elapsed_ms = (time.time() - start_time) * 1000
        
        llm_response = LLMResponse(
            text=text,
            finish_reason=finish_reason,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            generation_time_ms=elapsed_ms,
            model_name=self.config.model_name,
            raw_response=data,
        )
        
        self._record_generation(prompt, llm_response)
        return llm_response


class ThrottledOpenAIBackend(LocalLLMBackend):
    """
    OpenAI-compatible backend with throttling (for LM Studio / llama-server).
    """

    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self._client = ThrottledLLMClient(
            base_url=config.server_url.rstrip("/"),
            api_key=config.api_key or "not-needed",
            model=config.model_name,
            max_concurrent=config.throttle_max_concurrent,
            min_delay=config.throttle_min_delay,
            default_max_tokens=config.throttle_default_max_tokens,
        )

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        stop_sequences: Optional[List[str]] = None,
    ) -> LLMResponse:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        start_time = time.time()
        text = self._client.chat(messages, max_tokens=max_tokens)
        elapsed_ms = (time.time() - start_time) * 1000

        response = LLMResponse(
            text=text,
            finish_reason="stop",
            generation_time_ms=elapsed_ms,
            model_name=self.config.model_name,
        )
        self._record_generation(prompt, response)
        return response


def create_llm_backend(config: LLMConfig) -> LocalLLMBackend:
    """Factory function to create appropriate backend based on config."""
    if config.backend_type == LLMBackendType.MOCK:
        return MockLLMBackend(config)
    elif config.backend_type == LLMBackendType.SUBPROCESS:
        return SubprocessLLMBackend(config)
    elif config.backend_type == LLMBackendType.OPENAI_COMPATIBLE:
        return OpenAICompatibleBackend(config)
    elif config.backend_type == LLMBackendType.THROTTLED_OPENAI:
        return ThrottledOpenAIBackend(config)
    else:
        raise ValueError(f"Unsupported backend type: {config.backend_type}")

