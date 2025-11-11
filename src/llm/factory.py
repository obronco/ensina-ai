"""Factory for creating LLM providers."""
from typing import Optional
from .anthropic_provider import AnthropicProvider
from .openai_provider import OpenAIProvider


def create_llm_provider(
    provider_type: str,
    anthropic_api_key: Optional[str] = None,
    openai_api_key: Optional[str] = None,
    openai_base_url: Optional[str] = None,
    slow_model: str = None,
    fast_model: str = None
):
    """
    Factory to create LLM providers.

    Args:
        provider_type: "anthropic" or "openai"
        anthropic_api_key: Anthropic API key (required for anthropic)
        openai_api_key: OpenAI API key (or "not-needed-for-local")
        openai_base_url: Optional base URL for OpenAI-compatible endpoints
        slow_model: Model for complex tasks
        fast_model: Model for simple tasks

    Returns:
        LLMProvider instance

    Examples:
        # Anthropic (default)
        provider = create_llm_provider(
            "anthropic",
            anthropic_api_key="sk-ant-...",
            slow_model="claude-3-5-sonnet-20241022",
            fast_model="claude-3-5-haiku-20241022"
        )

        # OpenAI
        provider = create_llm_provider(
            "openai",
            openai_api_key="sk-...",
            slow_model="gpt-4o",
            fast_model="gpt-4o-mini"
        )

        # Local Ollama
        provider = create_llm_provider(
            "openai",
            openai_api_key="not-needed-for-local",
            openai_base_url="http://localhost:11434/v1",
            slow_model="llama3:70b",
            fast_model="llama3:8b"
        )

        # LM Studio
        provider = create_llm_provider(
            "openai",
            openai_api_key="not-needed-for-local",
            openai_base_url="http://localhost:1234/v1",
            slow_model="local-model",
            fast_model="local-model"
        )
    """
    if provider_type == "anthropic":
        if not anthropic_api_key:
            raise ValueError("anthropic_api_key is required for Anthropic provider")
        if not slow_model:
            slow_model = "claude-3-5-sonnet-20241022"
        if not fast_model:
            fast_model = "claude-3-5-haiku-20241022"

        return AnthropicProvider(
            api_key=anthropic_api_key,
            slow_model=slow_model,
            fast_model=fast_model
        )

    elif provider_type == "openai":
        if not openai_api_key:
            # Use dummy key for local endpoints
            openai_api_key = "not-needed-for-local" if openai_base_url else None
        if not openai_api_key:
            raise ValueError("openai_api_key is required for OpenAI provider")

        # Set sensible defaults based on whether it's local or cloud
        if openai_base_url and "localhost" in openai_base_url:
            # Local endpoint - use whatever models the user specified
            if not slow_model:
                slow_model = "llama3:70b"  # Common Ollama model
            if not fast_model:
                fast_model = "llama3:8b"
        else:
            # Cloud OpenAI
            if not slow_model:
                slow_model = "gpt-4o"
            if not fast_model:
                fast_model = "gpt-4o-mini"

        return OpenAIProvider(
            api_key=openai_api_key,
            slow_model=slow_model,
            fast_model=fast_model,
            base_url=openai_base_url
        )

    else:
        raise ValueError(
            f"Unknown provider type: {provider_type}. "
            f"Supported: 'anthropic', 'openai'"
        )
