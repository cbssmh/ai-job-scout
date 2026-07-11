import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # Provider switch for portfolio/demo use.
    # Available values: "openai" or "nvidia".
    llm_provider: str = os.getenv("LLM_PROVIDER", "openai")

    # OpenAI provider settings.
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

    # NVIDIA NIM provider settings.
    # NVIDIA hosted NIM APIs are OpenAI-compatible, so the same SDK can be reused.
    nvidia_api_key: str | None = os.getenv("NVIDIA_API_KEY")
    nvidia_base_url: str = os.getenv(
        "NVIDIA_BASE_URL",
        "https://integrate.api.nvidia.com/v1",
    )
    nvidia_model: str = os.getenv("NVIDIA_MODEL", "z-ai/glm-5.2")


settings = Settings()
