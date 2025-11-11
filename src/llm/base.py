"""Abstract base class for LLM providers."""
from abc import ABC, abstractmethod
from typing import List, Dict


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def chat(
        self,
        messages: List[Dict[str, str]],
        system: str = None,
        max_tokens: int = 1024,
        model: str = None
    ) -> str:
        """
        Send messages and get response.

        Args:
            messages: List of message dicts with 'role' and 'content'
            system: Optional system prompt
            max_tokens: Maximum tokens in response
            model: Optional model override

        Returns:
            Response text
        """
        pass

    @abstractmethod
    def get_model_info(self) -> Dict:
        """
        Return model capabilities and info.

        Returns:
            Dict with model information
        """
        pass
