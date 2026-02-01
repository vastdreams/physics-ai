"""
PATH: ai/llm/deepseek_provider.py
PURPOSE: DeepSeek API provider as fallback when local models unavailable

WHY: DeepSeek provides cost-effective API access with strong reasoning
     capabilities. Used as fallback when Ollama/local models are down.

API: https://api.deepseek.com
Models: deepseek-chat, deepseek-coder
"""

import asyncio
import json
import time
from typing import Any, Dict, List, Optional
import aiohttp

from .provider import LLMProvider, LLMResponse, Message, TokenUsage
from .config import get_config


class DeepSeekProvider(LLMProvider):
    """
    DeepSeek API provider.
    
    Provides fallback capability when local models are unavailable.
    Cost-effective with strong reasoning capabilities.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 60
    ):
        """
        Initialize DeepSeek provider.
        
        Args:
            api_key: DeepSeek API key (default from config/env)
            base_url: API base URL
            timeout: Request timeout in seconds
        """
        config = get_config()
        self.api_key = api_key or config.deepseek_api_key
        self.base_url = base_url or config.deepseek_base_url
        self.timeout = timeout
        self._is_healthy: bool = False
        self._last_health_check: float = 0
    
    @property
    def name(self) -> str:
        return "deepseek"
    
    @property
    def is_available(self) -> bool:
        """Check if API key is configured."""
        return bool(self.api_key and self.api_key.startswith("sk-"))
    
    async def health_check(self) -> bool:
        """Check if DeepSeek API is accessible."""
        if not self.is_available:
            return False
        
        try:
            # Simple models list check
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                async with session.get(
                    f"{self.base_url}/models",
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    self._is_healthy = response.status == 200
                    self._last_health_check = time.time()
                    return self._is_healthy
        except Exception:
            self._is_healthy = False
            self._last_health_check = time.time()
            return False
    
    async def generate(
        self,
        messages: List[Message],
        model: str = "deepseek-chat",
        temperature: float = 0.7,
        max_tokens: int = 2048,
        tools: Optional[List[Dict]] = None,
        json_mode: bool = False,
        **kwargs
    ) -> LLMResponse:
        """
        Generate a response using DeepSeek API.
        
        Args:
            messages: Conversation messages
            model: Model name (deepseek-chat or deepseek-coder)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            tools: Tool definitions for function calling
            json_mode: Request JSON output format
        """
        if not self.is_available:
            return LLMResponse(
                content="",
                model=model,
                provider=self.name,
                error="DeepSeek API key not configured"
            )
        
        start_time = time.perf_counter()
        
        # Convert messages to OpenAI-compatible format
        api_messages = [m.to_dict() for m in messages]
        
        # Build request
        request_data = {
            "model": model,
            "messages": api_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }
        
        if json_mode:
            request_data["response_format"] = {"type": "json_object"}
        
        if tools:
            request_data["tools"] = tools
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
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
                            error=f"DeepSeek API error {response.status}: {error_text}",
                            is_fallback=True
                        )
                    
                    data = await response.json()
                    
                    # Extract response
                    choice = data.get("choices", [{}])[0]
                    message = choice.get("message", {})
                    content = message.get("content", "")
                    
                    # Token usage
                    usage_data = data.get("usage", {})
                    usage = TokenUsage(
                        prompt_tokens=usage_data.get("prompt_tokens", 0),
                        completion_tokens=usage_data.get("completion_tokens", 0),
                        total_tokens=usage_data.get("total_tokens", 0)
                    )
                    
                    # Tool calls
                    tool_calls = message.get("tool_calls")
                    
                    return LLMResponse(
                        content=content,
                        model=data.get("model", model),
                        provider=self.name,
                        finish_reason=choice.get("finish_reason", "stop"),
                        usage=usage,
                        latency_ms=latency_ms,
                        tool_calls=tool_calls,
                        raw=data,
                        is_fallback=True
                    )
                    
        except asyncio.TimeoutError:
            return LLMResponse(
                content="",
                model=model,
                provider=self.name,
                latency_ms=(time.perf_counter() - start_time) * 1000,
                error=f"DeepSeek timeout after {self.timeout}s",
                is_fallback=True
            )
        except aiohttp.ClientError as e:
            return LLMResponse(
                content="",
                model=model,
                provider=self.name,
                latency_ms=(time.perf_counter() - start_time) * 1000,
                error=f"DeepSeek connection error: {str(e)}",
                is_fallback=True
            )
        except Exception as e:
            return LLMResponse(
                content="",
                model=model,
                provider=self.name,
                latency_ms=(time.perf_counter() - start_time) * 1000,
                error=f"DeepSeek error: {str(e)}",
                is_fallback=True
            )
    
    async def generate_stream(
        self,
        messages: List[Message],
        model: str = "deepseek-chat",
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ):
        """
        Generate a streaming response from DeepSeek.
        
        Yields chunks of text as they are generated.
        """
        if not self.is_available:
            yield "[Error: DeepSeek API key not configured]"
            return
        
        api_messages = [m.to_dict() for m in messages]
        
        request_data = {
            "model": model,
            "messages": api_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=request_data,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    async for line in response.content:
                        line = line.decode('utf-8').strip()
                        if line.startswith("data: "):
                            data_str = line[6:]
                            if data_str == "[DONE]":
                                break
                            try:
                                data = json.loads(data_str)
                                choice = data.get("choices", [{}])[0]
                                delta = choice.get("delta", {})
                                content = delta.get("content", "")
                                if content:
                                    yield content
                            except json.JSONDecodeError:
                                continue
        except Exception as e:
            yield f"[Error: {str(e)}]"


# Pricing info for cost estimation
DEEPSEEK_PRICING = {
    "deepseek-chat": {
        "input": 0.14,   # $ per 1M tokens
        "output": 0.28,  # $ per 1M tokens
    },
    "deepseek-coder": {
        "input": 0.14,
        "output": 0.28,
    }
}


def estimate_cost(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    """Estimate cost in USD for a request."""
    pricing = DEEPSEEK_PRICING.get(model, DEEPSEEK_PRICING["deepseek-chat"])
    input_cost = (prompt_tokens / 1_000_000) * pricing["input"]
    output_cost = (completion_tokens / 1_000_000) * pricing["output"]
    return input_cost + output_cost
