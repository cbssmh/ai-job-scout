from dataclasses import dataclass

from openai import OpenAI

from app.config import Settings, settings


@dataclass(frozen=True)
class LLMClientConfig:
    provider: str
    model: str
    client: OpenAI


def _require_config_value(value: str | None, name: str, provider: str) -> str:
    if not value or not value.strip():
        raise ValueError(
            f"{name} is missing. Set {name} in .env before using the {provider} provider."
        )
    return value.strip()


def get_llm_client_config(config: Settings | None = None) -> LLMClientConfig:
    """
    Build an OpenAI-compatible chat client for the configured provider.

    Supported providers:
    - openai: OpenAI API
    - nvidia: NVIDIA NIM hosted API endpoint

    The rest of the application can keep using the same chat.completions API.
    """
    config = config or settings
    provider = config.llm_provider.lower().strip()

    if provider == "nvidia":
        api_key = _require_config_value(
            config.nvidia_api_key,
            "NVIDIA_API_KEY",
            "NVIDIA",
        )
        model = _require_config_value(
            config.nvidia_model,
            "NVIDIA_MODEL",
            "NVIDIA",
        )
        base_url = _require_config_value(
            config.nvidia_base_url,
            "NVIDIA_BASE_URL",
            "NVIDIA",
        )

        return LLMClientConfig(
            provider="nvidia",
            model=model,
            client=OpenAI(
                base_url=base_url,
                api_key=api_key,
            ),
        )

    if provider == "openai":
        api_key = _require_config_value(
            config.openai_api_key,
            "OPENAI_API_KEY",
            "OpenAI",
        )
        model = _require_config_value(
            config.openai_model,
            "OPENAI_MODEL",
            "OpenAI",
        )

        return LLMClientConfig(
            provider="openai",
            model=model,
            client=OpenAI(api_key=api_key),
        )

    raise ValueError(
        f"Unsupported LLM_PROVIDER '{config.llm_provider}'. "
        "Set LLM_PROVIDER to one of: openai, nvidia."
    )
