"""
PATH: ai/llm/local_provider.py
PURPOSE: Ollama local LLM provider for running models locally

WHY: Run models 24/7 locally for cost optimization. Ollama provides
     easy management of quantized models on consumer hardware.

SUPPORTED MODELS:
- phi3.5:3.8b-mini-instruct-q4_K_M (Layer A - Gatekeeper)
- qwen2.5:7b-instruct-q4_K_M (Layer B - Workhorse)
- mistral:8b-instruct-q4_K_M (Layer C - Orchestrator)
"""

import asyncio
import json
import time
from typing import Any, Dict, List, Optional
import aiohttp

from .provider import LLMProvider, LLMResponse, Message, TokenUsage
from .config import get_config


class OllamaProvider(LLMProvider):
    """
    Ollama local LLM provider.
    
    Runs models locally via Ollama server for 24/7 availability
    without API costs.
    """
    
    def __init__(self, host: Optional[str] = None, timeout: int = 120):
        """
        Initialize Ollama provider.
        
        Args:
            host: Ollama server URL (default from config)
            timeout: Request timeout in seconds
        """
        config = get_config()
        self.host = host or config.ollama_host
        self.timeout = timeout
        self._available_models: Optional[List[str]] = None
        self._last_health_check: float = 0
        self._is_healthy: bool = False
    
    @property
    def name(self) -> str:
        return "ollama"
    
    @property
    def is_available(self) -> bool:
        """Check if Ollama is available (cached for 30 seconds)."""
        if time.time() - self._last_health_check < 30:
            return self._is_healthy
        # Will be updated by health_check
        return self._is_healthy
    
    async def health_check(self) -> bool:
        """Check if Ollama server is running and responsive."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.host}/api/tags",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    self._is_healthy = response.status == 200
                    self._last_health_check = time.time()
                    
                    if self._is_healthy:
                        data = await response.json()
                        self._available_models = [
                            m["name"] for m in data.get("models", [])
                        ]
                    
                    return self._is_healthy
        except Exception:
            self._is_healthy = False
            self._last_health_check = time.time()
            return False
    
    async def list_models(self) -> List[str]:
        """List available models."""
        if self._available_models is None:
            await self.health_check()
        return self._available_models or []
    
    async def pull_model(self, model: str) -> bool:
        """Pull a model if not available."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.host}/api/pull",
                    json={"name": model},
                    timeout=aiohttp.ClientTimeout(total=3600)  # Models can be large
                ) as response:
                    return response.status == 200
        except Exception:
            return False
    
    async def ensure_model(self, model: str) -> bool:
        """Ensure a model is available, pulling if necessary."""
        models = await self.list_models()
        
        # Check exact match or base model match
        model_base = model.split(":")[0]
        for m in models:
            if m == model or m.startswith(model_base):
                return True
        
        # Model not found, try to pull
        return await self.pull_model(model)
    
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
        """
        Generate a response using Ollama.
        
        Args:
            messages: Conversation messages
            model: Model name (e.g., "phi3.5:3.8b-mini-instruct-q4_K_M")
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            tools: Tool definitions (limited support)
            json_mode: Request JSON output format
        """
        start_time = time.perf_counter()
        
        # Convert messages to Ollama format
        ollama_messages = [m.to_dict() for m in messages]
        
        # Build request
        request_data = {
            "model": model,
            "messages": ollama_messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            }
        }
        
        if json_mode:
            request_data["format"] = "json"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.host}/api/chat",
                    json=request_data,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    latency_ms = (time.perf_counter() - start_time) * 1000
                    
                    if response.status != 200:
                        error_text = await response.text()
                        return LLMResponse(
                            content="",
                            model=model,
                            provider=self.name,
                            latency_ms=latency_ms,
                            error=f"Ollama error {response.status}: {error_text}"
                        )
                    
                    data = await response.json()
                    
                    # Extract response
                    message = data.get("message", {})
                    content = message.get("content", "")
                    
                    # Token usage (Ollama provides these)
                    usage = TokenUsage(
                        prompt_tokens=data.get("prompt_eval_count", 0),
                        completion_tokens=data.get("eval_count", 0),
                        total_tokens=data.get("prompt_eval_count", 0) + data.get("eval_count", 0)
                    )
                    
                    return LLMResponse(
                        content=content,
                        model=model,
                        provider=self.name,
                        finish_reason=data.get("done_reason", "stop"),
                        usage=usage,
                        latency_ms=latency_ms,
                        raw=data
                    )
                    
        except asyncio.TimeoutError:
            return LLMResponse(
                content="",
                model=model,
                provider=self.name,
                latency_ms=(time.perf_counter() - start_time) * 1000,
                error=f"Ollama timeout after {self.timeout}s"
            )
        except aiohttp.ClientError as e:
            return LLMResponse(
                content="",
                model=model,
                provider=self.name,
                latency_ms=(time.perf_counter() - start_time) * 1000,
                error=f"Ollama connection error: {str(e)}"
            )
        except Exception as e:
            return LLMResponse(
                content="",
                model=model,
                provider=self.name,
                latency_ms=(time.perf_counter() - start_time) * 1000,
                error=f"Ollama error: {str(e)}"
            )
    
    async def generate_stream(
        self,
        messages: List[Message],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ):
        """
        Generate a streaming response.
        
        Yields chunks of text as they are generated.
        """
        ollama_messages = [m.to_dict() for m in messages]
        
        request_data = {
            "model": model,
            "messages": ollama_messages,
            "stream": True,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            }
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.host}/api/chat",
                    json=request_data,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    async for line in response.content:
                        if line:
                            try:
                                data = json.loads(line)
                                message = data.get("message", {})
                                content = message.get("content", "")
                                if content:
                                    yield content
                                if data.get("done"):
                                    break
                            except json.JSONDecodeError:
                                continue
        except Exception as e:
            yield f"[Error: {str(e)}]"


# Model installation helper
async def setup_dream_models(provider: OllamaProvider) -> Dict[str, bool]:
    """
    Setup the DREAM agent stack models.
    
    Returns dict of model -> success status.
    """
    models = [
        "phi3.5:3.8b-mini-instruct-q4_K_M",  # Layer A
        "qwen2.5:7b-instruct-q4_K_M",         # Layer B
        "mistral:8b-instruct-q4_K_M",         # Layer C
    ]
    
    results = {}
    for model in models:
        results[model] = await provider.ensure_model(model)
    
    return results
