import os

from app.ai.providers.ollama_provider import OllamaProvider


def get_ai_provider():
    """
    Return the configured AI provider.
    """

    provider = os.getenv(
        "AI_PROVIDER",
        "ollama"
    ).lower()

    if provider == "ollama":
        return OllamaProvider()

    raise ValueError(
        f"Unsupported AI provider: {provider}"
    )