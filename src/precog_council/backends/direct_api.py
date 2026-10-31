"""Direct REST API backend using standard library (urllib)."""

from __future__ import annotations

import json
import logging
import os
import urllib.error
import urllib.request

from precog_council.backends.base import BaseBackend

logger = logging.getLogger("precog_council.backends.direct_api")


class DirectApiBackend(BaseBackend):
    """Directly queries Anthropic, Google Gemini, or OpenAI REST APIs via environment variables."""

    @property
    def name(self) -> str:
        return "direct_api"

    def query(self, model: str, prompt: str, timeout: int = 90) -> str:
        m_lower = model.lower()

        # Route by model prefix or available keys
        if "claude" in m_lower or "anthropic" in m_lower or "opus" in m_lower or "sonnet" in m_lower:
            return self._call_anthropic(model, prompt, timeout)
        elif "gemini" in m_lower or "argon" in m_lower or "flash" in m_lower:
            return self._call_gemini(model, prompt, timeout)
        elif "gpt" in m_lower or "openai" in m_lower:
            return self._call_openai(model, prompt, timeout)

        # Fallback based on keys
        if os.getenv("ANTHROPIC_API_KEY"):
            return self._call_anthropic(model, prompt, timeout)
        elif os.getenv("GEMINI_API_KEY"):
            return self._call_gemini(model, prompt, timeout)
        elif os.getenv("OPENAI_API_KEY"):
            return self._call_openai(model, prompt, timeout)

        raise RuntimeError("No API keys found in environment (ANTHROPIC_API_KEY, GEMINI_API_KEY, OPENAI_API_KEY).")

    def _call_anthropic(self, model: str, prompt: str, timeout: int) -> str:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY not set.")

        # Resolve concrete model or fallback to robust defaults
        resolved = model
        if model in ["inherit", "default", "claude", "sonnet"] or "sonnet" in model.lower():
            resolved = "claude-3-5-sonnet-20241022"
        elif "opus" in model.lower():
            resolved = "claude-3-opus-20240229"

        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        payload = {
            "model": resolved,
            "max_tokens": 4096,
            "messages": [{"role": "user", "content": prompt}],
        }

        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return str(data["content"][0]["text"])
        except (KeyError, IndexError, TypeError) as e:
            raise RuntimeError(f"Anthropic API returned unexpected response structure: {e}")
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Anthropic API HTTP {e.code}: {err_body}")
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            raise RuntimeError(f"Anthropic API connection error: {e}")

    def _call_gemini(self, model: str, prompt: str, timeout: int) -> str:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY not set.")

        resolved = model
        if model in ["inherit", "default", "gemini", "flash"] or "flash" in model.lower():
            resolved = "gemini-1.5-flash"
        elif "pro" in model.lower() or "argon" in model.lower():
            resolved = "gemini-1.5-pro"

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{resolved}:generateContent?key={api_key}"
        headers = {"content-type": "application/json"}
        payload = {"contents": [{"parts": [{"text": prompt}]}]}

        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return str(data["candidates"][0]["content"]["parts"][0]["text"])
        except (KeyError, IndexError, TypeError) as e:
            raise RuntimeError(f"Gemini API returned unexpected response structure: {e}")
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Gemini API HTTP {e.code}: {err_body}")
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            raise RuntimeError(f"Gemini API connection error: {e}")

    def _call_openai(self, model: str, prompt: str, timeout: int) -> str:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY not set.")

        resolved = "gpt-4o" if model in ["inherit", "default", "gpt", "openai"] else model

        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": resolved,
            "max_tokens": 4096,
            "messages": [{"role": "user", "content": prompt}],
        }

        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return str(data["choices"][0]["message"]["content"])
        except (KeyError, IndexError, TypeError) as e:
            raise RuntimeError(f"OpenAI API returned unexpected response structure: {e}")
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"OpenAI API HTTP {e.code}: {err_body}")
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            raise RuntimeError(f"OpenAI API connection error: {e}")
