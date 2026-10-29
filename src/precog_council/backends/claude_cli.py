"""Claude Code CLI backend implementation."""

from __future__ import annotations

import logging
import subprocess
from typing import List

from precog_council.backends.base import BaseBackend

logger = logging.getLogger("precog_council.backends.claude_cli")


class ClaudeCliBackend(BaseBackend):
    """Executes model prompts via Claude Code CLI (`claude -p`)."""

    @property
    def name(self) -> str:
        return "claude_cli"

    def build_command(self, model: str, prompt: str) -> List[str]:
        # Claude CLI supports -p / --print.
        cmd = ["claude", "-p", prompt]
        if model and model not in ["inherit", "default", "auto"]:
            # If model flag is supported
            cmd.extend(["--model", model])
        return cmd

    def query(self, model: str, prompt: str, timeout: int = 90) -> str:
        cmd = self.build_command(model, prompt)
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            if proc.returncode == 0:
                return proc.stdout
            else:
                logger.warning("claude CLI returned exit code %d: %s", proc.returncode, proc.stderr)
                raise RuntimeError(f"claude CLI error (code {proc.returncode}): {proc.stderr.strip()}")
        except subprocess.TimeoutExpired:
            raise TimeoutError(f"Model query timed out after {timeout}s via claude CLI")
