from dataclasses import dataclass

from openai import OpenAI

from app.config import settings


@dataclass(frozen=True)
class LLMClientConfig:
    provider: str
    model: str
    client: OpenAI


def get_llm_client_config() -> LLMClientConfig:
    """
    Build an OpenAI-compatible chat client for the configured provider.

    Supported providers:
    - openai: OpenAI API
    - nvidia: NVIDIA NIM hosted API endpoint

    The rest of the application can keep using the same chat.completions API.
    """
    provider = settings.llm_provider.lower().strip()

    if provider == "nvidia":
        if not settings.nvidia_api_key:
            raise ValueError("NVIDIA_API_KEY is required when LLM_PROVIDER=nvidia")

        return LLMClientConfig(
            provider="nvidia",
            model=settings.nvidia_model,
            client=OpenAI(
                base_url=settings.nvidia_base_url,
                api_key=settings.nvidia_api_key,
            ),
        )

    if provider == "openai":
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required when LLM_PROVIDER=openai")

        return LLMClientConfig(
            provider="openai",
            model=settings.openai_model,
            client=OpenAI(api_key=settings.openai_api_key),
        )

    raise ValueError(f"Unsupported LLM_PROVIDER: {settings.llm_provider}")
