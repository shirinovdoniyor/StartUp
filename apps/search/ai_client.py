"""Thin OpenAI chat-completions client used by AI search."""

import json
import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class OpenAIClient:
    def __init__(self, api_key=None, model=None):
        self.api_key = api_key or getattr(settings, "OPENAI_API_KEY", "")
        self.model = model or getattr(settings, "OPENAI_MODEL", "gpt-4o-mini")
        self.url = "https://api.openai.com/v1/chat/completions"

    def analyze(self, prompt: str, temperature: float = 0.2) -> dict:
        if not self.api_key:
            raise RuntimeError("OpenAI API key is not configured")

        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": 400,
        }
        resp = requests.post(self.url, headers=headers, json=payload, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError):
            logger.error("Unexpected OpenAI response: %s", data)
            raise RuntimeError("Unexpected OpenAI response")

        return self._parse_json(content)

    @staticmethod
    def _parse_json(content: str) -> dict:
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            start, end = content.find("{"), content.rfind("}")
            if start != -1 and end > start:
                try:
                    return json.loads(content[start : end + 1])
                except json.JSONDecodeError:
                    pass
        raise RuntimeError("OpenAI returned non-JSON response")
