"""Antigravity CLI (agy) backend implementation."""

from __future__ import annotations

import logging
import subprocess
from typing import List
from precog_council.backends.base import BaseBackend

logger = logging.getLogger("precog_council.backends.agy")


class AgyBackend(BaseBackend):
    """Executes model prompts via Google Antigravity CLI."""

    @property
    def name(self) -> str:
        return "agy_cli"

    def build_command(self, model: str, prompt: str) -> List[str]:
        # Handle inherit or generic aliases
        resolved_model = model
        if model in ["inherit", "default", ""]:
            resolved_model = "gemini-3.8-flash-high"
        return ["agy", "--model", resolved_model, "-p", prompt]

    def query(self, model: str, prompt: str, timeout: int = 90) -> str:
        cmd = self.build_command(model, prompt)
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            if proc.returncode == 0:
                return proc.stdout
            else:
                logger.warning("agy returned exit code %d: %s", proc.returncode, proc.stderr)
                raise RuntimeError(f"agy error (code {proc.returncode}): {proc.stderr.strip()}")
        except subprocess.TimeoutExpired:
            raise TimeoutError(f"Model {model} timed out after {timeout}s via agy")
