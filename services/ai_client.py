import json
import logging
from typing import Optional

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class OpenAIClient:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or getattr(settings, "OPENAI_API_KEY", "")
        self.model = model or getattr(settings, "OPENAI_MODEL", "gpt-4o-mini")
        self.url = "https://api.openai.com/v1/chat/completions"

    def analyze(self, prompt: str, temperature: float = 0.2) -> dict:
        if not self.api_key:
            raise RuntimeError("OpenAI API key is not configured")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": temperature,
            "max_tokens": 400,
        }

        try:
            resp = requests.post(self.url, headers=headers, json=payload, timeout=15)
            resp.raise_for_status()
        except Exception as exc:
            logger.exception("OpenAI request failed")
            raise

        data = resp.json()

        # Safely extract assistant content
        try:
            content = data["choices"][0]["message"]["content"]
        except Exception:
            logger.error("Unexpected OpenAI response: %s", data)
            raise RuntimeError("Unexpected OpenAI response")

        # Try to parse JSON embedded in the response. The model is instructed
        # to return JSON only, but be defensive.
        try:
            return json.loads(content)
        except Exception:
            # Attempt to extract a JSON substring
            start = content.find("{")
            end = content.rfind("}")
            if start != -1 and end != -1 and end > start:
                try:
                    return json.loads(content[start:end+1])
                except Exception:
                    logger.exception("Failed to parse JSON from model content")
            logger.error("Could not parse OpenAI content as JSON: %s", content)
            raise RuntimeError("OpenAI returned non-JSON response")
