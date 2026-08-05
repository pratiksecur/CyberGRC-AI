import logging
import os

import httpx

from app.ai.providers.base import AIProvider


logger = logging.getLogger(__name__)


class OllamaProvider(AIProvider):
    """
    Ollama AI Provider.
    Handles communication with the local Ollama server.
    """

    BASE_URL = os.getenv(
        "OLLAMA_BASE_URL",
        "http://localhost:11434/api/generate"
    )

    MODEL = os.getenv(
        "OLLAMA_MODEL",
        "mistral"
    )

    def generate(
        self,
        prompt: str,
        temperature: float = 0.2,
    ) -> str:
        """
        Send a prompt to the Ollama API and return the generated response.
        """

        payload = {
            "model": self.MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature
            }
        }

        logger.info(
            "Sending request to Ollama model '%s'",
            self.MODEL
        )

        try:
            response = httpx.post(
                self.BASE_URL,
                json=payload,
                timeout=120,
            )

            response.raise_for_status()

            logger.info(
                "Received successful response from Ollama."
            )

            return response.json()["response"]

        except httpx.HTTPError as e:

            logger.error(
                "Failed to communicate with Ollama: %s",
                e
            )

            raise RuntimeError(
                f"Failed to communicate with Ollama: {e}"
            )