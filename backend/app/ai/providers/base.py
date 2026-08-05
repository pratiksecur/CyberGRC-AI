from abc import ABC, abstractmethod


class AIProvider(ABC):
    """
    Base interface for all AI providers.
    """

    @abstractmethod
    def generate(
        self,
        prompt: str,
        temperature: float = 0.2,
    ) -> str:
        """
        Generate a response from an AI model.
        """
        pass