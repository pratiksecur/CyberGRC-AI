"""
Manual Ollama AI provider smoke test.

This file is intentionally not collected/executed as a pytest test.
Run it directly when Ollama is available:

    python test_ai.py
"""

from app.ai.provider_factory import get_ai_provider


def main():
    provider = get_ai_provider()

    response = provider.generate(
        """
Explain SQL Injection in 5 lines.
"""
    )

    print("\n==============================")
    print("AI RESPONSE")
    print("==============================\n")
    print(response)


if __name__ == "__main__":
    main()