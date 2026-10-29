"""Base interface and dispatcher for LLM execution backends."""

from __future__ import annotations

import os
import shutil
from abc import ABC, abstractmethod
from typing import Optional


class BaseBackend(ABC):
    """Abstract interface for querying models."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the backend."""
        pass

    @abstractmethod
    def query(self, model: str, prompt: str, timeout: int = 90) -> str:
        """Execute a prompt against the model and return raw response string."""
        pass


def detect_best_backend(preferred: str = "auto") -> BaseBackend:
    """Auto-detect the most suitable execution backend based on environment."""
    from precog_council.backends.agy import AgyBackend
    from precog_council.backends.claude_cli import ClaudeCliBackend
    from precog_council.backends.direct_api import DirectApiBackend

    pref = preferred.lower()
    if pref == "agy":
        return AgyBackend()
    elif pref == "claude":
        return ClaudeCliBackend()
    elif pref == "direct":
        return DirectApiBackend()

    # Auto detection:
    # 1. Direct API if keys are present
    if any(k in os.environ for k in ["ANTHROPIC_API_KEY", "GEMINI_API_KEY", "OPENAI_API_KEY"]):
        return DirectApiBackend()

    # 2. Check for CLI binaries
    if shutil.which("agy"):
        return AgyBackend()

    if shutil.which("claude"):
        return ClaudeCliBackend()

    # Fallback to direct API
    return DirectApiBackend()
