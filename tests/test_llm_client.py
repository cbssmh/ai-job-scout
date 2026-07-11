from unittest.mock import patch

import pytest

from app.config import Settings
from app.llm.client import get_llm_client_config


def test_nvidia_provider_config_succeeds_with_valid_settings():
    config = Settings(
        llm_provider="nvidia",
        nvidia_api_key="test-nvidia-key",
        nvidia_base_url="https://integrate.api.nvidia.com/v1",
        nvidia_model="z-ai/glm-5.2",
    )

    with patch("app.llm.client.OpenAI") as mock_openai:
        mock_client = object()
        mock_openai.return_value = mock_client

        result = get_llm_client_config(config)

    assert result.provider == "nvidia"
    assert result.model == "z-ai/glm-5.2"
    assert result.client is mock_client
    mock_openai.assert_called_once_with(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key="test-nvidia-key",
    )


def test_unsupported_provider_raises_clear_error():
    config = Settings(llm_provider="groq")

    with pytest.raises(ValueError) as exc_info:
        get_llm_client_config(config)

    assert "Unsupported LLM_PROVIDER 'groq'" in str(exc_info.value)
    assert "openai, nvidia" in str(exc_info.value)


def test_missing_nvidia_api_key_raises_clear_error():
    config = Settings(
        llm_provider="nvidia",
        nvidia_api_key="",
        nvidia_model="z-ai/glm-5.2",
    )

    with pytest.raises(ValueError) as exc_info:
        get_llm_client_config(config)

    assert (
        "NVIDIA_API_KEY is missing. Set NVIDIA_API_KEY in .env before using the "
        "NVIDIA provider."
    ) in str(exc_info.value)


def test_missing_nvidia_model_raises_clear_error():
    config = Settings(
        llm_provider="nvidia",
        nvidia_api_key="test-nvidia-key",
        nvidia_model=" ",
    )

    with pytest.raises(ValueError) as exc_info:
        get_llm_client_config(config)

    assert (
        "NVIDIA_MODEL is missing. Set NVIDIA_MODEL in .env before using the "
        "NVIDIA provider."
    ) in str(exc_info.value)
