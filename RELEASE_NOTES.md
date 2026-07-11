# Release Notes

## v1.0.0 - AI Job Scout MVP

AI Job Scout MVP is a portfolio-ready backend application for crawling software engineering jobs, extracting structured job signals, and returning explainable recommendations.

### Highlights

- AI-assisted structured job analysis for role, technology stack, experience level, language requirement, visa signal, and summary
- Deterministic recommendation scoring with skill, language, visa, and location score components
- Lightweight NVIDIA NIM provider support through an OpenAI-compatible API
- FastAPI REST API with Swagger documentation
- Docker Compose development environment
- Greenhouse job ingestion and job lifecycle handling
- Focused automated test suite for scoring, parsing, lifecycle, health routes, and provider configuration

### Installation Notes

Python 3.11+ is required.

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Create local environment variables:

```bash
cp .env.example .env
```

NVIDIA NIM development setup:

```env
LLM_PROVIDER=nvidia
NVIDIA_API_KEY=your_nvidia_api_key_here
NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1
NVIDIA_MODEL=z-ai/glm-5.2
```

Run tests:

```bash
python -m pytest
```

Optional manual NVIDIA smoke test:

```bash
python scripts/test_nvidia_api.py
```

### Known Limitations

- NVIDIA free access is externally controlled and may change.
- No automatic paid provider fallback is implemented by design.
- SQLite is used for local development and portfolio demonstration.
- Recommendation scoring is explainable but intentionally simple.
- Dependencies are not pinned yet, so reproducibility can vary across fresh installs.

### Not Included

- Provider benchmarking
- Cost or token dashboards
- Model routing
- Deployment automation
- GitHub Package publishing
- Production traffic or uptime claims
