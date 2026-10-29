"""Tests for model execution backends and auto-detection."""

from unittest.mock import patch

from precog_council.backends.agy import AgyBackend
from precog_council.backends.base import detect_best_backend
from precog_council.backends.claude_cli import ClaudeCliBackend


def test_detect_backend_with_agy():
    with patch("shutil.which", side_effect=lambda cmd: "/opt/bin/agy" if cmd == "agy" else None):
        with patch.dict("os.environ", {}, clear=True):
            backend = detect_best_backend()
            assert isinstance(backend, AgyBackend)


def test_detect_backend_with_claude_cli():
    with patch("shutil.which", side_effect=lambda cmd: "/usr/local/bin/claude" if cmd == "claude" else None):
        with patch.dict("os.environ", {}, clear=True):
            backend = detect_best_backend()
            assert isinstance(backend, ClaudeCliBackend)


def test_agy_backend_command_generation():
    backend = AgyBackend()
    cmd = backend.build_command("claude-opus-5-5-high", "Test Prompt")
    assert cmd == ["agy", "--model", "claude-opus-5-5-high", "-p", "Test Prompt"]


def test_claude_cli_backend_command_generation():
    backend = ClaudeCliBackend()
    cmd = backend.build_command("opus", "Test Prompt")
    assert cmd[0] == "claude"
    assert "-p" in cmd
