"""
Quick smoke test for the NVIDIA NIM API.

Usage:
    export NVIDIA_API_KEY="nvapi-..."
    python scripts/test_nvidia_api.py
"""

import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


NVIDIA_BASE_URL = os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")
NVIDIA_MODEL = os.getenv("NVIDIA_MODEL", "z-ai/glm-5.2")


def main() -> None:
    api_key = os.getenv("NVIDIA_API_KEY")
    if not api_key:
        raise SystemExit("Missing NVIDIA_API_KEY environment variable")

    client = OpenAI(base_url=NVIDIA_BASE_URL, api_key=api_key)
    response = client.chat.completions.create(
        model=NVIDIA_MODEL,
        messages=[
            {
                "role": "user",
                "content": "한국어로 한 문장만 답해줘. NVIDIA NIM API 테스트 성공 메시지를 써줘.",
            }
        ],
        temperature=0,
        max_tokens=200,
    )

    print(response.choices[0].message.content)


if __name__ == "__main__":
    main()
