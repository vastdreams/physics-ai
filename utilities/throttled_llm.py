# PATH: utilities/throttled_llm.py
# PURPOSE:
#   - OpenAI-compatible client wrapper with throttling for local LM Studio / llama.cpp
# ROLE IN ARCHITECTURE:
#   - Provides safe, rate-limited LLM access for all agents/critics/chatbot
# MAIN EXPORTS:
#   - ThrottledLLMClient
# NON-RESPONSIBILITIES:
#   - Does NOT manage model serving (handled by LM Studio/llama-server)
# NOTES FOR FUTURE AI:
#   - Adjust max_concurrent/min_delay/max_tokens via config/env
#   - This uses synchronous locks; sufficient for current usage

from __future__ import annotations

import os
import threading
import time
from typing import Any, Dict, List, Optional

from openai import OpenAI

# ---------------------------------------------------------------------------
# Environment variable keys & defaults
# ---------------------------------------------------------------------------
_ENV_BASE_URL = "LM_STUDIO_URL"
_ENV_MODEL = "LM_STUDIO_MODEL"
_ENV_MAX_CONCURRENT = "LM_STUDIO_MAX_CONCURRENT"
_ENV_MIN_DELAY = "LM_STUDIO_MIN_DELAY"
_ENV_MAX_TOKENS = "LM_STUDIO_MAX_TOKENS"

_DEFAULT_BASE_URL = "http://127.0.0.1:8080"
_DEFAULT_MODEL = "DeepSeek-R1-Distill-Qwen-14B"
_DEFAULT_MAX_CONCURRENT = 1
_DEFAULT_MIN_DELAY = 0.5
_DEFAULT_MAX_TOKENS = 512


class ThrottledLLMClient:
    """OpenAI-style client wrapper with simple throttling."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: str = "not-needed",
        model: Optional[str] = None,
        max_concurrent: Optional[int] = None,
        min_delay: Optional[float] = None,
        default_max_tokens: Optional[int] = None,
    ) -> None:
        base_url = (base_url or os.getenv(_ENV_BASE_URL, _DEFAULT_BASE_URL)) + "/v1"
        model = model or os.getenv(_ENV_MODEL, _DEFAULT_MODEL)
        max_concurrent = (
            max_concurrent
            if max_concurrent is not None
            else int(os.getenv(_ENV_MAX_CONCURRENT, str(_DEFAULT_MAX_CONCURRENT)))
        )
        min_delay = (
            min_delay
            if min_delay is not None
            else float(os.getenv(_ENV_MIN_DELAY, str(_DEFAULT_MIN_DELAY)))
        )
        default_max_tokens = (
            default_max_tokens
            if default_max_tokens is not None
            else int(os.getenv(_ENV_MAX_TOKENS, str(_DEFAULT_MAX_TOKENS)))
        )

        self.client = OpenAI(base_url=base_url, api_key=api_key)
        self.model = model
        self._sem = threading.Semaphore(max_concurrent)
        self._lock = threading.Lock()
        self._last_start = 0.0
        self.min_delay = min_delay
        self.default_max_tokens = default_max_tokens
        self._fail_count = 0
        self._circuit_open_until = 0.0
        self._max_failures = int(os.getenv("LLM_CIRCUIT_BREAKER_THRESHOLD", "5"))
        self._cooldown_seconds = float(os.getenv("LLM_CIRCUIT_COOLDOWN", "60"))

    def _respect_rate_limits(self) -> None:
        """Sleep if needed to enforce minimum delay between requests."""
        with self._lock:
            now = time.monotonic()
            elapsed = now - self._last_start
            if elapsed < self.min_delay:
                time.sleep(self.min_delay - elapsed)
            self._last_start = time.monotonic()

    def chat(
        self,
        messages: List[Dict[str, str]],
        max_tokens: Optional[int] = None,
        temperature: float = 0.6,
    ) -> str:
        """Send a chat completion request with throttling, retry, and circuit breaker."""
        max_tokens = max_tokens or self.default_max_tokens

        if time.monotonic() < self._circuit_open_until:
            raise RuntimeError("LLM circuit breaker open — too many failures; try again later")

        last_err = None
        for attempt in range(3):
            try:
                with self._sem:
                    self._respect_rate_limits()
                    completion = self.client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        max_tokens=max_tokens,
                        temperature=temperature,
                    )
                self._fail_count = 0
                return completion.choices[0].message.content
            except Exception as e:
                last_err = e
                self._fail_count += 1
                if self._fail_count >= self._max_failures:
                    self._circuit_open_until = time.monotonic() + self._cooldown_seconds
                if attempt < 2:
                    time.sleep(0.5 * (2 ** attempt))
        raise last_err
