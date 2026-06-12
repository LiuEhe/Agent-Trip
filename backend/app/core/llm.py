from __future__ import annotations

from app.core.config import settings


def get_chat_llm(*, temperature: float | None = None):
    """Create a chat model from project settings."""
    provider = settings.LLM_PROVIDER.lower()
    model_name = settings.LLM_MODEL_NAME
    model_temperature = settings.LLM_TEMPERATURE if temperature is None else temperature

    if provider == "openai":
        from langchain_openai import ChatOpenAI

        if not settings.OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY is not configured in .env")

        return ChatOpenAI(
            model=model_name,
            temperature=model_temperature,
            api_key=settings.OPENAI_API_KEY,
        )

    if provider == "anthropic":
        try:
            from langchain_anthropic import ChatAnthropic
        except ImportError as exc:
            raise RuntimeError(
                "LLM_PROVIDER is anthropic, but langchain-anthropic is not installed"
            ) from exc

        if not settings.ANTHROPIC_API_KEY:
            raise RuntimeError("ANTHROPIC_API_KEY is not configured in .env")

        return ChatAnthropic(
            model=model_name,
            temperature=model_temperature,
            api_key=settings.ANTHROPIC_API_KEY,
        )

    raise ValueError(f"Unsupported LLM_PROVIDER: {settings.LLM_PROVIDER}")
