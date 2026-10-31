"""Tests for model execution backends and auto-detection."""

import io
import json
import urllib.error
from unittest.mock import MagicMock, patch

import pytest

from precog_council.backends.agy import AgyBackend
from precog_council.backends.base import detect_best_backend
from precog_council.backends.claude_cli import ClaudeCliBackend
from precog_council.backends.direct_api import DirectApiBackend


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


def test_detect_backend_with_api_keys():
    with patch("shutil.which", return_value=None):
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test_key"}, clear=True):
            backend = detect_best_backend()
            assert isinstance(backend, DirectApiBackend)


def test_agy_backend_command_generation():
    backend = AgyBackend()
    cmd = backend.build_command("claude-opus-5-5-high", "Test Prompt")
    assert cmd == ["agy", "--model", "claude-opus-5-5-high", "-p", "Test Prompt"]


def test_claude_cli_backend_command_generation():
    backend = ClaudeCliBackend()
    cmd = backend.build_command("opus", "Test Prompt")
    assert cmd[0] == "claude"
    assert "-p" in cmd


def test_direct_api_anthropic_call():
    backend = DirectApiBackend()
    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps({"content": [{"text": "Anthropic response"}]}).encode("utf-8")
    mock_resp.__enter__.return_value = mock_resp

    with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-ant-test"}):
        with patch("urllib.request.urlopen", return_value=mock_resp):
            res = backend.query("claude-3-opus", "Hello Anthropic")
            assert res == "Anthropic response"


def test_direct_api_gemini_call():
    backend = DirectApiBackend()
    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps(
        {"candidates": [{"content": {"parts": [{"text": "Gemini response"}]}}]}
    ).encode("utf-8")
    mock_resp.__enter__.return_value = mock_resp

    with patch.dict("os.environ", {"GEMINI_API_KEY": "test-gemini-key"}):
        with patch("urllib.request.urlopen", return_value=mock_resp):
            res = backend.query("gemini-1.5-pro", "Hello Gemini")
            assert res == "Gemini response"


def test_direct_api_openai_call():
    backend = DirectApiBackend()
    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps({"choices": [{"message": {"content": "OpenAI response"}}]}).encode("utf-8")
    mock_resp.__enter__.return_value = mock_resp

    with patch.dict("os.environ", {"OPENAI_API_KEY": "sk-test"}):
        with patch("urllib.request.urlopen", return_value=mock_resp):
            res = backend.query("gpt-4o", "Hello OpenAI")
            assert res == "OpenAI response"


def test_direct_api_http_error():
    backend = DirectApiBackend()
    fp = io.BytesIO(b'{"error": "Rate limit exceeded"}')
    http_err = urllib.error.HTTPError("https://api.anthropic.com", 429, "Too Many Requests", {}, fp)

    with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test"}):
        with patch("urllib.request.urlopen", side_effect=http_err):
            with pytest.raises(RuntimeError, match="Anthropic API HTTP 429"):
                backend.query("claude-3-5-sonnet", "Hello")


def test_direct_api_missing_key():
    backend = DirectApiBackend()
    with patch.dict("os.environ", {}, clear=True):
        with pytest.raises(RuntimeError, match="ANTHROPIC_API_KEY not set"):
            backend._call_anthropic("claude-3", "test", 90)
