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


class ThrottledLLMClient:
    """OpenAI-style client wrapper with simple throttling."""

    def __init__(
        self,
        base_url: str = None,
        api_key: str = "not-needed",
        model: str = None,
        max_concurrent: int = None,
        min_delay: float = None,
        default_max_tokens: int = None,
    ) -> None:
        base_url = base_url or os.getenv("LM_STUDIO_URL", "http://127.0.0.1:8080") + "/v1"
        model = model or os.getenv("LM_STUDIO_MODEL", "DeepSeek-R1-Distill-Qwen-14B")
        max_concurrent = max_concurrent if max_concurrent is not None else int(os.getenv("LM_STUDIO_MAX_CONCURRENT", "1"))
        min_delay = min_delay if min_delay is not None else float(os.getenv("LM_STUDIO_MIN_DELAY", "0.5"))
        default_max_tokens = default_max_tokens if default_max_tokens is not None else int(os.getenv("LM_STUDIO_MAX_TOKENS", "512"))
        self.client = OpenAI(base_url=base_url, api_key=api_key)
        self.model = model
        self._sem = threading.Semaphore(max_concurrent)
        self._lock = threading.Lock()
        self._last_start = 0.0
        self.min_delay = min_delay
        self.default_max_tokens = default_max_tokens

    def _respect_rate_limits(self) -> None:
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
        """Send a chat completion request with throttling."""
        max_tokens = max_tokens or self.default_max_tokens

        with self._sem:
            self._respect_rate_limits()
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )
        return completion.choices[0].message.content

