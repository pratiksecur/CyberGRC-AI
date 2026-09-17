"""Ollama AI provider with security and governance controls."""

import logging
import os

import httpx

from app.ai.governance import (
    AIGovernanceError,
    record_ai_event,
    secure_prompt,
    validate_raw_response,
)
from app.ai.providers.base import AIProvider


logger = logging.getLogger(__name__)


class OllamaProvider(AIProvider):
    """Ollama provider protected by the AI governance boundary."""

    def __init__(self):
        self.base_url = os.getenv(
            "OLLAMA_BASE_URL",
            "http://localhost:11434/api/generate",
        )

        self.model = os.getenv(
            "OLLAMA_MODEL",
            "mistral",
        )

        try:
            self.timeout = float(
                os.getenv(
                    "OLLAMA_TIMEOUT",
                    "120",
                )
            )
        except ValueError:
            self.timeout = 120.0

    def generate(
        self,
        prompt: str,
        temperature: float = 0.2,
    ) -> str:
        try:
            secured_prompt = secure_prompt(prompt)

        except AIGovernanceError:
            record_ai_event(
                "generate",
                model=self.model,
                outcome="rejected",
                validation="prompt",
            )
            raise

        payload = {
            "model": self.model,
            "prompt": secured_prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
            },
        }

        logger.info(
            "AI request started provider=ollama model=%s",
            self.model,
        )

        try:
            response = httpx.post(
                self.base_url,
                json=payload,
                timeout=self.timeout,
            )

            response.raise_for_status()

            body = response.json()

            if not isinstance(body, dict):
                raise AIGovernanceError(
                    "AI provider returned an invalid response."
                )

            generated = validate_raw_response(
                body.get("response")
            )

            record_ai_event(
                "generate",
                model=self.model,
                outcome="success",
                validation="provider_response",
            )

            return generated

        except AIGovernanceError:
            record_ai_event(
                "generate",
                model=self.model,
                outcome="rejected",
                validation="provider_response",
            )
            raise

        except (
            httpx.HTTPError,
            ValueError,
            KeyError,
            TypeError,
        ):
            record_ai_event(
                "generate",
                model=self.model,
                outcome="failure",
                validation="provider_response",
            )

            logger.error(
                "Ollama request failed without exposing provider details"
            )

            raise RuntimeError(
                "AI provider request failed."
            ) from None