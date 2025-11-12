"""Anthropic Claude provider implementation."""
from typing import List, Dict, Any
from anthropic import Anthropic
from .base import LLMProvider


class AnthropicProvider(LLMProvider):
    """Anthropic Claude LLM provider with vision support."""

    def __init__(self, api_key: str, slow_model: str, fast_model: str):
        """
        Initialize Anthropic provider.

        Args:
            api_key: Anthropic API key
            slow_model: Model for complex tasks (e.g., claude-3-5-sonnet-20241022)
            fast_model: Model for simple tasks (e.g., claude-3-5-haiku-20241022)
        """
        self.client = Anthropic(api_key=api_key)
        self.slow_model = slow_model
        self.fast_model = fast_model

    def chat(
        self,
        messages: List[Dict[str, Any]],
        system: str = None,
        max_tokens: int = 1024,
        model: str = None
    ) -> str:
        """
        Send messages and get response from Claude.

        Supports both text-only and multi-modal (text + images) messages.
        For vision, pass content as list of dicts with type "text" or "image".
        """
        response = self.client.messages.create(
            model=model or self.slow_model,
            max_tokens=max_tokens,
            system=system,
            messages=messages
        )
        return response.content[0].text

    def get_model_info(self) -> Dict:
        """Return model information."""
        return {
            "provider": "anthropic",
            "slow_model": self.slow_model,
            "fast_model": self.fast_model,
            "supports_system_prompt": True,
            "supports_streaming": True,
            "supports_vision": True  # Claude Sonnet and Haiku support vision
        }
