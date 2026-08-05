from app.ai.provider_factory import get_ai_provider


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