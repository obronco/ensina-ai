"""OpenAI and OpenAI-compatible provider implementation."""
from typing import List, Dict, Optional
from openai import OpenAI
from .base import LLMProvider


class OpenAIProvider(LLMProvider):
    """
    OpenAI and OpenAI-compatible LLM provider.

    Works with:
    - OpenAI API (default)
    - Local Ollama (http://localhost:11434/v1)
    - LM Studio (http://localhost:1234/v1)
    - vLLM (custom endpoint)
    - llama.cpp server
    - Any OpenAI-compatible API
    """

    def __init__(
        self,
        api_key: str = "not-needed-for-local",
        slow_model: str = "gpt-4o",
        fast_model: str = "gpt-4o-mini",
        base_url: Optional[str] = None
    ):
        """
        Initialize OpenAI-compatible provider.

        Args:
            api_key: API key (use "not-needed-for-local" for local servers)
            slow_model: Model for complex tasks
            fast_model: Model for simple tasks
            base_url: Optional base URL for compatible endpoints
                     - None: Use OpenAI (https://api.openai.com/v1)
                     - "http://localhost:11434/v1": Ollama
                     - "http://localhost:1234/v1": LM Studio
                     - Custom: Your own endpoint
        """
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        self.slow_model = slow_model
        self.fast_model = fast_model
        self.base_url = base_url
        self.is_local = base_url is not None and "localhost" in base_url

    def chat(
        self,
        messages: List[Dict[str, str]],
        system: str = None,
        max_tokens: int = 1024,
        model: str = None
    ) -> str:
        """Send messages and get response from OpenAI-compatible API."""
        # OpenAI includes system in messages array
        formatted_messages = []
        if system:
            formatted_messages.append({"role": "system", "content": system})
        formatted_messages.extend(messages)

        response = self.client.chat.completions.create(
            model=model or self.slow_model,
            max_tokens=max_tokens,
            messages=formatted_messages
        )

        return response.choices[0].message.content

    def get_model_info(self) -> Dict:
        """Return model information."""
        provider_type = "local" if self.is_local else "openai"
        return {
            "provider": provider_type,
            "slow_model": self.slow_model,
            "fast_model": self.fast_model,
            "base_url": self.base_url or "https://api.openai.com/v1",
            "supports_system_prompt": True,
            "supports_streaming": True
        }
