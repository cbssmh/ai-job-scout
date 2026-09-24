import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


def _read_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default

    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ValueError(
        f"{name} must be one of: true, false, 1, 0, yes, no, on, off."
    )


@dataclass(frozen=True)
class Settings:
    provider_analysis_enabled: bool = False
    llm_provider: str = "nvidia"

    openai_api_key: str | None = None
    openai_model: str = "gpt-4.1-mini"

    nvidia_api_key: str | None = None
    nvidia_base_url: str = "https://integrate.api.nvidia.com/v1"
    nvidia_model: str = "z-ai/glm-5.2"


def load_settings() -> Settings:
    provider_analysis_enabled = _read_bool(
        "PROVIDER_ANALYSIS_ENABLED",
        default=False,
    )
    return Settings(
        provider_analysis_enabled=provider_analysis_enabled,
        llm_provider=os.getenv("LLM_PROVIDER", "nvidia"),
        openai_api_key=(
            os.getenv("OPENAI_API_KEY") if provider_analysis_enabled else None
        ),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
        nvidia_api_key=(
            os.getenv("NVIDIA_API_KEY") if provider_analysis_enabled else None
        ),
        nvidia_base_url=os.getenv(
            "NVIDIA_BASE_URL",
            "https://integrate.api.nvidia.com/v1",
        ),
        nvidia_model=os.getenv("NVIDIA_MODEL", "z-ai/glm-5.2"),
    )


settings = load_settings()


def get_settings() -> Settings:
    return settings
